"""
fetch_aiid_data.py
Step 1: Fetch real AI incident reports from AIID GraphQL API

Pulls incident reports, classifies them into 7 Expert 1 domains,
and writes aiid_raw_reports.json.

Run:
    python fetch_aiid_data.py
"""

import json
import time
import urllib.request
import urllib.error
from pathlib import Path

# --- CONFIG -----------------------------------------------------------------

AIID_GRAPHQL_URL = "https://incidentdatabase.ai/api/graphql"
OUTPUT_FILE      = "./aiid_raw_reports.json"
REQUEST_DELAY    = 1.5   # seconds between paginated requests

# Target counts per domain (fetch extra to account for filtering)
DOMAIN_TARGETS = {
    "nlp_llm":               30,
    "automated_decision":    25,
    "security_adversarial":  25,
    "humanitarian_aid":      25,
    "autonomous_agent":      25,
    "content_moderation":    20,
    "document_intelligence": 20,
}

# Domain classification keywords (checked against title + description)
DOMAIN_KEYWORDS = {
    "nlp_llm": [
        "language model", "llm", "chatbot", "gpt", "bert", "text generation",
        "natural language", "chatgpt", "bard", "claude", "large language",
        "autocomplete", "translation", "summarization", "question answering",
    ],
    "automated_decision": [
        "automated decision", "algorithmic decision", "credit scoring",
        "loan approval", "hiring algorithm", "recruitment", "benefits eligibility",
        "welfare algorithm", "parole", "sentencing", "risk score", "predictive",
        "automated scoring", "algorithmic hiring",
    ],
    "security_adversarial": [
        "adversarial", "jailbreak", "prompt injection", "bypass", "exploit",
        "manipulation", "attack", "red team", "safety bypass", "misuse",
        "harmful content", "content policy", "guardrail", "censorship bypass",
    ],
    "humanitarian_aid": [
        "refugee", "asylum", "humanitarian", "migration", "displacement",
        "disaster", "emergency response", "aid distribution", "peacekeeping",
        "human rights", "surveillance", "marginalized", "vulnerable population",
    ],
    "autonomous_agent": [
        "autonomous", "self-driving", "robot", "drone", "autopilot",
        "autonomous vehicle", "autonomous system", "agentic", "agent",
        "automated driving", "unmanned", "self-operating",
    ],
    "content_moderation": [
        "content moderation", "hate speech", "misinformation", "disinformation",
        "fake news", "social media", "platform", "flagging", "removal",
        "toxic content", "harassment", "moderation algorithm",
    ],
    "document_intelligence": [
        "document", "ocr", "form processing", "contract", "invoice",
        "medical record", "legal document", "extraction", "classification",
        "document analysis", "image recognition", "pdf", "scanning",
    ],
}

# GraphQL query — fetch incidents in batches
INCIDENTS_QUERY = """
query FetchIncidents($limit: Int, $skip: Int) {
  incidents(pagination: { limit: $limit, skip: $skip }, sort: { incident_id: ASC }) {
    incident_id
    title
    description
    date
    reports {
      report_number
      title
      text
      url
      source_domain
    }
    AllegedDeployerOfAISystem {
      name
    }
    AllegedDeveloperOfAISystem {
      name
    }
    AllegedHarmedOrNearlyHarmedParties {
      name
    }
  }
}
"""


# --- GRAPHQL CLIENT ---------------------------------------------------------

def graphql_request(query: str, variables: dict, retries: int = 3) -> dict:
    payload = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    req = urllib.request.Request(
        AIID_GRAPHQL_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "UNICC-AI-Safety-Lab/1.0",
        },
    )
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            print(f"  HTTP {e.code} on attempt {attempt + 1}")
            if attempt < retries - 1:
                time.sleep(5 * (attempt + 1))
            else:
                raise
        except Exception as e:
            print(f"  Error on attempt {attempt + 1}: {e}")
            if attempt < retries - 1:
                time.sleep(5)
            else:
                raise


# --- CLASSIFICATION ---------------------------------------------------------

def classify_domain(title: str, description: str) -> list[str]:
    """Return all matching domain labels for a given incident."""
    combined = (title + " " + (description or "")).lower()
    matched = []
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if any(kw in combined for kw in keywords):
            matched.append(domain)
    return matched


def pick_primary_domain(domains: list[str]) -> str:
    """Pick single primary domain using priority ordering."""
    priority = [
        "security_adversarial",
        "autonomous_agent",
        "automated_decision",
        "humanitarian_aid",
        "nlp_llm",
        "content_moderation",
        "document_intelligence",
    ]
    for d in priority:
        if d in domains:
            return d
    return domains[0] if domains else "nlp_llm"


