#!/usr/bin/env python3
"""
Auto-build prediction file for benchmark scoring.

Priority:
1) Use real outputs from council/results/reports/{agent_id}.json when available
2) Fall back to lightweight heuristics from scenario text
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_BASE = ROOT / "benchmark_data" / "v1"
REPORTS_DIR = ROOT / "council" / "results" / "reports"


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


def _heuristic_recommendation(desc: str) -> str:
    t = (desc or "").lower()
    reject_terms = [
        "biometric",
        "facial recognition",
        "asylum",
        "no human review",
        "conflict zone",
        "child",
        "detention",
        "without consent",
        "surveillance",
    ]
    review_terms = [
        "no dpia",
        "not documented",
        "missing",
        "unclear",
        "limited documentation",
        "needs review",
    ]
    rej = sum(1 for k in reject_terms if k in t)
    rev = sum(1 for k in review_terms if k in t)
    if rej >= 2:
        return "REJECT"
    if rej == 1 or rev >= 2:
        return "REVIEW"
    return "APPROVE"


def _extract_risk_tier(rec: str) -> str:
    if rec == "REJECT":
        return "UNACCEPTABLE"
    if rec == "REVIEW":
        return "HIGH"
    return "LIMITED"


def _from_report(agent_id: str, target: str) -> dict[str, Any] | None:
    path = REPORTS_DIR / f"{agent_id}.json"
    if not path.exists():
        return None
    try:
        r = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    exp = r.get("expert_reports") or {}
    if target == "e2":
        g = exp.get("governance") or {}
        return {
            "pred_recommendation": g.get("recommendation") or "",
            "pred_risk_tier": g.get("risk_tier") or "",
            "pred_human_review_required": True,
            "pred_key_findings": g.get("key_findings") or [],
            "pred_citations": g.get("regulatory_citations") or [],
            "pred_principles": [],
        }
    if target == "e3":
        u = exp.get("un_mission_fit") or {}
        return {
            "pred_recommendation": u.get("recommendation") or "",
            "pred_risk_tier": u.get("risk_tier") or "",
            "pred_human_review_required": bool(u.get("human_review_required", True)),
            "pred_key_findings": u.get("key_findings") or [],
            "pred_citations": [],
            "pred_principles": u.get("un_principle_violations") or [],
        }
    if target == "e1":
        s = exp.get("security") or {}
        return {
            "pred_recommendation": s.get("recommendation") or "",
            "pred_risk_tier": s.get("risk_tier") or "",
            "pred_human_review_required": bool(s.get("council_handoff", {}).get("human_oversight_required", True)),
            "pred_key_findings": s.get("key_findings") or [],
            "pred_citations": [],
            "pred_principles": [],
        }
    if target == "council":
        cd = r.get("council_decision") or {}
        note = r.get("council_note") or ""
        note_lines = [x.strip() for x in str(note).splitlines() if x.strip()][:4]
        return {
            "pred_recommendation": cd.get("final_recommendation") or "",
            "pred_risk_tier": cd.get("overall_risk_tier") or _extract_risk_tier(cd.get("final_recommendation") or ""),
            "pred_human_review_required": bool(cd.get("human_oversight_required", True)),
            "pred_key_findings": note_lines,
            "pred_citations": [],
            "pred_principles": [],
        }
    return None


def build_predictions(base: Path) -> Path:
    benchmark_path = base / "normalized" / "benchmark_final_v1.jsonl"
    if not benchmark_path.exists():
        benchmark_path = base / "normalized" / "candidate_seed_clean.jsonl"
    rows = _read_jsonl(benchmark_path)

    preds: list[dict[str, Any]] = []
    used_report = 0
    used_heuristic = 0
    for r in rows:
        sid = str(r.get("sample_id") or "")
        target = str(r.get("expert_target") or "")
        inp = r.get("input") if isinstance(r.get("input"), dict) else {}
        agent_id = str(inp.get("agent_id") or "")
        desc = str(inp.get("system_description") or "")

        from_report = _from_report(agent_id, target) if agent_id else None
        if from_report:
            used_report += 1
            pred = from_report
        else:
            used_heuristic += 1
            rec = _heuristic_recommendation(desc)
            pred = {
                "pred_recommendation": rec,
                "pred_risk_tier": _extract_risk_tier(rec),
                "pred_human_review_required": rec in {"REVIEW", "REJECT"},
                "pred_key_findings": ["Heuristic prediction from scenario text; no direct report output found."],
                "pred_citations": [],
                "pred_principles": [],
            }

        preds.append(
            {
                "sample_id": sid,
                "expert_target": target,
                **pred,
            }
        )

    out = base / "predictions" / "predictions_autofill_v1.jsonl"
    _write_jsonl(out, preds)

    summary = {
        "total": len(preds),
        "used_report_outputs": used_report,
        "used_heuristic_fallback": used_heuristic,
        "output": str(out.relative_to(ROOT)),
    }
    (base / "reports").mkdir(parents=True, exist_ok=True)
    (base / "reports" / "predictions_autofill_summary_v1.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False))
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Auto-build predictions for benchmark scoring")
    parser.add_argument("--base", default=str(DEFAULT_BASE), help="Benchmark base directory")
    args = parser.parse_args()
    build_predictions(Path(args.base))


if __name__ == "__main__":
    main()

