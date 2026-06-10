"""Langfuse observability callbacks with credential checking."""

import os


def get_callbacks(session_id: str):
    """Return a list of LangChain callbacks. Includes Langfuse if credentials are set.

    If LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY are not set,
    returns an empty list so the agent still runs without tracing.
    """
    callbacks = []

    public_key = os.environ.get("LANGFUSE_PUBLIC_KEY")
    secret_key = os.environ.get("LANGFUSE_SECRET_KEY")

    if public_key and secret_key:
        try:
            from langfuse.langchain import CallbackHandler
            handler = CallbackHandler(session_id=session_id)
            callbacks.append(handler)
        except Exception:
            # Any error during import (e.g., missing package, changed API) – continue without tracing
            pass

    return callbacks
