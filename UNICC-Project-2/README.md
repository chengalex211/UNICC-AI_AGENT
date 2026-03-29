 

## UNICC AI Safety Council

Unified multi‑expert evaluation pipeline for AI systems deployed in UN and humanitarian contexts.

This project implements a **Council of Experts** architecture: three specialized “experts” independently assess an AI system from different perspectives (security, governance/compliance, UN mission fit), then a **Council** layer generates cross‑expert critiques and an arbitration decision (Approve / Review / Reject) for human reviewers.

The system can run on commercial LLMs (e.g. Claude) or on a local SLM (e.g. Llama 3 70B via vLLM).

---

## 1. High‑level overview

### Goal

Provide a **structured, multi‑perspective safety and compliance assessment** for AI systems that may be deployed in:

- UN agencies and field offices  
- Humanitarian and conflict zones  
- Other high‑stakes public‑sector environments  

Given a **natural‑language description** of an AI system, the Council produces:

- Three **expert reports** (Security, Governance, UN Mission Fit)  
- Six **directional critiques** (each expert reviewing another)  
- A **Council decision** (final recommendation + consensus level + disagreement report)  
- A machine‑readable JSON report that can be rendered in a UI or exported to PDF

### Three experts

- **Expert 1 — Security & Adversarial Testing**
  - Assesses technical risk, adversarial robustness, harmful behaviors, deception, privacy and legal compliance.
  - Supports:
    - **Mode A**: active attack / red‑teaming (when a live API/adapter is available).
    - **Mode B**: documentation‑only analysis (no live system) — currently used by the Council.

- **Expert 2 — Governance & Compliance**
  - Evaluates the system against:
    - EU AI Act (risk tiers, high‑risk requirements, prohibited practices, transparency)
    - GDPR (lawful basis, DPIA, automated decisions)
    - NIST AI RMF
    - UNESCO AI Ethics, UN Human Rights guidance
  - Uses **Agentic RAG**: the model calls a `search_regulations` tool to retrieve specific articles from a legal knowledge base before issuing a final assessment.

- **Expert 3 — UN Mission‑Fit**
  - Evaluates alignment with:
    - UN Charter principles
    - UN Personal Data Protection & Privacy Principles (UNDPP)
    - UNESCO AI Ethics Recommendation
    - Humanitarian principles (humanity, neutrality, impartiality, independence)
  - Also uses **Agentic RAG** via a `search_un_principles` tool.

---

## 2. Repository structure (simplified)

```text
UNICC-Project-2/
├── council/                      # Council core
│   ├── agent_submission.py       # Unified input structure (AgentSubmission)
│   ├── council_orchestrator.py   # Main pipeline orchestrator
│   ├── council_report.py         # CouncilReport / CouncilDecision / CritiqueResult
│   ├── critique.py               # Cross‑expert critique generation (6 directions)
│   ├── slm_backends.py           # vLLM client (Anthropic-compatible, tool calling)
│   ├── slm_experts.py            # E2/E3 SLM wrappers (preserve Agentic RAG)
│   ├── run_slm_demo.py           # CLI demo for Llama 3 70B / vLLM
│   ├── critique_data_final_for_training.jsonl   # Council critique training data
│   └── test_output_refugeeassist.json           # Example full Council output
│
├── Expert1/ (or Expert 1/)       # Expert 1: Security & Adversarial Testing
│   ├── expert1_module.py         # Entry point: run_full_evaluation()
│   ├── expert1_router.py         # Phases + LLMBackend (Claude/VLLM/Mock)
│   ├── expert1_system_prompts.py # Prompts (including doc-analysis Mode B)
│   ├── standard_test_suite.py    # B1–B5 standard tests for Mode A
│   └── ...                       # Data generation / cleaning scripts & training data
│
├── Expert 2/                     # Expert 2: Governance & Compliance
│   ├── expert2_agent.py          # Agentic RAG engine + tools
│   ├── build_rag_expert2.py      # Build ChromaDB legal KB
│   ├── chroma_db_expert2/        # Legal knowledge base
│   └── expert2_training_data_clean.jsonl
│
├── Expert 3/                     # Expert 3: UN Mission Fit
│   ├── expert3_agent.py          # Agentic RAG engine + tools
│   ├── expert3_rag/
│   │   ├── build_rag.py          # Build UN principles KB
│   │   └── chroma_db/            # UN/UNESCO/UNDPP KB
│   └── expert3_training_data/    # Mission-fit training data
│
└── docs/                         # Subproject notes (may lag the monorepo)
    ├── 系统报告_完整版.md
    ├── UNICC_AI安全评估系统_完整说明.md
    └── 前端交接_核心文件一览.md
```

**Full monorepo system docs (authoritative):** `../docs/system-overview.zh-CN.md` and `../docs/system-overview.en.md`.

