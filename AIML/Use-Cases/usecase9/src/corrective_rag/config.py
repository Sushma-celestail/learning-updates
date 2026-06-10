from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from corrective_rag.env import load_local_env


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    knowledge_base_path: Path = PROJECT_ROOT / "data" / "knowledge_base.jsonl"
    eval_dataset_path: Path = PROJECT_ROOT / "data" / "eval_dataset.jsonl"
    audit_db_path: Path = PROJECT_ROOT / "rag_audit.sqlite3"
    llm_provider: str = "local"
    groq_model: str = "llama-3.1-8b-instant"
    retriever_provider: str = "local"
    langfuse_dataset_name: str = "corrective-rag-usecase9"
    baseline_report_path: Path = PROJECT_ROOT / "reports" / "baseline_eval_report.json"
    retrieval_top_k: int = 4
    min_retrieval_score: float = 0.12
    min_hallucination_score: float = 0.72
    min_helpfulness_score: float = 0.62
    min_faithfulness: float = 0.80
    min_answer_relevancy: float = 0.80
    min_context_precision: float = 0.75

    @classmethod
    def from_env(cls) -> "Settings":
        load_local_env(PROJECT_ROOT)
        return cls(
            knowledge_base_path=Path(
                os.getenv("CORRECTIVE_RAG_KB", cls.knowledge_base_path)
            ),
            eval_dataset_path=Path(
                os.getenv("CORRECTIVE_RAG_DATASET", cls.eval_dataset_path)
            ),
            audit_db_path=Path(os.getenv("CORRECTIVE_RAG_DB", cls.audit_db_path)),
            llm_provider=os.getenv("CORRECTIVE_RAG_LLM", cls.llm_provider).lower(),
            groq_model=os.getenv("GROQ_MODEL", cls.groq_model),
            retriever_provider=os.getenv("CORRECTIVE_RAG_RETRIEVER", cls.retriever_provider).lower(),
            langfuse_dataset_name=os.getenv(
                "LANGFUSE_DATASET_NAME", cls.langfuse_dataset_name
            ),
            baseline_report_path=Path(
                os.getenv("CORRECTIVE_RAG_BASELINE_REPORT", cls.baseline_report_path)
            ),
            retrieval_top_k=int(os.getenv("CORRECTIVE_RAG_TOP_K", cls.retrieval_top_k)),
            min_retrieval_score=float(
                os.getenv("CORRECTIVE_RAG_MIN_RETRIEVAL", cls.min_retrieval_score)
            ),
            min_hallucination_score=float(
                os.getenv("CORRECTIVE_RAG_MIN_GROUNDEDNESS", cls.min_hallucination_score)
            ),
            min_helpfulness_score=float(
                os.getenv("CORRECTIVE_RAG_MIN_HELPFULNESS", cls.min_helpfulness_score)
            ),
            min_faithfulness=float(
                os.getenv("CORRECTIVE_RAG_MIN_FAITHFULNESS", cls.min_faithfulness)
            ),
            min_answer_relevancy=float(
                os.getenv("CORRECTIVE_RAG_MIN_ANSWER_RELEVANCY", cls.min_answer_relevancy)
            ),
            min_context_precision=float(
                os.getenv("CORRECTIVE_RAG_MIN_CONTEXT_PRECISION", cls.min_context_precision)
            ),
        )
