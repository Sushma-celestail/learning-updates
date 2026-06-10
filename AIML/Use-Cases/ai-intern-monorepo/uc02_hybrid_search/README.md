# UC02 — Hybrid Search RAG

**Advanced retrieval pipeline: BM25 + dense vectors + cross-encoder reranking + Langfuse observability.**

---

## Complete End-to-End Workflow

```
Your Documents (PDF / HTML)
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  INGESTION  (ingest.py)                                     │
│                                                             │
│  1. Load PDFs  → PyPDFLoader   → source_type = "pdf"       │
│  2. Load HTML  → BSHTMLLoader  → source_type = "html"      │
│  3. Clean whitespace                                        │
│  4. Chunk  →  RecursiveCharacterTextSplitter                │
│             chunk_size=800, overlap=100                     │
│  5. SHA-256 IDs  →  idempotent re-runs                      │
│  6. Embed  →  Gemini embedding-001  (batches of 50)         │
│  7. Store  →  ChromaDB  (uc02_hybrid_search/data/chroma/)   │
│  8. Pickle chunks  →  bm25_docs.pkl  (BM25 corpus)         │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  QUERY PIPELINE  (chain.py)                                 │
│                                                             │
│  User Query                                                 │
│       │                                                     │
│       ▼                                                     │
│  ┌────────────────────────────────────┐                     │
│  │  SPAN 1 — Hybrid Retrieve (top-30) │  retriever.py       │
│  │                                    │                     │
│  │  BM25Retriever  ──┐                │                     │
│  │  (keyword/lexical) │               │                     │
│  │                    ├─ EnsembleRetriever (RRF 0.5/0.5)   │
│  │  ChromaDB Retriever┘               │                     │
│  │  (dense/semantic)                  │                     │
│  │                                    │                     │
│  │  Optional: metadata_filter         │                     │
│  │  e.g. {"source_type": "pdf"}       │                     │
│  └────────────────────────────────────┘                     │
│       │                                                     │
│       ▼  30 candidate documents                             │
│  ┌────────────────────────────────────┐                     │
│  │  SPAN 2 — Cross-Encoder Rerank     │  reranker.py        │
│  │                                    │                     │
│  │  Backend A (default):              │                     │
│  │    BAAI/bge-reranker-v2-m3         │                     │
│  │    runs locally via sentence-      │                     │
│  │    transformers (free, ~1 GB)      │                     │
│  │                                    │                     │
│  │  Backend B (optional):             │                     │
│  │    Cohere rerank-english-v3.0      │                     │
│  │    set RERANKER_BACKEND=cohere     │                     │
│  └────────────────────────────────────┘                     │
│       │                                                     │
│       ▼  5 reranked documents                               │
│  ┌────────────────────────────────────┐                     │
│  │  SPAN 3 — Generate                 │  chain.py           │
│  │                                    │                     │
│  │  Prompt: system + context +        │                     │
│  │          question                  │                     │
│  │  LLM: Gemini gemini-2.5-flash      │                     │
│  │  Parser: StrOutputParser           │                     │
│  └────────────────────────────────────┘                     │
│       │                                                     │
│       ▼                                                     │
│  Answer + Sources block                                     │
│       │                                                     │
│       ▼                                                     │
│  Langfuse Trace  (retrieve + rerank + generate spans)       │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  EVALUATION  (eval/eval_recall.py)                          │
│                                                             │
│  Compares 3 configs on 20 held-out questions:               │
│  (a) vector-only    → Recall@5 + avg latency                │
│  (b) hybrid         → Recall@5 + avg latency                │
│  (c) hybrid+rerank  → Recall@5 + avg latency  ← ship this  │
│                                                             │
│  AC6: hybrid+rerank Recall@5 ≥ 0.85 > vector-only          │
│  AC7: latency report printed for all 3 configs              │
└─────────────────────────────────────────────────────────────┘
```

---

## File Map

