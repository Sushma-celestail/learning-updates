# Convert raw documents → chunks →unique ids-> store in:
#   1. Vector DB (semantic search)
#   2. BM25 index (lexical search)

import glob
from dotenv import load_dotenv

from src.loaders import (
    load_pdf,
    load_fastapi_docs
)

from src.splitter import split_docs
from src.vectordb import create_vectorstore
from src.utils import generate_id

load_dotenv()


def ingest_documents():

    print(" Loading documents from sources...")

    all_docs = []

    # STEP 1: LOAD PDF DOCUMENTS
    pdf_files = glob.glob("data/pdfs/*.pdf")

    for pdf_file in pdf_files:
        docs = load_pdf(pdf_file)

        for doc in docs:
            doc.metadata["source"] = pdf_file
            doc.metadata["source_type"] = "pdf"

        all_docs.extend(docs)

    # STEP 2: LOAD HTML / FASTAPI DOCS
    html_docs = load_fastapi_docs()

    for doc in html_docs:
        doc.metadata["source_type"] = "html"

    all_docs.extend(html_docs)

    # STEP 3: VALIDATION CHECK
    if not all_docs:
        print(" No documents found.")
        return

    print(f" Loaded {len(all_docs)} documents")

    # STEP 4: CHUNKING
    chunks = split_docs(all_docs)

    print(f" Created {len(chunks)} chunks")

    # STEP 5: CREATE UNIQUE IDS
    ids = []

    for i, chunk in enumerate(chunks):
        unique_text = (
            chunk.page_content +
            str(chunk.metadata) +
            str(i)
        )

        chunk_id = generate_id(unique_text)
        ids.append(chunk_id)

    print(" Generated unique IDs")

    # STEP 6: INIT VECTOR DB
    vectordb = create_vectorstore()

    # STEP 7: BATCH INSERT INTO CHROMA
    BATCH_SIZE = 200  # optimal for stability + embeddings

    print(f" Starting ingestion in batches of {BATCH_SIZE}...")

    total_batches = (len(chunks) + BATCH_SIZE - 1) // BATCH_SIZE

    for i in range(0, len(chunks), BATCH_SIZE):

        batch_chunks = chunks[i:i + BATCH_SIZE]
        batch_ids = ids[i:i + BATCH_SIZE]

        batch_num = (i // BATCH_SIZE) + 1

        print(f" Batch {batch_num}/{total_batches} | size={len(batch_chunks)}")

        try:
            vectordb.add_documents(
                batch_chunks,
                ids=batch_ids
            )

        except Exception as e:
            print(f" Error in batch {batch_num}: {e}")

    print(" Ingestion complete!")


if __name__ == "__main__":
    ingest_documents()