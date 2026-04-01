# ─────────────────────────────────────────────────────────────────────────────
# UNICC AI Safety Council — Dockerfile
#
# Multi-stage build:
#   Stage 1 (frontend-builder) — Node 20: npm ci + npm run build → dist/
#   Stage 2 (runtime)          — Python 3.11-slim: install deps, copy everything
#
# Usage (no API keys required — runs in mock mode by default):
#   docker build -t unicc-council .
#   docker run -p 8100:8100 unicc-council
#
#   With real LLM (optional):
#   docker run -p 8100:8100 -e ANTHROPIC_API_KEY=sk-ant-... unicc-council
#
# Health check:  http://localhost:8100/health
# Frontend UI:   http://localhost:8100/
# API docs:      http://localhost:8100/docs
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage 1: build the React frontend ─────────────────────────────────────────
FROM node:20-slim AS frontend-builder

WORKDIR /build
COPY real_frontend/package*.json ./
RUN npm ci --prefer-offline

COPY real_frontend/ ./
RUN npm run build
# Output: /build/dist/


# ── Stage 2: Python runtime ────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# System deps for reportlab (PDF generation) and git (repo analysis)
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        libfreetype6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps (lightweight — no chromadb/torch, those are requirements-full.txt)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy project source
COPY . .

# Overlay the built frontend (overrides any stale dist/ if present in the repo)
COPY --from=frontend-builder /build/dist ./real_frontend/dist

# Ensure writable runtime directories exist
RUN mkdir -p council/reports \
    && chmod -R 777 council/

# ── Environment defaults ───────────────────────────────────────────────────────
# UNICC_MOCK_MODE=1 means: no LLM calls, instant mock reports, no API key needed.
# Override with -e ANTHROPIC_API_KEY=... or -e UNICC_MOCK_MODE=0 at runtime.
ENV UNICC_MOCK_MODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8100

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD python3 -c \
        "import urllib.request; \
         r = urllib.request.urlopen('http://localhost:8100/health', timeout=4); \
         assert r.status == 200, f'status={r.status}'"

# Start the backend — it also serves the built frontend at /
CMD ["uvicorn", "frontend_api.main:app", "--host", "0.0.0.0", "--port", "8100"]
