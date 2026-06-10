# Docs Buddy

Basic single-turn RAG chatbot over the public FastAPI documentation site.

## What It Builds

- Loads 50-200 FastAPI documentation pages from the public sitemap.
- Splits pages with `RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)`.
- Embeds chunks with Gemini `models/gemini-embedding-001`.
- Persists vectors in ChromaDB on disk.
- Answers questions through a Streamlit chat UI using LCEL and Gemini chat.
- Replies exactly `I don't know based on the provided docs` when the answer is not in retrieved docs.

## Setup

```powershell
cd C:\Users\sushma.s\Documents\Codex\usecase1
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

The `.env` file is already included locally. Keep it private.

If the configured chat model in `.env` is not available for your Gemini key, set `CHAT_MODEL=gemini-2.5-flash` and rerun the app.

## Ingest Docs

```powershell
python ingest.py
```

By default this ingests 80 FastAPI docs pages. Rerunning is idempotent because chunks use stable IDs and already-ingested IDs are skipped.

Useful knobs in `.env`:

```env
DOCS_PAGE_LIMIT=80
CHUNK_SIZE=800
CHUNK_OVERLAP=100
TOP_K=4
```

## Run The Chatbot

```powershell
streamlit run app.py
```

Ask one question at a time. The Streamlit chat history is kept only in the browser session; each answer is generated from the current question plus retrieved docs.

## Evaluate Acceptance Criteria

After ingestion:

```powershell
python evaluate.py
```

The evaluator checks:

- 10 hand-written FastAPI documentation questions.
- At least 8/10 in-scope answers include a source citation block.
- 3/3 out-of-scope questions return the configured fallback phrase.
- p50 latency for top-k=4 retrieval.

## Swap LLM Or Embedding Provider

The provider wiring lives in `config.py` and `rag.py`. In five lines or fewer:

1. Change `EMBEDDING_MODEL` / `CHAT_MODEL` in `.env`.
2. Replace `GoogleGenerativeAIEmbeddings(...)` in `rag.py`.
3. Replace `ChatGoogleGenerativeAI(...)` in `rag.py`.
4. Keep the retriever, prompt, and parser unchanged.

## Files

- `ingest.py` - sitemap discovery, page loading, chunking, and Chroma persistence.
- `rag.py` - LCEL retrieval chain and citation formatting.
- `app.py` - Streamlit chat interface.
- `evaluate.py` - acceptance criteria smoke evaluator.
- `data/eval_questions.json` - ground-truth and out-of-scope questions.