> Note: the exact Expert 1 folder name may be `Expert1` or ` Expert 1` depending on your local layout. In the README you can normalize it to `Expert1/` for clarity.

> **Web UI:** If you use the full **Capstone** monorepo (parent of `UNICC-Project-2/`), the production React app is **`../real_frontend/`** and the static mock-only UI is **`../mock_frontend/`**. This subfolder no longer ships a `frontend/` directory.

---

## 3. How the Council pipeline works

### 3.1 Input: AgentSubmission

All evaluations start from a unified input object:

```python
from council.agent_submission import AgentSubmission

submission = AgentSubmission(
    agent_id="refugee-assist-v2",
    system_description="""
    System: RefugeeAssist Allocation Engine v2
    Purpose: Automated resource allocation for refugee assistance programs...
    """,
    system_name="RefugeeAssist v2",
    metadata={
        "purpose": "Humanitarian resource allocation",
        "deployment_context": "UNHCR field offices in conflict zones",
        "data_access": ["PII", "special_category_data"],
        "risk_indicators": ["automated_decisions", "no_DPIA"],
    },
)
```

- `system_description` is a free‑text description: what the system does, where it runs, what data it uses, how it is governed.
- All three experts share the same description and add their own perspective.

### 3.2 Round 1 — Three independent expert reports

`CouncilOrchestrator` runs the three experts in parallel:

```python
from council.council_orchestrator import CouncilOrchestrator

orchestrator = CouncilOrchestrator(backend="claude")  # or backend="vllm"
report = orchestrator.evaluate(submission)
```

Round 1:

- **Expert 1 (Security)**:
  - In current Council configuration uses **Mode B (document analysis)**:
    - Reads the system description.
    - Scores seven dimensions: harmfulness, bias_fairness, transparency, deception, privacy, legal_compliance, self_preservation.
    - Produces a risk tier and a recommendation (APPROVE / REVIEW / REJECT).
- **Expert 2 (Governance)**:
  - Uses **Agentic RAG**:
    - Multiple rounds: propose a legal query → `search_regulations` → get legal text → refine → finally call `produce_assessment`.
    - Produces 9 compliance dimensions (PASS / FAIL / UNCLEAR), key gaps, citations, and an overall compliance status.
- **Expert 3 (UN Mission Fit)**:
  - Uses **Agentic RAG** over UN/UNESCO/UNDPP principles:
    - Multiple rounds of `search_un_principles` → `produce_assessment`.
    - Produces four risk dimensions (technical, ethical, legal, societal) and a mission‑fit risk tier.

Each expert also emits a standardized `council_handoff` section (privacy_score, transparency_score, bias_score, human_oversight_required, compliance_blocks_deployment, note) used by the Council.

### 3.3 Round 2 — Six directional critiques

Given the three expert reports, the Council generates six **directional critiques**:

- `security_on_governance`
- `security_on_un_mission_fit`
- `governance_on_security`
- `governance_on_un_mission_fit`
- `un_mission_fit_on_security`
- `un_mission_fit_on_governance`

Each critique answers:  

> “From my professional perspective, how do I view the **other** expert’s report? Where do I agree, where do I disagree, and what new information did they contribute that my framework could not have seen?”

Each `CritiqueResult` includes:

- `from_expert` / `on_expert`
- `agrees` (bool)
- `divergence_type`: `scope_gap` / `framework_difference` / `test_fail_doc_pass` / `test_pass_doc_fail`
- `key_point`: main professional observation
- `new_information`: what the other expert surfaced that this framework missed
- `stance`: e.g. “Maintain original assessment” or “Revise assessment: change from REVIEW to REJECT…”
- `evidence_references`: pointers into the other expert’s findings

### 3.4 Arbitration — Pure code, no LLM

The arbitration layer operates on **pure data**, no LLM calls:

- Selects the **most conservative recommendation** among the three experts:
  - `REJECT` > `REVIEW` > `APPROVE`.
- Computes **consensus level**: FULL / PARTIAL / SPLIT.
- Detects disagreements on key dimensions (privacy, transparency, bias), including type and which experts differ.
- Aggregates whether **human oversight is required** and whether **any expert blocks deployment**.
- Generates a human‑readable rationale string summarizing the decision.

Result is encapsulated in a `CouncilReport`:

```python
from council.council_report import CouncilReport

d = report.to_dict()
# d["expert_reports"]["security"] ...
# d["critiques"]["governance_on_security"] ...
# d["council_decision"]["final_recommendation"] == "REJECT"
```

A full example is available at `council/test_output_refugeeassist.json`.

---

## 4. Model backends (Claude vs Llama 3 70B via vLLM)

The system is designed to work with two backends:

- **Claude (Anthropic API)** — used for development, data generation, and early experiments.
- **Llama 3 70B via vLLM** — planned deployment SLM in a controlled environment.

