from langchain_groq import ChatGroq
from src.config.settings import GROQ_API_KEY


class SessionSummarizer:

    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=GROQ_API_KEY,
            temperature=0
        )

    def summarize(self, messages):

        prompt = f"""
Summarize this conversation into a short episodic memory:

Focus on:
- what user discussed
- decisions made
- context changes

Messages:
{messages}

Return a single paragraph.
"""

        return self.llm.invoke(prompt).content