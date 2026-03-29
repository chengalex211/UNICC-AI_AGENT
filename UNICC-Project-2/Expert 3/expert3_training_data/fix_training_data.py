"""
fix_training_data.py
Fixes three quality issues in training_data_expert3_final.jsonl:

  1. Empty un_principle_violations (51 samples) — infer from dimension scores + user content
  2. Non-standard violation label formats (49 samples) — normalize to 6 canonical labels
  3. risk_tier inconsistent with dimension scores (16 samples) — recalculate deterministically

Run:
    python fix_training_data.py
"""

import json
import re
from pathlib import Path
from collections import Counter

INPUT  = "./training_data_expert3_final.jsonl"
OUTPUT = "./training_data_expert3_final_fixed.jsonl"

VALID_LABELS = {
    "UN_Charter_Art1.3",
    "UN_Charter_Art2.1",
    "UN_Charter_Art2.7",
    "UNESCO_DoNoHarm",
    "UNESCO_HumanOversight",
    "UN_DataProtection_P9",
}

# ── Label normalisation map ───────────────────────────────────────────────────
# Each entry: (regex pattern, canonical label)
# Checked in order; first match wins.

LABEL_NORMALISE = [
    # UN Charter Art 1.3 — non-discrimination
    (r"art\.?\s*1\.3|non.?discriminat|race|gender|language.*discriminat|"
     r"protected.charact|equal.right|discrimin.*race|discrimin.*nation|"
     r"nationality.bias|racial.bias|ethnic.bias|gender.bias|"
     r"language.based.discriminat|color|colour",
     "UN_Charter_Art1.3"),

    # UN Charter Art 2.1 — sovereign equality
    (r"art\.?\s*2\.1|sovereign.equalit|member.state|unequal.*deploy|"
     r"global.south|least.develop|lmic|developing.countr|"
     r"disproportionate.*member|differential.*state",
     "UN_Charter_Art2.1"),

    # UN Charter Art 2.7 — non-intervention
    (r"art\.?\s*2\.7|non.?interven|non.?interfer|political.neutral|"
     r"political.manipul|state.surveill|domestic.affair|political.express|"
     r"political.repres|political.bias",
     "UN_Charter_Art2.7"),

    # UN Data Protection Principle 9 — transfers
    (r"p(?:rinciple)?\s*9|transfer|data.protection|personal.data|"
     r"biometric.data|privacy|gdpr|consent|purpose.limit|"
     r"data.sovereignty|data.breach|data.leak|unchecked.transfer|"
     r"third.party|data.sharing|data.retention|data.subject",
     "UN_DataProtection_P9"),

    # UNESCO Do No Harm
    (r"do.no.harm|proportional|harm|safety.risk|wellbeing|"
     r"real.world.harm|serious.harm|documented.harm|"
     r"severe.harm|physical.harm|wrongful|false.positive.*harm|"
     r"cause.*harm|dangerous",
     "UNESCO_DoNoHarm"),

    # UNESCO Human Oversight
    (r"human.oversight|human.review|accountability|appeal.mechanism|"
     r"no.appeal|no.recourse|rubber.stamp|oversight|human.control|"
     r"human.in.the.loop|human.supervis|override|explainab|"
     r"transparency.*decision|opaque.*decision|black.box",
     "UNESCO_HumanOversight"),
]


def normalise_label(raw: str) -> str | None:
    """Map a raw label string to one of the 6 canonical labels, or None if unrecognisable."""
    if raw in VALID_LABELS:
        return raw
    raw_lower = raw.lower()
    for pattern, canonical in LABEL_NORMALISE:
        if re.search(pattern, raw_lower):
            return canonical
    return None


# ── Risk tier recalculation ───────────────────────────────────────────────────

def compute_risk_tier(scores: dict) -> str:
    vals = list(scores.values())
    mx   = max(vals)
    avg  = sum(vals) / len(vals)
    if mx == 5 or avg >= 4.0:
        return "UNACCEPTABLE"
    if mx >= 4 or avg >= 3.0:
        return "HIGH"
    if mx == 3 or avg > 2.0:
        return "LIMITED"
    return "MINIMAL"


# ── Infer violations for empty lists ─────────────────────────────────────────
# Priority: use dimension scores to pick the most likely violated/evaluated principle.
# Even APPROVE samples should cite at least one principle that was evaluated.