```
uc02_hybrid_search/
├── ingest.py          Load PDFs + HTML → chunk → embed → ChromaDB + BM25 pickle
├── retriever.py       EnsembleRetriever: BM25 + ChromaDB with RRF fusion
├── reranker.py        Cross-encoder reranking (local BAAI or Cohere API)
├── chain.py           Full pipeline: retrieve → rerank → generate + Langfuse
├── data/
│   ├── raw/           ← DROP YOUR PDF AND HTML FILES HERE
│   ├── chroma/        ChromaDB vector store (auto-created)
│   └── bm25_docs.pkl  Pickled chunks for BM25 (auto-created by ingest.py)
├── eval/
│   └── eval_recall.py Recall@5 evaluation + latency report
├── logs/
│   └── hybrid_pipeline.log  All pipeline logs (auto-created)
└── tests/
    └── test_hybrid.py Unit + integration tests
```

---

## Prerequisites

### 1. Python environment

```bash
# From the project root (ai-intern-monorepo/)
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. API keys

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Open `.env` and set:

```env
# Required
GOOGLE_API_KEY=your_google_api_key_here

# Optional — Langfuse observability (AC8)
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com

# Optional — Cohere reranker (default is local BAAI model)
COHERE_API_KEY=your_cohere_api_key
RERANKER_BACKEND=local        # change to "cohere" to use Cohere API
RERANKER_MODEL=BAAI/bge-reranker-v2-m3
```

Get your free keys:
- Google API key → https://aistudio.google.com/app/apikey
- Langfuse keys  → https://cloud.langfuse.com (free tier)
- Cohere key     → https://dashboard.cohere.com/api-keys (free trial)

---

## Step-by-Step Execution

### Step 1 — Add your source documents

Drop PDF and/or HTML files into:

```
uc02_hybrid_search/data/raw/
```

The pipeline supports:
- `.pdf`  — any PDF (research papers, manuals, specs)
- `.html` / `.htm` — saved web pages

Example structure:
```
uc02_hybrid_search/data/raw/
├── fastapi_guide.pdf
├── pydantic_docs.pdf
├── deployment.html
└── authentication.html
```

> **Tip:** You can save FastAPI docs pages as HTML directly from your browser
> (File → Save Page As → Webpage, HTML Only) and drop them in this folder.

---

### Step 2 — Run ingestion

```bash
# From the project root
python uc02_hybrid_search/ingest.py
```

What happens:
1. Loads all PDFs and HTML files from `data/raw/`
2. Tags each document with `source_type` metadata (`"pdf"` or `"html"`)
3. Cleans whitespace and splits into 800-char chunks with 100-char overlap
4. Generates SHA-256 IDs — re-running is safe, no duplicates stored
5. Embeds chunks with Gemini `embedding-001` in batches of 50
6. Persists vectors to `data/chroma/`
7. Saves all chunks to `data/bm25_docs.pkl` for the BM25 index

Expected output:
```
▶ Embedding 420 chunks in 9 batches …
✅ UC02 ingestion complete — 420 chunks in 312.4s
```

> **Rate limit note:** The free Gemini tier allows ~1 000 embedding requests/day.
> The script pauses 65 s between batches automatically. If you hit a 429 error
> it retries once after 70 s. For large document sets, split ingestion across days.

---

### Step 3 — Test the pipeline (no UI needed)

Run a quick end-to-end test from Python:

```python
# From the project root
python -c "
from uc02_hybrid_search.chain import answer_question
answer = answer_question('What is dependency injection?')
print(answer)
"
```

Or with a metadata filter (PDF chunks only):

```python
python -c "
from uc02_hybrid_search.chain import answer_question
answer = answer_question(
    'What does the spec say about authentication?',
    metadata_filter={'source_type': 'pdf'}
)
print(answer)
"
```

---

### Step 4 — Run the evaluation report

```bash
python uc02_hybrid_search/eval/eval_recall.py
```

This runs 20 held-out questions through all three retrieval configurations
and prints a comparison report:

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
LATENCY REPORT (AC7)
============================================================
  (a) vector-only   : 0.412s avg
  (b) hybrid        : 0.631s avg
  (c) hybrid+rerank : 1.243s avg

RECOMMENDATION:
  ✅ Ship hybrid+rerank — Recall@5 meets the ≥0.85 target (0.90)
     and beats vector-only (0.70).
  Latency overhead vs vector-only: +0.831s — acceptable for production RAG.
============================================================

✅ AC6 passed — hybrid+rerank Recall@5 ≥ 0.85 and > vector-only baseline
```

