import json
import os
import sqlite3
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Tuple

from .council_report import CouncilReport


_COUNCIL_DIR = Path(__file__).parent
REPORTS_DIR = _COUNCIL_DIR / "reports"
DB_PATH = _COUNCIL_DIR / "council.db"
INDEX_PATH = _COUNCIL_DIR / "knowledge_index.jsonl"


def _ensure_dirs() -> None:
  REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def make_incident_id(agent_id: str) -> str:
  date = datetime.utcnow().strftime("%Y%m%d")
  token = os.urandom(3).hex()
  safe_agent = agent_id.replace(" ", "-")
  return f"inc_{date}_{safe_agent}_{token}"


def build_summary_core(report: CouncilReport) -> str:
  decision = report.council_decision
  system_name = getattr(report, "system_name", "") or report.agent_id
  agent_id = report.agent_id
  if decision:
    rec = decision.final_recommendation
    consensus = decision.consensus_level
  else:
    rec = "REVIEW"
    consensus = "PARTIAL"
  lines = [
    f"{system_name} ({agent_id}) is evaluated for deployment in UN/humanitarian contexts.",
    f"The Council issues a final decision: {rec} with consensus level {consensus}.",
  ]
  note = (report.council_note or "").strip()
  if note:
    first_line = note.splitlines()[0]
    lines.append(f"Council note: {first_line}")
  return " ".join(lines)


def save_full_report(report: CouncilReport) -> Tuple[str, Path]:
  _ensure_dirs()
  if not report.incident_id:
    report.incident_id = make_incident_id(report.agent_id)
  path = REPORTS_DIR / f"{report.incident_id}.json"
  path.write_text(report.to_json(), encoding="utf-8")
  return report.incident_id, path


def _expert_rec(report: CouncilReport, key: str) -> str | None:
  """Extract a single expert's recommendation from expert_reports dict."""
  er = (report.expert_reports or {}).get(key)
  if not er:
    return None
  if isinstance(er, dict):
    return er.get("recommendation")
  return getattr(er, "recommendation", None)


def save_to_sqlite(report: CouncilReport, file_path: Path) -> None:
  conn = sqlite3.connect(DB_PATH)
  cur = conn.cursor()
  cur.execute(
    """
    CREATE TABLE IF NOT EXISTS evaluations (
      incident_id       TEXT PRIMARY KEY,
      agent_id          TEXT,
      system_name       TEXT,
      created_at        TEXT,
      decision          TEXT,
      risk_tier         TEXT,
      consensus         TEXT,
      summary_core      TEXT,
      file_path         TEXT,
      rec_security      TEXT,
      rec_governance    TEXT,
      rec_un_mission    TEXT
    )
    """
  )
  # Migrate older DBs that don't have the three expert-rec columns yet
  for col in ("rec_security", "rec_governance", "rec_un_mission"):
    try:
      cur.execute(f"ALTER TABLE evaluations ADD COLUMN {col} TEXT")
    except sqlite3.OperationalError:
      pass  # column already exists

  decision = report.council_decision
  summary = build_summary_core(report)
  created_at = datetime.utcnow().isoformat() + "Z"
  system_name = getattr(report, "system_name", "") or report.agent_id
  cur.execute(
    """
    INSERT OR REPLACE INTO evaluations
    (incident_id, agent_id, system_name, created_at,
     decision, risk_tier, consensus, summary_core, file_path,
     rec_security, rec_governance, rec_un_mission)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (
      report.incident_id,
      report.agent_id,
      system_name,
      created_at,
      decision.final_recommendation if decision else "REVIEW",
      getattr(decision, "overall_risk_tier", None) if decision else None,
      decision.consensus_level if decision else "PARTIAL",
      summary,
      str(file_path),
      _expert_rec(report, "security"),
      _expert_rec(report, "governance"),
      _expert_rec(report, "un_mission_fit"),
    ),
  )
  conn.commit()
  conn.close()


def append_to_index(report: CouncilReport) -> None:
  summary = build_summary_core(report)
  record = {
    "incident_id": report.incident_id,
    "agent_id": report.agent_id,
    "summary_core": summary,
    "decision": report.council_decision.final_recommendation if report.council_decision else "REVIEW",
    "consensus": report.council_decision.consensus_level if report.council_decision else "PARTIAL",
    "timestamp": report.timestamp,
    "raw": asdict(report),
  }
  with INDEX_PATH.open("a", encoding="utf-8") as f:
    f.write(json.dumps(record, ensure_ascii=False) + "\n")


def persist_report(report: CouncilReport) -> CouncilReport:
  incident_id, path = save_full_report(report)
  save_to_sqlite(report, path)
  append_to_index(report)
  return report

