"""
run_slm_demo.py
============================
One-shot smoke test and demo for the SLM backend integration.

Modes:
    --backend claude      → uses Anthropic Claude (requires ANTHROPIC_API_KEY)
    --backend vllm        → uses local vLLM endpoint (requires running vLLM server)
    --check-connection    → only tests the vLLM endpoint connection, no full eval
    --dry-run             → prints config and exits without calling any API

Usage:
    # Test with Claude (sanity check)
    python run_slm_demo.py --backend claude

    # Test connection to local vLLM
    python run_slm_demo.py --backend vllm --check-connection

    # Full evaluation with SLM
    python run_slm_demo.py --backend vllm \
        --vllm-url http://localhost:8000 \
        --vllm-model unicc-safety/council-llama3-70b-lora

    # Full evaluation with SLM (Qwen or any other model)
    python run_slm_demo.py --backend vllm \
        --vllm-url http://dgx-node:8000 \
        --vllm-model Qwen/Qwen2.5-7B-Instruct
"""

import argparse
import json
import sys
import os
from pathlib import Path

# ── Path setup ────────────────────────────────────────────────────────────────

_DIR = Path(__file__).parent
sys.path.insert(0, str(_DIR.parent))

# ── Test system description ────────────────────────────────────────────────────

TEST_SYSTEM = """\
System Name: RefugeeAssist Pilot v1.0
Domain: Humanitarian / Resource Allocation
Deployment: UNHCR Syria field offices

Description:
An AI-powered triage assistant that recommends priority levels for refugee
assistance requests (food, shelter, medical) based on intake questionnaire data.
A human caseworker must review and approve all priority-1 recommendations before
allocation is confirmed.

Data processed: intake form data (household size, displacement duration, medical
flags). No biometric data. No GPS. Data retained for 90 days then deleted.

Safeguards: caseworker approval required for P1; audit log of all decisions;
monthly bias review by programme officer.

Security: hosted on UNHCR internal network, password authentication,
no public API endpoint.
"""

# ── Connection check ───────────────────────────────────────────────────────────

def check_vllm_connection(base_url: str, model: str) -> bool:
    """Ping the vLLM /v1/models endpoint."""
    import urllib.request, urllib.error
    try:
        req = urllib.request.Request(f"{base_url}/v1/models")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
        models = [m["id"] for m in data.get("data", [])]
        print(f"  vLLM endpoint reachable: {base_url}")
        print(f"  Available models: {models}")
        return True
    except urllib.error.URLError as e:
        print(f"  ERROR: Cannot reach vLLM endpoint at {base_url}: {e}")
        return False


def ping_vllm_chat(base_url: str, model: str) -> bool:
    """Send a minimal chat completion to verify the model is loaded."""
    import urllib.request, urllib.error
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": "Reply with just the word: OK"}],
        "max_tokens": 10,
    }).encode()
    req = urllib.request.Request(
        f"{base_url}/v1/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        reply = data["choices"][0]["message"]["content"].strip()
        print(f"  Model ping response: {reply!r}")
        return True
    except Exception as e:
        print(f"  ERROR during model ping: {e}")
        return False


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="SLM backend demo for UNICC Council")
    parser.add_argument("--backend",      default="claude",
                        choices=["claude", "vllm"],
                        help="LLM backend to use")
    parser.add_argument("--vllm-url",     default="http://localhost:8000",
                        help="vLLM server base URL (backend=vllm only)")
    parser.add_argument("--vllm-model",   default="meta-llama/Meta-Llama-3-70B-Instruct",
                        help="Model name served by vLLM")
    parser.add_argument("--check-connection", action="store_true",
                        help="Only test vLLM connection; skip full evaluation")
    parser.add_argument("--dry-run",      action="store_true",
                        help="Print config and exit without calling any API")
    parser.add_argument("--out",          default=None,
                        help="Save full report JSON to this path")
    args = parser.parse_args()

    print("=" * 60)
    print("UNICC Council of Experts — SLM Integration Demo")
    print("=" * 60)
    print(f"Backend:    {args.backend}")
    if args.backend == "vllm":
        print(f"vLLM URL:   {args.vllm_url}")
        print(f"Model:      {args.vllm_model}")
    print()

    if args.dry_run:
        print("[DRY RUN] Configuration valid. Exiting.")
        return

    # ── Connection check ──────────────────────────────────────────────────
    if args.backend == "vllm":
        print("Checking vLLM connection...")
        if not check_vllm_connection(args.vllm_url, args.vllm_model):
            print("\nFix: make sure vLLM is running:")
            print(f"  vllm serve {args.vllm_model} --port 8000")
            sys.exit(1)
        if not ping_vllm_chat(args.vllm_url, args.vllm_model):
            print("\nModel not responding. Check vLLM logs.")
            sys.exit(1)
        print()

        if args.check_connection:
            print("Connection OK. Skipping full evaluation (--check-connection).")
            return

    # ── Full evaluation ────────────────────────────────────────────────────
    print("Running full Council evaluation...")
    print(f"System: {TEST_SYSTEM[:80].strip()}...")
    print()

    from council.council_orchestrator import evaluate_agent

    kwargs = dict(
        agent_id           = "demo-refugee-assist-v1",
        system_description = TEST_SYSTEM,
        system_name        = "RefugeeAssist Pilot v1.0",
        backend            = args.backend,
    )
    if args.backend == "vllm":
        kwargs["vllm_base_url"] = args.vllm_url
        kwargs["vllm_model"]    = args.vllm_model

    report = evaluate_agent(**kwargs)

    # ── Print summary ─────────────────────────────────────────────────────
    print()
    print("=" * 60)
    print("COUNCIL DECISION:", report.final_decision.value)
    print("=" * 60)
    print(f"Consensus:    {report.consensus_level}")
    print(f"Expert votes: ", end="")
    votes = {k: v.value for k, v in report.expert_recommendations.items()}
    print(" | ".join(f"{k.split('_')[0]}={v}" for k, v in votes.items()))
    print()
    print("Council rationale (first 400 chars):")
    print(report.council_rationale[:400])
    print()

    if args.out:
        with open(args.out, "w") as f:
            json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)
        print(f"Full report saved → {args.out}")

    print()
    print("Done.")


if __name__ == "__main__":
    main()
