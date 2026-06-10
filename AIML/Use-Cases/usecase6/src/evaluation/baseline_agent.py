# shows the full history of the conversation, including all user inputs and agent responses, without any summarization or condensation.

from src.llm.gemini import GeminiClient

class BaselineAgent:
    def __init__(self):
        self.llm=GeminiClient()
        self.chat_history=[]
    def chat(self,query):
        self.chat_history.append(
            f"user:{query}"
        )
        prompt = "\n".join(
            self.chat_history
        )

        response = self.llm.generate(
            prompt
        )

        self.chat_history.append(
            f"Assistant: {response}"
        )

        return response