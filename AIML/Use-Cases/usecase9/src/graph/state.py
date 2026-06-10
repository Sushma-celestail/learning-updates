from __future__ import annotations

from dataclasses import dataclass, field

from corrective_rag.models import EvaluationResult, RetrievedDocument


@dataclass
class GraphState:
    question: str
    documents: list[RetrievedDocument] = field(default_factory=list)
    generation: str = ""
    grade: float = 0.0
    iterations: int = 0
    rewritten_question: str = ""
    web_documents: list[RetrievedDocument] = field(default_factory=list)
    evaluations: list[EvaluationResult] = field(default_factory=list)
    corrected: bool = False
    correction_reason: str | None = None
    scope: str = "local"
