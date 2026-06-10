"""Streamlit web interface for the Docs Buddy RAG chatbot."""
# This module creates the chat UI and logs every user interaction so the
# full session trace (question received → answer displayed) is recorded
# in rag_pipeline.log alongside the chain-level logs from chain.py.

import sys    # For adding project root to Python import path
import time   # For measuring UI-level latency
from pathlib import Path  # Cross-platform path operations

import streamlit as st   # Web framework for the chat interface

# Add project root to Python path so shared modules can be imported
PROJECT_ROOT = Path(__file__).resolve().parents[1]   # ai-intern-monorepo/
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Project imports
from chain import answer_question          # RAG pipeline entry point
from shared.logger import get_logger       # Shared logger (file + console)

# Module-level logger — log lines from this file show "app" as the source
log = get_logger("app")

# ---------------------------------------------------------------------------
# Streamlit page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Docs Buddy",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.title("📚 Docs Buddy")
st.caption(
    "Ask questions about the FastAPI documentation. "
    "I'll search through the docs and provide answers with source citations."
)

with st.expander("ℹ️ How it works"):
    st.markdown("""
    - **Retrieval**: Searches embedded FastAPI documentation chunks in ChromaDB
    - **Context**: Answers only from retrieved documentation content
    - **Citations**: Answers include source URLs from the documentation
    - **Fallback**: Out-of-scope questions get an honest "I don't know" response
    """)

# ---------------------------------------------------------------------------
# Session state — client-side chat history (persists across Streamlit reruns)
# ---------------------------------------------------------------------------
if "messages" not in st.session_state:
    # First load: initialise history and log the session start
    st.session_state.messages = []
    st.session_state.question_count = 0   # Track how many questions asked this session

    log.info("*" * 70)
    log.info("NEW STREAMLIT SESSION STARTED")
    log.info("*" * 70)

    # Welcome message shown to the user
    st.session_state.messages.append({
        "role": "assistant",
        "content": (
            "👋 Hi! I'm Docs Buddy. Ask me anything about FastAPI documentation "
            "and I'll help you find the answer!"
        ),
    })

# ---------------------------------------------------------------------------
# Render existing chat history
# ---------------------------------------------------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------------------------------------------------------------------
# Handle new user input
# ---------------------------------------------------------------------------
question = st.chat_input("Ask about FastAPI documentation...")

if question:
    # -----------------------------------------------------------------------
    # UI STEP A — Log and display the incoming question
    # -----------------------------------------------------------------------
    st.session_state.question_count += 1
    q_num = st.session_state.question_count   # Question number in this session

    log.info("─" * 70)
    log.info("[UI] QUESTION #%d SUBMITTED", q_num)
    log.info("[UI] Text : %s", question)

    # Save user message to history and render it immediately
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # -----------------------------------------------------------------------
    # UI STEP B — Call the RAG chain and measure wall-clock latency
    # -----------------------------------------------------------------------
    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching the FastAPI documentation..."):

            log.info("[UI] Calling RAG chain for question #%d", q_num)
            t_ui_start = time.perf_counter()   # Wall-clock timer starts here

            try:
                # answer_question() logs STEP 1-6 internally (see chain.py)
                answer = answer_question(question)
                ui_latency = time.perf_counter() - t_ui_start

                log.info(
                    "[UI] Answer received for question #%d — UI latency: %.3fs",
                    q_num, ui_latency
                )

            except Exception as exc:
                ui_latency = time.perf_counter() - t_ui_start
                log.error(
                    "[UI] Error on question #%d after %.3fs: %s",
                    q_num, ui_latency, exc, exc_info=True
                )
                # Show a user-friendly error message in the chat
                answer = (
                    "❌ Sorry, I encountered an error while processing your question.\n\n"
                    "Please make sure:\n"
                    "- Documentation has been ingested (`python ingest.py`)\n"
                    "- `GOOGLE_API_KEY` environment variable is set\n\n"
                    f"Error details: {exc}"
                )

        # -----------------------------------------------------------------------
        # UI STEP C — Display the answer
        # -----------------------------------------------------------------------
        st.markdown(answer)

        # Log whether the answer was in-scope or used the fallback phrase
        from shared.config.settings import FALLBACK_PHRASE
        if FALLBACK_PHRASE in answer:
            log.info("[UI] Question #%d → OUT-OF-SCOPE answer displayed", q_num)
        else:
            log.info("[UI] Question #%d → IN-SCOPE answer displayed", q_num)

    # Save assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": answer})

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    "💡 **Tip**: Ask specific questions about FastAPI features, syntax, or concepts."
)