> **Customise the eval set:** Open `eval/eval_recall.py` and edit the `EVAL_SET`
> list with questions relevant to your own documents. Each entry is a
> `(question, [expected_keywords])` tuple.

---

### Step 5 — Run the tests

```bash
# Unit tests only (no API key needed, runs in ~7s)
pytest uc02_hybrid_search/tests/ -m "not integration" -v

# All tests including integration (requires API key + ingested data)
pytest uc02_hybrid_search/tests/ -v
```

Unit tests check:
- BM25 + vector weights sum to 1.0
- `HYBRID_TOP_N` > `RERANK_TOP_K` (retrieve more than you keep)
- All three modules import without errors

Integration tests check:
- Hybrid retriever returns documents
- Reranker reduces doc count to ≤ top_k
- Metadata filter restricts to PDF chunks (AC9)
- Full pipeline returns a non-empty answer

---

## Configuration Reference

All settings live in `shared/config/settings.py`:

| Setting | Default | What it controls |
|---------|---------|-----------------|
| `EMBEDDING_MODEL` | `models/embedding-001` | Gemini embedding model |
| `CHAT_MODEL` | `gemini-2.5-flash` | Gemini chat model |
| `CHUNK_SIZE` | `800` | Characters per chunk |
| `CHUNK_OVERLAP` | `100` | Overlap between chunks |
| `HYBRID_TOP_N` | `30` | Docs retrieved before reranking |
| `RERANK_TOP_K` | `5` | Docs kept after reranking |
| `VECTOR_WEIGHT` | `0.5` | Weight for vector leg in RRF |
| `BM25_WEIGHT` | `0.5` | Weight for BM25 leg in RRF |

Environment variables (set in `.env`):

| Variable | Default | What it controls |
|----------|---------|-----------------|
| `GOOGLE_API_KEY` | — | Required. Gemini API key |
| `RERANKER_BACKEND` | `local` | `local` or `cohere` |
| `RERANKER_MODEL` | `BAAI/bge-reranker-v2-m3` | Local cross-encoder model |
| `COHERE_API_KEY` | — | Required only if `RERANKER_BACKEND=cohere` |
| `LANGFUSE_PUBLIC_KEY` | — | Optional. Enables Langfuse tracing |
| `LANGFUSE_SECRET_KEY` | — | Optional. Enables Langfuse tracing |
| `LANGFUSE_HOST` | `https://cloud.langfuse.com` | Langfuse server URL |

---

## Metadata Filtering (AC9)

Every ingested document is tagged with `source_type` metadata.
You can restrict retrieval to a specific document type using a Chroma `where` clause.

**In Python:**
```python
from uc02_hybrid_search.chain import answer_question

# Only search PDF chunks
answer = answer_question(
    "What does the spec say?",
    metadata_filter={"source_type": "pdf"}
)

# Only search HTML chunks
answer = answer_question(
    "What does the web page say?",
    metadata_filter={"source_type": "html"}
)

# No filter — search everything (default)
answer = answer_question("What is FastAPI?")
```

**Directly on the retriever:**
```python
from uc02_hybrid_search.retriever import get_hybrid_retriever

retriever = get_hybrid_retriever(
    metadata_filter={"source_type": "pdf"},
    top_n=30,
)
docs = retriever.invoke("authentication flow")
```

---

## Langfuse Observability (AC8)

When `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` are set in `.env`,
every call to `answer_question()` automatically creates a Langfuse trace
with three spans:

