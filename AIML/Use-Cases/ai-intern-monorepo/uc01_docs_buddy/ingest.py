"""
UC01 — Docs Buddy: Ingestion pipeline.

Run:
    python uc01_docs_buddy/ingest.py

Steps:
    1. Fetch FastAPI docs pages via SitemapLoader
    2. Clean whitespace
    3. Chunk text (chunk_size=800, overlap=100)
    4. Generate stable SHA-256 IDs  →  idempotent re-runs (no duplicates)
    5. Embed with Gemini embedding-001 in batches of 50
    6. Store in ChromaDB at uc01_docs_buddy/data/chroma/

Note: The free Gemini tier allows ~1 000 embedding requests/day.
      The script pauses 65 s between batches and retries once on 429.
"""

import hashlib
import os
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("USER_AGENT", "uc01-docs-buddy-ingest/1.0")

from langchain_community.document_loaders import SitemapLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from shared.config.settings import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    UC01_CHROMA_DIR,
    UC01_COLLECTION,
    UC01_MAX_PAGES,
    UC01_MIN_PAGES,
    UC01_SITEMAP_URL,
    UC01_URL_PREFIX,
)
from shared.vectorstore.chroma import get_vectorstore


def _check_api_key() -> None:
    """Abort early if GOOGLE_API_KEY is missing."""
    if not os.getenv("GOOGLE_API_KEY"):
        raise EnvironmentError(
            "GOOGLE_API_KEY is not set. "
            "Get a free key at https://aistudio.google.com/app/apikey "
            "and add it to .env"
        )


def _load_docs():
    """Download FastAPI docs pages from the sitemap."""
    print(f"Loading sitemap: {UC01_SITEMAP_URL}")

    loader = SitemapLoader(
        web_path=UC01_SITEMAP_URL,
        filter_urls=[UC01_URL_PREFIX],
    )
    docs = loader.load()

    # Drop empty pages, then cap at MAX_PAGES
    docs = [d for d in docs if d.page_content.strip()]
    docs = docs[:UC01_MAX_PAGES]

    if len(docs) < UC01_MIN_PAGES:
        raise ValueError(
            f"Only {len(docs)} pages loaded; need at least {UC01_MIN_PAGES}."
        )

    print(f"Pages loaded: {len(docs)}")
    return docs


def _clean_docs(docs):
    """Collapse all whitespace in every document."""
    for doc in docs:
        doc.page_content = " ".join(doc.page_content.split())
    return docs


def _split_docs(docs):
    """Split documents into overlapping chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(docs)
    print(f"Chunks created: {len(chunks)}")
    return chunks


def _make_id(index: int, source: str, text: str) -> str:
    """
    Generate a stable SHA-256 ID for a chunk.
    Same content always produces the same ID — guarantees idempotency.
    """
    raw = f"{index}|{source}|{text}"
    return hashlib.sha256(raw.encode()).hexdigest()


def ingest() -> None:
    """Run the full UC01 ingestion pipeline."""
    _check_api_key()

    docs   = _load_docs()
    docs   = _clean_docs(docs)
    chunks = _split_docs(docs)

    # Stable IDs for every chunk
    ids = [
        _make_id(i, c.metadata.get("source", ""), c.page_content)
        for i, c in enumerate(chunks)
    ]

    # Open the vector store
    vs = get_vectorstore(UC01_CHROMA_DIR, UC01_COLLECTION)

    # Skip chunks that are already stored (idempotency)
    existing_ids = set(vs.get()["ids"])
    new_chunks   = [c for c, i in zip(chunks, ids) if i not in existing_ids]
    new_ids      = [i for i in ids if i not in existing_ids]

    if not new_chunks:
        print("✅ ChromaDB is already up to date. Nothing to embed.")
        return

    # Embed in batches of 50 with rate-limit handling
    batch_size    = 50
    total_batches = (len(new_chunks) + batch_size - 1) // batch_size
    print(f"Embedding {len(new_chunks)} chunks in {total_batches} batches …")

    for b in range(total_batches):
        s        = b * batch_size
        e        = min(s + batch_size, len(new_chunks))
        b_chunks = new_chunks[s:e]
        b_ids    = new_ids[s:e]

        try:
            vs.add_documents(b_chunks, ids=b_ids)
            print(f"  Batch {b + 1}/{total_batches} done ✅")
        except Exception as exc:
            if "RESOURCE_EXHAUSTED" in str(exc) or "429" in str(exc):
                print("  Rate limit hit — waiting 70 s then retrying …")
                time.sleep(70)
                vs.add_documents(b_chunks, ids=b_ids)
                print(f"  Batch {b + 1} retry succeeded ✅")
            else:
                raise

        # Pause between batches to stay within the free-tier quota
        if b < total_batches - 1:
            print("  Pausing 65 s (free-tier rate limit) …")
            time.sleep(65)

    print(f"✅ Ingestion complete — {len(new_chunks)} chunks stored.")


if __name__ == "__main__":
    ingest()
