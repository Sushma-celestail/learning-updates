from src.memory.memory_manager import Mem0Manager

class RetrievalService:
    def __init__(self):
        self.memory_manager=Mem0Manager()
    def retrieve_memories(
        self,
        query,
        user_id
    ):
        memories=self.memory_manager.search(
            query=query,
            user_id=user_id
        )
        return self.memory.search(
            query=query,
            filters={"user_id": user_id}
        )