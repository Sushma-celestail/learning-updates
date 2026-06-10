"""
=========================================================
QUERY FLOW IN HYBRID RAG SYSTEM
=========================================================

1. USER QUERY
      ↓
---------------------------------------------------------
BM25 PATH (LEXICAL SEARCH 🔍)
---------------------------------------------------------
- tokenize query
- build inverted index lookup
- compute TF-IDF style scoring
- rank documents by keyword match

---------------------------------------------------------
VECTOR PATH (SEMANTIC SEARCH 🧠)
---------------------------------------------------------
- convert query → embedding vector
- cosine similarity with stored embeddings
- rank by semantic similarity

---------------------------------------------------------
ENSEMBLE FUSION (RRF ⚖️)
---------------------------------------------------------
- combine BM25 rank + Vector rank
- Reciprocal Rank Fusion formula:
      score = 1 / (rank + k)
- final unified ranking

---------------------------------------------------------
OUTPUT
---------------------------------------------------------
- top relevant documents returned
=========================================================
"""

# =========================
# IMPORTS
# =========================

from src.vectordb import create_vectorstore
from src.retriever import (
    create_bm25,
    create_ensemble_retriever
)

from langchain_core.documents import Document


# =========================
# LOAD VECTOR DATABASE (CHROMA)
# =========================
# Chroma loads:
# - stored document text
# - embeddings
# - metadata
# from disk

vectordb = create_vectorstore()


# =========================
# VECTOR RETRIEVER (SEMANTIC SEARCH)
# =========================
# Step:
# query → embedding → cosine similarity → top-k results

vector_retriever = vectordb.as_retriever(
    search_kwargs={"k": 10}   # top 10 semantic matches
)


# =========================
# LOAD RAW DOCUMENTS FROM VECTOR DB
# =========================
# BM25 cannot use embeddings
# It needs raw text → so we extract documents

data = vectordb.get()

documents = data["documents"]
metadatas = data["metadatas"]


# =========================
# REBUILD DOCUMENT OBJECTS
# =========================
# Convert raw text back into LangChain Document format

docs = []

for text, meta in zip(documents, metadatas):
    docs.append(
        Document(
            page_content=text,
            metadata=meta
        )
    )


# =========================
# BM25 RETRIEVER (LEXICAL SEARCH ENGINE)
# =========================
"""
BM25 INTERNAL FLOW:

1. Tokenization
   "fastapi middleware" → ["fastapi", "middleware"]

2. Inverted Index Lookup
   fastapi → [Doc1, Doc7, Doc20]
   middleware → [Doc1, Doc3]

3. TF (Term Frequency)
   how many times word appears in doc

4. IDF (Inverse Document Frequency)
   how rare the word is across corpus

5. Document Length Normalization
   avoids bias toward long docs

6. Final Ranking Score computed
"""

bm25_retriever = create_bm25(docs)


# =========================
# ENSEMBLE RETRIEVER (HYBRID SEARCH)
# =========================
"""
WHY ENSEMBLE?

Because:
- BM25 = exact keyword matching 🔍
- Vector = meaning matching 🧠

We combine both using RRF (Reciprocal Rank Fusion)

RRF FORMULA:
    score = 1 / (rank + k)

So:
- rank 1 doc contributes more
- rank 10 contributes less
"""

ensemble_retriever = create_ensemble_retriever(
    bm25_retriever,
    vector_retriever
)


# =========================
# QUERY
# =========================

query = "How to intercept requests in FastAPI?"


# =========================
# HYBRID RETRIEVAL EXECUTION
# =========================
# Step flow:
# 1. BM25 retrieves keyword-based docs
# 2. Vector retriever finds semantic matches
# 3. Ensemble merges both rankings
# 4. Final ranked docs returned

docs = ensemble_retriever.invoke(query)


# =========================
# RESULTS
# =========================

print("\n===== HYBRID RESULTS =====\n")

for i, doc in enumerate(docs[:5]):
    print(f"\n--- DOCUMENT {i+1} ---\n")
    print(doc.page_content[:500])