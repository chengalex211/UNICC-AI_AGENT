# UNICC AI Safety Council

AI 安全评估流水线：三位虚拟专家 + 仲裁委员会，用于在联合国 / 人道主义场景下，对 AI 系统进行系统性评估并输出结构化报告。

**生产 Web UI：** `real_frontend/` + `frontend_api/`（端口 8100）。系统说明：`docs/system-overview.zh-CN.md`。静态演示：`mock_frontend/`。

---

## 1. 项目目标

- **评估对象**：拟在 UN 或人道场景下部署的 AI 系统（chatbot、agent、带 MCP/skills 的系统等）
- **评估维度**：
  - **Expert 1 — Security & Adversarial Robustness（安全与对抗）**
  - **Expert 2 — Governance & Regulatory Compliance（治理与合规）**
  - **Expert 3 — UN Mission Fit & Human Rights（UN 使命契合）**
- **最终输出**：
  - 一份 `CouncilReport`（JSON / Markdown），包含：
    - 三位专家完整报告
    - 六条交叉批评（谁 critique 谁）
    - 仲裁层给出的最终建议（APPROVE / REVIEW / REJECT）
    - 共识程度（FULL / PARTIAL / SPLIT）
    - 必要条件 / 建议行动列表

系统可以在两种后端下工作：

- 开发 / 演示：Claude API
- 自主 / 本地：vLLM + Llama 3 70B（SLM）

---

## 2. 整体架构

### 2.1 逻辑架构

```text
Frontend (React)
   │
   │ HTTP
   ▼
API 层 (FastAPI / 未来 Council API)
   │
   ▼
Council Orchestrator (council/)
   ├─ 并行调用 Expert1 / Expert2 / Expert3
   ├─ 生成 6 Directional Critiques
   ├─ 规则仲裁 arbitrate()
   └─ 产出 CouncilReport + 落库 persist_report()

Experts:
   - Expert1: Safety & Adversarial Testing (Mode A/B)
   - Expert2: Governance & Compliance (Agentic RAG)
   - Expert3: UN Mission Fit (Agentic RAG)
```

### 2.2 存储与知识记忆库

系统对每一次完整评估做 **三层存储**：

1. **完整报告文件**（不丢细节）
   - 路径：`council/reports/{incident_id}.json`
   - 内容：`CouncilReport.to_json()` 完整体

2. **结构化数据库（SQLite）**
   - 文件：`council/council.db`
   - 表：`evaluations`
   - 用途：Dashboard 列表、过滤、统计
   - 字段示例：
     - `incident_id`（PK）
     - `agent_id`
     - `system_name`
     - `created_at`
     - `decision`
     - `risk_tier`
     - `consensus`
     - `summary_core`
     - `file_path`

3. **知识索引（JSONL）**
   - 文件：`council/knowledge_index.jsonl`
   - 每行一条记录：
     - `incident_id`
     - `agent_id`
     - `summary_core`（专门为 embedding 设计的短摘要）
     - `decision`
     - `consensus`
     - `timestamp`
     - `raw`（`asdict(CouncilReport)` 全量 dict）
   - 用途：未来可加载到向量库，做“类似案例检索”和 few-shot。

---

## 3. 目录结构（简要）

```text
Capstone/
├── api/
│   ├── main.py                  # Expert1 HTTP API (POST /evaluate/expert1-attack)
│   ├── requirements.txt
│   └── README.md
│
├── council/
│   ├── agent_submission.py      # AgentSubmission 输入结构
│   ├── council_orchestrator.py  # Orchestrator：3 专家 + 批评 + 仲裁 + persist_report
│   ├── council_report.py        # CouncilReport / CouncilDecision / CritiqueResult
│   ├── critique.py              # 6 条批评生成 & 上下文构建
│   ├── storage.py               # 报告落地到 reports/ + SQLite + JSONL 索引
│   ├── slm_backends.py          # vLLM 客户端（Llama 3-70B）
│   ├── slm_experts.py           # Expert2/3 的 SLM 入口
│   ├── reports/                 # 自动生成的完整 CouncilReport JSON
│   ├── council.db               # 自动生成的 SQLite DB
│   └── knowledge_index.jsonl    # 自动生成的知识索引（summary+raw）
│
├── Expert1/                     # 专家 1：安全与对抗
│   ├── expert1_module.py        # run_full_evaluation(profile, adapter, llm)
│   ├── expert1_router.py        # PROBE / BOUNDARY / ATTACK 编排
│   ├── expert1_system_prompts.py
│   ├── adapters/                # MockAdapter / ApiAdapter / WebAdapter
│   └── rag/                     # 攻击技术 & 案例的 RAG 知识库
│
├── Expert 2/                    # 专家 2：治理与合规
│   ├── expert2_agent.py
│   └── chroma_db_expert2/
│
├── Expert 3/                    # 专家 3：UN 使命契合
│   ├── expert3_agent.py
│   └── expert3_rag/
│
├── real_frontend/               # 生产前端：对接 frontend_api（8100），完整 Council 流程
│   ├── src/api/client.ts
│   ├── src/utils/parseAgentDoc.ts
│   ├── src/utils/mapCouncilReport.ts
│   ├── src/utils/reportToMarkdown.ts
│   └── src/pages/…
│
├── mock_frontend/               # 静态演示 UI（不调后端）；说明见 mock_frontend/README*.md
│
├── frontend_api/                # FastAPI：POST /evaluate/council、历史与 Markdown 等
```

