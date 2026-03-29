# Frontend API Suite (for designers)

This folder contains a **single FastAPI app** exposing all callable endpoints intended for frontend integration and UI design.

## Start

From project root:

```bash
pip install -r frontend_api/requirements.txt
uvicorn frontend_api.main:app --reload --port 8100
```

Production UI lives in **`real_frontend/`** (start with `cd real_frontend && npm run dev`). Static demo-only UI: **`mock_frontend/`**. System docs: `docs/system-overview.en.md` (Chinese: `docs/system-overview.zh-CN.md`).

Open API docs:

- Swagger: `http://localhost:8100/docs`
- OpenAPI JSON: `http://localhost:8100/openapi.json`

---

## Endpoint list

### Health

- `GET /health`

Returns service status.

---

### Evaluation APIs

- `POST /evaluate/expert1-attack`
  - Runs Expert 1 only (Mode A/B).
  - Use for quick security/adversarial testing demos.

- `POST /evaluate/council`
  - Runs full council pipeline:
    - 3 experts in parallel
    - 6 directional critiques
    - rules-based arbitration
    - auto persistence to report file + sqlite + knowledge index

---

### Report history APIs

- `GET /evaluations?limit=20&offset=0`
  - List historical evaluations from SQLite.

- `GET /evaluations/{incident_id}`
  - Get full saved `CouncilReport` JSON.

- `GET /evaluations/{incident_id}/markdown`
  - Download report as Markdown.

---

### Knowledge index APIs

- `GET /knowledge/index?limit=20`
  - Read latest records from `knowledge_index.jsonl`.

- `GET /knowledge/search?query=...&limit=20`
  - Simple search over SQLite summaries (`summary_core`) + ids/names.

---

## Notes for frontend designers

- This suite is designed to be self-describing via `/docs`; use request schemas directly from Swagger.
- CORS is enabled (`allow_origins=["*"]`) for local frontend prototyping.
- Recommended base URL for frontend mock integration:
  - `http://localhost:8100`

---

## Example request (full council)

```json
{
  "agent_id": "unhcr-allocator-v2.1",
  "system_name": "UNHCR Resource Allocation Assistant",
  "system_description": "Long system description here...",
  "purpose": "Humanitarian resource allocation",
  "deployment_context": "UNHCR field operations",
  "data_access": ["beneficiary_records", "case_files"],
  "risk_indicators": ["PII", "vulnerable populations"],
  "backend": "claude",
  "vllm_base_url": "http://localhost:8000",
  "vllm_model": "meta-llama/Meta-Llama-3-70B-Instruct"
}
```

---

## Files in this folder

- `main.py` — API implementation
- `requirements.txt` — runtime dependencies
- `README.md` — endpoint guide for frontend/UI teams

