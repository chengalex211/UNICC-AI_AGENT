# UNICC AI Safety Council — 系统说明（中文版）

> 英文版见同目录：[system-overview.en.md](./system-overview.en.md)

---

## 1. 系统是什么

**UNICC AI Safety Council** 是一套面向联合国与人道主义场景的 **AI 安全评估流水线**：对「待部署的 AI 系统」进行多维度分析，通过三位虚拟专家并行评估、六条定向交叉批评、规则仲裁，输出结构化结论（通过 / 需复核 / 不通过）及可追溯依据。

评估对象可以是聊天机器人、Agent、带工具或 MCP 的系统等。核心输入是一段**系统描述文本**，可由用户粘贴，或从 PDF、JSON、Markdown 文件解析得到。

---

## 2. 专家角色与产出

| 专家 | 典型入口 | 评估重点 |
|------|----------|----------|
| **Expert 1 — 安全与对抗** | `Expert1/expert1_module.py` | 技术风险、对抗鲁棒性、隐私、欺骗；可选纯文档分析或完整主动攻击（Mode A/B） |
| **Expert 2 — 治理与合规** | `Expert 2/expert2_agent.py` + ChromaDB | EU AI Act、GDPR、NIST、UNESCO 等；Agentic RAG 检索法规知识库 |
| **Expert 3 — UN 使命契合** | `Expert 3/expert3_agent.py` + RAG | UN Charter、人道原则、UNESCO 伦理；Agentic RAG 检索 UN 知识库 |
| **Council** | `council/council_orchestrator.py` | 六条定向批评 + 规则仲裁 → `final_recommendation`、共识程度、是否需人工监督 |

**主要产出：`CouncilReport`（JSON）**，包含 `expert_reports`、`critiques`、`council_decision`、`council_note`、`incident_id` 等。

持久化层：

| 层 | 路径 | 用途 |
|----|------|------|
| 完整报告 | `council/reports/{incident_id}.json` | 无损归档 |
| SQLite | `council/council.db`，表 `evaluations` | 列表与检索 API、看板历史 |
| 知识索引 | `council/knowledge_index.jsonl` | 每次运行的 `summary_core` + 原始 dict，为未来嵌入检索预留 |

---

## 3. 架构概览

```
用户 / real_frontend
        │
        ▼
frontend_api :8100  ──POST /evaluate/council──►  CouncilOrchestrator
        │                      │
        │                      ├── 并行运行 Expert 1 / 2 / 3
        │                      ├── 并行生成六条批评
        │                      ├── 仲裁 → council_decision
        │                      └── persist_report → JSON / DB / JSONL
        │
GET /evaluations / GET /evaluations/{id} / …/markdown
```

可选：**`api/` on :8000** 仅暴露 Expert 1：`POST /evaluate/expert1-attack`（Mode A/B），与完整 Council HTTP 流程独立。

模型后端：**Claude API**（开发演示）或 **vLLM + Llama 3 70B**（本地部署），在请求体或环境变量中切换。

---

## 4. 仓库结构（Capstone 根目录）

| 路径 | 说明 |
|------|------|
| `council/` | 编排、报告结构、批评、存储、SLM 后端封装等 |
| `Expert1/`、`Expert 2/`、`Expert 3/` | 各专家实现、ChromaDB、RAG 数据 |
| `frontend_api/` | **推荐**：面向前端的 FastAPI（Council、历史、Markdown 下载等） |
| `api/` | Expert 1 独立 HTTP 服务 |
| `real_frontend/` | 生产 Web UI；默认请求 `frontend_api` **8100** |
| `mock_frontend/` | 静态演示 UI；**不调后端**；数据来自 `mockData.ts` |
| `benchmark_data/` 等 | 基准与标注数据（若存在） |
| `UNICC-Project-2/` | 可与本仓库并存的子项目；完整 monorepo 下生产前端在根的 `real_frontend/` |

---

## 5. 快速运行

### 5.1 完整前端 + Council API（推荐）

```bash
cd /path/to/Capstone
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r frontend_api/requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
uvicorn frontend_api.main:app --reload --port 8100
```

```bash
cd real_frontend && npm install && npm run dev
```

浏览器打开 Vite 提示的地址（通常 `http://localhost:5173`）。New Evaluation 调用 `POST /evaluate/council`；Dashboard 使用 `GET /evaluations`。

### 5.2 仅 Python（无前端）

```python
from council.council_orchestrator import evaluate_agent

report = evaluate_agent(
    agent_id="demo-001",
    system_description="待评估系统的自然语言描述……",
    system_name="Demo",
    backend="claude",       # 或 "vllm"
)
print(report.incident_id)
print(report.council_decision)
```

### 5.3 仅 Expert 1 API

```bash
pip install -r api/requirements.txt
uvicorn api.main:app --reload --port 8000
```

Swagger：`http://localhost:8000/docs`

### 5.4 静态演示前端（无需 Python）

```bash
cd mock_frontend && npm install && npm run dev
```

说明见 `mock_frontend/README.zh-CN.md`。

---

## 6. HTTP API 摘要（frontend_api）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| POST | `/evaluate/council` | 完整 Council 评估并持久化 |
| POST | `/evaluate/expert1-attack` | 仅 Expert 1 |
| GET | `/evaluations` | 历史列表（分页：`limit`、`offset`） |
| GET | `/evaluations/{incident_id}` | 完整报告 JSON |
| GET | `/evaluations/{incident_id}/markdown` | 报告 Markdown 附件下载 |
| GET | `/knowledge/index` | JSONL 知识索引切片 |
| GET | `/knowledge/search` | 摘要 / ID 文本搜索 |

