"""

Goal:
Compare retrieval performance between:

1. Vector Search Only
2. Hybrid Search (BM25 + Vector)
3. Hybrid + Reranking

Metrics:
- Recall@5
- p50 Latency

"""

import json
import time
import statistics

from dotenv import load_dotenv

from langchain_core.documents import Document

from src.vectordb import get_vectorstore
from src.retriever import (
    create_bm25,
    create_ensemble_retriever
)
from src.reranker import rerank

load_dotenv()



# LOAD EVALUATION DATASET

# Dataset format:
#
# [
#   {
#       "question": "...",
#       "source": "data/pdfs/fastapi.pdf"
#   }
# ]

def load_dataset():

    with open("eval/qa_dataset.json", "r") as f:
        return json.load(f)



# EVALUATION FUNCTION


def run_evaluation():
    dataset = load_dataset()

    print(f"\nLoaded {len(dataset)} evaluation samples")

    vectordb = get_vectorstore()


    # VECTOR RETRIEVER

    # Semantic retrieval
    #
    # query
    #   ↓
    # embedding
    #   ↓
    # cosine similarity
    #   ↓
    # top-k documents

    vector_retriever = vectordb.as_retriever(
        search_kwargs={"k":10}
    )


    # LOAD RAW DOCUMENTS

    # Needed for BM25
    #
    # BM25 uses raw text
  

    all_data = vectordb.get()

    documents = all_data["documents"]
    metadatas = all_data["metadatas"]

    docs = []


    # REBUILD DOCUMENT OBJECTS
    for text, meta in zip(documents, metadatas):

        docs.append(
            Document(
                page_content=text,
                metadata=meta
            )
        )


    # VALIDATION CHECK


    if not docs:

        print("❌ No documents found.")
        print("Run: python ingest.py")

        return

    print(f"Loaded {len(docs)} chunks from ChromaDB")


    # BM25 RETRIEVER

    
    # INTERNAL FLOW:
    #
    # query
    #   ↓
    # tokenize
    #   ↓
    # inverted index lookup
    #   ↓
    # TF-IDF scoring
    #   ↓
    # ranking

    bm25_retriever = create_bm25(docs)


    # ENSEMBLE RETRIEVER
    # Combines:
    # - BM25 scores
    # - Vector similarity scores
    #
    # Uses:
    # Reciprocal Rank Fusion (RRF)

    ensemble_retriever = create_ensemble_retriever(
        bm25_retriever,
        vector_retriever
    )

  # 1. VECTOR ONLY EVALUATION

    print("\n==============================")
    print("Evaluating VECTOR ONLY")
    print("==============================")

    vector_correct = 0

    vector_latencies = []

    for sample in dataset:

        question = sample["question"]

        target_source = sample["source"]

        # =========================
        # START TIMER
        # =========================

        start = time.time()

        # =========================
        # VECTOR RETRIEVAL
        # =========================

        retrieved_docs = vector_retriever.invoke(question)

        latency = time.time() - start

        vector_latencies.append(latency)

        # =========================
        # RECALL@5 CHECK
        # =========================

        found = False

        for doc in retrieved_docs[:5]:

            source = doc.metadata.get(
                "source",
                ""
            )

            if target_source in source:

                found = True
                break

        if found:
            vector_correct += 1

    vector_recall = vector_correct / len(dataset)

    vector_p50 = statistics.median(
        vector_latencies
    )

    # =====================================================
    # 2. HYBRID EVALUATION
    # =====================================================

    print("\n==============================")
    print("Evaluating HYBRID")
    print("==============================")

    hybrid_correct = 0

    hybrid_latencies = []

    for sample in dataset:

        question = sample["question"]

        target_source = sample["source"]

        start = time.time()

        # =========================
        # HYBRID RETRIEVAL
        # =========================
        #
        # BM25 + Vector
        # → RRF fusion

        retrieved_docs = ensemble_retriever.invoke(
            question
        )

        latency = time.time() - start

        hybrid_latencies.append(latency)

        found = False

        for doc in retrieved_docs[:5]:

            source = doc.metadata.get(
                "source",
                ""
            )

            if target_source in source:

                found = True
                break

        if found:
            hybrid_correct += 1

    hybrid_recall = hybrid_correct / len(dataset)

    hybrid_p50 = statistics.median(
        hybrid_latencies
    )

    # =====================================================
    # 3. HYBRID + RERANK EVALUATION
    # =====================================================

    print("\n==============================")
    print("Evaluating HYBRID + RERANK")
    print("==============================")

    rerank_correct = 0

    rerank_latencies = []

    for sample in dataset:

        question = sample["question"]

        target_source = sample["source"]

        start = time.time()

        # =========================
        # HYBRID RETRIEVAL
        # =========================

        retrieved_docs = ensemble_retriever.invoke(
            question
        )

        # =========================
        # RERANKING
        # =========================
        #
        # Cross-encoder reranker
        #
        # top-30
        #   ↓
        # top-5

        reranked_docs = rerank(
            question,
            retrieved_docs,
            top_k=5
        )

        latency = time.time() - start

        rerank_latencies.append(latency)

        found = False

        for doc in reranked_docs:

            source = doc.metadata.get(
                "source",
                ""
            )

            if target_source in source:

                found = True
                break

        if found:
            rerank_correct += 1

    rerank_recall = rerank_correct / len(dataset)

    rerank_p50 = statistics.median(
        rerank_latencies
    )

    # =====================================================
    # FINAL RESULTS
    # =====================================================

    print("\n")
    print("=================================================")
    print("FINAL EVALUATION RESULTS")
    print("=================================================")

    print(
        f"{'Pipeline':<25}"
        f"{'Recall@5':<15}"
        f"{'p50 Latency (s)':<20}"
    )

    print("-" * 60)

    print(
        f"{'Vector Only':<25}"
        f"{vector_recall:<15.2f}"
        f"{vector_p50:<20.2f}"
    )

    print(
        f"{'Hybrid':<25}"
        f"{hybrid_recall:<15.2f}"
        f"{hybrid_p50:<20.2f}"
    )

    print(
        f"{'Hybrid + Rerank':<25}"
        f"{rerank_recall:<15.2f}"
        f"{rerank_p50:<20.2f}"
    )

    print("\n✅ Evaluation complete!")


if __name__ == "__main__":

    run_evaluation()