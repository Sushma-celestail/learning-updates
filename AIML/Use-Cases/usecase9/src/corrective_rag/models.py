from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class Document:
    doc_id: str
    title: str
    text: str
    source: str
    metadata: dict[str, Any] = field(default_factory=dict)

#immutable and it stores search results
@dataclass(frozen=True)
class RetrievedDocument:
    document: Document
    #similarity score if its high =more relevant
    score: float
    matched_terms: tuple[str, ...]


@dataclass(frozen=True)
class EvaluationResult:
    #matrx name means faithfullness,relevancy, correctness
    name: str
    score: float
    passed: bool
    rationale: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RAGAnswer:
    question: str
    answer: str
    citations: list[str]
    retrieved: list[RetrievedDocument]   
    evaluations: list[EvaluationResult]
    corrected: bool
    #correction reason is hallucianation deteted or not 
    correction_reason: str | None
    trace_id: str
    user_id: str = "local-user"
    model: str = "local"
    cost_usd: float = 0.0
    latency_ms: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def as_report_row(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "answer": self.answer,
            "citations": self.citations,
            "corrected": self.corrected,
            "correction_reason": self.correction_reason,
            "trace_id": self.trace_id,
            "user_id": self.user_id,
            "model": self.model,
            "cost_usd": round(self.cost_usd, 6),
            "latency_ms": round(self.latency_ms, 2),
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "created_at": self.created_at,
            "retrieval_scores": [round(item.score, 4) for item in self.retrieved],
            "evaluations": [
                {
                    "name": item.name,
                    "score": round(item.score, 4),
                    "passed": item.passed,
                    "rationale": item.rationale,
                }
                for item in self.evaluations
            ],
        }
