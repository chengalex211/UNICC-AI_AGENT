#!/usr/bin/env python3
"""
Leakage / overlap checker for benchmark candidates.

Input:
  benchmark_data/v1/normalized/candidate_seed_all.jsonl

Output:
  benchmark_data/v1/normalized/candidate_seed_clean.jsonl
  benchmark_data/v1/manifests/leakage_report_v1.json

Strategy:
  - Build exact hash index of training prompts/descriptions.
  - Remove candidate rows whose normalized description exactly matches training text.
  - Keep rows that pass, and emit summary by target.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_BASE = ROOT / "benchmark_data" / "v1"


def _normalize_text(s: str) -> str:
    return " ".join((s or "").lower().split())


def _h(s: str) -> str:
    return hashlib.sha256(_normalize_text(s).encode("utf-8")).hexdigest()


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


def _extract_training_texts(root: Path) -> list[str]:
    texts: list[str] = []
    # Expert 2 / 3 style prompt+messages datasets
    for rel in [
        "Expert 2/expert2_training_data_clean.jsonl",
        "Expert 2/expert2_training_data_supplementary.jsonl",
        "Expert 3/expert3_training_data/training_data_expert3_final_fixed.jsonl",
        "Expert 3/expert3_training_data/training_data_expert3_final.jsonl",
        "Expert 3/expert3_training_data/training_data_expert3.jsonl",
        "Expert1/expert1_mode_b_training_data.jsonl",
        "council/critique_data_final_for_training.jsonl",
        "council/critique_training_data.jsonl",
        "council/critique_training_data_supplements.jsonl",
    ]:
        path = root / rel
        if not path.exists():
            continue
        rows = _read_jsonl(path)
        for row in rows:
            msgs = row.get("messages")
            if isinstance(msgs, list):
                for m in msgs:
                    if isinstance(m, dict) and m.get("role") == "user":
                        c = m.get("content")
                        if isinstance(c, str) and c.strip():
                            texts.append(c)
    # council test cases
    tc_path = root / "council" / "test_cases_all.py"
    if tc_path.exists():
        # lightweight parse for "system_description": """..."""
        txt = tc_path.read_text(encoding="utf-8")
        marker = '"system_description": """'
        i = 0
        while True:
            start = txt.find(marker, i)
            if start == -1:
                break
            start += len(marker)
            end = txt.find('"""', start)
            if end == -1:
                break
            seg = txt[start:end].strip()
            if seg:
                texts.append(seg)
            i = end + 3
    return texts


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Check benchmark leakage against training corpora.")
    parser.add_argument(
        "--base",
        default=str(DEFAULT_BASE),
        help="Benchmark base directory (default: benchmark_data/v1)",
    )
    args = parser.parse_args()

    base = Path(args.base)
    candidate_path = base / "normalized" / "candidate_seed_all.jsonl"
    out_clean = base / "normalized" / "candidate_seed_clean.jsonl"
    out_report = base / "manifests" / "leakage_report_v1.json"

    candidates = _read_jsonl(candidate_path)
    train_texts = _extract_training_texts(ROOT)
    train_hashes = {_h(t) for t in train_texts if t.strip()}

    kept: list[dict[str, Any]] = []
    removed: list[dict[str, Any]] = []
    for row in candidates:
        desc = (
            row.get("input", {}).get("system_description", "")
            if isinstance(row.get("input"), dict)
            else ""
        )
        if not isinstance(desc, str):
            desc = ""
        if _h(desc) in train_hashes:
            r = dict(row)
            r["leakage_reason"] = "exact_match_training_text"
            removed.append(r)
        else:
            kept.append(row)

    _write_jsonl(out_clean, kept)
    _write_jsonl(base / "normalized" / "candidate_seed_removed_by_leakage.jsonl", removed)

    by_target_kept: dict[str, int] = {}
    by_target_removed: dict[str, int] = {}
    for r in kept:
        t = str(r.get("expert_target") or "unknown")
        by_target_kept[t] = by_target_kept.get(t, 0) + 1
    for r in removed:
        t = str(r.get("expert_target") or "unknown")
        by_target_removed[t] = by_target_removed.get(t, 0) + 1

    report = {
        "candidate_total": len(candidates),
        "kept_total": len(kept),
        "removed_total": len(removed),
        "by_target_kept": by_target_kept,
        "by_target_removed": by_target_removed,
        "note": "This script checks exact normalized text overlap only. Add semantic near-dup checks before final release.",
        "outputs": {
            "clean": str(out_clean.relative_to(ROOT)),
            "removed": str((base / "normalized" / "candidate_seed_removed_by_leakage.jsonl").relative_to(ROOT)),
        },
    }
    out_report.parent.mkdir(parents=True, exist_ok=True)
    out_report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()

