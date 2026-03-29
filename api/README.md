# Expert 1 主动攻击 API

对提交的 AI 系统描述执行 **Expert 1 完整流程**（PROBE → BOUNDARY → **ATTACK**），使用 MockAdapter 模拟被测 Agent，返回完整报告。

## 安装与运行

**必须在 Capstone 项目根目录**（即与 `api/` 同级的目录）执行，否则会报 `ModuleNotFoundError: No module named 'api'`：

```bash
cd /path/to/Capstone
pip install -r api/requirements.txt
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

- 文档与试玩: http://localhost:8000/docs  
- 健康检查: http://localhost:8000/health  

## 接口说明

### `POST /evaluate/expert1-attack`

**请求体 (JSON):**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| agent_id | string | 是 | 唯一标识 |
| system_name | string | 否 | 展示名称，默认用 agent_id |
| system_description | string | 是 | 系统描述（供 Expert 1 分析与攻击） |
| purpose | string | 否 | 用途说明 |
| deployment_context | string | 否 | 部署场景 |
| data_access | string[] | 否 | 数据访问类型 |
| risk_indicators | string[] | 否 | 风险关键词 |
| mock_level | string | 否 | Mock 被测 Agent 等级：`low` \| `medium` \| `high`，默认 `medium` |
| backend | string | 否 | LLM 后端：`claude` \| `mock`，默认 `claude`。`mock` 无需 API Key，仅用于联调 |

**响应:** Expert 1 完整报告（JSON），含 `phase_summaries.attack`、`test_coverage.attack_techniques_tested`、维度打分等。

**示例:**

```bash
curl -X POST http://localhost:8000/evaluate/expert1-attack \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "refugee-assist-v2",
    "system_name": "RefugeeAssist v2",
    "system_description": "AI system that allocates humanitarian resources to refugees in conflict zones, processes intake forms and UNHCR data.",
    "deployment_context": "UNHCR field office, Syria",
    "data_access": ["beneficiary_records", "case_files"],
    "risk_indicators": ["PII", "vulnerable population"],
    "mock_level": "medium",
    "backend": "mock"
  }'
```

## 依赖与前置条件

- **Expert 1 目录**: 项目根下需存在 `Expert1/`（含 `expert1_module.py`、`expert1_router.py`、`adapters/`、`rag/`）。
- **RAG（可选但推荐）**: 主动攻击会从 ATLAS/OWASP 等选技术，若未构建 RAG 可能退化为 fallback。在 `Expert1` 目录下执行：
  ```bash
  cd Expert1 && python rag/build_rag_expert1.py
  ```
- **Claude 后端**: 使用 `backend: "claude"` 时需设置环境变量 `ANTHROPIC_API_KEY`。仅联调时可使用 `backend: "mock"` 避免调用真实 LLM。
