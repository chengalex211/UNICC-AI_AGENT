#!/usr/bin/env python3
"""
Build benchmark candidate seeds for UNICC AI Safety Council.

This script creates a first-pass benchmark pool using:
1) Expert1/incidents.csv
2) atlas-data/dist/ATLAS.yaml
3) Expert 2 / Expert 3 training datasets (as provisional candidates)
4) council/test_cases_all.py + council/results/summary.json

Outputs are written under:
  data/benchmark/v1/{raw,normalized,splits,manifests}
"""

from __future__ import annotations

import csv
import json
import random
import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_OUT_BASE = ROOT / "benchmark_data" / "v1"

OUT_BASE = DEFAULT_OUT_BASE
RAW_DIR = OUT_BASE / "raw"
NORM_DIR = OUT_BASE / "normalized"
SPLIT_DIR = OUT_BASE / "splits"
MANIFEST_DIR = OUT_BASE / "manifests"

SEED = 42
RNG = random.Random(SEED)


@dataclass
class TargetCounts:
    e1_incidents: int = 25
    e1_atlas: int = 15
    e2: int = 15
    e3: int = 15
    council: int = 10

    @property
    def total(self) -> int:
        return self.e1_incidents + self.e1_atlas + self.e2 + self.e3 + self.council


COUNTS = TargetCounts()


def _ensure_dirs() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    NORM_DIR.mkdir(parents=True, exist_ok=True)
    SPLIT_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)


def _set_output_base(base_dir: Path) -> None:
    global OUT_BASE, RAW_DIR, NORM_DIR, SPLIT_DIR, MANIFEST_DIR
    OUT_BASE = base_dir
    RAW_DIR = OUT_BASE / "raw"
    NORM_DIR = OUT_BASE / "normalized"
    SPLIT_DIR = OUT_BASE / "splits"
    MANIFEST_DIR = OUT_BASE / "manifests"


def _severity(label: str | None) -> int:
    if label == "REJECT":
        return 2
    if label == "REVIEW":
        return 1
    return 0


def _derive_consensus_recommendation(expected_e1: str, expected_e2: str, expected_e3: str) -> str:
    labels = [expected_e1, expected_e2, expected_e3]
    score = max(_severity(v) for v in labels)
    return "REJECT" if score == 2 else ("REVIEW" if score == 1 else "APPROVE")


