#!/usr/bin/env python3
"""
smoke_test.py — UNICC AI Safety Council portability / CI smoke test

Verifies that the backend API is reachable and a full mock council
evaluation completes successfully without any LLM API keys.

Usage:
    # Against a running server (default: http://localhost:8100)
    python smoke_test.py

    # Against a custom host
    python smoke_test.py http://localhost:8200

Exit codes:
    0  — all checks passed
    1  — one or more checks failed
"""

import json
import sys
import time
import urllib.request
import urllib.error

BASE_URL = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:8100"
TIMEOUT  = 10   # seconds per HTTP call
MAX_POLL = 60   # seconds to wait for evaluation to complete

PASS = "\033[32m✓\033[0m"
FAIL = "\033[31m✗\033[0m"
INFO = "\033[34m·\033[0m"

failures: list[str] = []


def get(path: str, *, label: str) -> dict | None:
    url = f"{BASE_URL}{path}"
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT) as r:
            body = json.loads(r.read())
            print(f"  {PASS} {label} → HTTP {r.status}")
            return body
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        print(f"  {FAIL} {label} → HTTP {e.code}: {body[:120]}")
        failures.append(label)
        return None
    except Exception as e:
        print(f"  {FAIL} {label} → {e}")
        failures.append(label)
        return None


def post(path: str, payload: dict, *, label: str) -> dict | None:
    url = f"{BASE_URL}{path}"
    data = json.dumps(payload).encode()
    req  = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            body = json.loads(r.read())
            print(f"  {PASS} {label} → HTTP {r.status}")
            return body
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        print(f"  {FAIL} {label} → HTTP {e.code}: {body[:120]}")
        failures.append(label)
        return None
    except Exception as e:
        print(f"  {FAIL} {label} → {e}")
        failures.append(label)
        return None


def assert_field(data: dict, field: str, label: str) -> bool:
    if data and field in data:
        print(f"  {PASS} {label}: {repr(data[field])[:80]}")
        return True
    print(f"  {FAIL} {label}: field '{field}' missing in response")
    failures.append(label)
    return False


# ──────────────────────────────────────────────────────────────────────────────

print(f"\n{INFO} UNICC Council smoke test  →  {BASE_URL}\n")

# 1. Health check
print("1. Health check")
health = get("/health", label="GET /health")
if health:
    assert_field(health, "status", "health.status present")

# 2. Evaluation list (may be empty on a fresh container)
print("\n2. Evaluation list")
evals = get("/evaluations", label="GET /evaluations")

# 3. Submit a mock council evaluation
print("\n3. Submit mock council evaluation")
submission = {
    "agent_id":           "smoke-test-agent",
    "system_name":        "Smoke Test AI Agent",
    "system_description": (
        "A test AI assistant used for CI smoke testing of the UNICC Council API. "
        "Deployed in a sandboxed environment with no real data access. "
        "Backend is mock — no LLM API calls are made."
    ),
    "purpose":            "Automated portability verification",
    "deployment_context": "CI / Docker sandbox",
    "backend":            "mock",
}
submit_resp = post("/evaluate/council", submission, label="POST /evaluate/council")
if not submit_resp:
    print(f"\n{FAIL} Cannot continue without incident_id — aborting.\n")
    sys.exit(1)

assert_field(submit_resp, "incident_id",  "response.incident_id")
assert_field(submit_resp, "poll_url",     "response.poll_url")
incident_id = submit_resp.get("incident_id", "")

# 4. Poll until complete (mock should finish in < 1s)
print(f"\n4. Poll for completion  (incident_id={incident_id})")
poll_start = time.time()
final_status = None
while time.time() - poll_start < MAX_POLL:
    status_resp = get(f"/evaluations/{incident_id}/status", label=f"GET /evaluations/{incident_id}/status")
    if status_resp:
        s = status_resp.get("status", "")
        print(f"  {INFO}  status={s}  elapsed={status_resp.get('elapsed_seconds', '?')}s")
        if s == "complete":
            final_status = "complete"
            break
        if s == "failed":
            print(f"  {FAIL} Evaluation failed: {status_resp.get('error')}")
            failures.append("evaluation completed without error")
            break
    time.sleep(0.5)

if final_status != "complete":
    print(f"  {FAIL} Evaluation did not complete within {MAX_POLL}s")
    failures.append("evaluation completed within timeout")

# 5. Fetch the full report
print(f"\n5. Fetch completed report")
report = get(f"/evaluations/{incident_id}", label=f"GET /evaluations/{incident_id}")
if report:
    assert_field(report, "expert_reports",    "report.expert_reports present")
    assert_field(report, "council_decision",  "report.council_decision present")
    assert_field(report, "critiques",         "report.critiques present")
    # Check all three experts
    er = report.get("expert_reports", {})
    for key in ("security", "governance", "un_mission_fit"):
        if key in er:
            print(f"  {PASS} expert_reports.{key} present")
        else:
            print(f"  {FAIL} expert_reports.{key} missing")
            failures.append(f"expert_reports.{key}")
    # Check council decision
    cd = report.get("council_decision", {})
    if cd.get("final_recommendation") in ("APPROVE", "REVIEW", "REJECT"):
        print(f"  {PASS} council_decision.final_recommendation = {cd['final_recommendation']}")
    else:
        print(f"  {FAIL} council_decision.final_recommendation invalid: {cd.get('final_recommendation')}")
        failures.append("council_decision.final_recommendation")

# 6. Check frontend is served (only if dist was built into the image)
print(f"\n6. Frontend static files")
try:
    req = urllib.request.Request(BASE_URL + "/")
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        ct = r.headers.get("Content-Type", "")
        if "text/html" in ct:
            print(f"  {PASS} GET / → HTML (frontend served)")
        else:
            print(f"  {INFO} GET / → Content-Type: {ct} (may be API JSON if frontend not built)")
except Exception as e:
    print(f"  {INFO} GET / → {e} (frontend static files not available in this environment)")

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n" + "─" * 60)
if failures:
    print(f"{FAIL}  FAILED  ({len(failures)} check(s)):")
    for f in failures:
        print(f"     • {f}")
    print()
    sys.exit(1)
else:
    print(f"{PASS}  ALL CHECKS PASSED  — UNICC Council API is healthy\n")
    sys.exit(0)
