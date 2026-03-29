#!/usr/bin/env python3
"""
Prepare prioritized inference queue for when SLM is available.

Output:
- benchmark_data/v1/predictions/pending_slm_queue_v1.jsonl
- benchmark_data/v1/reports/pending_slm_queue_summary_v1.json
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


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _severity(rec: str) -> int:
    r = (rec or "").upper()
    if r == "REJECT":
        return 2
    if r == "REVIEW":
        return 1
    return 0


def _target_weight(target: str) -> int:
    # Prefer expert-level runs first; council after single experts.
    return {"e1": 4, "e2": 4, "e3": 4, "council": 3}.get(target, 1)


def main() -> None:
    src = BASE / "normalized" / "benchmark_final_v1.jsonl"
    rows = _read_jsonl(src)
    queue: list[dict[str, Any]] = []

    for r in rows:
        t = str(r.get("expert_target") or "unknown")
        inp = r.get("input") if isinstance(r.get("input"), dict) else {}
        pg = r.get("provisional_gold") if isinstance(r.get("provisional_gold"), dict) else {}
        rec = str(pg.get("recommendation") or "")
        sev = _severity(rec)
        priority = sev * 10 + _target_weight(t)
        queue.append(
            {
                "sample_id": r.get("sample_id"),
                "expert_target": t,
                "priority": priority,
                "gold_recommendation": rec,
                "gold_risk_tier": pg.get("risk_tier"),
                "input": {
                    "agent_id": inp.get("agent_id"),
                    "system_name": inp.get("system_name"),
                    "system_description": inp.get("system_description"),
                },
            }
        )

    queue.sort(key=lambda x: (x.get("priority", 0), str(x.get("sample_id"))), reverse=True)
    out_queue = BASE / "predictions" / "pending_slm_queue_v1.jsonl"
    _write_jsonl(out_queue, queue)

    by_target = Counter(str(x.get("expert_target") or "unknown") for x in queue)
    by_gold = Counter(str(x.get("gold_recommendation") or "MISSING").upper() for x in queue)
    top10 = [
        {
            "sample_id": q.get("sample_id"),
            "expert_target": q.get("expert_target"),
            "priority": q.get("priority"),
            "gold_recommendation": q.get("gold_recommendation"),
        }
        for q in queue[:10]
    ]
    summary = {
        "total": len(queue),
        "by_target": dict(by_target),
        "by_gold_recommendation": dict(by_gold),
        "queue_file": str(out_queue.relative_to(ROOT)),
        "top10": top10,
        "note": "Higher priority = higher risk first.",
    }
    out_summary = BASE / "reports" / "pending_slm_queue_summary_v1.json"
    out_summary.parent.mkdir(parents=True, exist_ok=True)
    out_summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"total": len(queue), "queue": str(out_queue.relative_to(ROOT))}, ensure_ascii=False))


if __name__ == "__main__":
    main()

