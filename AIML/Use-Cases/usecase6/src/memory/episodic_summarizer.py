from langchain_groq import ChatGroq
from src.config.settings import GROQ_API_KEY


class EpisodicSummarizer:

    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=GROQ_API_KEY,
            temperature=0
        )

    def summarize(self, conversation: list):

        prompt = f"""
Summarize this conversation into a SHORT episodic memory.

Rules:
- 2–3 lines max
- focus on events, goals, preferences
- no dialogue

Conversation:
{conversation}
"""

        return self.llm.invoke(prompt).content.strip()