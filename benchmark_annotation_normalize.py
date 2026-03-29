#!/usr/bin/env python3
"""
Normalize annotated benchmark CSV for consistent citation/list formatting.

Main goals:
- Normalize list separators to " || "
- Improve citation specificity for common weak patterns
- Standardize review_status ("annotated" -> "approved")
- Emit normalization report with changed rows/cells
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent
DEFAULT_IN = Path("/Users/yangjunjie/Downloads/annotation_template_v1_annotated.csv")
DEFAULT_OUT = ROOT / "benchmark_data" / "v1" / "manifests" / "annotation_template_v1_annotated_cleaned.csv"
DEFAULT_REPORT = ROOT / "benchmark_data" / "v1" / "manifests" / "annotation_normalize_report_v1.json"


LIST_FIELDS = ["gold_must_hit_findings", "gold_must_citations", "gold_must_principles"]
ACTIVE_STATUSES = {"approved", "done", "accepted", "annotated"}


def _split_multi(v: str) -> list[str]:
    s = (v or "").strip()
    if not s:
        return []
    parts = re.split(r"\s*\|\|\s*|[;；]+|\n+", s)
    out = [p.strip(" ,") for p in parts if p.strip(" ,")]
    return out


def _join_multi(items: Iterable[str]) -> str:
    return " || ".join([x.strip() for x in items if x.strip()])


def _normalize_citation(c: str) -> str:
    x = c.strip()
    low = x.lower()

    # "Art.22" -> "GDPR Art.22" (fallback heuristic)
    if re.match(r"^(art\.?|article)\s*\d+", x, re.I):
        x = f"GDPR {x}"
        low = x.lower()

    # "EU AI Act Annex III (...)" -> "EU AI Act Art.6 + Annex III (...)"
    if "eu ai act" in low and "annex iii" in low and "art." not in low and "article" not in low:
        x = re.sub(r"eu ai act\s*", "EU AI Act Art.6 + ", x, flags=re.I)
        low = x.lower()

    # UNGP general mention -> add principle index hint
    if "un guiding principles on business and human rights" in low and not re.search(r"\bprinciple\s*\d+", low):
        x = f"{x} (Principle 13)"
        low = x.lower()

    # Normalize spacing for Art./Article
    x = re.sub(r"\barticle\s+", "Art.", x, flags=re.I)
    x = re.sub(r"\bart\.\s*", "Art.", x, flags=re.I)
    x = re.sub(r"\s+", " ", x).strip(" ,")
    return x


def _is_active_status(v: str) -> bool:
    return (v or "").strip().lower() in ACTIVE_STATUSES


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize benchmark annotation CSV")
    parser.add_argument("--in-csv", default=str(DEFAULT_IN), help="Input annotated CSV path")
    parser.add_argument("--out-csv", default=str(DEFAULT_OUT), help="Output cleaned CSV path")
    parser.add_argument("--report", default=str(DEFAULT_REPORT), help="Output normalization report JSON")
    args = parser.parse_args()

    in_csv = Path(args.in_csv)
    out_csv = Path(args.out_csv)
    report_path = Path(args.report)

    if not in_csv.exists():
        raise FileNotFoundError(f"Input CSV not found: {in_csv}")

    with in_csv.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    changed_rows = 0
    changed_cells = 0
    change_log: list[dict] = []

    for idx, row in enumerate(rows, start=2):
        row_changed = False

        # status normalize
        status = (row.get("review_status") or "").strip().lower()
        if status == "annotated":
            old = row["review_status"]
            row["review_status"] = "approved"
            row_changed = True
            changed_cells += 1
            change_log.append(
                {"line": idx, "sample_id": row.get("sample_id", ""), "field": "review_status", "old": old, "new": "approved"}
            )

        # normalize list-like fields
        for f in LIST_FIELDS:
            old = row.get(f, "") or ""
            items = _split_multi(old)
            if f == "gold_must_citations":
                items = [_normalize_citation(x) for x in items]
            new = _join_multi(items)
            if new != old:
                row[f] = new
                row_changed = True
                changed_cells += 1
                change_log.append(
                    {"line": idx, "sample_id": row.get("sample_id", ""), "field": f, "old": old, "new": new}
                )

        # lightweight default annotator fill for active rows
        if _is_active_status(row.get("review_status", "")) and not (row.get("annotator") or "").strip():
            row["annotator"] = "annotator_v1"
            row_changed = True
            changed_cells += 1
            change_log.append(
                {"line": idx, "sample_id": row.get("sample_id", ""), "field": "annotator", "old": "", "new": "annotator_v1"}
            )

        if row_changed:
            changed_rows += 1

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "input_csv": str(in_csv),
        "output_csv": str(out_csv),
        "total_rows": len(rows),
        "changed_rows": changed_rows,
        "changed_cells": changed_cells,
        "notes": [
            "review_status: annotated -> approved",
            "list fields normalized to ' || ' separator",
            "common weak citation patterns made more explicit",
        ],
        "sample_changes": change_log[:80],
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"changed_rows": changed_rows, "changed_cells": changed_cells, "out_csv": str(out_csv)}, ensure_ascii=False))


if __name__ == "__main__":
    main()

