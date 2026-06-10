"""
UC02 — Hybrid Search RAG: Retrieval layer.

Architecture (exact spec):
    Documents
        ↓
    Chunking
        ↓
    ┌─────────────┬─────────────┐
    │  BM25 Index │ Vector Index│
    │  (BM25)     │ (ChromaDB)  │
    └─────────────┴─────────────┘
        ↓
    EnsembleRetriever (0.5 / 0.5 RRF)
        ↓
    Top 30

BM25 wins on:  exact-match queries — function names, error codes, HTTP
               status codes that appear verbatim in the documents.
Vectors win on: paraphrase queries — "make it faster" finds chunks about
               "performance optimisation" even without shared tokens.

Usage:
    from uc02_hybrid_search.retriever import get_hybrid_retriever

    retriever = get_hybrid_retriever()
    docs = retriever.invoke("What is dependency injection?")

    # Metadata filter — restrict vector leg to PDF chunks only (AC9)
    retriever = get_hybrid_retriever(metadata_filter={"source_type": "pdf"})
"""

import pickle
import sys
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from langchain_community.retrievers import BM25Retriever

# EnsembleRetriever location varies by LangChain version
try:
    from langchain_classic.retrievers import EnsembleRetriever  # type: ignore
except ImportError:
    try:
        from langchain.retrievers import EnsembleRetriever  # type: ignore
    except ImportError:
        from langchain_community.retrievers import EnsembleRetriever  # type: ignore

from shared.config.settings import (
    BM25_WEIGHT,
    HYBRID_TOP_N,
    UC02_CHROMA_DIR,
    UC02_COLLECTION,
    VECTOR_WEIGHT,
)
from shared.vectorstore.chroma import get_vectorstore

DOCS_PICKLE = Path(__file__).parent / "data" / "bm25_docs.pkl"


def _load_bm25_docs() -> list:
    """Load the pickled chunk list for BM25 index construction."""
    if not DOCS_PICKLE.exists():
        raise FileNotFoundError(
            f"BM25 corpus not found at {DOCS_PICKLE}\n"
            "Run: python uc02_hybrid_search/ingest.py"
        )
    with open(DOCS_PICKLE, "rb") as f:
        return pickle.load(f)


def get_hybrid_retriever(
    metadata_filter: Optional[dict] = None,
    top_n: int           = HYBRID_TOP_N,
    vector_weight: float = VECTOR_WEIGHT,
    bm25_weight: float   = BM25_WEIGHT,
) -> EnsembleRetriever:
    """
    Build and return the EnsembleRetriever (BM25 + ChromaDB).

    Parameters
    ----------
    metadata_filter : Chroma 'where' clause, e.g. {"source_type": "pdf"} (AC9)
    top_n           : total docs to retrieve before reranking (default 30)
    vector_weight   : weight for the dense-vector leg (default 0.5)
    bm25_weight     : weight for the BM25 leg (default 0.5)
    """
    # ── BM25 leg (keyword / lexical search) ─────────────────────────────────
    docs   = _load_bm25_docs()
    bm25   = BM25Retriever.from_documents(docs)
    bm25.k = top_n

    # ── Vector leg (dense / semantic search) ────────────────────────────────
    search_kwargs = {"k": top_n}
    if metadata_filter:
        search_kwargs["filter"] = metadata_filter   # Chroma where clause (AC9)
    vs         = get_vectorstore(UC02_CHROMA_DIR, UC02_COLLECTION)
    vector_ret = vs.as_retriever(search_kwargs=search_kwargs)

    # ── Ensemble — Reciprocal Rank Fusion (0.5 / 0.5) ───────────────────────
    return EnsembleRetriever(
        retrievers=[bm25, vector_ret],
        weights=[bm25_weight, vector_weight],
    )
