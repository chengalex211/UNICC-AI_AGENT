#!/usr/bin/env python3
"""
Benchmark annotation helper tools.

Commands:
  1) export-template
     Export a CSV template from candidate_seed_clean.jsonl for manual annotation.

  2) apply-annotations
     Merge filled annotation CSV back into JSONL and produce benchmark_final_v1.jsonl.
"""

from __future__ import annotations

import argparse
import csv
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


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def export_template(base: Path) -> None:
    clean_path = base / "normalized" / "candidate_seed_clean.jsonl"
    out_csv = base / "manifests" / "annotation_template_v1.csv"
    rows = _read_jsonl(clean_path)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "sample_id",
                "expert_target",
                "split",
                "source_type",
                "agent_id",
                "system_name",
                "system_description_short",
                "gold_recommendation",
                "gold_risk_tier",
                "gold_human_review_required",
                "gold_must_hit_findings",
                "gold_must_citations",
                "gold_must_principles",
                "annotator",
                "review_status",
                "notes",
            ],
        )
        writer.writeheader()
        for r in rows:
            inp = r.get("input", {}) if isinstance(r.get("input"), dict) else {}
            pg = r.get("provisional_gold", {}) if isinstance(r.get("provisional_gold"), dict) else {}
            writer.writerow(
                {
                    "sample_id": r.get("sample_id", ""),
                    "expert_target": r.get("expert_target", ""),
                    "split": r.get("split", ""),
                    "source_type": r.get("source_type", ""),
                    "agent_id": inp.get("agent_id", ""),
                    "system_name": inp.get("system_name", ""),
                    "system_description_short": str(inp.get("system_description", ""))[:500],
                    "gold_recommendation": pg.get("recommendation", "") or "",
                    "gold_risk_tier": pg.get("risk_tier", "") or "",
                    "gold_human_review_required": str(pg.get("human_review_required", True)).lower(),
                    "gold_must_hit_findings": "",
                    "gold_must_citations": "",
                    "gold_must_principles": "",
                    "annotator": "",
                    "review_status": "todo",
                    "notes": "",
                }
            )
    print(f"Template exported: {out_csv.relative_to(ROOT)}")


def _split_list_field(value: str) -> list[str]:
    if not value:
        return []
    parts = [x.strip() for x in value.split("||")]
    return [p for p in parts if p]


def apply_annotations(base: Path, csv_path: Path | None) -> None:
    clean_path = base / "normalized" / "candidate_seed_clean.jsonl"
    template_csv = base / "manifests" / "annotation_template_v1.csv"
    ann_csv = csv_path or template_csv
    out_final = base / "normalized" / "benchmark_final_v1.jsonl"
    out_report = base / "manifests" / "annotation_merge_report_v1.json"

    rows = _read_jsonl(clean_path)
    if not ann_csv.exists():
        raise FileNotFoundError(f"Annotation CSV not found: {ann_csv}")

    ann_map: dict[str, dict[str, str]] = {}
    with ann_csv.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid = (row.get("sample_id") or "").strip()
            if sid:
                ann_map[sid] = row

    merged: list[dict[str, Any]] = []
    updated = 0
    skipped = 0
    approved_for_final = 0
    for r in rows:
        sid = str(r.get("sample_id") or "")
        ann = ann_map.get(sid)
        if not ann:
            skipped += 1
            merged.append(r)
            continue

        review_status = (ann.get("review_status") or "").strip().lower()
        if review_status not in {"approved", "done", "accepted", "annotated"}:
            skipped += 1
            merged.append(r)
            continue

        pg = r.get("provisional_gold", {}) if isinstance(r.get("provisional_gold"), dict) else {}
        pg["recommendation"] = (ann.get("gold_recommendation") or "").strip() or pg.get("recommendation")
        pg["risk_tier"] = (ann.get("gold_risk_tier") or "").strip() or pg.get("risk_tier")
        hr = (ann.get("gold_human_review_required") or "").strip().lower()
        if hr in {"true", "false"}:
            pg["human_review_required"] = hr == "true"
        pg["must_hit_findings"] = _split_list_field(ann.get("gold_must_hit_findings") or "")
        pg["citations"] = _split_list_field(ann.get("gold_must_citations") or "")
        pg["must_principles"] = _split_list_field(ann.get("gold_must_principles") or "")
        pg["provenance"] = "human_annotated_v1"

        r["provisional_gold"] = pg
        r["annotation"] = {
            "annotator": (ann.get("annotator") or "").strip(),
            "review_status": review_status,
            "notes": (ann.get("notes") or "").strip(),
        }
        updated += 1
        approved_for_final += 1
        merged.append(r)

    _write_jsonl(out_final, merged)
    out_report.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "total_rows": len(rows),
        "updated_rows": updated,
        "skipped_rows": skipped,
        "approved_for_final": approved_for_final,
        "annotation_csv": _display_path(ann_csv),
        "output_final": _display_path(out_final),
        "note": "Only rows with review_status in {approved, done, accepted, annotated} are merged as final annotations.",
    }
    out_report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark annotation helper tools")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_export = sub.add_parser("export-template", help="Export CSV template for manual annotation")
    p_export.add_argument("--base", default=str(DEFAULT_BASE), help="Benchmark base directory")

    p_apply = sub.add_parser("apply-annotations", help="Apply annotation CSV into final benchmark JSONL")
    p_apply.add_argument("--base", default=str(DEFAULT_BASE), help="Benchmark base directory")
    p_apply.add_argument("--csv", default="", help="Optional path to filled annotation CSV")

    args = parser.parse_args()
    base = Path(args.base)

    if args.cmd == "export-template":
        export_template(base)
    elif args.cmd == "apply-annotations":
        csv_path = Path(args.csv) if args.csv else None
        apply_annotations(base, csv_path)


if __name__ == "__main__":
    main()

