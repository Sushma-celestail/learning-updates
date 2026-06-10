from src.services.retrieval_service import RetrievalService
from src.services.response_service import ResponseService
from src.memory.memory_manager import Mem0Manager
from src.memory.memory_classifier import MemoryClassifier
from src.memory.episodic_summarizer import EpisodicSummarizer


class PersonalAssistant:

    def __init__(self):
        self.retriever = RetrievalService()
        self.response_service = ResponseService()
        self.memory_manager = Mem0Manager()
        self.classifier = MemoryClassifier()
        self.summarizer = EpisodicSummarizer()

        # session buffer for episodic memory
        self.session_buffer = {}

    # ---------------------------
    # MAIN CHAT FUNCTION
    # ---------------------------
    def chat(self, user_id, query):

        # 1. Retrieve relevant memories
        memories = self.retriever.retrieve_memories(
            query=query,
            user_id=user_id
        )

        # 2. Generate response
        response = self.response_service.generate_response(
            memories=memories,
            query=query
        )

        # 3. CLASSIFY MEMORY (CRITICAL FIX 🔥)
        classification = self.classifier.classify(query)

        memory_type = classification.get("type", "semantic")
        memory_text = classification.get("memory", query)

        # 4. SESSION BUFFER (episodic tracking)
        if user_id not in self.session_buffer:
            self.session_buffer[user_id] = []

        self.session_buffer[user_id].append({
            "role": "user",
            "content": query
        })

        self.session_buffer[user_id].append({
            "role": "assistant",
            "content": response
        })

        # 5. STORE MEMORY (FIXED STRUCTURE)
        self.memory_manager.add(
            messages=[{
                "role": "user",
                "content": memory_text
            }],
            user_id=user_id,
            metadata={
                "type": memory_type,
                "memory": memory_text
            }
        )

        return response

    # ---------------------------
    # END SESSION → EPISODIC MEMORY
    # ---------------------------
    def end_session(self, user_id):

        if not self.session_buffer.get(user_id):
            return None

        summary = self.summarizer.summarize(
            self.session_buffer[user_id]
        )

        self.memory_manager.add(
            messages=[{
                "role": "system",
                "content": summary
            }],
            user_id=user_id,
            metadata={
                "type": "episodic",
                "memory": summary
            }
        )

        # clear session
        self.session_buffer[user_id] = []

        return summary

    # ---------------------------
    # MEMORY VIEW
    # ---------------------------
    def show_memories(self, user_id):
        return self.memory_manager.get_all(user_id)