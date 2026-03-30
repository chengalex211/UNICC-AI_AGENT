#!/usr/bin/env python3
"""
Build a deterministic dimension-score lookup table for every ATLAS technique
and case study, then save to atlas_dimension_scores.json.

Scoring approach (no LLM needed — fully deterministic):
  1. Each ATLAS tactic maps to 1-2 primary dimensions + impact weight
  2. Technique maturity (demonstrated / emerging) multiplies severity
  3. Attack layer (model / application / social_engineering) adds secondary dims
  4. Case studies add extra weight if humanitarian_risk == high

Dimension scale: 1 (lowest risk) → 5 (highest risk), matching Expert 1 convention.
"""

import json
import yaml
from pathlib import Path

ATLAS_YAML   = Path(__file__).parent.parent / "atlas-data" / "dist" / "ATLAS.yaml"
OUT_PATH     = Path(__file__).parent / "atlas_dimension_scores.json"

DIMS = ["harmfulness", "bias_fairness", "transparency",
        "deception", "privacy", "legal_compliance", "self_preservation"]

# ── Tactic → primary dimension impact ─────────────────────────────────────────
# (dimension, base_delta)  — delta added to that dimension's risk score
TACTIC_MAP: dict[str, list[tuple[str, float]]] = {
    "AML.TA0000": [("self_preservation", 1.5), ("harmfulness", 1.0)],   # AI Model Access
    "AML.TA0001": [("harmfulness", 1.5), ("self_preservation", 1.0)],   # AI Attack Staging
    "AML.TA0002": [("transparency", 1.0), ("privacy", 0.5)],            # Reconnaissance
    "AML.TA0003": [("harmfulness", 0.5)],                               # Resource Development
    "AML.TA0004": [("self_preservation", 1.0), ("harmfulness", 1.0)],   # Initial Access
    "AML.TA0005": [("harmfulness", 1.5)],                               # Execution
    "AML.TA0006": [("self_preservation", 1.5), ("harmfulness", 1.0)],   # Persistence
    "AML.TA0007": [("deception", 1.5), ("transparency", 1.0)],          # Defense Evasion
    "AML.TA0008": [("transparency", 1.0), ("privacy", 0.5)],            # Discovery
    "AML.TA0009": [("privacy", 1.5), ("legal_compliance", 1.0)],        # Collection → Exfiltration path
    "AML.TA0010": [("privacy", 2.0), ("legal_compliance", 1.5)],        # Exfiltration
    "AML.TA0011": [("harmfulness", 2.0), ("bias_fairness", 0.5)],       # Impact
    "AML.TA0012": [("self_preservation", 1.0), ("privacy", 1.0)],       # Privilege Escalation
    "AML.TA0013": [("privacy", 1.5), ("legal_compliance", 1.0)],        # Credential Access
    "AML.TA0014": [("harmfulness", 1.0), ("self_preservation", 0.5)],   # C2
    "AML.TA0015": [("harmfulness", 1.0), ("privacy", 0.5)],             # Lateral Movement
}

# ── Attack layer → secondary dimension boost ───────────────────────────────────
LAYER_MAP: dict[str, list[tuple[str, float]]] = {
    "model":              [("self_preservation", 0.5), ("bias_fairness", 0.5)],
    "application":        [("privacy", 0.5), ("deception", 0.5)],
    "social_engineering": [("deception", 1.0), ("transparency", 0.5)],
    "mixed":              [("self_preservation", 0.3), ("deception", 0.3)],
}

# ── Maturity multiplier ────────────────────────────────────────────────────────
MATURITY_MULT = {
    "demonstrated": 1.5,   # has real-world evidence
    "emerging":     1.0,
    "theoretical":  0.7,
}

# ── Humanitarian risk (case studies only) ─────────────────────────────────────
HUMANITARIAN_BOOST = {
    "high":   1.5,
    "medium": 1.0,
    "low":    0.7,
}


def base_scores() -> dict[str, float]:
    return {d: 1.0 for d in DIMS}


def clamp(v: float) -> int:
    return max(1, min(5, round(v)))


def score_technique(tech: dict) -> dict:
    scores = base_scores()
    tactics = tech.get("tactics", [])
    layer   = tech.get("attack_layer", tech.get("layer", "mixed"))
    maturity = tech.get("maturity", "emerging")
    mult    = MATURITY_MULT.get(maturity, 1.0)

    # Tactic contributions
    for tactic_id in tactics:
        for dim, delta in TACTIC_MAP.get(tactic_id, []):
            scores[dim] += delta * mult

    # Layer contributions
    for dim, delta in LAYER_MAP.get(layer, LAYER_MAP["mixed"]):
        scores[dim] += delta

    return {d: clamp(scores[d]) for d in DIMS}


