# memory/long_term.py
"""In‑memory long‑term store persisted across sessions.

The store saves a JSON dictionary keyed by ``user_id`` to a file inside the
project's ``data`` directory. ``get`` returns the stored dict (or an empty
dict) and ``set`` writes the updated dict back to disk.
"""

import json
from pathlib import Path
from typing import Dict, Any

_DATA_DIR = Path(__file__).resolve().parents[1] / "data"
_DATA_DIR.mkdir(parents=True, exist_ok=True)
_STORE_PATH = _DATA_DIR / "long_term_store.json"

class InMemoryStore:
    def __init__(self) -> None:
        # Load existing store if present; otherwise start empty.
        if _STORE_PATH.exists():
            try:
                self._store: Dict[str, Any] = json.load(_STORE_PATH.open("r", encoding="utf-8"))
            except Exception:
                self._store = {}
        else:
            self._store = {}

    def get(self, user_id: str) -> Dict[str, Any]:
        """Return the persisted context for *user_id* (empty dict if none)."""
        return self._store.get(user_id, {})

    def set(self, user_id: str, data: Dict[str, Any]) -> None:
        """Persist *data* for *user_id* and write the entire store to disk."""
        self._store[user_id] = data
        with _STORE_PATH.open("w", encoding="utf-8") as f:
            json.dump(self._store, f, ensure_ascii=False, indent=2)
