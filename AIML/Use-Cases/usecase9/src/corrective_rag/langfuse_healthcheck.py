from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any

from corrective_rag.env import load_local_env
from corrective_rag.tracing import get_langfuse_client


def main() -> None:
    load_local_env()
    host = os.getenv("LANGFUSE_HOST") or os.getenv("LANGFUSE_BASE_URL") or ""
    public_key_present = bool(os.getenv("LANGFUSE_PUBLIC_KEY"))
    secret_key_present = bool(os.getenv("LANGFUSE_SECRET_KEY"))
    client = get_langfuse_client()

    result: dict[str, Any] = {
        "host": host,
        "public_key_present": public_key_present,
        "secret_key_present": secret_key_present,
        "client_available": client is not None,
        "observation_name": "langfuse-healthcheck",
        "flushed": False,
    }

    if client is None:
        result["message"] = (
            "Langfuse client is unavailable. Install with: pip install -e \".[observability]\""
        )
        print(json.dumps(result, indent=2))
        return

    try:
        payload = {
            "status": "ok",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        trace_id = _create_healthcheck_span(client, payload)
        if trace_id:
            result["trace_id"] = trace_id
            trace_url = _trace_url(client, host, trace_id)
            if trace_url:
                result["trace_url"] = trace_url
        flush = getattr(client, "flush", None)
        if callable(flush):
            flush()
        result["flushed"] = True
    except Exception as exc:
        result["error"] = exc.__class__.__name__

    print(json.dumps(result, indent=2))


def _create_healthcheck_span(client: Any, payload: dict[str, str]) -> str | None:
    starter = getattr(client, "start_as_current_observation", None)
    if not callable(starter):
        raise RuntimeError("Langfuse client does not expose start_as_current_observation")

    trace_id = None
    with starter(
        as_type="span",
        name="langfuse-healthcheck",
        input={"check": "langfuse-healthcheck"},
    ) as span:
        update = getattr(span, "update", None)
        if callable(update):
            update(
                output=payload,
                metadata={"source": "langfuse-healthcheck", "client": "langfuse-v4"},
            )
        trace_id = _current_trace_id(client) or str(getattr(span, "trace_id", "") or "")
    return trace_id or None


def _current_trace_id(client: Any) -> str | None:
    for method_name in ("get_current_trace_id", "get_current_traceid"):
        method = getattr(client, method_name, None)
        if callable(method):
            try:
                trace_id = method()
                if trace_id:
                    return str(trace_id)
            except Exception:
                continue
    return None


def _trace_url(client: Any, host: str, trace_id: str) -> str | None:
    for method_name in ("get_trace_url", "trace_url"):
        method = getattr(client, method_name, None)
        if callable(method):
            try:
                url = method(trace_id)
                if url:
                    return str(url)
            except TypeError:
                try:
                    url = method()
                    if url:
                        return str(url)
                except Exception:
                    continue
            except Exception:
                continue
    if host and trace_id:
        return f"{host.rstrip('/')}/trace/{trace_id}"
    return None


if __name__ == "__main__":
    main()