def infer_violations(scores: dict, user_content: str) -> list[str]:
    """
    Infer the most relevant UN principles based on dimension scores and user content.
    Returns a list of 1-3 canonical labels.
    """
    content_lower = user_content.lower()
    candidates: list[tuple[float, str]] = []  # (priority, label)

    # Score each label based on dimension scores + content keywords
    eth = scores.get("ethical_risk", 1)
    leg = scores.get("legal_risk", 1)
    soc = scores.get("societal_risk", 1)
    tec = scores.get("technical_risk", 1)

    # UN_Charter_Art1.3 — triggered by ethical_risk or discrimination keywords
    p_art13 = eth * 1.5
    if any(kw in content_lower for kw in ["discriminat", "bias", "race", "gender",
                                           "nationality", "ethnic", "language", "equal"]):
        p_art13 += 3
    candidates.append((p_art13, "UN_Charter_Art1.3"))

    # UN_DataProtection_P9 — triggered by legal_risk or data keywords
    p_p9 = leg * 1.5
    if any(kw in content_lower for kw in ["data", "privacy", "biometric", "personal",
                                           "consent", "transfer", "gdpr", "breach"]):
        p_p9 += 3
    candidates.append((p_p9, "UN_DataProtection_P9"))

    # UNESCO_DoNoHarm — triggered by technical_risk or harm keywords
    p_harm = tec * 1.2
    if any(kw in content_lower for kw in ["harm", "risk", "danger", "safe", "wrong",
                                           "false", "error", "failure", "inaccura"]):
        p_harm += 2
    candidates.append((p_harm, "UNESCO_DoNoHarm"))

    # UNESCO_HumanOversight — triggered by automation or oversight keywords
    p_oversight = (tec + eth) * 0.7
    if any(kw in content_lower for kw in ["automat", "oversight", "review", "human",
                                           "appeal", "recourse", "black box", "opaque"]):
        p_oversight += 2
    candidates.append((p_oversight, "UNESCO_HumanOversight"))

    # UN_Charter_Art2.7 — triggered by political/surveillance keywords
    p_art27 = soc * 1.2
    if any(kw in content_lower for kw in ["political", "surveillance", "neutral",
                                           "non-interfer", "sovereign", "state"]):
        p_art27 += 3
    candidates.append((p_art27, "UN_Charter_Art2.7"))

    # UN_Charter_Art2.1 — triggered by sovereign equality keywords
    p_art21 = 1.0
    if any(kw in content_lower for kw in ["member state", "global south", "developing",
                                           "sovereign equalit", "lmic", "unequal"]):
        p_art21 += 4
    candidates.append((p_art21, "UN_Charter_Art2.1"))

    # Sort by priority, take top 1-2
    candidates.sort(key=lambda x: x[0], reverse=True)
    top = [label for _, label in candidates[:2] if _ > 0]
    return top if top else ["UN_Charter_Art1.3"]  # fallback


# ── Main fix logic ────────────────────────────────────────────────────────────

