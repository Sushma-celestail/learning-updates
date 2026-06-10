from src.config.prompts import SYSTEM_PROMPT
from src.llm.groq import GroqClient


class ResponseService:

    def __init__(self):
        self.llm = GroqClient()

    def build_prompt(
        self,
        memories,
        query
    ):

        print("\nRetrieved Memories:")
        print(memories)

        memory_text = ""

        memory_results = memories.get("results", [])

        for memory in memory_results:

            print("Memory Item:", memory)

            if isinstance(memory, dict):
                memory_text += (
                    f"- {memory.get('memory', '')}\n"
                )

        prompt = SYSTEM_PROMPT.format(
            memories=memory_text
        )

        prompt += f"\n\nUser Question:\n{query}"

        return prompt

    def generate_response(
        self,
        memories,
        query
    ):

        prompt = self.build_prompt(
            memories,
            query
        )

        return self.llm.generate(prompt)