```
Trace: "What is dependency injection?"
  ├── Span: retrieve   inputs={query}  outputs={30 docs}  latency=0.4s
  ├── Span: rerank     inputs={query, 30 docs}  outputs={5 docs}  latency=0.8s
  └── Span: generate   inputs={context, question}  outputs={answer}  latency=2.1s
```

View traces at https://cloud.langfuse.com after running any query.

If keys are not set the pipeline runs normally — observability is optional.

---

## Reranker Backends

### Default: Local BAAI model (no extra API key)

```env
RERANKER_BACKEND=local
RERANKER_MODEL=BAAI/bge-reranker-v2-m3
```

- Downloads ~1 GB model on first use (cached by HuggingFace in `~/.cache/huggingface/`)
- Runs on CPU — ~0.5–1 s for 30 documents
- Completely free, no rate limits

### Alternative: Cohere API (free trial)

```env
RERANKER_BACKEND=cohere
COHERE_API_KEY=your_cohere_api_key
```

- No local model download
- Free trial: 1 000 rerank calls/month
- Slightly faster than local CPU inference
- Get key at https://dashboard.cohere.com/api-keys

---

## When BM25 Wins vs When Vectors Win (AC10)

**BM25 wins on lexical exact-match recall.** When a user types a precise
function name, error code, HTTP status, or technical term that appears
verbatim in the documentation, BM25 surfaces it reliably — even when the
embedding space places the query vector far from the relevant chunk.
For example, searching for `"422 Unprocessable Entity"` or
`"HTTPException status_code=404"` will score highly in BM25 because those
exact tokens appear in the text.

**Dense vectors win on semantic / paraphrase recall.** When the user asks
*"how do I make my endpoint faster?"* the vector search finds chunks about
*"performance optimisation"* and *"async path operations"* even though those
words don't appear in the query. Vectors capture meaning, not just tokens.

**The ensemble with Reciprocal Rank Fusion captures both signals**,
consistently outperforming either retriever alone on mixed real-world query
sets. The cross-encoder reranker then re-scores the top-30 candidates with
full query-document attention, pushing the most relevant chunks to the top-5
that the LLM actually reads.

---

## Acceptance Criteria Checklist

| # | Criterion | File | Status |
|---|-----------|------|--------|
| AC6 | hybrid+rerank Recall@5 ≥ 0.85 AND > vector-only | `eval/eval_recall.py` | Run eval to verify |
| AC7 | Latency report for all 3 configs | `eval/eval_recall.py` | Printed automatically |
| AC8 | Langfuse trace per query (retrieve+rerank+generate spans) | `chain.py` + `shared/observability/langfuse_cb.py` | Set Langfuse keys in `.env` |
| AC9 | Metadata filter by `source_type` via Chroma `where` | `retriever.py` | Pass `metadata_filter={"source_type": "pdf"}` |
| AC10 | BM25 vs vectors explanation in README | This file | ✅ See section above |

---

## Troubleshooting

**`FileNotFoundError: BM25 corpus not found at ... bm25_docs.pkl`**
→ Run `python uc02_hybrid_search/ingest.py` first.

**`No PDF or HTML files found in data/raw/`**
→ Drop your source files into `uc02_hybrid_search/data/raw/` and re-run ingest.

**`RESOURCE_EXHAUSTED` / `429` during ingestion**
→ Free Gemini tier limit hit. The script retries automatically. If it fails again,
wait until tomorrow (quota resets daily) and re-run — already-embedded chunks are skipped.

**`GOOGLE_API_KEY is not set`**
→ Make sure `.env` exists in the project root with `GOOGLE_API_KEY=your_key`.

**Local reranker is slow**
→ First run downloads ~1 GB model. Subsequent runs use the cached model and are fast.
Switch to `RERANKER_BACKEND=cohere` for faster API-based reranking.

**`ModuleNotFoundError: No module named 'langchain_classic'`**
→ Run `pip install langchain-classic` or `pip install -r requirements.txt`.

**Recall@5 below 0.85**
→ Check that your eval set keywords match terms actually present in your documents.
Try adding more source documents to `data/raw/` and re-ingesting.
