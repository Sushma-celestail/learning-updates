"""
UC02 — Bootstrap from UC01 data (no new embedding API calls needed).

Run this INSTEAD of ingest.py when the embedding API is unavailable
or you want to reuse the 1700 chunks already embedded in UC01.

What it does:
    1. Copies UC01's ChromaDB into UC02's chroma directory
    2. Loads all documents from UC01's vector store
    3. Builds the BM25 corpus pickle from those documents
    4. UC02 is then fully ready: hybrid retrieval + reranking works

Run:
    python uc02_hybrid_search/setup_from_uc01.py
"""

import pickle
import shutil
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from shared.config.settings import (
    UC01_CHROMA_DIR,
    UC01_COLLECTION,
    UC02_CHROMA_DIR,
    UC02_COLLECTION,
)
from shared.vectorstore.chroma import get_vectorstore

# Where BM25 corpus pickle is saved
DOCS_PICKLE = Path(__file__).parent / "data" / "bm25_docs.pkl"


def copy_chroma() -> None:
    """Copy UC01 ChromaDB files into UC02 chroma directory."""
    print(f"Source : {UC01_CHROMA_DIR}")
    print(f"Target : {UC02_CHROMA_DIR}")

    if UC02_CHROMA_DIR.exists():
        shutil.rmtree(UC02_CHROMA_DIR)

    shutil.copytree(UC01_CHROMA_DIR, UC02_CHROMA_DIR)
    print(f"ChromaDB copied ✅")

    # Rename the collection inside the SQLite DB from UC01 name to UC02 name
    db_path = UC02_CHROMA_DIR / "chroma.sqlite3"
    conn    = sqlite3.connect(str(db_path))
    conn.execute(
        "UPDATE collections SET name = ? WHERE name = ?",
        (UC02_COLLECTION, UC01_COLLECTION),
    )
    conn.commit()

    # Verify
    count = conn.execute("SELECT COUNT(*) FROM embeddings").fetchone()[0]
    name  = conn.execute("SELECT name FROM collections").fetchone()[0]
    conn.close()

    print(f"Collection renamed to: {name}")
    print(f"Embeddings in store  : {count}")


def build_bm25_corpus() -> None:
    """Load all documents from the copied ChromaDB and save as BM25 pickle."""
    print("\nBuilding BM25 corpus from ChromaDB documents …")

    vs     = get_vectorstore(UC02_CHROMA_DIR, UC02_COLLECTION)
    result = vs.get(include=["documents", "metadatas"])

    # Reconstruct Document objects
    from langchain_core.documents import Document
    docs = [
        Document(page_content=text, metadata=meta)
        for text, meta in zip(result["documents"], result["metadatas"])
    ]

    # Tag every document with source_type = "html" (they came from FastAPI HTML pages)
    for doc in docs:
        if "source_type" not in doc.metadata:
            doc.metadata["source_type"] = "html"

    DOCS_PICKLE.parent.mkdir(parents=True, exist_ok=True)
    with open(DOCS_PICKLE, "wb") as f:
        pickle.dump(docs, f)

    print(f"BM25 corpus saved : {DOCS_PICKLE}")
    print(f"Documents in corpus: {len(docs)}")


def main() -> None:
    print("=" * 60)
    print("UC02 — Bootstrap from UC01 data")
    print("=" * 60)

    # Step 1 — copy ChromaDB
    copy_chroma()

    # Step 2 — build BM25 corpus
    build_bm25_corpus()

    print("\n" + "=" * 60)
    print("✅ UC02 is ready!")
    print("   ChromaDB : uc02_hybrid_search/data/chroma/")
    print("   BM25     : uc02_hybrid_search/data/bm25_docs.pkl")
    print("\nNext steps:")
    print("  Test a query:")
    print("    python -c \"import sys; sys.path.insert(0,'.');"
          " from uc02_hybrid_search.chain import answer_question;"
          " print(answer_question('What is FastAPI?'))\"")
    print("\n  Run evaluation:")
    print("    python uc02_hybrid_search/eval/eval_recall.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
