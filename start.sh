#!/usr/bin/env bash
# Entry point for DGX runner / CI
# Setup:  pip install -r requirements.txt
# Run:    bash start.sh
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"

# Install frontend deps if needed
if [ ! -d "$ROOT/real_frontend/node_modules" ]; then
  echo "[start] Installing frontend dependencies..."
  cd "$ROOT/real_frontend" && npm install --silent
fi

# Start FastAPI backend
echo "[start] Starting UNICC Council backend on port 8100..."
cd "$ROOT/frontend_api"
exec uvicorn main:app --host 0.0.0.0 --port 8100
