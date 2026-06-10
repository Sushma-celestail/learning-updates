# How to Run This Project

Complete step-by-step guide for both use-cases on Windows.

---

## Your Environment (already confirmed working)

| Item | Status |
|------|--------|
| Python | 3.14.3 ✅ |
| Virtual env | `.venv/` ✅ |
| GOOGLE_API_KEY | Set in `.env` ✅ |
| All packages | Installed ✅ |
| Unit tests | 11/11 passing ✅ |

---

## Project Structure at a Glance

```
ai-intern-monorepo/
│
├── uc01_docs_buddy/        ← Use Case 1: Basic RAG chatbot
│   ├── ingest.py           step 1: scrape + embed FastAPI docs
│   ├── chain.py            RAG pipeline (retriever → LLM)
│   ├── app.py              Streamlit chat UI
│   └── tests/
│
├── uc02_hybrid_search/     ← Use Case 2: Hybrid BM25 + vector + reranking
│   ├── ingest.py           step 1: load PDFs/HTML → embed → ChromaDB
│   ├── retriever.py        BM25 + ChromaDB ensemble
│   ├── reranker.py         cross-encoder reranking
│   ├── chain.py            full pipeline
│   ├── eval/
│   │   └── eval_recall.py  Recall@5 evaluation
│   └── tests/
│
├── shared/                 ← shared config, logger, vector store
│   ├── config/settings.py  all settings in one place
│   └── vectorstore/chroma.py
│
├── .env                    your API keys
└── requirements.txt
```

---

## Activate the Virtual Environment

**Always do this first** before running any command:

```bash
# Windows (PowerShell or CMD)
.venv\Scripts\activate
```

Your prompt will change to show `(.venv)`.

---

## Use Case 1 — Docs Buddy (Basic RAG)

### What it does
Scrapes 50–80 FastAPI documentation pages, embeds them with Gemini, stores in ChromaDB,
and serves a Streamlit chat UI where you can ask questions about FastAPI.

---

### Step 1 — Ingest the FastAPI docs

```bash
python uc01_docs_buddy/ingest.py
```

**What happens:**
1. Downloads FastAPI sitemap → fetches 50–80 pages
2. Cleans and chunks text (800 chars, 100 overlap)
3. Embeds with Gemini `embedding-001` in batches of 50
4. Saves to `uc01_docs_buddy/data/chroma/`

**Expected output:**
```
▶ Resuming ingestion — 320 chunks remaining across 7 batches
✅ Ingestion complete — 320 chunks stored in 412.3s
```

**Time:** ~7–10 minutes (free Gemini tier pauses 65 s between batches)

**Re-running is safe** — already-embedded chunks are skipped automatically.

> ⚠️ If you see `RESOURCE_EXHAUSTED` / `429`: the free Gemini tier allows
> ~1 000 embedding requests/day. The script retries once automatically.
> If it still fails, wait until tomorrow and re-run — progress is saved.

---

### Step 2 — Launch the chat UI

```bash
streamlit run uc01_docs_buddy/app.py
```

Opens at **http://localhost:8501** in your browser.

**Try these questions:**
- `What is FastAPI?`
- `How do I define path parameters?`
- `How does dependency injection work in FastAPI?`
- `What is the weather today?` ← should return the fallback phrase

---

### Step 3 — Run UC01 tests

```bash
# Unit tests (no API key needed, ~7s)
pytest uc01_docs_buddy/tests/ -m "not integration" -v

# Integration tests (requires ingested data + API key, ~2 min)
pytest uc01_docs_buddy/tests/ -v
```

---

## Use Case 2 — Hybrid Search RAG

### What it does
Combines BM25 keyword search + ChromaDB vector search via Reciprocal Rank Fusion,
then reranks the top-30 results to top-5 using a cross-encoder model before
sending to Gemini. Produces Langfuse traces for every query.

---

### Step 1 — Add your source documents

Drop PDF and/or HTML files into:

```
uc02_hybrid_search/data/raw/
```

**Supported formats:** `.pdf`  `.html`  `.htm`

**Where to get files:**
- Save FastAPI docs pages as HTML: open any page at https://fastapi.tiangolo.com,
  press `Ctrl+S` → "Webpage, HTML Only" → save to `data/raw/`
- Download any PDF documentation you want to search over

**Minimum recommended:** 5–10 files to get meaningful retrieval results.

Example after adding files:
```
uc02_hybrid_search/data/raw/
├── fastapi_intro.html
├── fastapi_tutorial.html
├── fastapi_advanced.html
├── pydantic_guide.pdf
└── deployment_guide.pdf
```

---

### Step 2 — Ingest your documents

```bash
python uc02_hybrid_search/ingest.py
```

**What happens:**
1. Loads all PDFs (`PyPDFLoader`) and HTML files (`BSHTMLLoader`)
2. Tags each chunk with `source_type = "pdf"` or `"html"` metadata
3. Cleans and chunks text (800 chars, 100 overlap)
4. Generates SHA-256 IDs → re-running skips already-stored chunks
5. Embeds with Gemini `embedding-001` → saves to `data/chroma/`
6. Pickles all chunks to `data/bm25_docs.pkl` for the BM25 index

