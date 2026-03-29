# UNICC AI Safety Council — System Overview (English)

> Chinese version: [system-overview.zh-CN.md](./system-overview.zh-CN.md)

---

## 1. What this system is

**UNICC AI Safety Council** is an **AI safety evaluation pipeline** aimed at UN and humanitarian contexts. For a candidate AI system, it runs **three experts in parallel → six directional cross-critiques → rule-based arbitration**, and returns structured outcomes (approve / review / reject) with auditable rationale.

Targets include chatbots, agents, and tool/MCP-enabled systems. The main input is a **system description** (pasted by the user or extracted from PDF / JSON / Markdown uploads).

---

## 2. Goals and outputs

| Pillar | Role |
|--------|------|
| **Expert 1 — Security & adversarial** | Technical risk, robustness, privacy, deception, etc.; document-only or full active probing (see Expert1 module and standalone API). |
| **Expert 2 — Governance & compliance** | EU AI Act, GDPR, NIST, UNESCO, etc.; agentic RAG over a legal knowledge base. |
| **Expert 3 — UN mission fit** | UN Charter, humanitarian principles, UNESCO ethics; agentic RAG over UN-related KB. |
| **Council** | Six directed critiques (e.g., governance on security), then **rule-based arbitration** for `final_recommendation`, consensus, human oversight flags, etc. |

**Primary artifact: `CouncilReport` (JSON)** with `expert_reports`, `critiques`, `council_decision`, `council_note`, `incident_id`, etc. Persistence:

- `council/reports/{incident_id}.json`
- `council/council.db` (SQLite for lists and search)
- `council/knowledge_index.jsonl` (summary + raw dict for future embedding workflows)

---

## 3. Architecture (high level)

```
User / real_frontend
        │
        ▼
frontend_api :8100  ──POST /evaluate/council──►  CouncilOrchestrator
        │                      │
        │                      ├── Run Expert 1 / 2 / 3 in parallel
        │                      ├── Generate six critiques in parallel
        │                      ├── Arbitrate → council_decision
        │                      └── persist_report → JSON / DB / JSONL
        │
GET /evaluations / GET /evaluations/{id} / …/markdown
```

Optional: **`api/` on :8000** exposes **Expert 1 only**: `POST /evaluate/expert1-attack` (Mode A/B), independent of the full Council HTTP path.

Model backends: **Claude API** (dev/demo) or **vLLM + Llama 3 70B** (on-prem), configured in `council` and expert modules.

---

## 4. Repository layout (Capstone root)

| Path | Role |
|------|------|
| `council/` | Orchestration, report types, critiques, storage, SLM client helpers. |
| `Expert1/`, `Expert 2/`, `Expert 3/` | Expert implementations and assets. |
| `frontend_api/` | **Recommended** FastAPI surface: Council, history, Markdown download. |
| `api/` | Standalone Expert 1 HTTP service. |
| `real_frontend/` | Production web UI; targets `frontend_api` **8100** by default. |
| `mock_frontend/` | Static demo UI; **no** backend calls; `mockData.ts` only. |
| `benchmark_data/`, etc. | Benchmarks and annotations where present. |
| `UNICC-Project-2/` | Optional sibling project copy; in the full monorepo, production UI lives at repo-root `real_frontend/`. |

---

## 5. Quick start

### 5.1 Full Council (Python)

```bash
cd /path/to/Capstone
export ANTHROPIC_API_KEY=...   # or configure vLLM

python -c "
from council.council_orchestrator import evaluate_agent
r = evaluate_agent(
    agent_id='demo-001',
    system_description='System description text...',
    system_name='Demo',
    backend='claude',
)
print(r.incident_id)
"
```

### 5.2 Web UI + frontend_api (recommended)

```bash
# Terminal 1
pip install -r frontend_api/requirements.txt
uvicorn frontend_api.main:app --reload --port 8100

# Terminal 2
cd real_frontend && npm install && npm run dev
```

Open the URL Vite prints (usually `http://localhost:5173`). **New Evaluation** calls `POST /evaluate/council`; **Dashboard** uses `GET /evaluations`.

### 5.3 Expert 1 API only

```bash
pip install -r api/requirements.txt
uvicorn api.main:app --reload --port 8000
```

Swagger: `http://localhost:8000/docs`.

### 5.4 Static demo UI

```bash
cd mock_frontend && npm install && npm run dev
```

No Python required. See `mock_frontend/README.md`.

---

## 6. HTTP API summary (frontend_api)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness |
| POST | `/evaluate/council` | Full Council run + persist |
| POST | `/evaluate/expert1-attack` | Expert 1 only |
| GET | `/evaluations` | Paginated history |
| GET | `/evaluations/{incident_id}` | Full report JSON |
| GET | `/evaluations/{incident_id}/markdown` | Markdown attachment |
| GET | `/knowledge/index` | Slice of JSONL index |
| GET | `/knowledge/search` | Simple text search |

OpenAPI: `http://localhost:8100/docs`.

---

## 7. Core data contract (integrators & frontend)

**Evaluation request (minimal)**

- `agent_id` (string)
- `system_name` (display)
- `system_description` (main long text)
- Optional: `purpose`, `deployment_context`, `data_access`, `risk_indicators`, `backend` (`claude` / `vllm`), etc.

**Response**: JSON aligned with shapes like `council/test_output_refugeeassist.json` (includes `incident_id`).

The production app maps JSON to UI via `real_frontend/src/utils/mapCouncilReport.ts`. **Final Report** supports client-side **Markdown export**.

---

## 8. Configuration and safety

### Backend server

| Variable | Role |
|----------|------|
| `ANTHROPIC_API_KEY` | Required for Claude backend (`backend=claude`) |
| — | For vLLM: pass `vllm_base_url` and `vllm_model` in the request body |

### Frontend (`real_frontend`) — copy `real_frontend/.env.example` → `real_frontend/.env.local`

| Variable | Default | Role |
|----------|---------|------|
| `VITE_API_URL` | `http://localhost:8100` | Points the UI at the `frontend_api` server |
| `VITE_COUNCIL_BACKEND` | `claude` | Pre-selects backend in the New Evaluation form (`claude` or `vllm`) |
| `VITE_VLLM_BASE_URL` | `http://127.0.0.1:8000` | vLLM inference server URL |
| `VITE_VLLM_MODEL` | `meta-llama/Meta-Llama-3-70B-Instruct` | Model name sent to vLLM |

**Never commit `.env` / `.env.local`.** Root `.gitignore` covers `.env*`, `node_modules/`, `__pycache__/`, etc. The `.env.example` template files are intentionally tracked.

---

## 9. Scope limits and roadmap

**Not included today (extend as needed):**

- Auto **repo analysis** (GitHub/local tree → system description).
- **PDF** report export (JSON and Markdown are supported; UI exports Markdown).
- **Vector / similar-case** retrieval over `knowledge_index.jsonl` (index exists; retrieval service is future work).

**Possible next steps:** PDF export, embedding-based memory, LoRA on vLLM for experts/critiques, finer RBAC and audit logs.

---

## 10. Documentation index

| Doc | Description |
|-----|-------------|
| This file `system-overview.en.md` | System overview (English) |
| `system-overview.zh-CN.md` | Same (Chinese) |
| Root `README.md` | English overview (GitHub default) |
| `frontend_api/README.md` | How to run API and sample payloads |
| `mock_frontend/README.md` | Static UI notes |

---

*Update this document when behavior changes; OpenAPI and code remain authoritative.*
