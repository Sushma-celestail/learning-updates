"""
UC02 — Hybrid Search RAG: Reranking stage.

Architecture (exact spec):
    Top 30 (from EnsembleRetriever)
        ↓
    Cross Encoder Reranker
    (BAAI/bge-reranker-v2-m3)
        ↓
    Top 5

Two backends — set RERANKER_BACKEND in .env:
    "local"  — BAAI/bge-reranker-v2-m3 via sentence-transformers
               Free, runs on CPU, ~2.3 GB download on first use (then cached).
    "cohere" — Cohere rerank-english-v3.0 API
               Free trial (1 000 calls/month), requires COHERE_API_KEY.

Default: "local"

Usage:
    from uc02_hybrid_search.reranker import rerank
    top5 = rerank(query="What is FastAPI?", docs=top30_docs, top_k=5)
"""

import os
import sys
from pathlib import Path
from typing import List

from langchain_core.documents import Document

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from shared.config.settings import RERANK_TOP_K

RERANKER_BACKEND = os.getenv("RERANKER_BACKEND", "local").lower()
LOCAL_MODEL      = os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-v2-m3")


def _rerank_local(query: str, docs: List[Document], top_k: int) -> List[Document]:
    """
    Rerank using BAAI/bge-reranker-v2-m3 (sentence-transformers).

    How it works:
        - Takes every (query, document) pair
        - Passes both through a single transformer (full cross-attention)
        - Outputs one relevance score per pair
        - Returns top_k documents sorted by score descending

    First run downloads ~2.3 GB model to ~/.cache/huggingface/
    Subsequent runs use the cached model — fast (~1–2 s for 30 docs on CPU).
    """
    try:
        from sentence_transformers import CrossEncoder  # type: ignore
    except ImportError:
        raise ImportError(
            "sentence-transformers is not installed.\n"
            "Run: pip install sentence-transformers"
        )

    model  = CrossEncoder(LOCAL_MODEL)
    pairs  = [(query, doc.page_content) for doc in docs]
    scores = model.predict(pairs)

    ranked = sorted(zip(scores, docs), key=lambda x: x[0], reverse=True)
    return [doc for _, doc in ranked[:top_k]]


def _rerank_cohere(query: str, docs: List[Document], top_k: int) -> List[Document]:
    """
    Rerank using Cohere rerank-english-v3.0 API.
    Requires COHERE_API_KEY in .env.
    """
    try:
        import cohere  # type: ignore
    except ImportError:
        raise ImportError("cohere not installed. Run: pip install cohere")

    api_key = os.getenv("COHERE_API_KEY", "")
    if not api_key:
        raise EnvironmentError(
            "COHERE_API_KEY not set.\n"
            "Get a free key at https://dashboard.cohere.com/api-keys"
        )

    co     = cohere.Client(api_key)
    texts  = [doc.page_content for doc in docs]
    result = co.rerank(
        query=query,
        documents=texts,
        model="rerank-english-v3.0",
        top_n=top_k,
    )
    return [docs[r.index] for r in result.results]


def rerank(
    query: str,
    docs: List[Document],
    top_k: int = RERANK_TOP_K,
) -> List[Document]:
    """
    Rerank candidate documents and return the top_k most relevant.

    Parameters
    ----------
    query  : the user's original query string
    docs   : candidate documents from the ensemble retriever (top-30)
    top_k  : number of documents to keep (default 5)
    """
    if not docs:
        return []

    if RERANKER_BACKEND == "cohere":
        return _rerank_cohere(query, docs, top_k)
    return _rerank_local(query, docs, top_k)
