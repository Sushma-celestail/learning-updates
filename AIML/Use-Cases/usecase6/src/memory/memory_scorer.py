import time


class MemoryScorer:

    def score(self, memory_type: str, text: str):

        base_score = {
            "semantic": 0.9,
            "preference": 1.0,
            "episodic": 0.7
        }.get(memory_type, 0.5)

        # boost important signals
        keywords = ["prefer", "always", "never", "name", "live", "hate", "like"]

        importance_boost = 0.1 * sum(
            1 for word in keywords if word in text.lower()
        )

        return min(base_score + importance_boost, 1.0)