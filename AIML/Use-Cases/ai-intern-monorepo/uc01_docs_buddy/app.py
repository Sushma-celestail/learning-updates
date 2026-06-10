"""
UC01 — Docs Buddy: Streamlit chat UI.

Run:
    streamlit run uc01_docs_buddy/app.py
"""

import sys
import time
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from uc01_docs_buddy.chain import answer_question


def _error_message(exc: Exception) -> str:
    """Convert a pipeline exception into a user-friendly message."""
    msg = str(exc)
    if "No documentation chunks" in msg or "quota" in msg.lower():
        return (
            "⚠️ **Embedding API quota exhausted**\n\n"
            "1. Get a fresh key at https://aistudio.google.com/app/apikey\n"
            "2. Update `GOOGLE_API_KEY` in `.env`\n"
            "3. Restart with `streamlit run uc01_docs_buddy/app.py`"
        )
    if "RESOURCE_EXHAUSTED" in msg or "429" in msg:
        return "⚠️ **Rate limit hit** — please wait a minute and try again."
    return (
        f"❌ **Error**: {exc}\n\n"
        "Make sure you have run `python uc01_docs_buddy/ingest.py` first."
    )


# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Docs Buddy", page_icon="📚", layout="centered")

st.title("📚 Docs Buddy")
st.caption("Ask anything about the FastAPI documentation.")

with st.expander("ℹ️ How it works"):
    st.markdown(
        """
        | Step | What happens |
        |------|-------------|
        | 1 | Your question is embedded with Gemini `embedding-001` |
        | 2 | Top-4 chunks are retrieved from ChromaDB |
        | 3 | Gemini `gemini-2.5-flash` generates an answer from those chunks |
        | 4 | A **Citations** block lists the source URLs used |

        Out-of-scope questions return the fallback phrase.
        """
    )

# ---------------------------------------------------------------------------
# Session state — client-side chat history
# ---------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role":    "assistant",
        "content": "👋 Hi! I'm Docs Buddy. Ask me anything about FastAPI!",
    })

# Render existing history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------------------------------------------------------
# Handle new user input
# ---------------------------------------------------------------------------
question = st.chat_input("Ask about FastAPI …")

if question:
    # Show the user's message
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # Generate and show the answer
    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching the FastAPI docs …"):
            t0 = time.perf_counter()
            try:
                answer = answer_question(question)
            except Exception as exc:
                answer = _error_message(exc)
            latency = time.perf_counter() - t0

        st.markdown(answer)
        st.caption(f"⏱ {latency:.2f}s")

    st.session_state.messages.append({"role": "assistant", "content": answer})

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown("💡 **Tip**: Ask specific questions about FastAPI features or syntax.")