---

## 4. 核心数据结构

### 4.1 AgentSubmission

```python
@dataclass
class AgentSubmission:
    agent_id:           str
    system_description: str
    system_name:        str = ""
    metadata:           dict = field(default_factory=dict)
```

- `agent_id`：机器可读 ID（如 `refugee-assist-v2`）
- `system_description`：系统主描述（可从 PDF/JSON/MD 提取）
- `system_name`：展示名
- `metadata`：可选元信息（purpose, deployment_context, data_access, risk_indicators）

### 4.2 CouncilReport（带 incident_id）

```python
@dataclass
class CouncilReport:
    agent_id:   str
    session_id: str
    timestamp:  str
    incident_id: str = \"\"         # 用于知识库和 DB

    expert_reports: dict = field(default_factory=dict)
    critiques:      dict = field(default_factory=dict)
    council_decision: Optional[CouncilDecision] = None
    council_note:   str = \"\"
```

`incident_id` 由 `storage.persist_report()` 自动生成，如：  
`inc_20260317_refugee-assist-v2_a1b2c3`。

---

## 5. Expert1 HTTP API（已实现）

### 5.1 启动

```bash
cd /path/to/Capstone
pip install -r api/requirements.txt
uvicorn api.main:app --reload --port 8000
# 本地文档: http://localhost:8000/docs
```

### 5.2 接口

`POST /evaluate/expert1-attack`

请求体（简化）：

```json
{
  "agent_id": "refugee-assist-v2",
  "system_name": "RefugeeAssist v2",
  "system_description": "...",
  "purpose": "Humanitarian aid allocation",
  "deployment_context": "UNHCR field office, Syria",
  "data_access": ["beneficiary_records", "case_files"],
  "risk_indicators": ["PII", "conflict_zone"],
  "mode": "A" | "B",
  "mock_level": "low" | "medium" | "high",
  "backend": "claude" | "mock"
}
```

- `mode = "A"`：文档分析（无 live 攻击）
- `mode = "B"`：完整主动攻击（MockAdapter 模拟被测 Agent）

返回：Expert 1 报告（包含维度分数、风险等级、关键发现等）。

---

## 6. 前端使用方式（简要）

### 6.1 启动前端

```bash
cd real_frontend
npm install
npm run dev
# http://localhost:5173
```

### 6.2 启动 frontend_api（生产前端必需）

```bash
cd ..   # 回到 Capstone 根目录
pip install -r frontend_api/requirements.txt
uvicorn frontend_api.main:app --reload --port 8100
```

### 6.3 可选：仅 Expert 1 API（端口 8000）

```bash
uvicorn api.main:app --reload --port 8000
```

### 6.4 在浏览器里体验流程（real_frontend）

1. 打开 Dashboard → 从 **frontend_api** 拉取历史评估列表。
2. **New Evaluation**：填写系统信息；可粘贴描述或上传 PDF / JSON / Markdown（前端解析进表单）。
3. **Submit** → 调用 **POST /evaluate/council**，完成后进入 Report：Overview、Expert Analysis、Council Review、Final Report 均基于 **真实 Council JSON**（经 `mapCouncilReport` 映射）。
4. Final Report 支持 **Export Markdown**。系统说明见 **`docs/system-overview.zh-CN.md`**。

### 6.5 静态演示（mock_frontend）

无需后端：`cd mock_frontend && npm run dev`。仅 `mockData`，不调用 API。说明见 **`mock_frontend/README.zh-CN.md`**。

---

## 7. 未来扩展路线

- 用 `knowledge_index.jsonl` + 向量库，实现“类似案例检索”和 few-shot；
- 将 Final Report 导出扩展为 PDF；
- 在 vLLM 上微调 Llama 3-70B，使 Expert1/2/3 和 Council 批评在本地模型上跑通；
- 可选：从代码仓库自动生成 system_description 的「仓库分析」模块。