### 4.1 Switching backend

- At the Council level:

```python
# Claude:
orchestrator = CouncilOrchestrator(backend="claude")

# vLLM (Llama 3 70B):
orchestrator = CouncilOrchestrator(
    backend="vllm",
    vllm_base_url="http://localhost:8000",
    vllm_model="meta-llama/Meta-Llama-3.1-70B-Instruct",
)
```

- For Expert 1:
  - `expert1_router.VLLMBackend` bridges Expert 1 to the same vLLM endpoint.

- For Expert 2 & 3:
  - `council.slm_backends.VLLMChatClient` implements an **Anthropic‑compatible client** on top of a **tool‑calling OpenAI‑style API**, so the existing Agentic RAG logic (tools, tool_choice, multi‑turn conversation) works unchanged with Llama 3 70B.

### 4.2 CLI demo with SLM

```bash
cd UNICC-Project-2/council

# Dry run (no API call)
python run_slm_demo.py --backend vllm --dry-run

# Check vLLM connection
python run_slm_demo.py --backend vllm --check-connection \
  --vllm-url http://localhost:8000 \
  --vllm-model meta-llama/Meta-Llama-3.1-70B-Instruct

# Full evaluation with SLM
python run_slm_demo.py --backend vllm \
  --vllm-url http://localhost:8000 \
  --vllm-model meta-llama/Meta-Llama-3.1-70B-Instruct \
  --out report.json
```

---

## 5. Web UI (Capstone monorepo)

- **`real_frontend/`** (sibling of `UNICC-Project-2/`): production UI wired to **`frontend_api`** (`POST /evaluate/council`, history, etc.). System docs: `docs/system-overview.en.md` in the Capstone root (Chinese: `docs/system-overview.zh-CN.md`).
- **`mock_frontend/`**: static prototype only (`mockData.ts`, no HTTP). See `mock_frontend/README.md`.

The FastAPI suite that wraps `evaluate_agent()` lives in **`frontend_api/`** at the Capstone root.

---

## 6. Training data (high‑level)

The project includes curated training data for:

- **Expert 1 (Security)**:
  - Active attack mode (Mode A) and document‑analysis mode (Mode B).
- **Expert 2 (Governance)**:
  - Clean governance / compliance assessments with citations.
- **Expert 3 (UN Mission Fit)**:
  - Mission‑fit evaluations covering technical, ethical, legal, societal risk.
- **Council critiques**:
  - 282 examples of directional critiques, including:
    - Governance→Security `test_pass_doc_fail` cases
    - Explicit “two independent problems” (L3 narrative) cases
    - Cases where reading both reports is necessary for a full decision.

These JSONL files are used for data analysis and (in SLM deployments) can be used for LoRA fine‑tuning on top of Llama 3 70B.

---

## 7. Getting started (development)

### 7.1 Python environment

```bash
cd UNICC-Project-2
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate

pip install -r Expert1/requirements.txt  # for Expert 1
pip install -r atlas-data/tools/requirements.txt  # if applicable
# plus: chromadb, anthropic, vllm, streamlit, reportlab, etc. as needed
```

(Exact dependency lists may be split across submodules; see per‑folder `requirements.txt`.)

### 7.2 Run a single evaluation (Claude backend)

Set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

Then:

```bash
cd UNICC-Project-2
python - << 'PY'
from council.agent_submission import AgentSubmission
from council.council_orchestrator import evaluate_agent

submission = AgentSubmission(
    agent_id="demo-system-001",
    system_description="...",
    system_name="Demo System",
)

report = evaluate_agent(
    agent_id=submission.agent_id,
    system_description=submission.system_description,
    system_name=submission.system_name,
    backend="claude",
)

print(report.to_json())
PY
```

---

## 8. Status & roadmap

### Current capabilities

- Full Council pipeline (3 experts → 6 critiques → arbitration) for any textual system description.
- Dual backend support: Claude API for development; vLLM + Llama 3 70B for local SLM deployments.
- Legal and UN principles knowledge bases (ChromaDB) for Expert 2 and Expert 3.
- Rich training data for all experts and the Council critique behavior.
- Production + mock frontends in the parent Capstone repo (`real_frontend/`, `mock_frontend/`).

### Planned / possible next steps

- Vector search over `knowledge_index.jsonl` for similar past cases.
- Implement `CouncilReport.to_markdown()` / `to_pdf()` for human‑readable exports.
- LoRA fine‑tuning on Llama 3 70B for each expert and the Council critique head.
- Optional: “Repo → system_description” helper that scans a GitHub repo (README, configs, main entrypoint) and auto‑generates the textual description consumed by the experts.

---

## 9. License

MIT License

Copyright (c) 2026 Junjie Yang

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
