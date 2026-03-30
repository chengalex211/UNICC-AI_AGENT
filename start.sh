#!/usr/bin/env bash
# Entry point for DGX runner / CI
# Setup:  pip install -r requirements.txt
# Run:    bash start.sh
#
# LLM backend priority (auto-detected at request time, no restart needed):
#   1. vLLM   — if running at http://localhost:8000  (DGX local model, no API key needed)
#   2. Claude — fallback if ANTHROPIC_API_KEY is set  (cloud, set env var below)
#
# To use Claude fallback:
#   export ANTHROPIC_API_KEY=sk-ant-...
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"

# On DGX (GPU available), install full ML dependencies too
if python3 -c "import torch; torch.cuda.is_available()" 2>/dev/null; then
  echo "[start] GPU detected — installing full ML dependencies..."
  pip install -q -r "$ROOT/requirements-full.txt"
fi

# Install frontend deps if needed
if [ ! -d "$ROOT/real_frontend/node_modules" ]; then
  echo "[start] Installing frontend dependencies..."
  cd "$ROOT/real_frontend" && npm install --silent
fi

# Start FastAPI backend
echo "[start] Starting UNICC Council backend on port 8100..."
cd "$ROOT/frontend_api"
exec uvicorn main:app --host 0.0.0.0 --port 8100
