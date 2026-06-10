from mem0 import Memory
from src.config.settings import MEMORY_CONFIG


class Mem0Manager:

    def __init__(self):
        self.memory = Memory.from_config(MEMORY_CONFIG)

    def search(self, query, user_id):
        return self.memory.search(
            query=query,
            filters={"user_id": user_id}
        )

    def add(self, messages, user_id, metadata=None):
        return self.memory.add(
            messages,
            user_id=user_id,
            metadata=metadata or {}
        )

    def get_all(self, user_id):
        try:
            return self.memory.get_all(user_id=user_id)
        except Exception:
            return self.memory.search(
                query="",
                filters={"user_id": user_id}
            )