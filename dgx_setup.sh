#!/usr/bin/env bash
# =============================================================================
#  UNICC Council — DGX Setup & Evaluation Runner
#  Target repo: https://github.com/dondondon123456/unicc-ai-safety (Team 9)
#
#  Usage:
#    bash dgx_setup.sh                  # full setup + evaluate Team 9
#    bash dgx_setup.sh --all            # evaluate all 7 teams
#    bash dgx_setup.sh --model <name>   # custom HuggingFace model
#    bash dgx_setup.sh --vllm-url http://HOST:8000  # use existing vLLM server
#    bash dgx_setup.sh --skip-vllm      # skip starting vLLM (already running)
#    bash dgx_setup.sh --dry-run        # analyze repos only, skip evaluation
#
#  Requirements on DGX:
#    - Python 3.10+  (conda or system)
#    - NVIDIA GPU with 40+ GB VRAM for 70B  (or use 8B model on smaller GPU)
#    - Internet access to HuggingFace (or pre-downloaded model)
# =============================================================================

set -euo pipefail

# ── Defaults ──────────────────────────────────────────────────────────────────
CAPSTONE_DIR="$(cd "$(dirname "$0")" && pwd)"
MODEL="meta-llama/Meta-Llama-3.1-70B-Instruct"
VLLM_URL="http://localhost:8000"
API_URL="http://localhost:8100"
SKIP_VLLM=false
EVAL_ALL=false
DRY_RUN=false
LOG_DIR="$CAPSTONE_DIR/logs"

# ── Arg parsing ───────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --model)       MODEL="$2"; shift 2 ;;
    --vllm-url)    VLLM_URL="$2"; SKIP_VLLM=true; shift 2 ;;
    --skip-vllm)   SKIP_VLLM=true; shift ;;
    --all)         EVAL_ALL=true; shift ;;
    --dry-run)     DRY_RUN=true; shift ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

mkdir -p "$LOG_DIR"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   UNICC AI Safety Council — DGX Evaluation Runner           ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo "  Model    : $MODEL"
echo "  vLLM URL : $VLLM_URL"
echo "  API URL  : $API_URL"
echo "  All teams: $EVAL_ALL"
echo ""

# ── Step 0: Python environment ────────────────────────────────────────────────
echo "▶ [0/4] Checking Python environment…"

if ! command -v python3 &>/dev/null; then
  echo "  ✗ python3 not found. Install Miniconda or system Python 3.10+"
  exit 1
fi

PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "  Python $PY_VER found"

# Install backend dependencies
echo "  Installing backend dependencies…"
pip install -q fastapi uvicorn anthropic chromadb sentence-transformers \
  pyyaml httpx gitpython requests 2>&1 | tail -3

# Install vLLM if we need to start it
if [ "$SKIP_VLLM" = false ]; then
  if ! python3 -c "import vllm" &>/dev/null 2>&1; then
    echo "  Installing vLLM (this may take a few minutes)…"
    pip install -q "vllm>=0.4.0" 2>&1 | tail -5
  else
    echo "  vLLM already installed"
  fi
fi

# ── Step 1: Start vLLM server ─────────────────────────────────────────────────
if [ "$SKIP_VLLM" = false ]; then
  echo ""
  echo "▶ [1/4] Starting vLLM server…"
  echo "  Model : $MODEL"
  echo "  Log   : $LOG_DIR/vllm.log"
  echo ""

  # Pick tensor-parallel degree based on available GPUs
  GPU_COUNT=$(python3 -c "import torch; print(torch.cuda.device_count())" 2>/dev/null || echo "1")
  TP=$(( GPU_COUNT >= 4 ? 4 : GPU_COUNT >= 2 ? 2 : 1 ))
  echo "  GPUs: $GPU_COUNT  →  tensor-parallel: $TP"

  nohup python3 -m vllm.entrypoints.openai.api_server \
    --model "$MODEL" \
    --tensor-parallel-size "$TP" \
    --max-model-len 8192 \
    --port 8000 \
    --host 0.0.0.0 \
    > "$LOG_DIR/vllm.log" 2>&1 &

  VLLM_PID=$!
  echo "  vLLM PID: $VLLM_PID"
  echo "$VLLM_PID" > "$LOG_DIR/vllm.pid"

  echo "  Waiting for vLLM to be ready (may take 2-5 min for large models)…"
  WAITED=0
  until curl -sf "$VLLM_URL/health" &>/dev/null; do
    sleep 10
    WAITED=$((WAITED + 10))
    echo "    …${WAITED}s elapsed"
    if [ $WAITED -gt 600 ]; then
      echo "  ✗ vLLM did not start within 10 minutes. Check $LOG_DIR/vllm.log"
      exit 1
    fi
  done
  echo "  ✓ vLLM server ready at $VLLM_URL"
