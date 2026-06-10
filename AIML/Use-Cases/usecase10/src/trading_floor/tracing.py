from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from .audit import AuditLog
from .config import DEFAULT_CONFIG


class GovernanceTracer:
    """Langfuse adapter that always falls back to audit-only spans."""

    def __init__(self, audit: AuditLog):
        self.audit = audit
        self._langfuse = None
        self.last_error: str | None = None
        if DEFAULT_CONFIG.langfuse_public_key and DEFAULT_CONFIG.langfuse_secret_key:
            try:
                from langfuse import Langfuse  # type: ignore

                self._langfuse = Langfuse(
                    public_key=DEFAULT_CONFIG.langfuse_public_key,
                    secret_key=DEFAULT_CONFIG.langfuse_secret_key,
                    host=DEFAULT_CONFIG.langfuse_host,
                )
            except Exception as exc:
                self.last_error = str(exc)
                self._langfuse = None

    def status(self) -> dict:
        return {
            "configured": bool(DEFAULT_CONFIG.langfuse_public_key and DEFAULT_CONFIG.langfuse_secret_key),
            "host": DEFAULT_CONFIG.langfuse_host,
            "client_initialized": self._langfuse is not None,
            "last_error": self.last_error,
        }

    def flush(self) -> None:
        if self._langfuse:
            try:
                self._langfuse.flush()
            except Exception as exc:
                self.last_error = str(exc)

    @contextmanager
    def span(self, name: str, agent: str, payload: dict) -> Iterator[None]:
        self.audit.append(f"{name}.start", agent, payload)
        observation_cm = None
        if self._langfuse:
            try:
                observation_cm = self._langfuse.start_as_current_observation(
                    name=name,
                    as_type="span",
                    metadata={"agent": agent, **payload},
                )
                observation_cm.__enter__()
            except Exception as exc:
                self.last_error = str(exc)
                observation_cm = None
        try:
            yield
            self.audit.append(f"{name}.success", agent, payload)
            if observation_cm:
                try:
                    observation_cm.__exit__(None, None, None)
                    self.flush()
                except Exception as exc:
                    self.last_error = str(exc)
        except Exception as exc:
            self.audit.append(f"{name}.error", agent, {"error": str(exc), **payload})
            if observation_cm:
                try:
                    observation_cm.__exit__(type(exc), exc, exc.__traceback__)
                    self.flush()
                except Exception as flush_exc:
                    self.last_error = str(flush_exc)
            raise
