"""
Langfuse callback handler — optional observability for UC02.

Returns a LangChain CallbackHandler when LANGFUSE_PUBLIC_KEY and
LANGFUSE_SECRET_KEY are set in .env, otherwise returns None.

The pipeline works normally either way — tracing is fully optional.

Usage:
    from shared.observability.langfuse_cb import get_langfuse_handler

    handler   = get_langfuse_handler()
    callbacks = [handler] if handler else []
    chain.invoke(inputs, config={"callbacks": callbacks})
"""

import os


def get_langfuse_handler():
    """Return a Langfuse CallbackHandler, or None if keys are not configured."""
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY", "")
    host       = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

    if not public_key or not secret_key:
        return None

    try:
        from langfuse.callback import CallbackHandler  # type: ignore
        return CallbackHandler(
            public_key=public_key,
            secret_key=secret_key,
            host=host,
        )
    except ImportError:
        return None
