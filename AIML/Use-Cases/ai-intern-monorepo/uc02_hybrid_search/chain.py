"""
UC02 — Hybrid Search RAG: Full pipeline chain.

Exact pipeline from spec:
    User Query
        ↓
    EnsembleRetriever (BM25 + ChromaDB, top-30)
        ↓
    Cross Encoder Reranker (BAAI/bge-reranker-v2-m3, top-5)
        ↓
    Gemini gemini-2.5-flash
        ↓
    Answer + Sources

Langfuse tracing (AC8):
    Set LANGFUSE_PUBLIC_KEY + LANGFUSE_SECRET_KEY in .env.
    Every query produces a trace: retrieve → rerank → generate spans.
    Pipeline works normally without keys — tracing is optional.

Metadata filtering (AC9):
    Pass metadata_filter={"source_type": "pdf"} to restrict the
    vector search leg to PDF-sourced chunks only.

Usage:
    from uc02_hybrid_search.chain import answer_question

    answer = answer_question("What is dependency injection?")
    answer = answer_question("Show PDF content",
                             metadata_filter={"source_type": "pdf"})
"""

import sys
import time
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from langchain_core.output_parsers import StrOutputParser

from shared.config.prompts import get_hybrid_prompt
from shared.config.settings import HYBRID_TOP_N, RERANK_TOP_K
from shared.llm.gemini import GeminiChat
from shared.observability.langfuse_cb import get_langfuse_handler
from uc02_hybrid_search.reranker import rerank
from uc02_hybrid_search.retriever import get_hybrid_retriever


def _format_docs(docs) -> str:
    """Format reranked documents into a numbered context string with source labels."""
    if not docs:
        raise RuntimeError(
            "No documents retrieved.\n"
            "Run: python uc02_hybrid_search/ingest.py"
        )
    parts = []
    for i, doc in enumerate(docs, 1):
        source      = doc.metadata.get("source", doc.metadata.get("file_name", "unknown"))
        source_type = doc.metadata.get("source_type", "unknown")
        parts.append(f"[Source {i} ({source_type}): {source}]\n{doc.page_content}")
    return "\n\n".join(parts)


def answer_question(
    question: str,
    metadata_filter: Optional[dict] = None,
) -> str:
    """
    Run the full UC02 hybrid-search pipeline for one question.

    Pipeline:
        query
          → EnsembleRetriever (BM25 + ChromaDB, top-30)
          → Cross-Encoder Reranker (top-5)
          → Gemini gemini-2.5-flash
          → answer + Sources block

    Parameters
    ----------
    question        : the user's natural-language question
    metadata_filter : optional Chroma where clause, e.g. {"source_type": "pdf"}

    Returns
    -------
    Answer string with Sources block, or the fallback phrase.
    """
    t0 = time.perf_counter()

    # ── Step 1: Hybrid retrieval — BM25 + Vector → top-30 ───────────────────
    retriever = get_hybrid_retriever(metadata_filter=metadata_filter)
    raw_docs  = retriever.invoke(question)
    t_ret     = time.perf_counter() - t0
    print(f"  [retrieve] {len(raw_docs)} docs in {t_ret:.2f}s")

    # ── Step 2: Cross-encoder reranking → top-5 ──────────────────────────────
    t1            = time.perf_counter()
    reranked_docs = rerank(question, raw_docs, top_k=RERANK_TOP_K)
    t_rer         = time.perf_counter() - t1
    print(f"  [rerank]   {len(reranked_docs)} docs in {t_rer:.2f}s")

    # ── Step 3: Generate with Gemini ─────────────────────────────────────────
    t2      = time.perf_counter()
    context = _format_docs(reranked_docs)
    prompt  = get_hybrid_prompt()

    # Langfuse callback (AC8) — None if keys not set in .env
    handler   = get_langfuse_handler()
    callbacks = [handler] if handler else []

    chain  = prompt | GeminiChat | StrOutputParser()
    answer = chain.invoke(
        {"question": question, "context": context},
        config={"callbacks": callbacks} if callbacks else {},
    )
    t_gen  = time.perf_counter() - t2
    total  = time.perf_counter() - t0
    print(f"  [generate] {t_gen:.2f}s  |  total: {total:.2f}s")

    return answer
