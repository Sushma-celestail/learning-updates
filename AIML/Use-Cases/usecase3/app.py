import os
from dotenv import load_dotenv

load_dotenv()

# =========================
# ENV FIXES
# =========================

os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import streamlit as st

from src.graph.builder import build_graph

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="Adaptive RAG Assistant",
    page_icon="📚",
    layout="wide"
)

# =========================
# TITLE
# =========================

st.title("📚 Adaptive RAG Assistant")

st.markdown(
    """
Ask questions from your PDF knowledge base
or let the agent search the web automatically.
"""
)

# =========================
# LOAD GRAPH
# =========================

@st.cache_resource
def load_graph():
    return build_graph()

graph = load_graph()

# =========================
# SESSION STATE
# =========================

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# =========================
# INPUT
# =========================

question = st.chat_input("Ask your question...")

# =========================
# PROCESS QUESTION
# =========================

if question:

    question = question.strip()

    # =========================
    # BASIC INPUT VALIDATION
    # =========================

    if len(question) > 500:

        st.warning("Question too long. Please shorten it.")

        st.stop()

    if len(question) < 2:

        st.warning("Please enter a valid question.")

        st.stop()

    # =========================
    # SAVE USER MESSAGE
    # =========================

    st.session_state.chat_history.append({
        "role": "user",
        "content": question
    })

    # =========================
    # INVOKE GRAPH
    # =========================

    with st.spinner("Thinking... 🧠"):

        try:

            result = graph.invoke({
                "question": question
            })

        except Exception as e:

            result = {
                "generation": f"❌ Error: {str(e)}",
                "grade": "error",
                "iterations": 0,
                "scores": [],
                "avg_score": 0.0,
                "source": "unknown",
            }

    # =========================
    # SAFE GETTER
    # =========================

    def safe_get(obj, key, default=None):

        if isinstance(obj, dict):
            return obj.get(key, default)

        return getattr(obj, key, default)

    # =========================
    # EXTRACT OUTPUTS
    # =========================

    answer = (
        safe_get(result, "generation")
        or safe_get(result, "answer")
        or "No answer generated"
    )

    grade = safe_get(result, "grade", "unknown")

    iterations = safe_get(result, "iterations", 0)

    source_raw = safe_get(result, "source", "unknown")

    scores = safe_get(result, "scores", [])

    avg_score = float(
        safe_get(result, "avg_score", 0.0)
    )

    # =========================
    # SOURCE LABEL
    # =========================

    source_map = {
        "chroma": "📚 ChromaDB",
        "tavily": "🌐 Tavily Web Search",
        "unknown": "❓ Unknown"
    }

    source_used = source_map.get(
        source_raw,
        "❓ Unknown"
    )

    # =========================
    # STORE RESPONSE
    # =========================

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": answer,
        "grade": grade,
        "iterations": iterations,
        "source": source_used,
        "scores": scores,
        "avg_score": avg_score,
    })

# =========================
# DISPLAY CHAT
# =========================

for message in st.session_state.chat_history:

    # =========================
    # USER
    # =========================

    if message["role"] == "user":

        with st.chat_message("user"):
            st.markdown(message["content"])

    # =========================
    # ASSISTANT
    # =========================

    else:

        with st.chat_message("assistant"):

            st.markdown("### 🧾 Answer")

            st.write(message["content"])

            st.divider()

            col1, col2, col3, col4 = st.columns(4)

            # =========================
            # GRADE
            # =========================

            with col1:

                grade_val = message.get(
                    "grade",
                    "unknown"
                )

                grade_map = {
                    "relevant": "✅ relevant",
                    "ambiguous": "⚠️ ambiguous",
                    "irrelevant": "❌ irrelevant",
                    "error": "💥 error"
                }

                st.info(
                    f"Grade: {grade_map.get(grade_val, grade_val)}"
                )

            # =========================
            # ITERATIONS
            # =========================

            with col2:

                st.info(
                    f"Iterations: {message.get('iterations', 0)}"
                )

            # =========================
            # SOURCE
            # =========================

            with col3:

                st.info(
                    f"Source: {message.get('source', '—')}"
                )

            # =========================
            # AVG SCORE
            # =========================

            with col4:

                avg = float(
                    message.get("avg_score", 0.0)
                )

                st.info(f"Avg Score: {avg:.3f}")

            