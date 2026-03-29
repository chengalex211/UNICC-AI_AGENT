import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


COUNCIL_DIR = Path(__file__).parent
DB_PATH = COUNCIL_DIR / "council.db"


def _utc_now() -> str:
  return datetime.utcnow().isoformat() + "Z"


def _conn() -> sqlite3.Connection:
  conn = sqlite3.connect(DB_PATH)
  conn.row_factory = sqlite3.Row
  _ensure_schema(conn)
  return conn


def _ensure_schema(conn: sqlite3.Connection) -> None:
  cur = conn.cursor()
  cur.execute(
    """
    CREATE TABLE IF NOT EXISTS audit_events (
      event_id TEXT PRIMARY KEY,
      incident_id TEXT,
      session_id TEXT,
      agent_id TEXT,
      stage TEXT NOT NULL,
      status TEXT NOT NULL,
      actor TEXT NOT NULL,
      severity TEXT NOT NULL DEFAULT 'INFO',
      source TEXT,
      message TEXT,
      payload_json TEXT,
      created_at TEXT NOT NULL
    )
    """
  )
  cur.execute("CREATE INDEX IF NOT EXISTS idx_audit_events_incident ON audit_events(incident_id)")
  cur.execute("CREATE INDEX IF NOT EXISTS idx_audit_events_session ON audit_events(session_id)")
  cur.execute("CREATE INDEX IF NOT EXISTS idx_audit_events_created ON audit_events(created_at)")

  cur.execute(
    """
    CREATE TABLE IF NOT EXISTS audit_spans (
      span_id TEXT PRIMARY KEY,
      incident_id TEXT,
      session_id TEXT,
      agent_id TEXT,
      span_name TEXT NOT NULL,
      actor TEXT NOT NULL,
      status TEXT NOT NULL,
      started_at TEXT NOT NULL,
      ended_at TEXT,
      duration_ms INTEGER,
      meta_json TEXT
    )
    """
  )
  cur.execute("CREATE INDEX IF NOT EXISTS idx_audit_spans_incident ON audit_spans(incident_id)")
  cur.execute("CREATE INDEX IF NOT EXISTS idx_audit_spans_session ON audit_spans(session_id)")
  conn.commit()


def log_event(
  *,
  stage: str,
  status: str,
  actor: str,
  message: str = "",
  payload: Optional[dict[str, Any]] = None,
  severity: str = "INFO",
  source: str = "council",
  incident_id: Optional[str] = None,
  session_id: Optional[str] = None,
  agent_id: Optional[str] = None,
) -> str:
  event_id = str(uuid.uuid4())
  conn = _conn()
  cur = conn.cursor()
  cur.execute(
    """
    INSERT INTO audit_events
    (event_id, incident_id, session_id, agent_id, stage, status, actor, severity, source, message, payload_json, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (
      event_id,
      incident_id,
      session_id,
      agent_id,
      stage,
      status,
      actor,
      severity,
      source,
      message,
      json.dumps(payload or {}, ensure_ascii=False),
      _utc_now(),
    ),
  )
  conn.commit()
  conn.close()
  return event_id


def span_start(
  *,
  span_name: str,
  actor: str,
  incident_id: Optional[str] = None,
  session_id: Optional[str] = None,
  agent_id: Optional[str] = None,
  meta: Optional[dict[str, Any]] = None,
) -> str:
  span_id = str(uuid.uuid4())
  conn = _conn()
  cur = conn.cursor()
  cur.execute(
    """
    INSERT INTO audit_spans
    (span_id, incident_id, session_id, agent_id, span_name, actor, status, started_at, ended_at, duration_ms, meta_json)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, ?)
    """,
    (
      span_id,
      incident_id,
      session_id,
      agent_id,
      span_name,
      actor,
      "started",
      _utc_now(),
      json.dumps(meta or {}, ensure_ascii=False),
    ),
  )
  conn.commit()
  conn.close()
  return span_id


def span_end(span_id: str, *, status: str = "success", duration_ms: Optional[int] = None, meta: Optional[dict[str, Any]] = None) -> None:
  conn = _conn()
  cur = conn.cursor()
  cur.execute(
    """
    UPDATE audit_spans
    SET status = ?, ended_at = ?, duration_ms = ?, meta_json = COALESCE(?, meta_json)
    WHERE span_id = ?
    """,
    (
      status,
      _utc_now(),
      duration_ms,
      json.dumps(meta, ensure_ascii=False) if meta is not None else None,
      span_id,
    ),
  )
  conn.commit()
  conn.close()


def bind_incident_to_session(session_id: str, incident_id: str) -> None:
  conn = _conn()
  cur = conn.cursor()
  cur.execute(
    """
    UPDATE audit_events
    SET incident_id = ?
    WHERE session_id = ? AND (incident_id IS NULL OR incident_id = '')
    """,
    (incident_id, session_id),
  )
  cur.execute(
    """
    UPDATE audit_spans
    SET incident_id = ?
    WHERE session_id = ? AND (incident_id IS NULL OR incident_id = '')
    """,
    (incident_id, session_id),
  )
  conn.commit()
  conn.close()


def list_events(*, incident_id: Optional[str] = None, session_id: Optional[str] = None, limit: int = 500, offset: int = 0) -> list[dict]:
  conn = _conn()
  cur = conn.cursor()
  if incident_id:
    cur.execute(
      """
      SELECT * FROM audit_events
      WHERE incident_id = ?
      ORDER BY created_at ASC
      LIMIT ? OFFSET ?
      """,
      (incident_id, limit, offset),
    )
  elif session_id:
    cur.execute(
      """
      SELECT * FROM audit_events
      WHERE session_id = ?
      ORDER BY created_at ASC
      LIMIT ? OFFSET ?
      """,
      (session_id, limit, offset),
    )
  else:
    cur.execute(
      """
      SELECT * FROM audit_events
      ORDER BY created_at DESC
      LIMIT ? OFFSET ?
      """,
      (limit, offset),
    )
  rows = [dict(r) for r in cur.fetchall()]
  conn.close()
  for r in rows:
    try:
      r["payload"] = json.loads(r.pop("payload_json") or "{}")
    except Exception:
      r["payload"] = {}
  return rows


def list_spans(*, incident_id: Optional[str] = None, session_id: Optional[str] = None, limit: int = 500, offset: int = 0) -> list[dict]:
  conn = _conn()
  cur = conn.cursor()
  if incident_id:
    cur.execute(
      """
      SELECT * FROM audit_spans
      WHERE incident_id = ?
      ORDER BY started_at ASC
      LIMIT ? OFFSET ?
      """,
      (incident_id, limit, offset),
    )
  elif session_id:
    cur.execute(
      """
      SELECT * FROM audit_spans
      WHERE session_id = ?
      ORDER BY started_at ASC
      LIMIT ? OFFSET ?
      """,
      (session_id, limit, offset),
    )
  else:
    cur.execute(
      """
      SELECT * FROM audit_spans
      ORDER BY started_at DESC
      LIMIT ? OFFSET ?
      """,
      (limit, offset),
    )
  rows = [dict(r) for r in cur.fetchall()]
  conn.close()
  for r in rows:
    try:
      r["meta"] = json.loads(r.pop("meta_json") or "{}")
    except Exception:
      r["meta"] = {}
  return rows

