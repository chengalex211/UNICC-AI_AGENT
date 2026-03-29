# UNICC AI Safety Council (English Overview)

Multi‑expert AI safety evaluation pipeline for UN / humanitarian deployments.  
Three virtual experts plus a rules‑based council produce structured safety reports for any AI system description (including agents with tools/MCP/skills).

**Production web UI:** `real_frontend/` + `frontend_api/` (port 8100). System docs: `docs/system-overview.en.md`. Static demo only: `mock_frontend/`.

---

## 1. What the system does

**Input**
- `agent_id`: machine‑readable ID (e.g. `refugee-assist-v2`)
- `system_description`: natural‑language description or text extracted from PDF/JSON/Markdown
- optional metadata: purpose, deployment context, data access, risk indicators

**Process**
1. Three independent experts assess the same system description:
   - **Expert 1 — Security & Adversarial Testing**
     - Technical security, adversarial robustness, privacy, self‑preservation.
     - Mode A: document‑only analysis (no live attacks).
     - Mode B: full PROBE → BOUNDARY → ATTACK using an adapter to a live agent.
   - **Expert 2 — Governance & Regulatory Compliance**
     - EU AI Act, GDPR, NIST AI RMF, UNESCO etc., via agentic RAG + legal KB.
   - **Expert 3 — UN Mission Fit & Human Rights**
     - UN Charter, ICESCR, humanitarian law, UNESCO AI ethics.
2. Council generates **6 directional critiques** (each expert critiques the other two).
3. **Arbitration layer (pure code, no LLM)**:
   - Aggregates expert recommendations (most conservative wins).
   - Computes consensus level (FULL / PARTIAL / SPLIT).
   - Detects disagreements on key dimensions (privacy / transparency / bias).
4. Assembles a **`CouncilReport`**:
   - `expert_reports`, `critiques`, `council_decision`, `council_note`.
5. Persists the report into:
   - Full JSON file store
   - SQLite database
   - JSONL index for future knowledge/embedding use

**Output**
- Machine‑readable `CouncilReport` (JSON).
- Human‑friendly Final Report page + Markdown export (frontend).

---

## 2. High‑level architecture

```text
Frontend (React + Vite + Tailwind)
   │
   │ HTTP
   ▼
API layer (FastAPI now, Council API later)
   │
   ▼
Council Orchestrator (Python / council/)
   ├─ Run Expert1 / Expert2 / Expert3 in parallel
   ├─ Generate 6 directional Critiques
   ├─ Rules‑based arbitration → CouncilDecision
   └─ persist_report() → files + SQLite + JSONL index

Experts:
   - Expert1: Security & Adversarial Testing (Mode A/B)
   - Expert2: Governance & Compliance (Agentic RAG + Chroma)
   - Expert3: UN Mission Fit (Agentic RAG + Chroma)

Model backends:
   - Claude (development / demo)
   - vLLM (Llama 3‑70B) for SLM / on‑prem deployment
```

---

## 3. Repository layout (simplified)

```text
Capstone/
├── api/
│   ├── main.py                  # Expert1 HTTP API (POST /evaluate/expert1-attack)
│   └── requirements.txt
│
├── council/
│   ├── agent_submission.py      # AgentSubmission input dataclass
│   ├── council_orchestrator.py  # Orchestrator: 3 experts + critiques + arbitration
│   ├── council_report.py        # CouncilReport / CouncilDecision / CritiqueResult
│   ├── critique.py              # Builds critique contexts, calls critique LLM
│   ├── storage.py               # Persist CouncilReport to JSON, SQLite, JSONL
│   ├── slm_backends.py          # vLLM client (Llama 3‑70B)
│   ├── slm_experts.py           # SLM wrappers for Expert2/3
│   ├── reports/                 # Auto‑generated full CouncilReport JSON files
│   ├── council.db               # SQLite DB: evaluations table
│   └── knowledge_index.jsonl    # JSONL index: summary_core + raw dict per incident
│
├── Expert1/                     # Expert 1: Security & Adversarial Testing
│   ├── expert1_module.py        # run_full_evaluation(profile, adapter, llm)
│   ├── expert1_router.py        # PROBE / BOUNDARY / ATTACK orchestration
│   ├── expert1_system_prompts.py
│   ├── adapters/                # MockAdapter / ApiAdapter / WebAdapter
│   └── rag/                     # ATLAS/OWASP/NIST attack technique KB
│
├── Expert 2/                    # Expert 2: Governance & Compliance
│   ├── expert2_agent.py         # Agentic RAG engine
│   └── chroma_db_expert2/       # Legal KB
│
├── Expert 3/                    # Expert 3: UN Mission Fit
│   ├── expert3_agent.py         # Agentic RAG engine
│   └── expert3_rag/             # UN/UNESCO KB
│
├── real_frontend/               # Production UI → frontend_api :8100, full Council flow
│   ├── src/api/client.ts
│   ├── src/utils/mapCouncilReport.ts
│   ├── src/utils/parseAgentDoc.ts
│   ├── src/utils/reportToMarkdown.ts
│   └── src/pages/…
├── mock_frontend/               # Static demo only (no API); see mock_frontend/README.md
│
├── frontend_api/                # FastAPI: POST /evaluate/council, history, markdown, etc.
```