**Expected output:**
```
▶ Embedding 420 chunks in 9 batches …
✅ UC02 ingestion complete — 420 chunks in 312.4s
```

---

### Step 3 — Test a query from the terminal

```bash
python -c "
import sys; sys.path.insert(0, '.')
from uc02_hybrid_search.chain import answer_question
answer = answer_question('What is dependency injection?')
print(answer)
"
```

**With metadata filter (PDF chunks only):**
```bash
python -c "
import sys; sys.path.insert(0, '.')
from uc02_hybrid_search.chain import answer_question
answer = answer_question(
    'What does the spec say about authentication?',
    metadata_filter={'source_type': 'pdf'}
)
print(answer)
"
```

---

### Step 4 — Run the Recall@5 evaluation

```bash
python uc02_hybrid_search/eval/eval_recall.py
```

This compares three retrieval configurations on 20 questions and prints:

```
============================================================
UC02 — Recall@5 Evaluation
============================================================
Eval set size: 20 questions

Running evaluations …

  [(a) vector-only  ] Recall@5=0.70  avg_latency=0.412s
  [(b) hybrid       ] Recall@5=0.80  avg_latency=0.631s
  [(c) hybrid+rerank] Recall@5=0.90  avg_latency=1.243s

============================================================
LATENCY REPORT
============================================================
  (a) vector-only   : 0.412s avg
  (b) hybrid        : 0.631s avg
  (c) hybrid+rerank : 1.243s avg

RECOMMENDATION:
  ✅ Ship hybrid+rerank — Recall@5=0.90 meets ≥0.85 target
============================================================
```

> **Customise the eval set:** Edit `EVAL_SET` in `eval/eval_recall.py`
> with questions relevant to your own documents.

---

### Step 5 — Run UC02 tests

```bash
# Unit tests (no API key needed, ~70s — loads reranker model)
pytest uc02_hybrid_search/tests/ -m "not integration" -v

# Integration tests (requires ingested data + API key)
pytest uc02_hybrid_search/tests/ -v
```

---

## Optional: Enable Langfuse Observability (UC02)

Every UC02 query automatically creates a Langfuse trace showing
`retrieve → rerank → generate` spans with inputs, outputs, and latencies.

1. Sign up free at https://cloud.langfuse.com
2. Create a project and copy your keys
3. Add to `.env`:

```env
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxxxxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxxxxxxxxxx
LANGFUSE_HOST=https://cloud.langfuse.com
```

4. Run any query — traces appear in your Langfuse dashboard automatically.

If keys are not set the pipeline runs normally without tracing.

---

## Optional: Switch Reranker to Cohere (UC02)

The default reranker downloads BAAI/bge-reranker-v2-m3 (~1 GB) locally.
To use Cohere's API instead (no download, free trial):

1. Get a free key at https://dashboard.cohere.com/api-keys
2. Add to `.env`:

```env
RERANKER_BACKEND=cohere
COHERE_API_KEY=your_cohere_api_key
```

---

## Run Both Use Cases Together

```bash
# Terminal 1 — UC01 chat UI
streamlit run uc01_docs_buddy/app.py

# Terminal 2 — UC02 query test
python -c "
import sys; sys.path.insert(0, '.')
from uc02_hybrid_search.chain import answer_question
print(answer_question('What is FastAPI?'))
"
```

---

## All Commands at a Glance

```bash
# ── Setup (one time) ──────────────────────────────────────────
.venv\Scripts\activate                          # activate venv

# ── UC01 ──────────────────────────────────────────────────────
python uc01_docs_buddy/ingest.py                # ingest FastAPI docs (~10 min)
streamlit run uc01_docs_buddy/app.py            # launch chat UI
pytest uc01_docs_buddy/tests/ -m "not integration" -v   # unit tests

# ── UC02 ──────────────────────────────────────────────────────
# (drop files in uc02_hybrid_search/data/raw/ first)
python uc02_hybrid_search/ingest.py             # ingest PDFs + HTML
python uc02_hybrid_search/eval/eval_recall.py   # Recall@5 report
pytest uc02_hybrid_search/tests/ -m "not integration" -v   # unit tests

# ── Both ──────────────────────────────────────────────────────
pytest -m "not integration" -v                  # all unit tests (11 tests)
```

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'X'`**
```bash
pip install -r requirements.txt
```

**`GOOGLE_API_KEY is not set`**
→ Check `.env` in the project root has `GOOGLE_API_KEY=your_key`

**`RESOURCE_EXHAUSTED` / `429` during ingest**
→ Free Gemini tier daily limit hit. Wait until tomorrow and re-run.
   Already-embedded chunks are skipped — you won't lose progress.

**`FileNotFoundError: BM25 corpus not found`** (UC02)
→ Run `python uc02_hybrid_search/ingest.py` first.

**`No PDF or HTML files found`** (UC02)
→ Drop files into `uc02_hybrid_search/data/raw/` and re-run ingest.

**Streamlit shows blank page**
→ Hard-refresh the browser (`Ctrl+Shift+R`).

**First UC02 query is slow (~30s)**
→ The BAAI reranker model downloads ~1 GB on first use.
   Subsequent queries use the cached model and are fast (~1–2s).

**`streamlit: command not found`**
→ Make sure the venv is activated: `.venv\Scripts\activate`
