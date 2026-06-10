"""
UC02 — Embedding-only script.

Loads the 60 HTML files from data/raw/, chunks them, and embeds
them into ChromaDB using the current Gemini embedding model.
Also saves the BM25 corpus pickle.

Run:
    python uc02_hybrid_search/embed_only.py

This is safe to re-run — already-stored chunks are skipped.
The free Gemini tier allows ~1500 embed requests/day.
Each batch of 50 chunks = 1 request. 1386 chunks = 28 batches.
Total time: ~35 minutes (65s pause between batches).
"""

import hashlib
import os
import pickle
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("USER_AGENT", "uc02-embed-only/1.0")

from langchain_community.document_loaders import BSHTMLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from shared.config.settings import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    EMBEDDING_MODEL,
    UC02_CHROMA_DIR,
    UC02_COLLECTION,
    UC02_DATA_DIR,
)
from shared.vectorstore.chroma import get_vectorstore

DOCS_PICKLE = Path(__file__).parent / "data" / "bm25_docs.pkl"
BATCH_SIZE  = 50
PAUSE_SECS  = 65   # free-tier rate limit pause between batches


def load_html_files() -> list:
    """Load all HTML files from data/raw/."""
    html_files = list(UC02_DATA_DIR.glob("**/*.html")) + \
                 list(UC02_DATA_DIR.glob("**/*.htm"))

    if not html_files:
        raise FileNotFoundError(
            f"No HTML files found in {UC02_DATA_DIR}\n"
            "Run: python uc02_hybrid_search/download_sample_data.py"
        )

    print(f"Found {len(html_files)} HTML files")
    docs = []
    for path in html_files:
        try:
            pages = BSHTMLLoader(str(path), open_encoding="utf-8").load()
            for page in pages:
                page.metadata["source_type"] = "html"
                page.metadata["file_name"]   = path.name
            docs.extend(pages)
        except Exception as exc:
            print(f"  Skipping {path.name}: {exc}")

    print(f"Documents loaded: {len(docs)}")
    return docs


def chunk_docs(docs) -> list:
    """Split documents into overlapping chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(docs)
    print(f"Chunks created  : {len(chunks)}")
    return chunks


def make_id(i: int, source: str, text: str) -> str:
    """Stable SHA-256 ID — same content always gives the same ID."""
    return hashlib.sha256(f"{i}|{source}|{text}".encode()).hexdigest()


def embed_and_store(chunks: list) -> None:
    """Embed chunks and store in ChromaDB, skipping already-stored ones."""
    ids = [
        make_id(i, c.metadata.get("source", c.metadata.get("file_name", "")),
                c.page_content)
        for i, c in enumerate(chunks)
    ]

    vs           = get_vectorstore(UC02_CHROMA_DIR, UC02_COLLECTION)
    existing_ids = set(vs.get()["ids"])
    new_chunks   = [c for c, i in zip(chunks, ids) if i not in existing_ids]
    new_ids      = [i for i in ids if i not in existing_ids]

    print(f"Already stored  : {len(existing_ids)}")
    print(f"To embed        : {len(new_chunks)}")

    if not new_chunks:
        print("✅ Nothing new to embed — ChromaDB is up to date.")
        return

    total_batches = (len(new_chunks) + BATCH_SIZE - 1) // BATCH_SIZE
    print(f"\nEmbedding {len(new_chunks)} chunks in {total_batches} batches")
    print(f"Model: {EMBEDDING_MODEL}")
    print(f"Estimated time: ~{total_batches * (PAUSE_SECS + 5) // 60} minutes\n")

    for b in range(total_batches):
        s = b * BATCH_SIZE
        e = min(s + BATCH_SIZE, len(new_chunks))

        print(f"  Batch {b+1:2d}/{total_batches} | chunks {s+1}–{e} ...", end=" ", flush=True)
        t0 = time.perf_counter()

        try:
            vs.add_documents(new_chunks[s:e], ids=new_ids[s:e])
            print(f"✅ ({time.perf_counter()-t0:.1f}s)")
        except Exception as exc:
            err = str(exc)
            if "RESOURCE_EXHAUSTED" in err or "429" in err:
                print(f"⚠️  Rate limit — waiting 70s ...")
                time.sleep(70)
                vs.add_documents(new_chunks[s:e], ids=new_ids[s:e])
                print(f"  Retry ✅")
            else:
                print(f"❌ ERROR: {err[:100]}")
                raise

        if b < total_batches - 1:
            print(f"  Pausing {PAUSE_SECS}s ...", end="\r", flush=True)
            time.sleep(PAUSE_SECS)

    print(f"\n✅ Embedding complete — {len(new_chunks)} chunks stored.")


def save_bm25_corpus(chunks: list) -> None:
    """Save all chunks as a pickle file for the BM25 index."""
    DOCS_PICKLE.parent.mkdir(parents=True, exist_ok=True)
    with open(DOCS_PICKLE, "wb") as f:
        pickle.dump(chunks, f)
    print(f"✅ BM25 corpus saved: {DOCS_PICKLE} ({len(chunks)} docs)")


def main() -> None:
    if not os.getenv("GOOGLE_API_KEY"):
        raise EnvironmentError(
            "GOOGLE_API_KEY is not set. "
            "Add it to .env"
        )

    print("=" * 55)
    print("UC02 — Embedding Pipeline")
    print(f"Model : {EMBEDDING_MODEL}")
    print("=" * 55)

    docs   = load_html_files()
    chunks = chunk_docs(docs)

    # Clean whitespace
    for c in chunks:
        c.page_content = " ".join(c.page_content.split())

    embed_and_store(chunks)
    save_bm25_corpus(chunks)

    print("\n" + "=" * 55)
    print("✅ UC02 is ready!")
    print("   Test: python uc02_hybrid_search/embed_only.py --test")
    print("=" * 55)


if __name__ == "__main__":
    main()