def score_case_study(cs: dict, technique_lookup: dict[str, dict]) -> dict:
    """Aggregate technique scores + humanitarian boost."""
    scores = base_scores()

    # Pull humanitarian_risk from tags in ChromaDB version, or from YAML directly
    hum_risk = cs.get("humanitarian_risk", "medium")
    hum_mult = HUMANITARIAN_BOOST.get(str(hum_risk).lower(), 1.0)

    # Aggregate all techniques used in this case study
    procedures = cs.get("procedure", [])
    tech_scores_list = []
    for proc in procedures:
        tech_id = proc.get("technique", "")
        if tech_id in technique_lookup:
            tech_scores_list.append(technique_lookup[tech_id]["scores"])

    if tech_scores_list:
        for dim in DIMS:
            avg = sum(ts[dim] for ts in tech_scores_list) / len(tech_scores_list)
            scores[dim] = avg * hum_mult
    else:
        # No techniques → conservative defaults
        for dim in DIMS:
            scores[dim] = 3.0

    return {d: clamp(scores[d]) for d in DIMS}


def main():
    print(f"Loading ATLAS from {ATLAS_YAML}…")
    with open(ATLAS_YAML) as f:
        atlas = yaml.safe_load(f)

    matrix     = atlas["matrices"][0]
    techniques = matrix["techniques"]
    case_studies = atlas["case-studies"]

    lookup: dict[str, dict] = {}

    # ── Score techniques ───────────────────────────────────────────────────────
    print(f"Scoring {len(techniques)} techniques…")
    for tech in techniques:
        tid = tech["id"]
        scores = score_technique(tech)
        lookup[tid] = {
            "id":          tid,
            "name":        tech["name"],
            "type":        "technique",
            "tactics":     tech.get("tactics", []),
            "maturity":    tech.get("maturity", "emerging"),
            "attack_layer": tech.get("attack_layer", "mixed"),
            "scores":      scores,
            "citation":    f"MITRE ATLAS {tid} — {tech['name']}",
        }
        # Also add subtechniques as aliases
        for sub in [t for t in techniques if t.get("subtechnique-of") == tid]:
            sub_id = sub["id"]
            sub_scores = score_technique(sub)
            lookup[sub_id] = {
                "id":     sub_id,
                "name":   sub["name"],
                "type":   "subtechnique",
                "parent": tid,
                "tactics": sub.get("tactics", tech.get("tactics", [])),
                "maturity": sub.get("maturity", tech.get("maturity", "emerging")),
                "attack_layer": sub.get("attack_layer", tech.get("attack_layer", "mixed")),
                "scores":  sub_scores,
                "citation": f"MITRE ATLAS {sub_id} — {sub['name']} (sub of {tid})",
            }

    # ── Score case studies ─────────────────────────────────────────────────────
    print(f"Scoring {len(case_studies)} case studies…")
    for cs in case_studies:
        cid = cs["id"]
        scores = score_case_study(cs, lookup)
        lookup[cid] = {
            "id":     cid,
            "name":   cs["name"],
            "type":   "case_study",
            "scores": scores,
            "citation": f"MITRE ATLAS {cid} — {cs['name']} (real-world incident)",
        }

    # ── Dimension → all techniques sorted by impact ────────────────────────────
    dim_leaders: dict[str, list] = {}
    for dim in DIMS:
        ranked = sorted(
            [(v["id"], v["name"], v["scores"][dim]) for v in lookup.values()
             if v["type"] in ("technique", "subtechnique")],
            key=lambda x: -x[2]
        )
        dim_leaders[dim] = ranked[:10]

    output = {
        "meta": {
            "total_entries": len(lookup),
            "techniques":    sum(1 for v in lookup.values() if v["type"] == "technique"),
            "subtechniques": sum(1 for v in lookup.values() if v["type"] == "subtechnique"),
            "case_studies":  sum(1 for v in lookup.values() if v["type"] == "case_study"),
            "dimensions":    DIMS,
            "scoring_logic": {
                "tactic_map":    {k: v for k, v in TACTIC_MAP.items()},
                "maturity_mult": MATURITY_MULT,
                "layer_map":     {k: v for k, v in LAYER_MAP.items()},
            },
        },
        "dim_leaders":  dim_leaders,
        "entries":      lookup,
    }

    OUT_PATH.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    print(f"\nSaved {len(lookup)} entries → {OUT_PATH}")
    print("\nTop-3 per dimension:")
    for dim in DIMS:
        top3 = dim_leaders[dim][:3]
        print(f"  {dim:20s}: {[(t[0], t[2]) for t in top3]}")


if __name__ == "__main__":
    main()
