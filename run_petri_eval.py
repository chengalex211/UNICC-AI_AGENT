"""One-shot script: analyze Petri repo + run full Council evaluation."""
import os, json, sys

# Load key directly from file — bypasses any stale shell env var
_env_file = os.path.join(os.path.dirname(__file__), "expert3_rag", "env")
with open(_env_file) as f:
    for line in f:
        line = line.strip()
        if line.startswith("ANTHROPIC_API_KEY="):
            os.environ["ANTHROPIC_API_KEY"] = line.split("=", 1)[1]
            break

print("Key loaded:", os.environ.get("ANTHROPIC_API_KEY", "NOT SET")[:20], "...")

sys.path.insert(0, os.path.dirname(__file__))
from council.repo_analyzer import analyze_repo
from council.council_orchestrator import evaluate_agent

print("\nStep 1: Fetching repo and generating description...")
desc = analyze_repo(
    "https://github.com/hg3016-guo/unicc-ai-agent",
    backend="claude",
)
print(f"Description ready ({len(desc)} chars)\n")

print("Step 2: Running full Council evaluation (3 experts + critiques)...")
report = evaluate_agent(
    agent_id="petri-unicc-ai-agent",
    system_name="Petri AI Safety Agent",
    system_description=desc,
    backend="claude",
)

result = json.loads(report.to_json())

print("\n" + "="*60)
print("FINAL DECISION:", result.get("council_decision", {}).get("final_recommendation", "N/A"))
print("CONSENSUS:     ", result.get("council_decision", {}).get("consensus_level", "N/A"))
print("COUNCIL NOTE:  ", result.get("council_note", "")[:300])
print("="*60)
print("\nFull report saved to:", f"council/reports/{result.get('incident_id')}.json")
print("\nFull JSON:")
print(json.dumps(result, indent=2))
