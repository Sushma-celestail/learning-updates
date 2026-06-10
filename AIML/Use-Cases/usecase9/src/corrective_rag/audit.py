from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from corrective_rag.models import RAGAnswer
from corrective_rag.tracing import observe


SCHEMA = """
CREATE TABLE IF NOT EXISTS rag_audit_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  trace_id TEXT NOT NULL,
  user_id TEXT NOT NULL DEFAULT 'local-user',
  created_at TEXT NOT NULL,
  question TEXT NOT NULL,
  answer TEXT NOT NULL,
  model TEXT NOT NULL DEFAULT 'local',
  cost REAL NOT NULL DEFAULT 0.0,
  latency REAL NOT NULL DEFAULT 0.0,
  input_tokens INTEGER NOT NULL DEFAULT 0,
  output_tokens INTEGER NOT NULL DEFAULT 0,
  total_tokens INTEGER NOT NULL DEFAULT 0,
  hallucination_score REAL NOT NULL DEFAULT 0.0,
  helpfulness_score REAL NOT NULL DEFAULT 0.0,
  citations_json TEXT NOT NULL,
  retrieval_json TEXT NOT NULL,
  evaluations_json TEXT NOT NULL,
  corrected INTEGER NOT NULL,
  correction_reason TEXT
);
CREATE INDEX IF NOT EXISTS idx_rag_audit_trace_id ON rag_audit_log(trace_id);
CREATE INDEX IF NOT EXISTS idx_rag_audit_created_at ON rag_audit_log(created_at);
"""

AUDIT_VIEW = """
DROP VIEW IF EXISTS audit_logs;
CREATE VIEW IF NOT EXISTS audit_logs AS
SELECT
  id,
  user_id,
  question AS prompt,
  answer AS response,
  citations_json AS retrieved_doc_ids,
  model,
  cost,
  latency,
  input_tokens,
  output_tokens,
  total_tokens,
  hallucination_score,
  helpfulness_score,
  created_at
FROM rag_audit_log;
"""


class AuditLogger:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(SCHEMA)
            self._migrate_columns(conn)
            conn.executescript(AUDIT_VIEW)

    def _migrate_columns(self, conn: sqlite3.Connection) -> None:
        existing = {
            row[1]
            for row in conn.execute("PRAGMA table_info(rag_audit_log)").fetchall()
        }
        migrations = {
            "user_id": "ALTER TABLE rag_audit_log ADD COLUMN user_id TEXT NOT NULL DEFAULT 'local-user'",
            "model": "ALTER TABLE rag_audit_log ADD COLUMN model TEXT NOT NULL DEFAULT 'local'",
            "cost": "ALTER TABLE rag_audit_log ADD COLUMN cost REAL NOT NULL DEFAULT 0.0",
            "latency": "ALTER TABLE rag_audit_log ADD COLUMN latency REAL NOT NULL DEFAULT 0.0",
            "input_tokens": "ALTER TABLE rag_audit_log ADD COLUMN input_tokens INTEGER NOT NULL DEFAULT 0",
            "output_tokens": "ALTER TABLE rag_audit_log ADD COLUMN output_tokens INTEGER NOT NULL DEFAULT 0",
            "total_tokens": "ALTER TABLE rag_audit_log ADD COLUMN total_tokens INTEGER NOT NULL DEFAULT 0",
            "hallucination_score": "ALTER TABLE rag_audit_log ADD COLUMN hallucination_score REAL NOT NULL DEFAULT 0.0",
            "helpfulness_score": "ALTER TABLE rag_audit_log ADD COLUMN helpfulness_score REAL NOT NULL DEFAULT 0.0",
        }
        for column, statement in migrations.items():
            if column not in existing:
                try:
                    conn.execute(statement)
                except sqlite3.OperationalError as exc:
                    if "duplicate column name" not in str(exc).lower():
                        raise

    @observe(name="audit_log")
    def record(self, answer: RAGAnswer) -> None:
        retrieval = [
            {
                "doc_id": item.document.doc_id,
                "title": item.document.title,
                "score": item.score,
                "matched_terms": item.matched_terms,
                "source": item.document.source,
            }
            for item in answer.retrieved
        ]
        evaluations = [
            {
                "name": item.name,
                "score": item.score,
                "passed": item.passed,
                "rationale": item.rationale,
                "details": item.details,
            }
            for item in answer.evaluations
        ]
        hallucination_score = _score(answer, "online_hallucination_guard")
        helpfulness_score = _score(answer, "online_helpfulness_guard")
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO rag_audit_log (
                  trace_id, user_id, created_at, question, answer, model, cost, latency,
                  input_tokens, output_tokens, total_tokens, hallucination_score, helpfulness_score, citations_json,
                  retrieval_json, evaluations_json, corrected, correction_reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    answer.trace_id,
                    answer.user_id,
                    answer.created_at,
                    answer.question,
                    answer.answer,
                    answer.model,
                    answer.cost_usd,
                    answer.latency_ms,
                    answer.input_tokens,
                    answer.output_tokens,
                    answer.total_tokens,
                    hallucination_score,
                    helpfulness_score,
                    json.dumps(answer.citations),
                    json.dumps(retrieval),
                    json.dumps(evaluations),
                    int(answer.corrected),
                    answer.correction_reason,
                ),
            )

    def latest(self, limit: int = 20) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM rag_audit_log ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(row) for row in rows]


def _score(answer: RAGAnswer, name: str) -> float:
    for evaluation in answer.evaluations:
        if evaluation.name == name:
            return evaluation.score
    return 0.0
