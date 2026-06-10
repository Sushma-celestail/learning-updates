"""Ingest FastAPI documentation pages into ChromaDB vector store."""
# This script downloads documentation pages, splits them into chunks,
# embeds them using Gemini, and stores them in a persistent ChromaDB collection

import hashlib  # For creating stable, unique IDs for document chunks
import os       # For reading environment variables and setting user agent
import sys      # For adding project root to Python import path
import time     # For adding delays between API calls to respect rate limits
from pathlib import Path  # For cross-platform file path operations

# Set a polite user agent for web scraping before importing web loaders
os.environ.setdefault("USER_AGENT", "docs-buddy-rag-demo")

from langchain_community.document_loaders import SitemapLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from shared.config.settings import (
    CHROMA_DIR, CHUNK_OVERLAP, CHUNK_SIZE, DOCS_SITEMAP_URL,
    DOCS_URL_PREFIX, MAX_PAGES, MIN_PAGES, QUICK_TEST_MODE, TEST_PAGES,
)
from shared.vectorstore.chroma import get_vectorstore
from shared.logger import get_logger   # ← shared logger

log = get_logger("ingest")   # All ingest log lines show "ingest" as source


def check_api_key():
    """Verify that GOOGLE_API_KEY exists before ingestion starts."""
    if not os.getenv("GOOGLE_API_KEY"):
        log.error("[INGEST] GOOGLE_API_KEY is not set — aborting")

        raise ValueError(
            "Please set GOOGLE_API_KEY before running ingest.py."
        )

    log.info("[INGEST] STEP 1 — API key verified ✅")


def load_docs():
    """
    Download FastAPI documentation pages from the sitemap.
    Returns raw documents.
    """
    log.info(
        "[INGEST] STEP 2 — Loading docs from sitemap: %s",
        DOCS_SITEMAP_URL
    )

    loader = SitemapLoader(
        web_path=DOCS_SITEMAP_URL,
        filter_urls=[DOCS_URL_PREFIX]
    )

    docs = loader.load()

    log.info(
        "[INGEST] STEP 2 — Raw pages fetched: %d",
        len(docs)
    )

    # Remove empty pages
    docs = [
        doc
        for doc in docs
        if doc.page_content.strip()
    ]

    log.info(
        "[INGEST] STEP 2 — Non-empty pages: %d",
        len(docs)
    )

    # Keep only first MAX_PAGES pages
    docs = docs[:MAX_PAGES]

    if len(docs) < MIN_PAGES:
        raise ValueError(
            f"Only loaded {len(docs)} pages; "
            f"expected at least {MIN_PAGES}."
        )

    log.info(
        "[INGEST] STEP 2 — Pages loaded: %d ✅",
        len(docs)
    )

    return docs


def clean_text(text):
    """
    Normalize whitespace.

    Example:
        FastAPI

        is     great

    becomes:
        FastAPI is great
    """
    return " ".join(text.split())


def clean_docs(docs):
    """
    Clean text content of all documents.
    """
    log.info("[INGEST] STEP 3 — Cleaning document text")

    for doc in docs:
        doc.page_content = clean_text(
            doc.page_content
        )

    log.info(
        "[INGEST] STEP 3 — Cleaned %d documents ✅",
        len(docs)
    )

    return docs


