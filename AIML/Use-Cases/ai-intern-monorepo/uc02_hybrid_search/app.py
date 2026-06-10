"""
UC02 — Hybrid Search RAG: Streamlit chat UI.

Run:
    streamlit run uc02_hybrid_search/app.py

Pipeline per query:
    BM25 + ChromaDB (top-30)  →  Cross-Encoder Rerank (top-5)  →  Gemini
"""

import sys
import time
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from uc02_hybrid_search.chain import answer_question


# ---------------------------------------------------------------------------
# Error helper
# ---------------------------------------------------------------------------
def _error_message(exc: Exception) -> str:
    msg = str(exc)
    if "RESOURCE_EXHAUSTED" in msg or "429" in msg:
        return (
            "⚠️ **Embedding quota hit** — the daily free-tier limit was reached.\n\n"
            "Re-run `python uc02_hybrid_search/ingest.py` tomorrow to finish ingestion, "
            "or get a new API key at https://aistudio.google.com/app/apikey"
        )
    if "BM25 corpus not found" in msg or "No documents retrieved" in msg:
        return (
            "❌ **Data not ready**\n\n"
            "Run ingestion first:\n"
            "```\npython uc02_hybrid_search/ingest.py\n```"
        )
    return f"❌ **Error**: {exc}"


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Hybrid Search RAG",
    page_icon="🔍",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("🔍 Hybrid Search RAG")
st.caption("UC02 — BM25 + Vector Search + Cross-Encoder Reranking + Gemini")

# ---------------------------------------------------------------------------
# Sidebar — pipeline info + filter
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Pipeline")
    st.markdown("""
    ```
    Your Query
         ↓
    BM25 Retriever
    + ChromaDB Vector
         ↓
    EnsembleRetriever
    (RRF 0.5 / 0.5)
         ↓
    Top 30 docs
         ↓
    Cross-Encoder Reranker
    (BAAI/bge-reranker-v2-m3)
         ↓
    Top 5 docs
         ↓
    Gemini 2.5 Flash
         ↓
    Answer + Sources
    ```
    """)

    st.divider()
    st.header("🔎 Metadata Filter")
    filter_option = st.selectbox(
        "Search within:",
        options=["All documents", "HTML only", "PDF only"],
        index=0,
    )
    metadata_filter = None
    if filter_option == "HTML only":
        metadata_filter = {"source_type": "html"}
    elif filter_option == "PDF only":
        metadata_filter = {"source_type": "pdf"}

    st.divider()
    st.caption("Langfuse tracing is enabled if keys are set in `.env`")

# ---------------------------------------------------------------------------
# How it works expander
# ---------------------------------------------------------------------------
with st.expander("ℹ️ How it works"):
    st.markdown("""
    | Step | What happens | Why |
    |------|-------------|-----|
    | 1 | **BM25** scores chunks by exact keyword match | Catches precise terms like `HTTPException 422` |
    | 2 | **ChromaDB** scores chunks by semantic similarity | Catches paraphrase queries like "make it faster" |
    | 3 | **EnsembleRetriever** fuses both lists (RRF 0.5/0.5) → top-30 | Best of both worlds |
    | 4 | **Cross-Encoder** re-scores all 30 pairs (query, doc) → top-5 | Full attention = higher accuracy |
    | 5 | **Gemini 2.5 Flash** generates answer from top-5 context | Grounded, cited answer |

    Every query is traced in **Langfuse** (retrieve → rerank → generate spans).
    """)

# ---------------------------------------------------------------------------
# Session state — chat history
# ---------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role":    "assistant",
        "content": (
            "👋 Hi! I'm the **Hybrid Search RAG** assistant.\n\n"
            "I use BM25 + vector search + cross-encoder reranking to find "
            "the most relevant FastAPI documentation for your question.\n\n"
            "Ask me anything about FastAPI!"
        ),
    })

# Render history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------------------------------------------------------
# Handle new input
# ---------------------------------------------------------------------------
question = st.chat_input("Ask about FastAPI …")

if question:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # Generate answer
    with st.chat_message("assistant"):
        with st.spinner("🔍 BM25 + vector retrieval → reranking → generating …"):
            t0 = time.perf_counter()
            try:
                answer = answer_question(
                    question,
                    metadata_filter=metadata_filter,
                )
            except Exception as exc:
                answer = _error_message(exc)
            latency = time.perf_counter() - t0

        st.markdown(answer)

        # Show latency + active filter
        filter_label = f" | Filter: `{filter_option}`" if metadata_filter else ""
        st.caption(f"⏱ {latency:.2f}s{filter_label}")

    st.session_state.messages.append({"role": "assistant", "content": answer})

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.markdown("💡 **Tip**: Try exact terms like `HTTPException 422` — BM25 will find them.")
with col2:
    st.markdown("💡 **Tip**: Try paraphrases like `how to make endpoints faster` — vectors will find them.")