def fix_sample(sample: dict) -> tuple[dict, list[str]]:
    """Fix one sample. Returns (fixed_sample, list_of_changes_made)."""
    changes = []
    msgs = sample.get("messages", [])

    # Find assistant message
    asst_msg = next((m for m in msgs if m["role"] == "assistant"), None)
    if not asst_msg:
        return sample, ["SKIP: no assistant message"]

    try:
        asst = json.loads(asst_msg["content"])
    except json.JSONDecodeError:
        return sample, ["SKIP: assistant content not valid JSON"]

    scores = asst.get("dimension_scores", {})
    user_content = next((m["content"] for m in msgs if m["role"] == "user"), "")

    # ── Fix 1: Normalise violation labels ────────────────────────────────────
    raw_violations = asst.get("un_principle_violations", [])
    normalised = []
    skipped    = []
    for raw in raw_violations:
        if not raw or raw.strip() == "":
            continue
        canon = normalise_label(raw)
        if canon:
            if canon not in normalised:
                normalised.append(canon)
            if canon != raw:
                changes.append(f"LABEL: '{raw[:50]}' → {canon}")
        else:
            skipped.append(raw)
            changes.append(f"LABEL_SKIP (unrecognised): '{raw[:60]}'")

    if skipped:
        # Try harder: pick best match from skipped using infer logic
        for raw in skipped:
            inferred = infer_violations(scores, raw + " " + user_content[:200])
            for label in inferred:
                if label not in normalised:
                    normalised.append(label)
                    changes.append(f"LABEL_INFERRED from unrecognised: {label}")

    # ── Fix 2: Fill empty violations ─────────────────────────────────────────
    if not normalised:
        normalised = infer_violations(scores, user_content)
        changes.append(f"VIOLATIONS_INFERRED (was empty): {normalised}")

    asst["un_principle_violations"] = normalised

    # ── Fix 3: Recalculate risk_tier ─────────────────────────────────────────
    if scores:
        correct_tier = compute_risk_tier(scores)
        if asst.get("risk_tier") != correct_tier:
            changes.append(f"TIER: {asst.get('risk_tier')} → {correct_tier}")
            asst["risk_tier"] = correct_tier

        # Also fix human_review_required consistency
        tech = scores.get("technical_risk", 1)
        eth  = scores.get("ethical_risk", 1)
        leg  = scores.get("legal_risk", 1)
        soc  = scores.get("societal_risk", 1)
        correct_review = (
            tech >= 4 or eth >= 4 or leg >= 4 or soc >= 3
            or correct_tier in ("HIGH", "UNACCEPTABLE")
        )
        if asst.get("human_review_required") != correct_review:
            changes.append(f"REVIEW: {asst.get('human_review_required')} → {correct_review}")
            asst["human_review_required"] = correct_review

        # Fix recommendation consistency
        correct_rec = {
            "MINIMAL": "APPROVE", "LIMITED": "APPROVE",
            "HIGH": "REVIEW", "UNACCEPTABLE": "REJECT"
        }.get(correct_tier, asst.get("recommendation", "REVIEW"))
        if asst.get("recommendation") != correct_rec:
            changes.append(f"REC: {asst.get('recommendation')} → {correct_rec}")
            asst["recommendation"] = correct_rec

    asst_msg["content"] = json.dumps(asst, ensure_ascii=False)
    return sample, changes


# ── Run ───────────────────────────────────────────────────────────────────────

def main():
    lines = Path(INPUT).read_text(encoding="utf-8").splitlines()
    samples = []
    for line in lines:
        line = line.strip()
        if line:
            samples.append(json.loads(line))

    print(f"Loaded {len(samples)} samples from {INPUT}\n")

    fixed_samples = []
    change_log    = []
    n_changed     = 0

    for i, sample in enumerate(samples):
        fixed, changes = fix_sample(sample)
        fixed_samples.append(fixed)
        if changes:
            n_changed += 1
            change_log.append(f"[{i+1}] {changes}")

    # Write output
    with open(OUTPUT, "w", encoding="utf-8") as f:
        for s in fixed_samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")

    print(f"Fixed {n_changed} samples → {OUTPUT}\n")

    # Statistics
    label_counts = Counter()
    empty_count  = 0
    tier_counts  = Counter()
    rec_counts   = Counter()

    for s in fixed_samples:
        asst_msg = next((m for m in s["messages"] if m["role"] == "assistant"), None)
        if not asst_msg:
            continue
        try:
            asst = json.loads(asst_msg["content"])
        except Exception:
            continue
        violations = asst.get("un_principle_violations", [])
        if not violations:
            empty_count += 1
        for v in violations:
            label_counts[v] += 1
        tier_counts[asst.get("risk_tier", "?")] += 1
        rec_counts[asst.get("recommendation", "?")] += 1

    print("=" * 55)
    print("POST-FIX STATISTICS")
    print("=" * 55)
    print(f"\nSamples with empty violations: {empty_count}")
    print(f"\nViolation label distribution:")
    for label, count in sorted(label_counts.items()):
        valid = "✓" if label in VALID_LABELS else "✗ NON-STANDARD"
        print(f"  {valid}  {label}: {count}")
    print(f"\nRisk tier distribution: {dict(tier_counts)}")
    print(f"Recommendation distribution: {dict(rec_counts)}")

    if change_log:
        print(f"\n--- Change log (first 20) ---")
        for entry in change_log[:20]:
            print(entry)
        if len(change_log) > 20:
            print(f"... and {len(change_log) - 20} more")


if __name__ == "__main__":
    main()
