from __future__ import annotations

from corrective_rag.evaluators import helpfulness_evaluator
from corrective_rag.models import RetrievedDocument


def judge_helpfulness(
    question: str,
    answer: str,
    contexts: list[RetrievedDocument],
    threshold: float = 0.62,
):
    return helpfulness_evaluator(question, answer, contexts, threshold)
