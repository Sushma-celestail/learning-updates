# src/graph/checkpointer.py

import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver

_conn = sqlite3.connect(
    "checkpoints.db",
    check_same_thread=False
)

_checkpointer = SqliteSaver(_conn)


def get_checkpointer():
    return _checkpointer