#!/usr/bin/env python3
"""
Benchmark preflight checks for v1.

Checks:
- required files exist
- sample_id uniqueness
- per-row gold completeness
- per-target coverage
- recommendation distribution

Outputs:
- benchmark_data/v1/reports/benchmark_readiness_v1.json
- benchmark_data/v1/reports/benchmark_readiness_v1.md
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
BASE = ROOT / "benchmark_data" / "v1"


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if isinstance(obj, dict):
                rows.append(obj)
    return rows


def _severity(rec: str) -> int:
    r = (rec or "").upper()
    if r == "REJECT":
        return 2
    if r == "REVIEW":
        return 1
    return 0


def main() -> None:
    required = {
        "benchmark_final": BASE / "normalized" / "benchmark_final_v1.jsonl",
        "schema": BASE / "manifests" / "benchmark_schema_v1.json",
        "sources": BASE / "manifests" / "benchmark_sources_v1.md",
        "annotation_report": BASE / "manifests" / "annotation_merge_report_v1.json",
    }
    existence = {k: v.exists() for k, v in required.items()}

    rows = _read_jsonl(required["benchmark_final"]) if required["benchmark_final"].exists() else []
    ids = [str(r.get("sample_id") or "") for r in rows]
    uniq_ids = len(set(ids))

    by_target = Counter(str(r.get("expert_target") or "unknown") for r in rows)
    by_rec = Counter(
        str((r.get("provisional_gold") or {}).get("recommendation") or "MISSING").upper()
        for r in rows
    )

    missing_gold_recommendation = 0
    missing_gold_human_review = 0
    missing_findings = 0
    e2_missing_citations = 0
    e3_missing_principles = 0
    risk_dist = Counter()

    for r in rows:
        t = str(r.get("expert_target") or "")
        pg = r.get("provisional_gold") if isinstance(r.get("provisional_gold"), dict) else {}
        rec = str(pg.get("recommendation") or "").upper()
        if rec not in {"APPROVE", "REVIEW", "REJECT"}:
            missing_gold_recommendation += 1
        if not isinstance(pg.get("human_review_required"), bool):
            missing_gold_human_review += 1
        findings = pg.get("must_hit_findings") if isinstance(pg.get("must_hit_findings"), list) else []
        if len(findings) == 0:
            missing_findings += 1
        if t == "e2":
            cits = pg.get("citations") if isinstance(pg.get("citations"), list) else []
            if len(cits) == 0:
                e2_missing_citations += 1
        if t == "e3":
            prs = pg.get("must_principles") if isinstance(pg.get("must_principles"), list) else []
            if len(prs) == 0:
                e3_missing_principles += 1
        rt = str(pg.get("risk_tier") or "MISSING").upper()
        risk_dist[rt] += 1

    high_risk = sum(1 for r in rows if _severity(str((r.get("provisional_gold") or {}).get("recommendation") or "")) >= 1)
    high_risk_ratio = (high_risk / len(rows)) if rows else 0.0

    blockers: list[str] = []
    if not all(existence.values()):
        blockers.append("Missing required benchmark artifacts")
    if uniq_ids != len(ids):
        blockers.append("sample_id is not unique")
    if missing_gold_recommendation > 0:
        blockers.append(f"{missing_gold_recommendation} rows missing valid gold recommendation")
    if missing_gold_human_review > 0:
        blockers.append(f"{missing_gold_human_review} rows missing gold_human_review_required bool")
    if missing_findings > 0:
        blockers.append(f"{missing_findings} rows missing must_hit_findings")
    if e2_missing_citations > 0:
        blockers.append(f"{e2_missing_citations} E2 rows missing citations")
    if e3_missing_principles > 0:
        blockers.append(f"{e3_missing_principles} E3 rows missing principles")

    readiness = "READY_FOR_MODEL_BENCHMARKING" if not blockers else "NEEDS_FIXES"

    report = {
        "status": readiness,
        "required_files_exist": existence,
        "total_rows": len(rows),
        "unique_sample_ids": uniq_ids,
        "by_target": dict(by_target),
        "recommendation_distribution": dict(by_rec),
        "risk_tier_distribution": dict(risk_dist),
        "high_risk_ratio": high_risk_ratio,
        "completeness": {
            "missing_gold_recommendation": missing_gold_recommendation,
            "missing_gold_human_review_required": missing_gold_human_review,
            "missing_must_hit_findings": missing_findings,
            "e2_missing_citations": e2_missing_citations,
            "e3_missing_principles": e3_missing_principles,
        },
        "blockers": blockers,
        "next_actions": [
            "Run model inference to create real predictions for all samples.",
            "Score with benchmark_eval_runner.py score --pred <predictions.jsonl>.",
            "Compare pre-finetune vs post-finetune reports.",
        ],
    }

    out_json = BASE / "reports" / "benchmark_readiness_v1.json"
    out_md = BASE / "reports" / "benchmark_readiness_v1.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        "# Benchmark Readiness v1",
        "",
        f"- status: `{report['status']}`",
        f"- total_rows: `{report['total_rows']}`",
        f"- unique_sample_ids: `{report['unique_sample_ids']}`",
        f"- high_risk_ratio: `{report['high_risk_ratio']:.3f}`",
        "",
        "## Coverage",
        f"- by_target: `{report['by_target']}`",
        f"- recommendation_distribution: `{report['recommendation_distribution']}`",
        f"- risk_tier_distribution: `{report['risk_tier_distribution']}`",
        "",
        "## Completeness",
        f"- missing_gold_recommendation: `{missing_gold_recommendation}`",
        f"- missing_gold_human_review_required: `{missing_gold_human_review}`",
        f"- missing_must_hit_findings: `{missing_findings}`",
        f"- e2_missing_citations: `{e2_missing_citations}`",
        f"- e3_missing_principles: `{e3_missing_principles}`",
        "",
        "## Blockers",
    ]
    if blockers:
        md.extend([f"- {b}" for b in blockers])
    else:
        md.append("- none")
    md.extend(
        [
            "",
            "## Next Actions",
            "- Run model inference for all samples (SLM/Claude baseline).",
            "- Score and compare pre/post fine-tuning.",
        ]
    )
    out_md.write_text("\n".join(md), encoding="utf-8")
    print(json.dumps({"status": readiness, "rows": len(rows), "blockers": len(blockers)}, ensure_ascii=False))


if __name__ == "__main__":
    main()

