from __future__ import annotations

from corrective_rag.tracing import get_langchain_callback_handler


def get_callback_handler():
    handlers = get_langchain_callback_handler()
    return handlers[0] if handlers else None
