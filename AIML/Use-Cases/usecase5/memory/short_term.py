# memory/short_term.py
"""In‑memory short‑term memory wrapper.

The ``InMemorySaver`` mimics LangChain's checkpointer but stores state in a
simple dictionary keyed by a thread identifier. For this demo we only need the
ability to ``save_state`` and ``load_state``.
"""

from typing import Any, Dict

class InMemorySaver:
    def __init__(self) -> None:
        self._store: Dict[str, Any] = {}

    def save_state(self, thread_id: str, state: Any) -> None:
        """Persist ``state`` for ``thread_id`` in memory."""
        self._store[thread_id] = state

    def load_state(self, thread_id: str) -> Any:
        """Retrieve previously saved state or ``None`` if not present."""
        return self._store.get(thread_id)