---

## 4. Core Python APIs

### 4.1 Council evaluation (Python)

```python
from council.council_orchestrator import evaluate_agent

report = evaluate_agent(
    agent_id=\"refugee-assist-v2\",
    system_description=\"...\",   # from text or parsed PDF/JSON/MD
    system_name=\"RefugeeAssist v2\",
    backend=\"claude\",          # or \"vllm\" when using Llama 3‑70B
)

print(report.council_decision.final_recommendation)
print(report.incident_id)
```

`evaluate_agent(...)` will internally:

1. Construct an `AgentSubmission`.
2. Run `CouncilOrchestrator.evaluate(submission)`.
3. Persist the resulting `CouncilReport` via `storage.persist_report()`:
   - `council/reports/{incident_id}.json`
   - `council/council.db` (evaluations table)
   - `council/knowledge_index.jsonl` (summary_core + raw dict)

### 4.2 Expert 1 HTTP API

```bash
cd /path/to/Capstone
pip install -r api/requirements.txt
uvicorn api.main:app --reload --port 8000
# Docs at: http://localhost:8000/docs
```

Example request:

```json
POST /evaluate/expert1-attack
{
  \"agent_id\": \"refugee-assist-v2\",
  \"system_name\": \"RefugeeAssist v2\",
  \"system_description\": \"...\",
  \"purpose\": \"Humanitarian aid allocation\",
  \"deployment_context\": \"UNHCR field office, Syria\",
  \"data_access\": [\"beneficiary_records\", \"case_files\"],
  \"risk_indicators\": [\"PII\", \"conflict_zone\"],
  \"mode\": \"A\" | \"B\",
  \"mock_level\": \"low\" | \"medium\" | \"high\",
  \"backend\": \"claude\" | \"mock\"
}
```

- `mode = \"A\"` → document‑only analysis.
- `mode = \"B\"` → full active attack pipeline using MockAdapter.

---

## 5. Frontend usage (developer quickstart)

**Production app (`real_frontend`)**

```bash
cd real_frontend
npm install
npm run dev
# http://localhost:5173
```

Start **`frontend_api`** (required for live Council + dashboard history):

```bash
cd ..
pip install -r frontend_api/requirements.txt
uvicorn frontend_api.main:app --reload --port 8100
```

Flow:

1. `Dashboard` loads evaluations from `GET /evaluations`.
2. `New Evaluation` → paste text or upload PDF/JSON/MD → `POST /evaluate/council`.
3. `Report` steps use **`mapCouncilReport`** on the returned JSON (live data, not static mock).
4. `Final Report` → Markdown download via `reportToMarkdown.ts`.

System overview: **`docs/system-overview.en.md`** (Chinese: **`docs/system-overview.zh-CN.md`**).

**Static demo (`mock_frontend`)** — no backend:

```bash
cd mock_frontend && npm install && npm run dev
```

See **`mock_frontend/README.md`**.

---

## 6. Roadmap (short)

- Build a vector‑based knowledge memory from `knowledge_index.jsonl` (embeddings over `summary_core`) to:
  - retrieve similar past incidents,
  - provide few‑shot context to experts.
- Extend Final Report export from Markdown to PDF.
- Optional “repo → system_description” analyzer module.
- Fine‑tune Llama 3‑70B on the expert and critique training data and switch `backend=\"vllm\"` by default for on‑prem deployment.

