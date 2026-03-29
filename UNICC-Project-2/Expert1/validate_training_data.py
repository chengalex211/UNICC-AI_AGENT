#!/usr/bin/env python3
"""Validate the generated Expert 1 training data."""

import json

PATH = "/Users/yangjunjie/Capstone/unicc-ai-agent Team 1 Expert 1 Training Data"
REQUIRED_KEYS = ["id", "split", "language", "domain", "autonomy_level", "final_label", "audit_dialogue", "strategy_trace", "training_sample", "evidence"]
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
    
    print(f"Parsed {len(records)} records successfully")
    
    errors = []
    
    # Counts
    splits = {}
    domains = {}
    labels = {}
    single_count = 0
    switch_count = 0
    esc_count = 0
    
    for r in records:
        for k in REQUIRED_KEYS:
            if k not in r:
                errors.append(f"{r['id']}: missing key '{k}'")
        
        splits[r["split"]] = splits.get(r["split"], 0) + 1
        domains[r["domain"]] = domains.get(r["domain"], 0) + 1
        labels[r["final_label"]] = labels.get(r["final_label"], 0) + 1
        
        # Strategy complexity
        n_trace = len(r["strategy_trace"])
        if n_trace == 1:
            single_count += 1
        elif n_trace >= 2 and n_trace <= 4:
            refusals = sum(1 for t in r["strategy_trace"] if t.get("target_response_type") == "refusal")
            has_esc = any(t.get("tier_escalation_event") for t in r["strategy_trace"])
            if refusals >= 3 and has_esc:
                esc_count += 1
            else:
                switch_count += 1
        else:
            switch_count += 1
        
        # Training sample: exactly 3 messages
        msgs = r["training_sample"]["messages"]
        if len(msgs) != 3:
            errors.append(f"{r['id']}: training_sample.messages has {len(msgs)} messages (expected 3)")
        if msgs[0]["role"] != "system" or msgs[1]["role"] != "user" or msgs[2]["role"] != "assistant":
            errors.append(f"{r['id']}: message roles wrong: {[m['role'] for m in msgs]}")
        
        # Assistant content = valid JSON with required keys
        try:
            out = json.loads(msgs[2]["content"])
            for k in ["expert", "dimension_scores", "risk_tier", "needs_human_review", "review_trigger_reasons", "key_findings", "recommendation", "confidence"]:
                if k not in out:
                    errors.append(f"{r['id']}: assistant JSON missing '{k}'")
            for d in DIMENSIONS:
                if d not in out.get("dimension_scores", {}):
                    errors.append(f"{r['id']}: dimension_scores missing '{d}'")
        except json.JSONDecodeError as e:
            errors.append(f"{r['id']}: assistant content not valid JSON: {e}")
        
        # Strategy names
        for t in r["strategy_trace"]:
            s = t.get("strategy")
            if s not in STRATEGIES:
                errors.append(f"{r['id']}: invalid strategy '{s}'")
        
        # Evidence >= 3
        if len(r["evidence"]) < 3:
            errors.append(f"{r['id']}: evidence has {len(r['evidence'])} items (expected >=3)")
        
        # Turns content >= 2 sentences
        for t in r["audit_dialogue"]["turns"]:
            sents = t["content"].replace("?", ".").split(".")
            if len([x for x in sents if x.strip()]) < 2:
                errors.append(f"{r['id']} turn {t['turn_id']}: content has <2 sentences")
    
    # Report
    print(f"\nCounts:")
    print(f"  split: {splits} (expect train=40 eval=10)")
    print(f"  domain: {domains}")
    print(f"  final_label: {labels} (expect pass=18 needs_review=20 fail=12)")
    print(f"  strategy: single={single_count} switching={switch_count} full_escalation={esc_count} (expect 13, 20, 17)")
    
    partial_count = sum(1 for r in records if any(t.get("target_response_type") == "partial_compliance" for t in r["strategy_trace"]))
    tier_count = sum(1 for r in records if any(t.get("tier_escalation_event") for t in r["strategy_trace"]))
    print(f"  partial_compliance: {partial_count} (expect >=15)")
    print(f"  tier_escalation_event: {tier_count} (expect >=10)")
    
    if errors:
        print(f"\n{len(errors)} errors:")
        for e in errors[:20]:
            print(f"  {e}")
        if len(errors) > 20:
            print(f"  ... and {len(errors)-20} more")
        return 1
    
    print("\nAll validations passed.")
    return 0

if __name__ == "__main__":
    exit(main())
