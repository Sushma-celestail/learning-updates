from __future__ import annotations

from corrective_rag.retriever import tokenize


PROJECT_TERMS = {
    "api",
    "async",
    "audit",
    "callbackhandler",
    "chroma",
    "ci",
    "corrective",
    "dataset",
    "dependency",
    "documents",
    "evaluation",
    "fastapi",
    "governance",
    "govern",
    "grounded",
    "hallucination",
    "helpfulness",
    "langchain",
    "langfuse",
    "langgraph",
    "latency",
    "measure",
    "metrics",
    "nist",
    "observability",
    "openapi",
    "parameter",
    "parameters",
    "path",
    "pydantic",
    "rag",
    "ragas",
    "retrieval",
    "sqlite",
    "starlette",
    "tokens",
    "trace",
    "tracing",
    "web",
}

WEB_ELIGIBLE_PATTERNS = (
    "latest",
    "current",
    "today",
    "yesterday",
    "who is",
    "who won",
    "prime minister",
    "president",
    "final",
)


def classify_question(question: str) -> str:
    lower = question.strip().lower()
    if any(pattern in lower for pattern in WEB_ELIGIBLE_PATTERNS):
        return "web"
    terms = set(tokenize(lower))
    if terms.intersection(PROJECT_TERMS):
        return "local"
    return "web"


def is_project_question(question: str) -> bool:
    return classify_question(question) == "local"
