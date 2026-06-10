"""
UC02 — Hybrid Search RAG: Ingestion pipeline.

Run:
    python uc02_hybrid_search/ingest.py

Drop source files into:  uc02_hybrid_search/data/raw/
Supported:  .pdf   .html   .htm

What it does:
    1. Load PDFs  → PyPDFLoader   → source_type = "pdf"
    2. Load HTML  → BSHTMLLoader  → source_type = "html"
    3. Clean whitespace
    4. Chunk  (chunk_size=800, overlap=100)
    5. SHA-256 IDs  →  idempotent re-runs (no duplicates)
    6. Embed with Gemini  →  store in ChromaDB
    7. Pickle all chunks  →  bm25_docs.pkl  (BM25 index corpus)

Rate limit note:
    Free Gemini tier: ~1 500 embed requests/day.
    Script pauses 65 s between batches of 50 and retries once on 429.
"""

import hashlib
import os
import pickle
import re
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("USER_AGENT", "uc02-hybrid-ingest/1.0")

from langchain_community.document_loaders import BSHTMLLoader, PyPDFLoader
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

# BM25 corpus pickle — read by retriever.py at query time
DOCS_PICKLE = UC02_DATA_DIR.parent / "bm25_docs.pkl"


# ---------------------------------------------------------------------------
# Document loaders
# ---------------------------------------------------------------------------

def _load_pdfs(data_dir: Path) -> list:
    """Load all PDFs, tag each page with source_type='pdf'."""
    docs      = []
    pdf_files = list(data_dir.glob("**/*.pdf"))
    print(f"  PDF files  : {len(pdf_files)}")
    for path in pdf_files:
        try:
            pages = PyPDFLoader(str(path)).load()
            for p in pages:
                p.metadata["source_type"] = "pdf"
                p.metadata["file_name"]   = path.name
            docs.extend(pages)
        except Exception as exc:
            print(f"  Skipping {path.name}: {exc}")
    return docs


def _load_html(data_dir: Path) -> list:
    """Load all HTML files, tag each with source_type='html'."""
    docs       = []
    html_files = (list(data_dir.glob("**/*.html")) +
                  list(data_dir.glob("**/*.htm")))
    print(f"  HTML files : {len(html_files)}")
    for path in html_files:
        try:
            pages = BSHTMLLoader(str(path), open_encoding="utf-8").load()
            for p in pages:
                p.metadata["source_type"] = "html"
                p.metadata["file_name"]   = path.name
            docs.extend(pages)
        except Exception as exc:
            print(f"  Skipping {path.name}: {exc}")
    return docs


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def ingest() -> None:
    """Run the full UC02 ingestion pipeline."""
    if not os.getenv("GOOGLE_API_KEY"):
        raise EnvironmentError(
            "GOOGLE_API_KEY is not set.\n"
            "Add it to .env — get a free key at https://aistudio.google.com/app/apikey"
        )

    UC02_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # ── Step 1 & 2: Load documents ──────────────────────────────────────────
    print(f"\nLoading documents from: {UC02_DATA_DIR}")
    docs = _load_pdfs(UC02_DATA_DIR) + _load_html(UC02_DATA_DIR)

    if not docs:
        print(
            f"\n⚠️  No PDF or HTML files found in {UC02_DATA_DIR}\n"
            "    Run: python uc02_hybrid_search/download_sample_data.py\n"
            "    Or drop your own files there and re-run."
        )
        return

    print(f"  Total docs : {len(docs)}")

    # ── Step 3: Clean whitespace ─────────────────────────────────────────────
    for doc in docs:
        doc.page_content = " ".join(doc.page_content.split())

    # ── Step 4: Chunk ────────────────────────────────────────────────────────
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(docs)
    print(f"  Chunks     : {len(chunks)}")

    # ── Step 5: Stable SHA-256 IDs ───────────────────────────────────────────
    ids = [
        hashlib.sha256(
            f"{i}|{c.metadata.get('source', c.metadata.get('file_name', ''))}|{c.page_content}".encode()
        ).hexdigest()
        for i, c in enumerate(chunks)
    ]

    # ── Step 6: Embed → ChromaDB ─────────────────────────────────────────────
    print(f"\nEmbedding model : {EMBEDDING_MODEL}")
    vs           = get_vectorstore(UC02_CHROMA_DIR, UC02_COLLECTION)
    existing_ids = set(vs.get()["ids"])
    new_chunks   = [c for c, i in zip(chunks, ids) if i not in existing_ids]
    new_ids      = [i for i in ids if i not in existing_ids]

    print(f"Already stored  : {len(existing_ids)}")
    print(f"To embed        : {len(new_chunks)}")

    if new_chunks:
        batch_size    = 50
        total_batches = (len(new_chunks) + batch_size - 1) // batch_size
        print(f"\nEmbedding {len(new_chunks)} chunks in {total_batches} batches …")

        for b in range(total_batches):
            s = b * batch_size
            e = min(s + batch_size, len(new_chunks))
            print(f"  Batch {b+1:2d}/{total_batches} (chunks {s+1}–{e}) …", end=" ", flush=True)

            # Retry loop — handles both per-minute and daily quota errors
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    vs.add_documents(new_chunks[s:e], ids=new_ids[s:e])
                    print("✅")
                    break
                except Exception as exc:
                    err = str(exc)
                    if "429" in err or "RESOURCE_EXHAUSTED" in err:
                        # Parse retry delay from error message if available
                        import re
                        match = re.search(r'retry in (\d+)', err)
                        wait  = int(match.group(1)) + 5 if match else 70
                        if attempt < max_retries - 1:
                            print(f"⚠️  rate limit — waiting {wait}s (attempt {attempt+1}/{max_retries}) …")
                            time.sleep(wait)
                        else:
                            print(f"\n❌ Daily quota exhausted after {attempt+1} attempts.")
                            print(f"   Already stored: {s} chunks.")
                            print(f"   Remaining     : {len(new_chunks) - s} chunks.")
                            print(f"   Re-run tomorrow — already-stored chunks will be skipped.")
                            # Still save BM25 corpus with what we have
                            with open(DOCS_PICKLE, "wb") as f:
                                pickle.dump(chunks, f)
                            print(f"\nBM25 corpus saved with all {len(chunks)} chunks.")
                            return
                    else:
                        print(f"\n❌ Unexpected error: {err[:120]}")
                        raise

            if b < total_batches - 1:
                print(f"  Pausing 65 s …", end="\r", flush=True)
                time.sleep(65)
    else:
        print("✅ ChromaDB already up to date.")

    # ── Step 7: Save BM25 corpus ─────────────────────────────────────────────
    with open(DOCS_PICKLE, "wb") as f:
        pickle.dump(chunks, f)
    print(f"\nBM25 corpus     : {DOCS_PICKLE} ({len(chunks)} docs)")
    print(f"\n✅ UC02 ingestion complete — {len(chunks)} total chunks.")


if __name__ == "__main__":
    ingest()