def _ensure_unique_sample_ids(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[str, int] = {}
    out: list[dict[str, Any]] = []
    for r in rows:
        base = str(r.get("sample_id") or "sample")
        n = seen.get(base, 0) + 1
        seen[base] = n
        if n == 1:
            out.append(r)
            continue
        rr = dict(r)
        rr["sample_id"] = f"{base}__{n}"
        out.append(rr)
    return out


def _safe_jsonl_read(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    return rows


def _extract_recommendation_from_messages(messages: list[dict[str, Any]]) -> str | None:
    if not messages:
        return None
    last = messages[-1]
    if last.get("role") != "assistant":
        return None
    content = last.get("content", "")
    if not isinstance(content, str):
        return None
    try:
        parsed = json.loads(content)
    except Exception:
        return None
    rec = parsed.get("recommendation")
    if isinstance(rec, str):
        return rec
    # Expert 2 data may use overall_compliance instead of recommendation.
    compliance = parsed.get("overall_compliance")
    if isinstance(compliance, str):
        cmap = {
            "COMPLIANT": "APPROVE",
            "CONDITIONAL": "REVIEW",
            "NON_COMPLIANT": "REJECT",
            "FAIL": "REJECT",
            "PASS": "APPROVE",
        }
        return cmap.get(compliance.upper())
    return None


def build_e1_incident_candidates(limit: int) -> list[dict[str, Any]]:
    path = ROOT / "Expert1" / "incidents.csv"
    if not path.exists():
        return []
    candidates: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            title = (row.get("title") or "").strip()
            text = (row.get("text") or "").strip()
            incident_id = (row.get("incident_id") or "").strip()
            if not title or not text:
                continue
            snippet = text[:1800]
            ref_number = (row.get("ref_number") or "").strip()
            suffix = f"{incident_id}_{ref_number}" if incident_id and ref_number else (incident_id or str(idx))
            candidates.append(
                {
                    "sample_id": f"e1_inc_{suffix}",
                    "expert_target": "e1",
                    "source_type": "incident_csv",
                    "source_path": str(path.relative_to(ROOT)),
                    "input": {
                        "agent_id": f"incident-{incident_id or idx}",
                        "system_name": title[:120],
                        "system_description": (
                            f"Incident-derived scenario for security evaluation.\n\n"
                            f"Title: {title}\n\nExcerpt:\n{snippet}"
                        ),
                    },
                    "provisional_gold": {
                        "recommendation": None,
                        "risk_tier": None,
                        "human_review_required": True,
                        "citations": [],
                        "must_hit_findings": [],
                        "provenance": "requires_human_annotation",
                    },
                    "tags": ["e1", "incident", "real_world_like", "needs_gold"],
                }
            )
            if len(candidates) >= max(limit * 4, 200):
                break
    candidates.sort(key=lambda x: len(x["input"]["system_description"]), reverse=True)
    return candidates[:limit]


def build_e1_atlas_candidates(limit: int) -> list[dict[str, Any]]:
    atlas_path = ROOT / "atlas-data" / "dist" / "ATLAS.yaml"
    if not atlas_path.exists():
        return []
    try:
        import yaml  # type: ignore
    except Exception:
        return []
    with atlas_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    studies = data.get("case-studies") or []
    candidates: list[dict[str, Any]] = []
    for idx, cs in enumerate(studies):
        if not isinstance(cs, dict):
            continue
        cs_id = str(cs.get("id") or f"atlas-{idx}")
        name = str(cs.get("name") or cs.get("title") or f"ATLAS Case {idx}")
        description = str(cs.get("description") or "").strip()
        summary = str(cs.get("summary") or "").strip()
        text = description or summary
        if not text:
            continue
        external_refs = cs.get("external_references") or []
        refs: list[str] = []
        if isinstance(external_refs, list):
            for r in external_refs[:3]:
                if isinstance(r, dict):
                    src = r.get("source_name")
                    url = r.get("url")
                    if src and url:
                        refs.append(f"{src}: {url}")
        techniques = cs.get("techniques") or []
        t_list = [str(t) for t in techniques[:5]] if isinstance(techniques, list) else []
        desc_block = (
            f"ATLAS case-study derived scenario.\n\n"
            f"Case ID: {cs_id}\n"
            f"Case Name: {name}\n"
            f"Summary: {text[:1600]}\n"
            f"Techniques: {', '.join(t_list) if t_list else 'N/A'}\n"
            f"Refs: {' | '.join(refs) if refs else 'N/A'}"
        )
        candidates.append(
            {
                "sample_id": f"e1_atlas_{cs_id}",
                "expert_target": "e1",
                "source_type": "atlas_case_study",
                "source_path": str(atlas_path.relative_to(ROOT)),
                "input": {
                    "agent_id": f"atlas-{cs_id.lower()}",
                    "system_name": name[:120],
                    "system_description": desc_block,
                },
                "provisional_gold": {
                    "recommendation": None,
                    "risk_tier": None,
                    "human_review_required": True,
                    "citations": refs,
                    "must_hit_findings": [],
                    "provenance": "atlas_seed_requires_human_annotation",
                },
                "tags": ["e1", "atlas", "attack_taxonomy", "needs_gold"],
            }
        )
    RNG.shuffle(candidates)
    return candidates[:limit]


def build_e2_candidates(limit: int) -> list[dict[str, Any]]:
    summary_path = ROOT / "council" / "results" / "summary.json"
    if not summary_path.exists():
        return []
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    rows = summary.get("results", [])
    candidates: list[dict[str, Any]] = []
    for idx, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        agent_id = str(row.get("agent_id") or f"e2-{idx+1}")
        system_name = str(row.get("system_name") or agent_id)
        pattern = str(row.get("pattern") or "unknown")
        source = str(row.get("source") or "unknown")
        expected_e2 = str(row.get("expected_e2") or "REVIEW")
        scenario = (
            f"Governance and compliance benchmark seed.\n\n"
            f"System: {system_name}\n"
            f"Agent ID: {agent_id}\n"
            f"Scenario source cohort: {source}\n"
            f"Pattern tag: {pattern}\n\n"
            f"This candidate is derived from prior council evaluation cohorts and requires "
            f"manual legal citation annotation (EU AI Act / GDPR / UNESCO / NIST as applicable)."
        )
        candidates.append(
            {
                "sample_id": f"e2_trainseed_{idx+1}",
                "expert_target": "e2",
                "source_type": "council_summary_compliance_seed",
                "source_path": str(summary_path.relative_to(ROOT)),
                "input": {
                    "agent_id": agent_id,
                    "system_name": system_name,
                    "system_description": scenario,
                },
                "provisional_gold": {
                    "recommendation": expected_e2,
                    "risk_tier": None,
                    "human_review_required": True,
                    "citations": [],
                    "must_hit_findings": [],
                    "provenance": "summary_derived_requires_human_annotation",
                },
                "tags": ["e2", "compliance", "summary_derived", "needs_gold"],
            }
        )
    RNG.shuffle(candidates)
    return candidates[:limit]


def build_e3_candidates(limit: int) -> list[dict[str, Any]]:
    path = ROOT / "Expert 3" / "expert3_training_data" / "aiid_selected_incidents.csv"
    if not path.exists():
        return []
    candidates: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            title = str(row.get("title") or "").strip()
            if not title:
                continue
            recommendation = str(row.get("recommendation") or "REVIEW").strip().upper()
            risk_tier = str(row.get("risk_tier") or "").strip().upper() or None
            description = (
                f"UN mission-fit benchmark seed from AI incident corpus.\n\n"
                f"Title: {title}\n"
                f"Incident ID: {row.get('incident_id')}\n"
                f"Risk indicators: technical={row.get('technical_risk')}, "
                f"ethical={row.get('ethical_risk')}, legal={row.get('legal_risk')}, "
                f"societal={row.get('societal_risk')}\n"
                f"Keyword hints: {row.get('high_keywords') or ''}\n\n"
                f"This scenario requires manual principle mapping (UN Charter / UNESCO / IHL / human rights)."
            )
            if recommendation not in {"APPROVE", "REVIEW", "REJECT"}:
                recommendation = "REVIEW"
            rank = str(row.get("rank") or idx + 1)
            sid = f"{row.get('incident_id') or idx+1}_{rank}"
            candidates.append(
                {
                    "sample_id": f"e3_aiid_{sid}",
                    "expert_target": "e3",
                    "source_type": "aiid_selected_incident_seed",
                    "source_path": str(path.relative_to(ROOT)),
                    "input": {
                        "agent_id": f"e3-aiid-{row.get('incident_id') or idx+1}",
                        "system_name": title[:120],
                        "system_description": description,
                    },
                    "provisional_gold": {
                        "recommendation": recommendation,
                        "risk_tier": risk_tier,
                        "human_review_required": recommendation in {"REVIEW", "REJECT"},
                        "citations": [],
                        "must_hit_findings": [],
                        "provenance": "aiid_ranked_seed_requires_human_annotation",
                    },
                    "tags": ["e3", "un_mission_fit", "incident_seed", "needs_gold"],
                }
            )
            if len(candidates) >= max(limit * 4, 120):
                break
    RNG.shuffle(candidates)
    return candidates[:limit]


def build_council_candidates(limit: int) -> list[dict[str, Any]]:
    summary_path = ROOT / "council" / "results" / "summary.json"
    reports_dir = ROOT / "council" / "results" / "reports"
    if not summary_path.exists() or not reports_dir.exists():
        return []

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    results = summary.get("results", [])
    candidates: list[dict[str, Any]] = []
    for idx, r in enumerate(results):
        if not isinstance(r, dict):
            continue
        agent_id = str(r.get("agent_id") or f"council-{idx}")
        system_name = str(r.get("system_name") or agent_id)
        report_path = reports_dir / f"{agent_id}.json"
        findings_snippet = ""
        if report_path.exists():
            try:
                rp = json.loads(report_path.read_text(encoding="utf-8"))
                exp = rp.get("expert_reports") or {}
                fparts: list[str] = []
                for ek in ["security", "governance", "un_mission_fit"]:
                    er = exp.get(ek) or {}
                    kf = er.get("key_findings") or []
                    if isinstance(kf, list) and kf:
                        fparts.append(f"{ek}: {str(kf[0])[:220]}")
                findings_snippet = " | ".join(fparts)[:1200]
            except Exception:
                findings_snippet = ""
        system_description = (
            f"Council end-to-end benchmark seed.\n\n"
            f"System: {system_name}\n"
            f"Agent ID: {agent_id}\n"
            f"Prior pattern: {r.get('pattern')}\n"
            f"Source cohort: {r.get('source')}\n"
            f"Observed finding snippets: {findings_snippet or 'N/A'}\n\n"
            f"Manual annotation required for final arbitration-quality gold."
        )
        exp_e1 = str(r.get("expected_e1") or "APPROVE")
        exp_e2 = str(r.get("expected_e2") or "APPROVE")
        exp_e3 = str(r.get("expected_e3") or "APPROVE")
        final_exp = _derive_consensus_recommendation(exp_e1, exp_e2, exp_e3)

        candidates.append(
            {
                "sample_id": f"council_seed_{agent_id}",
                "expert_target": "council",
                "source_type": "council_results_seed",
                "source_path": str(summary_path.relative_to(ROOT)),
                "input": {
                    "agent_id": agent_id,
                    "system_name": system_name,
                    "system_description": system_description[:3000],
                },
                "provisional_gold": {
                    "recommendation": final_exp,
                    "risk_tier": None,
                    "human_review_required": final_exp in {"REVIEW", "REJECT"},
                    "citations": [],
                    "must_hit_findings": [],
                    "provenance": "expected_labels_projection_requires_human_review",
                },
                "tags": [
                    "council",
                    "multi_expert",
                    f"pattern_{str(r.get('pattern') or 'unknown').lower()}",
                    f"source_{str(r.get('source') or 'unknown').lower()}",
                ],
            }
        )
    RNG.shuffle(candidates)
    return candidates[:limit]


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def build_splits(all_rows: list[dict[str, Any]], dev_ratio: float = 0.4) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for r in all_rows:
        t = str(r.get("expert_target") or "unknown")
        grouped.setdefault(t, []).append(r)
    dev: list[dict[str, Any]] = []
    test: list[dict[str, Any]] = []
    for target, rows in grouped.items():
        rows_copy = rows[:]
        RNG.shuffle(rows_copy)
        cut = max(1, int(len(rows_copy) * dev_ratio))
        d = rows_copy[:cut]
        t = rows_copy[cut:]
        for x in d:
            x["split"] = "dev"
        for x in t:
            x["split"] = "test"
        dev.extend(d)
        test.extend(t)
    return dev, test


def main() -> None:
    parser = argparse.ArgumentParser(description="Build benchmark seed candidates.")
    parser.add_argument(
        "--out-base",
        default=str(DEFAULT_OUT_BASE),
        help="Output directory for benchmark seed pack (default: benchmark_data/v1)",
    )
    args = parser.parse_args()
    _set_output_base(Path(args.out_base))

    _ensure_dirs()

    e1_inc = build_e1_incident_candidates(COUNTS.e1_incidents)
    e1_atlas = build_e1_atlas_candidates(COUNTS.e1_atlas)
    e2 = build_e2_candidates(COUNTS.e2)
    e3 = build_e3_candidates(COUNTS.e3)
    council = build_council_candidates(COUNTS.council)

    _write_jsonl(RAW_DIR / "candidate_seed_e1_incidents.jsonl", e1_inc)
    _write_jsonl(RAW_DIR / "candidate_seed_e1_atlas.jsonl", e1_atlas)
    _write_jsonl(RAW_DIR / "candidate_seed_e2.jsonl", e2)
    _write_jsonl(RAW_DIR / "candidate_seed_e3.jsonl", e3)
    _write_jsonl(RAW_DIR / "candidate_seed_council.jsonl", council)

    all_rows = e1_inc + e1_atlas + e2 + e3 + council
    all_rows = _ensure_unique_sample_ids(all_rows)
    RNG.shuffle(all_rows)

    _write_jsonl(NORM_DIR / "candidate_seed_all.jsonl", all_rows)
    dev_rows, test_rows = build_splits(all_rows, dev_ratio=0.4)
    _write_jsonl(SPLIT_DIR / "dev.jsonl", dev_rows)
    _write_jsonl(SPLIT_DIR / "test.jsonl", test_rows)

    by_target: dict[str, int] = {}
    for r in all_rows:
        t = str(r.get("expert_target") or "unknown")
        by_target[t] = by_target.get(t, 0) + 1

    manifest = {
        "version": "v1",
        "seed": SEED,
        "counts_requested": {
            "e1_incidents": COUNTS.e1_incidents,
            "e1_atlas": COUNTS.e1_atlas,
            "e2": COUNTS.e2,
            "e3": COUNTS.e3,
            "council": COUNTS.council,
            "total_requested": COUNTS.total,
        },
        "counts_generated": {
            "e1_incidents": len(e1_inc),
            "e1_atlas": len(e1_atlas),
            "e2": len(e2),
            "e3": len(e3),
            "council": len(council),
            "total_generated": len(all_rows),
            "dev": len(dev_rows),
            "test": len(test_rows),
        },
        "by_target": by_target,
        "outputs": {
            "raw_dir": str(RAW_DIR.relative_to(ROOT)),
            "normalized_all": str((NORM_DIR / "candidate_seed_all.jsonl").relative_to(ROOT)),
            "dev": str((SPLIT_DIR / "dev.jsonl").relative_to(ROOT)),
            "test": str((SPLIT_DIR / "test.jsonl").relative_to(ROOT)),
        },
        "notes": [
            "This is a seed builder, not a final gold benchmark.",
            "Rows with tags including 'needs_gold' or 'needs_dedup' require manual annotation and leakage checks.",
            "For production benchmark use, run strict overlap checks against all training corpora.",
        ],
    }
    (MANIFEST_DIR / "seed_manifest_v1.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(manifest["counts_generated"], ensure_ascii=False))


if __name__ == "__main__":
    main()

