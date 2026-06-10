# User Question
#       │
#       ▼
# answer()
#       │
#       ▼
# workflow.run()
#       │
#       ▼
# retrieve()
#       │
#       ▼
# grade_documents()
#       │
#       ▼
# rewrite_query() (optional)
#       │
#       ▼
# web_search() (optional)
#       │
#       ▼
# generate()
#       │
#       ▼
# hallucination_eval()
#       │
#       ▼
# helpfulness_eval()
#       │
#       ▼
# RAGAnswer
#       │
#       ▼
# Audit Logger
#       │
#       ▼
# Langfuse Metrics

from __future__ import annotations

import os
import re
from time import perf_counter

from corrective_rag.audit import AuditLogger
from corrective_rag.config import Settings
from corrective_rag.corpus import load_documents
from corrective_rag.llm import LocalGroundedGenerator
from corrective_rag.models import RAGAnswer
from corrective_rag.retriever import LocalBM25Retriever
from corrective_rag.tracing import flush_langfuse, new_trace_id, observe, score_langfuse_trace
from graph.workflow import CorrectiveRAGWorkflow
from llm.groq import GroqGenerator
from observability.metrics import capture_langfuse_metrics
from retriever.chroma import ChromaRetriever


class CorrectiveRAGPipeline:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings.from_env()
        self.documents = load_documents(self.settings.knowledge_base_path)
        self.retriever = (
            ChromaRetriever(self.documents)
            if self.settings.retriever_provider == "chroma"
            else LocalBM25Retriever(self.documents)
        )
        self.audit_logger = AuditLogger(self.settings.audit_db_path)
        self.generator = self._build_generator()
        self.workflow = CorrectiveRAGWorkflow(self.retriever, self.generator, self.settings)

    @observe(name="corrective-rag-answer")
    def answer(self, question: str, user_id: str | None = None) -> RAGAnswer:
        trace_id = new_trace_id()
        started_at = perf_counter()
        state = self.workflow.run(question)
        latency_ms = (perf_counter() - started_at) * 1000
        metrics = capture_langfuse_metrics(state, self._model_name(), latency_ms)

        answer = RAGAnswer(
            question=question,
            answer=state.generation,
            citations=self._citations_from_answer(state.generation, state.documents),
            retrieved=state.documents,
            evaluations=state.evaluations,
            corrected=state.corrected,
            correction_reason=state.correction_reason,
            trace_id=trace_id,
            user_id=user_id or os.getenv("CORRECTIVE_RAG_USER_ID", "local-user"),
            model=metrics.model,
            cost_usd=metrics.cost_usd,
            latency_ms=metrics.latency_ms,
            input_tokens=metrics.input_tokens,
            output_tokens=metrics.output_tokens,
            total_tokens=metrics.total_tokens,
        )
        self.audit_logger.record(answer)
        score_langfuse_trace(trace_id, state.evaluations)
        flush_langfuse()
        return answer

    def _build_generator(self):
        if self.settings.llm_provider == "groq":
            return GroqGenerator(self.settings.groq_model)
        return LocalGroundedGenerator()

    def _model_name(self) -> str:
        if self.settings.llm_provider == "groq":
            return self.settings.groq_model
        return "local-grounded-generator"

    def _citations_from_answer(self, answer: str, documents: list) -> list[str]:
        cited = re.findall(r"\[([A-Z0-9_-]+)\]", answer)
        available = {item.document.doc_id for item in documents}
        filtered = [doc_id for doc_id in cited if doc_id in available]
        if filtered:
            return list(dict.fromkeys(filtered))
        return [item.document.doc_id for item in documents[:3]]
