from langchain_groq import ChatGroq
from src.config.settings import GROQ_API_KEY
import json


class MemoryClassifier:

    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=GROQ_API_KEY,
            temperature=0
        )

    def classify(self, text: str):

        prompt = f"""
You are a memory classification system.

Classify into exactly ONE category:

- semantic → facts about user (name, location, identity)
- episodic → events or experiences
- preference → likes, dislikes, habits

Return ONLY valid JSON:

{{
  "type": "semantic|episodic|preference",
  "memory": "clean extracted memory"
}}

User Input:
{text}
"""

        response = self.llm.invoke(prompt).content

        try:
            return json.loads(response)
        except:
            # safe fallback
            return {
                "type": "semantic",
                "memory": text
            }