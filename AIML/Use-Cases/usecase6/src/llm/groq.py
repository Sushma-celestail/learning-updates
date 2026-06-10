from langchain_groq import ChatGroq
from src.config.settings import GROQ_API_KEY


class GroqClient:

    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=GROQ_API_KEY,
            temperature=0.3
        )

    def generate(self, prompt: str):
        response = self.llm.invoke(prompt)
        return response.content