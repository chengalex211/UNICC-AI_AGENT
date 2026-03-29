#!/usr/bin/env python3
"""
Benchmark evaluation runner.

Subcommands:
1) export-pred-template
   Build a prediction template from benchmark final JSONL.

2) score
   Score predictions against benchmark final JSONL and emit JSON/Markdown reports.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_BASE = ROOT / "benchmark_data" / "v1"


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


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def export_pred_template(base: Path) -> None:
    benchmark_path = base / "normalized" / "benchmark_final_v1.jsonl"
    if not benchmark_path.exists():
        benchmark_path = base / "normalized" / "candidate_seed_clean.jsonl"
    rows = _read_jsonl(benchmark_path)

    out = base / "predictions" / "predictions_template_v1.jsonl"
    templates: list[dict[str, Any]] = []
    for r in rows:
        templates.append(
            {
                "sample_id": r.get("sample_id"),
                "expert_target": r.get("expert_target"),
                "pred_recommendation": "",
                "pred_risk_tier": "",
                "pred_human_review_required": None,
                "pred_key_findings": [],
                "pred_citations": [],
                "pred_principles": [],
            }
        )
    _write_jsonl(out, templates)
    print(f"Prediction template exported: {out.relative_to(ROOT)}")


def _norm(s: str) -> str:
    return " ".join((s or "").lower().split())


def _list_hit_rate(required: list[str], predicted: list[str]) -> float | None:
    if not required:
        return None
    pred_blob = " || ".join(_norm(x) for x in predicted if isinstance(x, str))
    hit = 0
    for req in required:
        r = _norm(req)
        if r and r in pred_blob:
            hit += 1
    return hit / len(required)


def score(base: Path, pred_path: Path | None) -> None:
    benchmark_path = base / "normalized" / "benchmark_final_v1.jsonl"
    if not benchmark_path.exists():
        benchmark_path = base / "normalized" / "candidate_seed_clean.jsonl"
    predictions_path = pred_path or (base / "predictions" / "predictions_template_v1.jsonl")

    gold_rows = _read_jsonl(benchmark_path)
    pred_rows = _read_jsonl(predictions_path)
    pred_map = {str(r.get("sample_id")): r for r in pred_rows}

    total = 0
    rec_correct = 0
    hr_total = 0
    hr_correct = 0
    finding_scores: list[float] = []
    citation_scores: list[float] = []
    principle_scores: list[float] = []
    finding_applicable = 0
    citation_applicable = 0
    principle_applicable = 0

    by_target: dict[str, dict[str, float]] = {}

    for g in gold_rows:
        sid = str(g.get("sample_id") or "")
        t = str(g.get("expert_target") or "unknown")
        pg = g.get("provisional_gold", {}) if isinstance(g.get("provisional_gold"), dict) else {}
        pr = pred_map.get(sid, {})

        gold_rec = str(pg.get("recommendation") or "").strip().upper()
        pred_rec = str(pr.get("pred_recommendation") or "").strip().upper()
        if not gold_rec:
            continue

        total += 1
        rec_ok = int(pred_rec == gold_rec)
        rec_correct += rec_ok

        gold_hr = pg.get("human_review_required")
        pred_hr = pr.get("pred_human_review_required")
        if isinstance(gold_hr, bool):
            hr_total += 1
            hr_ok = int(pred_hr is gold_hr)
            hr_correct += hr_ok

        req_findings = pg.get("must_hit_findings") if isinstance(pg.get("must_hit_findings"), list) else []
        pred_findings = pr.get("pred_key_findings") if isinstance(pr.get("pred_key_findings"), list) else []
        fs = _list_hit_rate(req_findings, pred_findings)
        if fs is not None:
            finding_scores.append(fs)
            finding_applicable += 1

        req_cit = pg.get("citations") if isinstance(pg.get("citations"), list) else []
        pred_cit = pr.get("pred_citations") if isinstance(pr.get("pred_citations"), list) else []
        cs = _list_hit_rate(req_cit, pred_cit)
        if cs is not None:
            citation_scores.append(cs)
            citation_applicable += 1

        req_pr = pg.get("must_principles") if isinstance(pg.get("must_principles"), list) else []
        pred_pr = pr.get("pred_principles") if isinstance(pr.get("pred_principles"), list) else []
        ps = _list_hit_rate(req_pr, pred_pr)
        if ps is not None:
            principle_scores.append(ps)
            principle_applicable += 1

        bucket = by_target.setdefault(
            t,
            {
                "count": 0.0,
                "rec_correct": 0.0,
                "finding_sum": 0.0,
                "citation_sum": 0.0,
                "principle_sum": 0.0,
                "finding_applicable": 0.0,
                "citation_applicable": 0.0,
                "principle_applicable": 0.0,
            },
        )
        bucket["count"] += 1
        bucket["rec_correct"] += rec_ok
        if fs is not None:
            bucket["finding_sum"] += fs
            bucket["finding_applicable"] += 1
        if cs is not None:
            bucket["citation_sum"] += cs
            bucket["citation_applicable"] += 1
        if ps is not None:
            bucket["principle_sum"] += ps
            bucket["principle_applicable"] += 1

    report = {
        "benchmark_file": str(benchmark_path.relative_to(ROOT)),
        "predictions_file": str(predictions_path.relative_to(ROOT)),
        "samples_scored": total,
        "recommendation_accuracy": (rec_correct / total) if total else 0.0,
        "human_review_accuracy": (hr_correct / hr_total) if hr_total else 0.0,
        "must_hit_findings_coverage": (sum(finding_scores) / len(finding_scores)) if finding_scores else 0.0,
        "citation_coverage": (sum(citation_scores) / len(citation_scores)) if citation_scores else 0.0,
        "principle_coverage": (sum(principle_scores) / len(principle_scores)) if principle_scores else 0.0,
        "coverage_applicable_counts": {
            "must_hit_findings": finding_applicable,
            "citations": citation_applicable,
            "principles": principle_applicable,
        },
        "by_target": {},
    }
    for t, b in by_target.items():
        c = int(b["count"])
        report["by_target"][t] = {
            "count": c,
            "recommendation_accuracy": (b["rec_correct"] / c) if c else 0.0,
            "must_hit_findings_coverage": (b["finding_sum"] / b["finding_applicable"]) if b["finding_applicable"] else 0.0,
            "citation_coverage": (b["citation_sum"] / b["citation_applicable"]) if b["citation_applicable"] else 0.0,
            "principle_coverage": (b["principle_sum"] / b["principle_applicable"]) if b["principle_applicable"] else 0.0,
            "coverage_applicable_counts": {
                "must_hit_findings": int(b["finding_applicable"]),
                "citations": int(b["citation_applicable"]),
                "principles": int(b["principle_applicable"]),
            },
        }

    out_json = base / "reports" / "benchmark_eval_report_v1.json"
    out_md = base / "reports" / "benchmark_eval_report_v1.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    md_lines = [
        "# Benchmark Eval Report v1",
        "",
        f"- samples_scored: {report['samples_scored']}",
        f"- recommendation_accuracy: {report['recommendation_accuracy']:.4f}",
        f"- human_review_accuracy: {report['human_review_accuracy']:.4f}",
        f"- must_hit_findings_coverage: {report['must_hit_findings_coverage']:.4f}",
        f"- citation_coverage: {report['citation_coverage']:.4f}",
        f"- principle_coverage: {report['principle_coverage']:.4f}",
        "",
        "## By Target",
        "",
    ]
    for t, m in report["by_target"].items():
        md_lines.append(f"### {t}")
        md_lines.append(f"- count: {m['count']}")
        md_lines.append(f"- recommendation_accuracy: {m['recommendation_accuracy']:.4f}")
        md_lines.append(f"- must_hit_findings_coverage: {m['must_hit_findings_coverage']:.4f}")
        md_lines.append(f"- citation_coverage: {m['citation_coverage']:.4f}")
        md_lines.append(f"- principle_coverage: {m['principle_coverage']:.4f}")
        md_lines.append("")
    out_md.write_text("\n".join(md_lines), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark evaluation runner")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_export = sub.add_parser("export-pred-template", help="Export prediction JSONL template")
    p_export.add_argument("--base", default=str(DEFAULT_BASE), help="Benchmark base directory")

    p_score = sub.add_parser("score", help="Score predictions against benchmark")
    p_score.add_argument("--base", default=str(DEFAULT_BASE), help="Benchmark base directory")
    p_score.add_argument("--pred", default="", help="Optional predictions JSONL path")

    args = parser.parse_args()
    base = Path(args.base)

    if args.cmd == "export-pred-template":
        export_pred_template(base)
    elif args.cmd == "score":
        pred = Path(args.pred) if args.pred else None
        score(base, pred)


if __name__ == "__main__":
    main()

