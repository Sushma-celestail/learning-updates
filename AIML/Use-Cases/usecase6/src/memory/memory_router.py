class MemoryRouter:

    def route(self, query: str):

        query = query.lower()

        if any(word in query for word in ["prefer", "like", "hate", "want"]):
            return "preference"

        if any(word in query for word in ["yesterday", "last time", "earlier", "conversation"]):
            return "episodic"

        return "semantic"