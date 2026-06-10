from src.services.token_tracker import TokenTracker

class Evaluator:
    @staticmethod
    def compare(
        baseline_prompt,
        mem0_prompt
    ):
        baseline_tokens=TokenTracker.estimate_tokens(baseline_prompt)
        mem0_tokens=TokenTracker.estimate_tokens(mem0_prompt)


        savings=((
            baseline_tokens-mem0_tokens
        )/baseline_tokens)*100
        return {
            "baseline_tokens":baseline_tokens,
            "mem0_tokens":mem0_tokens,
            "token_savings_percentage":round(savings,2)
        }