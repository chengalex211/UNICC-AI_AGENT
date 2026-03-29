#!/usr/bin/env python3
"""Validate the corrected Expert 1 training data against all constraints."""

import json

PATH = "/Users/yangjunjie/Capstone/expert1_training_data.jsonl"
STRATEGIES = {"direct", "reframing", "role_playing", "step_by_step", "hypothetical", "technical", "authority", "urgency"}
DIMENSIONS = {"harmfulness", "bias_fairness", "transparency", "deception", "privacy", "legal_compliance", "self_preservation"}


def main():
    records = []
    with open(PATH) as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                records.append(rec)
            except json.JSONDecodeError as e:
                print(f"Line {i+1}: JSON parse error: {e}")
                return 1

    print(f"Parsed {len(records)} records")
    errors = []

    for r in records:
        # ID format
        if not r["id"].startswith("expert1_") or len(r["id"]) != 12:
            errors.append(f"{r['id']}: invalid id format (expect expert1_0001..expert1_0050)")

        # Autonomy
        if r["autonomy_level"] not in ("low", "medium", "high"):
            errors.append(f"{r['id']}: invalid autonomy_level '{r['autonomy_level']}'")

        # Audit dialogue turns: 6-16
        turns = r["audit_dialogue"]["turns"]
        if len(turns) < 6 or len(turns) > 16:
            errors.append(f"{r['id']}: turns count {len(turns)} (expect 6-16)")

        # Each turn >= 2 sentences
        for t in turns:
            sents = [x for x in t["content"].replace("?", ".").split(".") if x.strip()]
            if len(sents) < 2:
                errors.append(f"{r['id']} turn {t['turn_id']}: content has <2 sentences")

        # Strategy names
        for st in r["strategy_trace"]:
            if st.get("strategy") not in STRATEGIES:
                errors.append(f"{r['id']}: invalid strategy '{st.get('strategy')}'")
            if st.get("target_response_type") not in ("refusal", "defensive", "partial_compliance", "edge", "compliant", "unknown"):
                errors.append(f"{r['id']}: invalid target_response_type '{st.get('target_response_type')}'")
            for k in ["turn_id", "strategy", "auditor_intent", "target_response_type", "refusal_count_running", "tier_escalation_event"]:
                if k not in st:
                    errors.append(f"{r['id']}: strategy_trace missing key '{k}'")

        # Training sample: exactly 3 messages
        msgs = r["training_sample"]["messages"]
        if len(msgs) != 3:
            errors.append(f"{r['id']}: training_sample.messages has {len(msgs)} messages (expected 3)")
        if len(msgs) >= 3:
            if msgs[0]["role"] != "system":
                errors.append(f"{r['id']}: message[0] should be system")
            if msgs[1]["role"] != "user":
                errors.append(f"{r['id']}: message[1] should be user")
            if msgs[2]["role"] != "assistant":
                errors.append(f"{r['id']}: message[2] should be assistant")
            if "Evaluate the following AI system interaction for safety" not in msgs[1]["content"]:
                errors.append(f"{r['id']}: user message missing evaluation prompt")
            try:
                out = json.loads(msgs[2]["content"])
                if out.get("expert") != "security_adversarial":
                    errors.append(f"{r['id']}: expert should be security_adversarial")
                for d in DIMENSIONS:
                    if d not in out.get("dimension_scores", {}):
                        errors.append(f"{r['id']}: dimension_scores missing '{d}'")
                if not isinstance(out.get("key_findings"), list) or len(out.get("key_findings", [])) > 3:
                    errors.append(f"{r['id']}: key_findings must be array with max 3 items")
                if out.get("recommendation") not in ("PASS", "REVIEW", "FAIL"):
                    errors.append(f"{r['id']}: recommendation must be PASS|REVIEW|FAIL")
                if not out.get("needs_human_review") and out.get("review_trigger_reasons") != []:
                    errors.append(f"{r['id']}: review_trigger_reasons must be [] when needs_human_review=false")
            except json.JSONDecodeError as e:
                errors.append(f"{r['id']}: assistant content not valid JSON: {e}")

        # Evidence: >=3, only valid dimensions
        if len(r["evidence"]) < 3:
            errors.append(f"{r['id']}: evidence has {len(r['evidence'])} items (expected >=3)")
        for ev in r["evidence"]:
            if ev.get("dimension") not in DIMENSIONS:
                errors.append(f"{r['id']}: evidence invalid dimension '{ev.get('dimension')}'")
            for k in ["dimension", "turn_id", "quote", "reason"]:
                if k not in ev:
                    errors.append(f"{r['id']}: evidence item missing '{k}'")

    # Counts
    splits = {}
    domains = {}
    labels = {}
    for r in records:
        splits[r["split"]] = splits.get(r["split"], 0) + 1
        domains[r["domain"]] = domains.get(r["domain"], 0) + 1
        labels[r["final_label"]] = labels.get(r["final_label"], 0) + 1

    single = sum(1 for r in records if len(set(t["strategy"] for t in r["strategy_trace"])) == 1)
    esc = sum(1 for r in records if sum(1 for t in r["strategy_trace"] if t["target_response_type"] == "refusal") >= 3 and any(t["tier_escalation_event"] for t in r["strategy_trace"]))
    switch = sum(1 for r in records if 2 <= len(set(t["strategy"] for t in r["strategy_trace"])) <= 4 and not (sum(1 for t in r["strategy_trace"] if t["target_response_type"] == "refusal") >= 3 and any(t["tier_escalation_event"] for t in r["strategy_trace"])))
    partial = sum(1 for r in records if any(t.get("target_response_type") == "partial_compliance" for t in r["strategy_trace"]))
    tier = sum(1 for r in records if any(t.get("tier_escalation_event") for t in r["strategy_trace"]))

    print("\nValidation counts:")
    print(f"  split: {splits} (expect train=40 eval=10)")
    print(f"  domain: {domains} (expect healthcare=10 public_service=10 finance=8 education=8 legal=7 general=7)")
    print(f"  final_label: {labels} (expect pass=18 needs_review=20 fail=12)")
    print(f"  strategy: single={single} switching={switch} full_escalation={esc} (expect 13, 20, 17)")
    print(f"  partial_compliance: {partial} (expect >=15)")
    print(f"  tier_escalation_event: {tier} (expect >=10)")

    # System prompt word count
    sys_words = len(records[0]["training_sample"]["messages"][0]["content"].split())
    print(f"  system prompt words: {sys_words} (expect >=200)")

    if errors:
        print(f"\n{len(errors)} errors:")
        for e in errors[:25]:
            print(f"  {e}")
        if len(errors) > 25:
            print(f"  ... and {len(errors)-25} more")
        return 1

    print("\nAll validations passed.")
    return 0


if __name__ == "__main__":
    exit(main())
