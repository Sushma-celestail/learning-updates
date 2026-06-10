from src.agents.personal_assistant import (
    PersonalAssistant
)


class Mem0Agent:

    def __init__(self):

        self.agent = PersonalAssistant()

    def chat(
        self,
        user_id,
        query
    ):

        return self.agent.chat(
            user_id,
            query
        )