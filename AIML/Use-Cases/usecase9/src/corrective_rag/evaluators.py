from __future__ import annotations

import re
from collections import Counter

from corrective_rag.models import EvaluationResult, RetrievedDocument
from corrective_rag.retriever import tokenize


def run_online_evaluators(
    question: str,
    answer: str,
    contexts: list[RetrievedDocument],
    min_groundedness: float,
    min_helpfulness: float,
) -> list[EvaluationResult]:
    return [
        hallucination_evaluator(answer, contexts, min_groundedness),
        helpfulness_evaluator(question, answer, contexts, min_helpfulness),
    ]


def hallucination_evaluator(
    answer: str,
    contexts: list[RetrievedDocument],
    threshold: float = 0.72,
) -> EvaluationResult:
    if "do not have enough grounded" in answer.lower():
        return EvaluationResult(
            name="online_hallucination_guard",
            score=1.0,
            passed=True,
            rationale="The answer explicitly abstained because context was insufficient.",
        )

    answer_terms = Counter(tokenize(strip_citations(answer)))
    if not answer_terms:
        return EvaluationResult(
            name="online_hallucination_guard",
            score=0.0,
            passed=False,
            rationale="No meaningful answer terms were produced.",
        )

    context_terms = set()
    cited_ids = set(re.findall(r"\[([A-Z0-9_-]+)\]", answer))
    available_ids = {item.document.doc_id for item in contexts}
    for item in contexts:
        context_terms.update(tokenize(item.document.text))
        context_terms.update(tokenize(item.document.title))

    supported = sum(count for term, count in answer_terms.items() if term in context_terms)
    total = sum(answer_terms.values())
    citation_bonus = 0.08 if cited_ids and cited_ids.issubset(available_ids) else 0.0
    score = min(1.0, supported / max(total, 1) + citation_bonus)
    return EvaluationResult(
        name="online_hallucination_guard",
        score=score,
        passed=score >= threshold,
        rationale=(
            f"{supported}/{total} answer terms were supported by retrieved context; "
            f"citation check={'passed' if citation_bonus else 'weak'}."
        ),
        details={"cited_ids": sorted(cited_ids), "available_ids": sorted(available_ids)},
    )


def helpfulness_evaluator(
    question: str,
    answer: str,
    contexts: list[RetrievedDocument],
    threshold: float = 0.62,
) -> EvaluationResult:
    question_terms = set(tokenize(question))
    answer_terms = set(tokenize(answer))
    coverage = len(question_terms.intersection(answer_terms)) / max(len(question_terms), 1)
    context_strength = max((item.score for item in contexts), default=0.0)
    has_actionable_shape = any(
        marker in answer.lower()
        for marker in ["should", "use", "include", "based", "run", "add", "policy", "score"]
    )
    score = min(
        1.0,
        coverage * 0.45 + min(context_strength, 1.0) * 0.4 + (0.15 if has_actionable_shape else 0.0),
    )
    return EvaluationResult(
        name="online_helpfulness_guard",
        score=score,
        passed=score >= threshold,
        rationale=(
            f"Question-term coverage={coverage:.2f}, retrieval strength={context_strength:.2f}, "
            f"actionable shape={'yes' if has_actionable_shape else 'no'}."
        ),
    )


def strip_citations(answer: str) -> str:
    return re.sub(r"\[[^\]]+\]", "", answer)
