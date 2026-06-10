from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


class MemoryStore:
    """Mem0 adapter with local JSON fallback for demos and tests."""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._mem0 = None
        self.backend = "local_json"
        mem0_api_key = os.getenv("MEM0_API_KEY")
        mem0_host = os.getenv("MEM0_HOST")
        try:
            if mem0_api_key:
                from mem0 import MemoryClient  # type: ignore

                self._mem0 = MemoryClient(api_key=mem0_api_key, host=mem0_host)
                self.backend = "mem0_cloud"
            else:
                from mem0 import Memory  # type: ignore

                self._mem0 = Memory()
                self.backend = "mem0_local"
        except Exception:
            self._mem0 = None
            self.backend = "local_json"

    def status(self) -> dict[str, Any]:
        return {"backend": self.backend, "live_mem0": self.backend.startswith("mem0")}

    def _load(self) -> dict[str, list[dict[str, Any]]]:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, payload: dict[str, list[dict[str, Any]]]) -> None:
        self.path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    def add(self, trader_id: str, text: str, memory_type: str, metadata: dict[str, Any] | None = None) -> None:
        metadata = metadata or {}
        if self._mem0:
            try:
                payload_metadata = {"memory_type": memory_type, **metadata}
                if self.backend == "mem0_cloud":
                    self._mem0.add(
                        [{"role": "user", "content": text}],
                        user_id=trader_id,
                        metadata=payload_metadata,
                    )
                else:
                    self._mem0.add(
                        [{"role": "user", "content": text}],
                        user_id=trader_id,
                        metadata=payload_metadata,
                        infer=False,
                        memory_type=memory_type,
                    )
            except Exception:
                pass
        data = self._load()
        data.setdefault(trader_id, []).append(
            {"memory": text, "memory_type": memory_type, "metadata": metadata}
        )
        self._save(data)

    def search(self, trader_id: str, query: str, limit: int = 5) -> list[str]:
        if self._mem0:
            try:
                if self.backend == "mem0_cloud":
                    results = self._mem0.search(query, user_id=trader_id, limit=limit)
                    memories = results.get("results", results) if isinstance(results, dict) else results
                else:
                    memories = self._mem0.search(query=query, user_id=trader_id, top_k=limit)
                found = []
                for item in list(memories)[:limit]:
                    if isinstance(item, dict):
                        found.append(item.get("memory") or item.get("text") or str(item))
                    else:
                        found.append(str(item))
                if found:
                    return found
            except Exception:
                pass
        terms = {term.lower().strip(".,:;!?") for term in query.split() if len(term) > 2}
        memories = self._load().get(trader_id, [])
        scored: list[tuple[int, str]] = []
        for item in memories:
            text = item["memory"]
            score = sum(1 for term in terms if term in text.lower())
            scored.append((score, text))
        scored.sort(reverse=True)
        return [text for _, text in scored[:limit]]

    def seed_demo_memories(self, trader_id: str) -> None:
        existing = set(self.search(trader_id, "", limit=100))
        seeds = [
            ("episodic", "User wanted to invest in technology leaders after strong AI demand."),
            ("episodic", "User previously preferred paper trades before committing real capital."),
            ("episodic", "User asked to avoid oversized single-stock exposure."),
            ("semantic", "Risk preference: keep one stock at or below 10% of the portfolio."),
        ]
        for memory_type, text in seeds:
            if text not in existing:
                self.add(trader_id, text, memory_type)
