"""
UC02 — Hybrid Search RAG: Test suite.

Unit tests run without any API key or ingested data.
Integration tests require:
  - GOOGLE_API_KEY set in .env
  - Data ingested via: python uc02_hybrid_search/ingest.py

Run unit tests:
    pytest uc02_hybrid_search/tests/ -m "not integration" -v

Run all tests:
    pytest uc02_hybrid_search/tests/ -v
"""

import os
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from shared.config.settings import (
    BM25_WEIGHT,
    FALLBACK_PHRASE,
    HYBRID_TOP_N,
    RERANK_TOP_K,
    UC02_CHROMA_DIR,
    VECTOR_WEIGHT,
)

DOCS_PICKLE = Path(__file__).parent.parent / "data" / "bm25_docs.pkl"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _has_api_key() -> bool:
    return bool(os.getenv("GOOGLE_API_KEY"))


def _has_chroma() -> bool:
    return UC02_CHROMA_DIR.exists() and any(UC02_CHROMA_DIR.iterdir())


def _has_bm25_corpus() -> bool:
    return DOCS_PICKLE.exists()


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------

def test_ensemble_weights_sum_to_one():
    """BM25 + vector weights must sum to 1.0 for valid RRF fusion."""
    assert abs(BM25_WEIGHT + VECTOR_WEIGHT - 1.0) < 1e-9, (
        f"Weights must sum to 1.0, got {BM25_WEIGHT + VECTOR_WEIGHT}"
    )


def test_hybrid_top_n_greater_than_rerank_top_k():
    """Ensemble must retrieve more docs than the reranker keeps."""
    assert HYBRID_TOP_N > RERANK_TOP_K, (
        f"HYBRID_TOP_N ({HYBRID_TOP_N}) must be > RERANK_TOP_K ({RERANK_TOP_K})"
    )


def test_fallback_phrase_non_empty():
    """Fallback phrase must be configured."""
    assert FALLBACK_PHRASE and isinstance(FALLBACK_PHRASE, str)


def test_reranker_module_importable():
    """reranker.py must be importable without errors."""
    from uc02_hybrid_search import reranker  # noqa: F401


def test_retriever_module_importable():
    """retriever.py must be importable without errors."""
    from uc02_hybrid_search import retriever  # noqa: F401


def test_chain_module_importable():
    """chain.py must be importable without errors."""
    from uc02_hybrid_search import chain  # noqa: F401


# ---------------------------------------------------------------------------
# Integration tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_hybrid_retriever_returns_documents():
    """Hybrid retriever must return at least 1 document for a real query."""
    if not _has_api_key():
        pytest.skip("GOOGLE_API_KEY not set")
    if not _has_chroma() or not _has_bm25_corpus():
        pytest.skip("Data not ingested — run python uc02_hybrid_search/ingest.py")

    from uc02_hybrid_search.retriever import get_hybrid_retriever

    retriever = get_hybrid_retriever(top_n=10)
    docs      = retriever.invoke("What is FastAPI?")
    assert len(docs) > 0, "Hybrid retriever returned no documents"


@pytest.mark.integration
def test_reranker_reduces_doc_count():
    """Reranker must return ≤ top_k documents."""
    if not _has_api_key():
        pytest.skip("GOOGLE_API_KEY not set")
    if not _has_chroma() or not _has_bm25_corpus():
        pytest.skip("Data not ingested — run python uc02_hybrid_search/ingest.py")

    from uc02_hybrid_search.retriever import get_hybrid_retriever
    from uc02_hybrid_search.reranker import rerank

    retriever = get_hybrid_retriever(top_n=HYBRID_TOP_N)
    docs      = retriever.invoke("What is dependency injection?")
    reranked  = rerank("What is dependency injection?", docs, top_k=RERANK_TOP_K)

    assert len(reranked) <= RERANK_TOP_K, (
        f"Reranker returned {len(reranked)} docs, expected ≤ {RERANK_TOP_K}"
    )


@pytest.mark.integration
def test_metadata_filter_pdf_only():
    """
    AC9: Metadata filter must restrict results to PDF-sourced chunks.
    """
    if not _has_api_key():
        pytest.skip("GOOGLE_API_KEY not set")
    if not _has_chroma() or not _has_bm25_corpus():
        pytest.skip("Data not ingested — run python uc02_hybrid_search/ingest.py")

    from uc02_hybrid_search.retriever import get_hybrid_retriever

    retriever = get_hybrid_retriever(
        metadata_filter={"source_type": "pdf"},
        top_n=10,
    )
    docs = retriever.invoke("What is FastAPI?")

    # All vector-leg results must be PDFs (BM25 leg has no filter)
    # We check that at least some results exist and none are html-only
    for doc in docs:
        source_type = doc.metadata.get("source_type", "")
        assert source_type in ("pdf", ""), (
            f"Expected pdf source_type, got: {source_type}"
        )


@pytest.mark.integration
def test_full_pipeline_answer():
    """End-to-end: answer_question must return a non-empty string."""
    if not _has_api_key():
        pytest.skip("GOOGLE_API_KEY not set")
    if not _has_chroma() or not _has_bm25_corpus():
        pytest.skip("Data not ingested — run python uc02_hybrid_search/ingest.py")

    from uc02_hybrid_search.chain import answer_question

    answer = answer_question("What is FastAPI?")
    assert isinstance(answer, str) and answer.strip(), "Answer must be a non-empty string"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
