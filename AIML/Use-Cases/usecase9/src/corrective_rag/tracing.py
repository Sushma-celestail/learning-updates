from __future__ import annotations

import os
import uuid
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from corrective_rag.env import load_local_env
from corrective_rag.models import EvaluationResult

F = TypeVar("F", bound=Callable[..., Any])

load_local_env()


try:
    from langfuse import get_client as langfuse_get_client
    from langfuse import observe as langfuse_observe
    try:
        from langfuse import propagate_attributes as langfuse_propagate_attributes
    except Exception:  # pragma: no cover - older/partial installs.
        langfuse_propagate_attributes = None
except Exception:  # pragma: no cover - exercised when optional dependency is absent.
    langfuse_get_client = None
    langfuse_observe = None
    langfuse_propagate_attributes = None


def observe(name: str | None = None) -> Callable[[F], F]:
    if langfuse_observe is not None:
        def decorator(func: F) -> F:
            observed = langfuse_observe(name=name)(func)

            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                result = observed(*args, **kwargs)
                flush_langfuse()
                return result

            return wrapper  # type: ignore[return-value]

        return decorator

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


def new_trace_id() -> str:
    return uuid.uuid4().hex


def get_langchain_callback_handler() -> list[Any]:
    langfuse_host = os.getenv("LANGFUSE_HOST") or os.getenv("LANGFUSE_BASE_URL")
    if langfuse_host and not os.getenv("LANGFUSE_HOST"):
        os.environ["LANGFUSE_HOST"] = langfuse_host

    if not all(
        [
            os.getenv("LANGFUSE_PUBLIC_KEY"),
            os.getenv("LANGFUSE_SECRET_KEY"),
            langfuse_host,
        ]
    ):
        return []

    for import_path in ("langfuse.langchain", "langfuse.callback"):
        try:
            module = __import__(import_path, fromlist=["CallbackHandler"])
            return [module.CallbackHandler()]
        except Exception:
            continue
    return []


def get_langfuse_client() -> Any | None:
    ensure_langfuse_env()
    if langfuse_get_client is None:
        return None
    try:
        return langfuse_get_client()
    except Exception:
        return None


def ensure_langfuse_env() -> None:
    load_local_env()
    langfuse_host = os.getenv("LANGFUSE_HOST") or os.getenv("LANGFUSE_BASE_URL")
    if langfuse_host and not os.getenv("LANGFUSE_HOST"):
        os.environ["LANGFUSE_HOST"] = langfuse_host


def propagate_trace_attributes(**attributes: Any) -> Any:
    if langfuse_propagate_attributes is None:
        return _NoopContext()
    try:
        return langfuse_propagate_attributes(**attributes)
    except Exception:
        return _NoopContext()


class _NoopContext:
    def __enter__(self) -> None:
        return None

    def __exit__(self, *args: Any) -> bool:
        return False


def score_langfuse_trace(trace_id: str, evaluations: list[EvaluationResult]) -> None:
    client = get_langfuse_client()
    if client is None:
        return
    for result in evaluations:
        _score_current(client, name=result.name, value=result.score, comment=result.rationale)
    try:
        update_trace = getattr(client, "update_current_trace", None)
        if callable(update_trace):
            update_trace(tags=["corrective-rag", "usecase9"], session_id=trace_id)
    except Exception:
        pass


def _score_current(client: Any, name: str, value: float, comment: str | None = None) -> None:
    for method_name in ("score_current_span", "score_current_trace", "score_current_observation"):
        method = getattr(client, method_name, None)
        if not callable(method):
            continue
        try:
            method(name=name, value=value, comment=comment)
            return
        except TypeError:
            try:
                method(name=name, value=value)
                return
            except Exception:
                continue
        except Exception:
            continue


def update_current_span(**kwargs: Any) -> None:
    client = get_langfuse_client()
    if client is None:
        return
    if not _has_active_trace(client):
        return
    for method_name in (
        "update_current_generation",
        "update_current_span",
        "update_current_observation",
    ):
        method = getattr(client, method_name, None)
        if not callable(method):
            continue
        try:
            method(**kwargs)
            return
        except Exception:
            continue


def _has_active_trace(client: Any) -> bool:
    for method_name in ("get_current_trace_id", "get_current_traceid"):
        method = getattr(client, method_name, None)
        if not callable(method):
            continue
        try:
            return bool(method())
        except Exception:
            return False
    return True


def flush_langfuse() -> None:
    client = get_langfuse_client()
    if client is None:
        return
    flush = getattr(client, "flush", None)
    if callable(flush):
        try:
            flush()
        except Exception:
            pass
