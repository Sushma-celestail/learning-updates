from __future__ import annotations

import sqlite3
from pathlib import Path

from corrective_rag.audit import AuditLogger
from corrective_rag.config import Settings


def get_connection(db_path: str | Path | None = None) -> sqlite3.Connection:
    settings = Settings.from_env()
    path = Path(db_path) if db_path else settings.audit_db_path
    AuditLogger(path)
    return sqlite3.connect(path)
