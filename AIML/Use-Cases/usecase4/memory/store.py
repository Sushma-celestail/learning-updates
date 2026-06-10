"""Checkpointer factory — toggles between MemorySaver and SqliteSaver."""

import os
import sqlite3
from langgraph.checkpoint.memory import MemorySaver


def get_checkpointer():
    """Return the appropriate checkpointer based on MEMORY_BACKEND env var.

    - "sqlite" : persists across server restarts via memory.db
    - "memory" (default) : fast, in-process, resets on restart
    """
    backend = os.environ.get("MEMORY_BACKEND", "memory").lower()

    if backend == "sqlite":
        from langgraph.checkpoint.sqlite import SqliteSaver
        conn = sqlite3.connect("memory.db", check_same_thread=False)
        return SqliteSaver(conn)
    else:
        return MemorySaver()