def split_docs(docs):
    """
    Split documents into overlapping chunks.
    """
    log.info(
        "[INGEST] STEP 4 — Splitting docs "
        "| chunk_size=%d overlap=%d",
        CHUNK_SIZE,
        CHUNK_OVERLAP
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    chunks = splitter.split_documents(docs)

    log.info(
        "[INGEST] STEP 4 — Chunks created: %d ✅",
        len(chunks)
    )

    return chunks


def make_id(index, source, text):
    """
    Generate a stable SHA256 ID for a chunk.
    """
    raw_text = f"{index}|{source}|{text}"

    return hashlib.sha256(
        raw_text.encode("utf-8")
    ).hexdigest()

def ingest_with_rate_limiting():
    """Main ingestion workflow with rate limiting for free tier API usage."""
    log.info("=" * 70)
    log.info("[INGEST] INGESTION PIPELINE STARTED")
    log.info("=" * 70)
    t_total = time.perf_counter()

    check_api_key()
    docs   = load_docs()
    chunks = split_docs(docs)

    log.info("[INGEST] STEP 4 — Generating stable IDs for %d chunks", len(chunks))
    ids = [
        make_id(i, chunk.metadata.get("source", ""), chunk.page_content)
        for i, chunk in enumerate(chunks)
    ]
    log.info("[INGEST] STEP 4 — IDs generated ✅")

    log.info("[INGEST] STEP 5 — Opening ChromaDB vector store at: %s", CHROMA_DIR)
    vectorstore = get_vectorstore()
    log.info("[INGEST] STEP 5 — Vector store ready ✅")

    batch_size    = 50
    # --- Skip chunks already stored so new API key only embeds what's missing ---
    log.info("[INGEST] STEP 6 — Checking which chunks are already in ChromaDB...")
    existing_ids = set(vectorstore.get()["ids"])   # IDs currently in the collection
    new_chunks   = [c for c, i in zip(chunks, ids) if i not in existing_ids]
    new_ids      = [i for i in ids if i not in existing_ids]

    log.info(
        "[INGEST] STEP 6 — Already stored: %d | Still to embed: %d",
        len(existing_ids), len(new_chunks)
    )

    if not new_chunks:
        log.info("[INGEST] STEP 6 — All chunks already stored. Nothing to do ✅")
        print("✅ All chunks already stored in ChromaDB. Nothing to embed.")
        return

    # Work only with the chunks that still need embedding
    chunks        = new_chunks
    ids           = new_ids
    total_batches = (len(chunks) + batch_size - 1) // batch_size

    print(f"▶ Resuming ingestion — {len(chunks)} chunks remaining across {total_batches} batches")
    log.info(
        "[INGEST] STEP 6 — Embedding %d new chunks in %d batches of %d",
        len(chunks), total_batches, batch_size
    )

    for batch_num in range(total_batches):
        start_idx    = batch_num * batch_size
        end_idx      = min(start_idx + batch_size, len(chunks))
        batch_chunks = chunks[start_idx:end_idx]
        batch_ids    = ids[start_idx:end_idx]

        log.info(
            "[INGEST] STEP 6 — Batch %d/%d | chunks %d-%d",
            batch_num + 1, total_batches, start_idx + 1, end_idx
        )
        t_batch = time.perf_counter()

        try:
            vectorstore.add_documents(batch_chunks, ids=batch_ids)
            log.info(
                "[INGEST] STEP 6 — Batch %d/%d completed ✅ (%.2fs)",
                batch_num + 1, total_batches, time.perf_counter() - t_batch
            )

            if batch_num < total_batches - 1:
                log.info("[INGEST] STEP 6 — Rate-limit pause: 65 seconds...")
                time.sleep(65)

        except Exception as e:
            if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
                log.warning(
                    "[INGEST] STEP 6 — Rate limit hit on batch %d — waiting 70s then retrying",
                    batch_num + 1
                )
                time.sleep(70)
                try:
                    vectorstore.add_documents(batch_chunks, ids=batch_ids)
                    log.info("[INGEST] STEP 6 — Batch %d retry succeeded ✅", batch_num + 1)
                except Exception as retry_err:
                    log.error(
                        "[INGEST] STEP 6 — Batch %d retry FAILED: %s",
                        batch_num + 1, retry_err
                    )
                    log.error("[INGEST] Daily quota likely exhausted — resume tomorrow")
                    return
            else:
                log.error("[INGEST] STEP 6 — Unexpected error on batch %d: %s", batch_num + 1, e)
                return

    elapsed = time.perf_counter() - t_total
    log.info("=" * 70)
    log.info("[INGEST] INGESTION COMPLETE ✅")
    log.info("[INGEST] Pages: %d | Chunks: %d | Time: %.1fs", len(docs), len(chunks), elapsed)
    log.info("[INGEST] Vector store saved to: %s", CHROMA_DIR)
    log.info("=" * 70)


def ingest():
    """Entry point — calls the rate-limited ingestion workflow."""
    ingest_with_rate_limiting()


# Run ingestion when this script is executed directly
if __name__ == "__main__":
    log.info("Docs Buddy — ingest.py started")
    ingest()