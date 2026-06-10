from typing import List, Optional
from pydantic import BaseModel, Field


class GraphState(BaseModel):
    """
    State schema for the Corrective RAG LangGraph workflow.

    Fields
    ------
    question    : current (possibly rewritten) question
    documents   : list of retrieved document chunks (strings)
    scores      : per-document relevance scores (list of floats)
    avg_score   : mean of scores — used by edges to decide routing
    generation  : final answer produced by the generate node
    grade       : "relevant" | "ambiguous" | "irrelevant" from the grader
    iterations  : grading cycles elapsed (capped at 3)
    source      : "chroma" | "tavily" — which retriever was last used
    """

    question: str
    documents: List[str] = Field(default_factory=list)
    scores: List[float] = Field(default_factory=list)   # per-doc scores
    avg_score: float = 0.0                              # mean relevance
    generation: str = ""
    grade: str = ""
    iterations: int = 0
    source: str = "chroma"                              # default = local KB
