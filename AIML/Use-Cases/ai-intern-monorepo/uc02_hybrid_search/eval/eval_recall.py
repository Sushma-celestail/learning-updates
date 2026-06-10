"""
UC02 — Hybrid Search RAG: Recall@5 evaluation.

Run:
    python uc02_hybrid_search/eval/eval_recall.py

What it measures:
    Recall@5 = fraction of eval questions where the correct answer chunk
               appears in the top-5 retrieved documents.

Three configurations compared:
    (a) vector-only   — ChromaDB top-5, no BM25, no reranking
    (b) hybrid        — EnsembleRetriever top-5, no reranking
    (c) hybrid+rerank — EnsembleRetriever top-30 → cross-encoder top-5

Acceptance criteria:
    AC6: hybrid+rerank Recall@5 ≥ 0.85 AND > vector-only baseline
    AC7: latency report printed for all three configurations

Customise EVAL_SET below with questions relevant to your own documents.
A question "passes" if any of its expected keywords appear in the text
of at least one of the top-5 retrieved chunks.
"""

import sys
import time
from pathlib import Path
from typing import List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from shared.config.settings import (
    HYBRID_TOP_N,
    RERANK_TOP_K,
    UC02_CHROMA_DIR,
    UC02_COLLECTION,
)
from shared.vectorstore.chroma import get_vectorstore
from uc02_hybrid_search.reranker import rerank
from uc02_hybrid_search.retriever import get_hybrid_retriever

# ---------------------------------------------------------------------------
# Eval set — 20 question / keyword pairs
# Replace with questions relevant to YOUR ingested documents.
# ---------------------------------------------------------------------------
EVAL_SET: List[Tuple[str, List[str]]] = [
    ("What is dependency injection?",           ["dependency", "inject"]),
    ("How do path parameters work?",            ["path", "parameter"]),
    ("How do I validate request bodies?",       ["pydantic", "model", "body"]),
    ("What is async in FastAPI?",               ["async", "await"]),
    ("How do I add authentication?",            ["oauth2", "token", "auth"]),
    ("How do I handle file uploads?",           ["upload", "file", "form"]),
    ("What is CORS and how to enable it?",      ["cors", "middleware"]),
    ("How do I write tests for FastAPI?",       ["testclient", "pytest", "test"]),
    ("What are background tasks?",              ["background", "task"]),
    ("How do I use query parameters?",          ["query", "parameter"]),
    ("What is OpenAPI in FastAPI?",             ["openapi", "swagger", "docs"]),
    ("How do I return JSON responses?",         ["jsonresponse", "json"]),
    ("What are response models?",               ["response_model", "schema"]),
    ("How do I use environment variables?",     ["env", "settings", "config"]),
    ("What is middleware in FastAPI?",          ["middleware", "request"]),
    ("How do I handle errors and exceptions?",  ["exception", "handler", "http"]),
    ("What are routers in FastAPI?",            ["router", "apirouter", "include"]),
    ("How do I add custom headers?",            ["header", "response"]),
    ("What is lifespan in FastAPI?",            ["lifespan", "startup", "shutdown"]),
    ("How do I deploy FastAPI with Docker?",    ["docker", "dockerfile", "container"]),
]


def _hits(docs, keywords: List[str]) -> bool:
    """Return True if any keyword appears in any of the retrieved docs."""
    combined = " ".join(d.page_content.lower() for d in docs)
    return any(kw.lower() in combined for kw in keywords)


def _eval_config(name: str, retrieve_fn, questions_keywords) -> Tuple[float, float]:
    """Evaluate one retrieval configuration. Returns (recall@5, avg_latency)."""
    hits      = 0
    latencies = []

    for question, keywords in questions_keywords:
        t0   = time.perf_counter()
        docs = retrieve_fn(question)
        latencies.append(time.perf_counter() - t0)
        if _hits(docs, keywords):
            hits += 1

    recall  = hits / len(questions_keywords)
    avg_lat = sum(latencies) / len(latencies)
    print(f"  [{name}] Recall@5={recall:.2f}  avg_latency={avg_lat:.3f}s")
    return recall, avg_lat


def run_eval() -> None:
    """Run all three retrieval configurations and print the comparison report."""
    print("\n" + "=" * 60)
    print("UC02 — Recall@5 Evaluation")
    print("=" * 60)
    print(f"Eval set size: {len(EVAL_SET)} questions\n")

    # (a) Vector-only
    vs      = get_vectorstore(UC02_CHROMA_DIR, UC02_COLLECTION)
    vec_ret = vs.as_retriever(search_kwargs={"k": RERANK_TOP_K})

    def vector_only(q):
        return vec_ret.invoke(q)

    # (b) Hybrid (no rerank)
    hybrid_ret = get_hybrid_retriever(top_n=RERANK_TOP_K)

    def hybrid(q):
        return hybrid_ret.invoke(q)

    # (c) Hybrid + rerank
    hybrid_ret_30 = get_hybrid_retriever(top_n=HYBRID_TOP_N)

    def hybrid_rerank(q):
        docs = hybrid_ret_30.invoke(q)
        return rerank(q, docs, top_k=RERANK_TOP_K)

    print("Running evaluations …\n")
    r_vec, l_vec = _eval_config("(a) vector-only  ", vector_only,   EVAL_SET)
    r_hyb, l_hyb = _eval_config("(b) hybrid       ", hybrid,        EVAL_SET)
    r_rer, l_rer = _eval_config("(c) hybrid+rerank", hybrid_rerank, EVAL_SET)

    print("\n" + "=" * 60)
    print("LATENCY REPORT (AC7)")
    print("=" * 60)
    print(f"  (a) vector-only   : {l_vec:.3f}s avg")
    print(f"  (b) hybrid        : {l_hyb:.3f}s avg")
    print(f"  (c) hybrid+rerank : {l_rer:.3f}s avg")
    print()
    print("RECOMMENDATION:")
    if r_rer >= 0.85 and r_rer > r_vec:
        print(
            f"  ✅ Ship hybrid+rerank — Recall@5={r_rer:.2f} meets ≥0.85 target "
            f"and beats vector-only ({r_vec:.2f}).\n"
            f"  Latency overhead vs vector-only: +{l_rer - l_vec:.3f}s"
        )
    else:
        print(
            f"  ⚠️  hybrid+rerank Recall@5={r_rer:.2f} — "
            "check your eval set or reranker model."
        )
    print("=" * 60)

    assert r_rer >= 0.85, f"AC6 FAILED: hybrid+rerank Recall@5={r_rer:.2f} < 0.85"
    assert r_rer > r_vec, (
        f"AC6 FAILED: hybrid+rerank ({r_rer:.2f}) not better than vector-only ({r_vec:.2f})"
    )
    print("\n✅ AC6 passed — hybrid+rerank Recall@5 ≥ 0.85 and > vector-only baseline")


if __name__ == "__main__":
    run_eval()