else
  echo ""
  echo "▶ [1/4] Skipping vLLM start (--skip-vllm or --vllm-url provided)"
  if curl -sf "$VLLM_URL/health" &>/dev/null; then
    echo "  ✓ vLLM reachable at $VLLM_URL"
  else
    echo "  ✗ vLLM not reachable at $VLLM_URL — check your server"
    exit 1
  fi
fi

# ── Step 2: Start FastAPI backend ─────────────────────────────────────────────
echo ""
echo "▶ [2/4] Starting UNICC FastAPI backend…"

# Kill any existing instance
pkill -f "uvicorn main:app" 2>/dev/null && sleep 2 || true

cd "$CAPSTONE_DIR/frontend_api"
nohup uvicorn main:app --host 0.0.0.0 --port 8100 \
  > "$LOG_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo "  Backend PID: $BACKEND_PID"
echo "$BACKEND_PID" > "$LOG_DIR/backend.pid"

echo "  Waiting for backend to be ready…"
WAITED=0
until curl -sf "$API_URL/health" &>/dev/null; do
  sleep 3
  WAITED=$((WAITED + 3))
  if [ $WAITED -gt 60 ]; then
    echo "  ✗ Backend did not start. Check $LOG_DIR/backend.log"
    cat "$LOG_DIR/backend.log" | tail -20
    exit 1
  fi
done
echo "  ✓ Backend ready at $API_URL"

# ── Step 3: Run evaluations ───────────────────────────────────────────────────
echo ""
echo "▶ [3/4] Running council evaluations…"
cd "$CAPSTONE_DIR"

BATCH_ARGS="--backend vllm"
[ "$DRY_RUN" = true ] && BATCH_ARGS="$BATCH_ARGS --dry-run"

if [ "$EVAL_ALL" = true ]; then
  echo "  Mode: all 7 teams"
  python3 run_batch_eval.py $BATCH_ARGS
else
  # Single repo mode — Team 9 as default demo target
  echo "  Mode: single repo (Team 9 — unicc-ai-safety)"
  python3 - <<'PYEOF'
import json, sys, time, urllib.request, urllib.error

API     = "http://localhost:8100"
REPO    = "https://github.com/dondondon123456/unicc-ai-safety"
BACKEND = "vllm"

def post(path, body, timeout=600):
    data = json.dumps(body).encode()
    req  = urllib.request.Request(f"{API}{path}", data=data,
                                   headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())

print(f"\n  Analyzing: {REPO}")
t0   = time.time()
info = post("/analyze/repo", {"source": REPO, "backend": BACKEND})
print(f"  ✓ Analyzed in {time.time()-t0:.1f}s")
print(f"  System      : {info['system_name']}")
print(f"  Description : {info['system_description'][:200]}…")

print(f"\n  Running council evaluation (2-5 min)…")
t1     = time.time()
report = post("/evaluate/council", {
    "agent_id":           info["agent_id"],
    "system_name":        info["system_name"],
    "system_description": info["system_description"],
    "purpose":            info.get("capabilities", ""),
    "deployment_context": f"{info.get('deploy_zone','')} — {info.get('category','')}",
    "backend":            BACKEND,
})
elapsed = time.time()-t1
print(f"  ✓ Evaluated in {elapsed:.1f}s")

cd  = report.get("council_decision", {})
dec = cd.get("final_recommendation", "?")
con = cd.get("consensus_level", "?")
inc = report.get("incident_id", "?")
note = report.get("council_note", "")

COLORS = {"APPROVE": "\033[32m", "REVIEW": "\033[33m", "REJECT": "\033[31m"}
c = COLORS.get(dec, "")
RESET = "\033[0m"

print(f"\n{'═'*60}")
print(f"  Decision    : {c}{dec}{RESET}")
print(f"  Consensus   : {con}")
print(f"  Incident ID : {inc}")
print(f"\n  Council Note:\n{note}")
print(f"{'═'*60}")

with open("dgx_eval_result.json", "w") as f:
    json.dump({"repo": REPO, "decision": dec, "consensus": con,
               "incident_id": inc, "report": report}, f, indent=2)
print(f"\n  Full report → dgx_eval_result.json")
PYEOF
fi

# ── Step 4: Summary ───────────────────────────────────────────────────────────
echo ""
echo "▶ [4/4] Done."
echo ""
echo "  Backend log : $LOG_DIR/backend.log"
echo "  vLLM log    : $LOG_DIR/vllm.log"
echo "  Results     : dgx_eval_result.json  (single) / batch_eval_results.json (--all)"
echo ""
echo "  To stop services:"
echo "    kill \$(cat $LOG_DIR/backend.pid)"
[ "$SKIP_VLLM" = false ] && echo "    kill \$(cat $LOG_DIR/vllm.pid)"
echo ""
