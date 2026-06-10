# Acceptance Criteria Mapping

1. `python ingest.py` ingests at least 50 pages. The default is 80 pages from the FastAPI sitemap, capped between 50 and 200.
2. ChromaDB persists to `chroma_db/` with collection name `fastapi_docs`.
3. Reruns are idempotent because each chunk ID is a stable hash of source URL and chunk index; existing IDs are skipped.
4. The app uses an LCEL retrieval chain with a retriever, prompt, Gemini chat model, and `StrOutputParser`.
5. The prompt forces answers to use only retrieved context and otherwise return the configured fallback phrase.
6. Citation blocks are appended from retrieved chunk source URLs for in-scope answers.
7. `evaluate.py` checks 10 in-scope questions, 3 out-of-scope questions, and p50 latency.