# --- FETCH ------------------------------------------------------------------

def fetch_all_incidents(batch_size: int = 50) -> list[dict]:
    """Page through AIID and return all incidents."""
    all_incidents = []
    skip = 0

    print("Fetching incidents from AIID...")
    while True:
        print(f"  Fetching batch skip={skip}...")
        try:
            result = graphql_request(
                INCIDENTS_QUERY,
                {"limit": batch_size, "skip": skip},
            )
        except Exception as e:
            print(f"  Failed: {e}. Stopping fetch.")
            break

        batch = result.get("data", {}).get("incidents", [])
        if not batch:
            break

        all_incidents.extend(batch)
        print(f"  Got {len(batch)} incidents (total so far: {len(all_incidents)})")

        if len(batch) < batch_size:
            break

        skip += batch_size
        time.sleep(REQUEST_DELAY)

    print(f"Total incidents fetched: {len(all_incidents)}")
    return all_incidents


# --- BUILD REPORT -----------------------------------------------------------

def build_report(incident: dict, domain: str) -> dict:
    """Convert an AIID incident into a flat report dict."""
    # Grab best available text from first report
    reports   = incident.get("reports") or []
    best_text = ""
    best_url  = ""
    for r in reports:
        text = (r.get("text") or "").strip()
        if len(text) > len(best_text):
            best_text = text
            best_url  = r.get("url", "")

    deployers  = [e.get("name", "") for e in (incident.get("AllegedDeployerOfAISystem")  or [])]
    developers = [e.get("name", "") for e in (incident.get("AllegedDeveloperOfAISystem") or [])]
    harmed     = [e.get("name", "") for e in (incident.get("AllegedHarmedOrNearlyHarmedParties") or [])]

    # Truncate text to ~2000 chars to keep prompts manageable
    if len(best_text) > 2000:
        best_text = best_text[:2000] + "... [truncated]"

    return {
        "aiid_incident_id": incident.get("incident_id"),
        "domain":           domain,
        "title":            incident.get("title", ""),
        "date":             incident.get("date", ""),
        "description":      incident.get("description", ""),
        "full_text":        best_text,
        "source_url":       best_url,
        "deployer":         ", ".join(deployers) if deployers else "Unknown",
        "developer":        ", ".join(developers) if developers else "Unknown",
        "harmed_parties":   harmed,
    }


# --- MAIN -------------------------------------------------------------------

def main() -> None:
    print("=" * 50)
    print("AIID Data Fetch — Expert 1 Training Pipeline")
    print("=" * 50 + "\n")

    incidents = fetch_all_incidents()

    # Classify and bucket
    domain_buckets: dict[str, list[dict]] = {d: [] for d in DOMAIN_TARGETS}
    unclassified = 0

    for inc in incidents:
        title       = inc.get("title", "")
        description = inc.get("description", "")
        domains     = classify_domain(title, description)

        if not domains:
            unclassified += 1
            continue

        primary = pick_primary_domain(domains)
        report  = build_report(inc, primary)

        # Add to primary bucket
        domain_buckets[primary].append(report)

        # Also add to secondary buckets (useful for padding later)
        for d in domains:
            if d != primary and d in domain_buckets:
                report_copy       = dict(report)
                report_copy["domain"] = d
                domain_buckets[d].append(report_copy)

    # Trim each bucket to target
    final_reports: list[dict] = []
    for domain, target in DOMAIN_TARGETS.items():
        bucket = domain_buckets[domain]
        # Deduplicate by incident_id
        seen    = set()
        unique  = []
        for r in bucket:
            if r["aiid_incident_id"] not in seen:
                seen.add(r["aiid_incident_id"])
                unique.append(r)
        trimmed = unique[:target]
        final_reports.extend(trimmed)
        print(f"  {domain}: {len(trimmed)} reports (target {target})")

    print(f"\nTotal reports selected: {len(final_reports)}")
    print(f"Unclassified incidents: {unclassified}")

    # Write output
    output = {
        "metadata": {
            "source":        "AIID GraphQL API",
            "total_fetched": len(incidents),
            "total_selected": len(final_reports),
            "unclassified":  unclassified,
            "domain_counts": {d: sum(1 for r in final_reports if r["domain"] == d) for d in DOMAIN_TARGETS},
        },
        "reports": final_reports,
    }

    Path(OUTPUT_FILE).write_text(json.dumps(output, indent=2, ensure_ascii=False))
    print(f"\n✓ Saved to {OUTPUT_FILE}")
    print("Run generate_expert1_training_data.py next.")


if __name__ == "__main__":
    main()
