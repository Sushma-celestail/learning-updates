# RETRIEVER MODULE
# Goal:
# Build 2 retrieval systems:
#   1. BM25 → keyword search (lexical)
#   2. Vector DB → semantic search
# Then combine using Ensemble (RRF)

from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers.ensemble import EnsembleRetriever

# BM25 RETRIEVER
# INTERNAL FLOW:
# 1. Tokenize documents
# 2. Build inverted index
# 3. Compute TF, IDF, document length
# 4. Rank documents for query

def create_bm25(docs):

    bm25 = BM25Retriever.from_documents(docs)

    # number of documents returned
    bm25.k = 10

    return bm25


# ENSEMBLE RETRIEVER
# COMBINES:
#   BM25 (keyword matching)
#   Vector search (semantic similarity)
#
# FINAL STEP:
# → Reciprocal Rank Fusion (RRF)
# → merges rankings from both systems

def create_ensemble_retriever(
    bm25_retriever,
    vector_retriever
):

    ensemble = EnsembleRetriever(
        retrievers=[
            bm25_retriever,
            vector_retriever
        ],
        weights=[0.5, 0.5]   # equal importance
    )

    return ensemble