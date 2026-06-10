from __future__ import annotations

from corrective_rag.env import load_local_env
from corrective_rag.tracing import get_langfuse_client as _get_langfuse_client


def get_langfuse_client():
    load_local_env()
    return _get_langfuse_client()
