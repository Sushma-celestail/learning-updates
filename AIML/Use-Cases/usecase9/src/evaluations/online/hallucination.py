from __future__ import annotations

from corrective_rag.evaluators import hallucination_evaluator
from corrective_rag.models import RetrievedDocument


def judge_hallucination(answer: str, contexts: list[RetrievedDocument], threshold: float = 0.72):
    return hallucination_evaluator(answer, contexts, threshold)