OpenAPI：`http://localhost:8100/docs`

---

## 7. 核心数据契约

**提交评估（最少字段）：**

- `agent_id`（string，唯一标识）
- `system_name`（展示名）
- `system_description`（长文本，评估主输入）
- 可选：`purpose`、`deployment_context`、`data_access`、`risk_indicators`、`backend`（`claude` 或 `vllm`）、`vllm_base_url`、`vllm_model`

**`CouncilReport` 响应关键字段：**

- `incident_id` — 存储 ID（如 `inc_YYYYMMDD_agent_suffix`）
- `expert_reports` — 含 `security`、`governance`、`un_mission_fit` 三个子块
- `critiques` — 六条定向批评对象
- `council_decision` — `final_recommendation`、`consensus_level`、flags
- `council_note` — 简短叙述摘要

数据类定义：`council/council_report.py`；提交数据类：`council/agent_submission.py`。参考输出：`council/test_output_refugeeassist.json`。

生产前端通过 `real_frontend/src/utils/mapCouncilReport.ts` 将 JSON 映射为界面模型；Final Report 支持浏览器端 Markdown 导出。

---

## 8. 配置与安全

### 后端服务器

| 变量 | 说明 |
|------|------|
| `ANTHROPIC_API_KEY` | Claude 后端必需 |
| — | vLLM 后端：在请求体传 `vllm_base_url` 和 `vllm_model` |

### 前端（`real_frontend`）— 复制 `real_frontend/.env.example` 为 `real_frontend/.env.local`

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `VITE_API_URL` | `http://localhost:8100` | 指向 `frontend_api` 的地址 |
| `VITE_COUNCIL_BACKEND` | `claude` | 预设前端默认后端（`claude` 或 `vllm`） |
| `VITE_VLLM_BASE_URL` | `http://127.0.0.1:8000` | vLLM 推理服务地址 |
| `VITE_VLLM_MODEL` | `meta-llama/Meta-Llama-3-70B-Instruct` | 发送给 vLLM 的模型名称 |

**勿将 `.env` / `.env.local` 提交到 Git。** 根目录 `.gitignore` 已忽略 `.env*`、`node_modules/`、`__pycache__/` 等；`.env.example` 模板文件可以追踪。

---

## 9. 核心文件索引（不完整）

```
council/
├── agent_submission.py       # AgentSubmission 数据类
├── council_orchestrator.py   # evaluate_agent、CouncilOrchestrator
├── council_report.py         # CouncilReport、CouncilDecision、CritiqueResult
├── critique.py               # 六条定向批评生成
├── storage.py                # JSON + SQLite + JSONL 写入
├── slm_backends.py           # vLLM 客户端封装
└── slm_experts.py            # Expert 2/3 在 SLM 上的调用

frontend_api/
├── main.py                   # 全部 :8100 路由
└── requirements.txt

real_frontend/
├── src/api/client.ts         # HTTP 客户端与类型定义
├── src/utils/mapCouncilReport.ts   # JSON → UI 模型映射
├── src/utils/parseAgentDoc.ts      # PDF / JSON / Markdown 解析
├── src/utils/reportToMarkdown.ts   # 报告 Markdown 导出
└── src/pages/*.tsx           # 各页面（NewEvaluation、FinalReport 等）
```

---

## 10. 故障排查

| 症状 | 排查方向 |
|------|----------|
| Dashboard 无法加载 | 确认 `frontend_api` 在 **8100** 运行；检查 `GET /health`；浏览器控制台 CORS 报错 |
| `evaluate/council` 请求挂起 | 模型延迟正常（Claude 需网络，vLLM 需 GPU）；看服务器日志；确认 API Key 或 vLLM 地址可达 |
| 专家模块返回空 | Mapper 期望 `security` / `governance` / `un_mission_fit` 三个 key；对照 `test_output_refugeeassist.json` |
| ChromaDB / RAG 报错 | Expert 2 DB 路径：`Expert 2/chroma_db_expert2/`；Expert 3：`Expert 3/expert3_rag/` |
| 前端 vLLM 选项不生效 | `vllm_base_url` 必须从运行 `frontend_api` 的机器可达，不是从浏览器 |

---

## 11. 能力边界与后续方向

**当前未包含：**

- 从 GitHub 或本地目录自动扫描生成系统描述（无独立仓库分析模块）
- 报告 PDF 导出（JSON 与 Markdown 已有；前端可导出 Markdown）
- 基于 `knowledge_index.jsonl` 的向量检索服务（数据已预留）

**可选路线图：** PDF 导出、嵌入向量记忆、vLLM 专家微调（LoRA）、更细 RBAC 与审计日志。

---

## 12. 文档索引

| 文件 | 说明 |
|------|------|
| 本文 `system-overview.zh-CN.md` | 系统总览（中文） |
| `system-overview.en.md` | 同上（英文） |
| 仓库根 `README.md` | 英文概览（GitHub 默认展示） |
| `frontend_api/README.md` | API 启动与示例 payload |
| `mock_frontend/README.zh-CN.md` | 静态前端说明 |
| `real_frontend/.env.example` | 前端环境变量模板 |

*以仓库内实现与 OpenAPI 为准；本文档随代码演进更新。*
