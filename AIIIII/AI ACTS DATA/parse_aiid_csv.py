"""
parse_aiid_csv.py
Parse incidents.csv from AIID and classify into 7 Expert 1 domains

Setup:
    pip install pandas

Run:
    python parse_aiid_csv.py
    (incidents.csv must be in the same folder)
"""

import json
import pandas as pd
from pathlib import Path
from collections import defaultdict, Counter

# ─── CONFIG ───────────────────────────────────────────────────────────────────

INPUT_CSV   = "./incidents.csv"
OUTPUT_FILE = "./aiid_raw_reports.json"
TARGET_PER_DOMAIN = 20

# ─── DOMAIN KEYWORDS ──────────────────────────────────────────────────────────

DOMAINS = {
    "nlp_llm": {
        "label": "Natural Language Processing / LLM",
        "keywords": [
            "chatbot", "language model", "translation", "text generation",
            "document", "llm", "large language model", "natural language",
            "generative", "gpt", "conversation", "summarization",
            "speech recognition", "voice assistant", "autocomplete"
        ]
    },
    "automated_decision": {
        "label": "Automated Decision Making",
        "keywords": [
            "automated decision", "classification", "recommendation",
            "hiring", "recruitment", "content moderation", "predictive",
            "scoring", "algorithmic", "approval", "screening", "ranking",
            "filtering", "credit", "loan", "insurance", "sentencing",
            "parole", "risk score", "profiling"
        ]
    },
    "security_adversarial": {
        "label": "Security & Adversarial",
        "keywords": [
            "adversarial", "poisoning", "prompt injection", "jailbreak",
            "data leak", "privacy breach", "manipulation", "attack",
            "vulnerability", "exploit", "bypass", "evasion",
            "deepfake", "synthetic media", "disinformation", "fake"
        ]
    },
    "humanitarian_aid": {
        "label": "Humanitarian Aid & Crisis Response",
        "keywords": [
            "humanitarian", "refugee", "disaster", "crisis", "aid",
            "emergency", "conflict", "food security", "migration",
            "health", "medical", "welfare", "poverty", "vulnerable",
            "child", "abuse", "exploitation", "trafficking"
        ]
    },
    "autonomous_agent": {
        "label": "Autonomous AI Agent",
        "keywords": [
            "autonomous", "self-driving", "robot", "agent", "automated",
            "autopilot", "unmanned", "drone", "vehicle", "tesla",
            "waymo", "uber", "crash", "collision", "accident"
        ]
    },
    "content_moderation": {
        "label": "Content Moderation",
        "keywords": [
            "content moderation", "hate speech", "misinformation",
            "disinformation", "fake news", "harmful content",
            "toxic", "harassment", "propaganda", "youtube",
            "facebook", "twitter", "social media", "platform",
            "inappropriate", "ban", "removal", "flagging"
        ]
    },
    "document_intelligence": {
        "label": "Document Intelligence",
        "keywords": [
            "facial recognition", "face recognition", "biometric",
            "identity", "passport", "document", "ocr",
            "recognition", "scanning", "surveillance", "camera",
            "image recognition", "photo", "mugshot"
        ]
    }
}

# ─── CLASSIFY ─────────────────────────────────────────────────────────────────

def classify_domains(text: str) -> list:
    text_lower = text.lower()
    matched = []
    for domain_key, domain_info in DOMAINS.items():
        for keyword in domain_info["keywords"]:
            if keyword in text_lower:
                matched.append(domain_key)
                break
    return matched


def clean_text(text: str, max_chars: int = 1200) -> str:
    if not isinstance(text, str) or not text.strip():
        return ""
    text = " ".join(text.split())
    return text[:max_chars]


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 50)
    print("Parsing AIID incidents.csv")
    print("=" * 50)

    if not Path(INPUT_CSV).exists():
        print(f"\nERROR: {INPUT_CSV} not found.")
        print("Download from:")
        print("https://github.com/responsible-ai-collaborative/nlp-lambdas/blob/main/inference/db_state/incidents.csv")
        return

    # Load CSV
    df = pd.read_csv(INPUT_CSV, on_bad_lines='skip')
    print(f"\nLoaded {len(df)} rows")
    print(f"Columns: {list(df.columns)}")

    # Deduplicate by incident_id (keep first report per incident)
    if 'incident_id' in df.columns:
        df = df.drop_duplicates(subset='incident_id', keep='first')
        print(f"After dedup by incident_id: {len(df)} unique incidents")

    # Classify
    domain_buckets = defaultdict(list)
    unclassified   = 0

    for _, row in df.iterrows():
        title   = str(row.get('title', ''))
        text    = str(row.get('text', ''))
        combined = f"{title} {text[:600]}"

        domains = classify_domains(combined)
        if not domains:
            unclassified += 1
            continue

        # Build clean record
        record = {
            "id":          f"aiid_{row.get('incident_id', row.get('report_number', ''))}",
            "title":       title,
            "description": clean_text(text, max_chars=800),
            "full_text":   clean_text(text, max_chars=1200),
            "date":        str(row.get('incident_date', row.get('date_published', ''))),
            "source":      str(row.get('source_domain', '')),
            "url":         str(row.get('url', '')),
            "domains":     domains
        }

        for domain in domains:
            domain_buckets[domain].append(record)

    # Select top records per domain
    print("\nDomain distribution:")
    final_data = {}
    total = 0

    for domain in DOMAINS.keys():
        records = domain_buckets.get(domain, [])

        # Deduplicate by ID within domain
        seen = set()
        unique = []
        for r in records:
            if r['id'] not in seen and len(r['description']) > 80:
                seen.add(r['id'])
                unique.append(r)

        # Sort by description length (more text = more useful)
        unique.sort(key=lambda x: len(x['description']), reverse=True)
        selected = unique[:TARGET_PER_DOMAIN]

        final_data[domain] = selected
        total += len(selected)
        print(f"  {domain}: {len(selected)} records (pool: {len(unique)})")

    print(f"\nUnclassified: {unclassified}")
    print(f"Total selected: {total}")

    # Save
    output = {
        "metadata": {
            "total_records":   total,
            "source":          "AIID incidents.csv",
            "domains":         list(final_data.keys()),
            "per_domain":      {d: len(r) for d, r in final_data.items()}
        },
        "data": final_data
    }

    Path(OUTPUT_FILE).write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )
    print(f"\nSaved → {OUTPUT_FILE}")
    print("Next: run generate_expert1_training_data.py")


if __name__ == '__main__':
    main()
