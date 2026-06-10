from __future__ import annotations

import html
import os
import re
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from corrective_rag.pipeline import CorrectiveRAGPipeline


st.set_page_config(page_title="Corrective RAG Governance Chat", page_icon="◐", layout="wide")

st.markdown(
    """
    <style>
    :root {
        color-scheme: dark;
    }

    .stApp {
        background: #000;
        color: #f5f5f5;
    }

    [data-testid="stSidebar"] {
        background: #090909;
        border-right: 1px solid #202020;
    }

    [data-testid="stSidebar"] * {
        color: #f7f7f7;
    }

    .block-container {
        max-width: 980px;
        padding-top: 1.2rem;
        padding-bottom: 7rem;
    }

    .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 2rem;
    }

    .brand {
        font-size: 1.35rem;
        font-weight: 700;
        letter-spacing: 0;
    }

    .assistant-card {
        background: transparent;
        color: #f4f4f5;
        padding: 0.35rem 0 0.75rem 0;
        border-bottom: 1px solid #202020;
    }

    .answer-title {
        font-weight: 700;
        margin-bottom: 0.75rem;
        color: #fafafa;
    }

    .answer-text {
        line-height: 1.65;
        font-size: 1.02rem;
        white-space: pre-wrap;
    }

    .sources {
        margin-top: 1rem;
        padding-top: 0.8rem;
        color: #d6d6d6;
        font-size: 0.95rem;
    }

    .source-chip {
        display: inline-block;
        background: #1f1f1f;
        border: 1px solid #333;
        border-radius: 999px;
        padding: 0.3rem 0.7rem;
        margin: 0.18rem 0.25rem 0.18rem 0;
        color: #ececec;
    }

    .source-row {
        display: block;
        color: #dbeafe;
        margin: 0.35rem 0;
        word-break: break-word;
        text-decoration: none;
    }

    .source-row:hover {
        color: #ffffff;
        text-decoration: underline;
    }

    .answer-badge {
        display: inline-block;
        background: #12351f;
        border: 1px solid #1f6f3a;
        border-radius: 999px;
        padding: 0.22rem 0.62rem;
        margin: 0 0 0.75rem 0;
        color: #d9fbe4;
        font-size: 0.86rem;
        font-weight: 650;
    }

    .metric-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.7rem;
        margin-top: 0.8rem;
    }

    .metric-card {
        background: #151515;
        border: 1px solid #2b2b2b;
        border-radius: 8px;
        padding: 0.8rem;
    }

    .metric-label {
        color: #a3a3a3;
        font-size: 0.8rem;
    }

    .metric-value {
        color: #fff;
        font-size: 1.05rem;
        font-weight: 700;
        margin-top: 0.2rem;
    }

    .path {
        color: #d4d4d8;
        font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
        font-size: 0.9rem;
        background: #111;
        border: 1px solid #27272a;
        border-radius: 8px;
        padding: 0.75rem;
        margin: 0.4rem 0 0.9rem;
    }

    .stChatInput {
        background: #000;
    }

    div[data-testid="stChatInput"] textarea {
        background: #262626;
        color: #f7f7f7;
        border: 1px solid #333;
        border-radius: 26px;
    }

    div[data-testid="stExpander"] {
        border: 1px solid #303030;
        background: #0f0f0f;
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_pipeline() -> CorrectiveRAGPipeline:
    return CorrectiveRAGPipeline()


def source_label(source: str) -> str:
    if not source:
        return "Internal Knowledge Base"
    if source.startswith("http"):
        return source
    path = Path(source)
    return path.name if path.suffix else source


def source_markup(item) -> str:
    label = source_label(item.document.source)
    source = item.document.source
    if source.startswith("http"):
        return (
            f"<a class='source-row' href='{html.escape(source)}' target='_blank'>"
            f"{html.escape(label)}</a>"
        )
    return f"<span class='source-chip'>{html.escape(label)}</span>"


def graph_path(corrected: bool, web_results: int) -> list[str]:
    path = ["retrieve", "grade_documents"]
    if corrected:
        path.extend(["rewrite_query", "web_search"])
    path.extend(["generate", "langfuse_metrics", "hallucination_eval", "helpfulness_eval", "audit_log"])
    return path


def evaluation_score(result, name: str) -> float:
    for evaluation in result.evaluations:
        if evaluation.name == name:
            return evaluation.score
    return 0.0


def is_greeting(question: str) -> bool:
    normalized = re.sub(r"[^a-zA-Z\s]", "", question).strip().lower()
    greetings = {
        "hi",
        "hello",
        "hey",
        "good morning",
        "good afternoon",
        "good evening",
        "namaste",
    }
    return normalized in greetings


def greeting_response() -> dict[str, object]:
    return {
        "answer": (
            "Hello!\n\n"
            "How can I help you today?\n\n"
            "You can ask me questions about:\n"
            "- FastAPI\n"
            "- Corrective RAG\n"
            "- LangGraph\n"
            "- AI governance\n"
            "- Documents in the knowledge base"
        ),
        "sources": [],
        "badge": "Ready to help",
    }


def clean_user_answer(answer: str) -> str:
    cleaned = re.sub(
        r"\n\nSources:\n.*?(?=\n\nCitations:|\Z)",
        "",
        answer,
        flags=re.DOTALL,
    )
    cleaned = re.sub(r"\s*Citations:\s*(\[[^\]]+\]\s*)+$", "", cleaned)
    return cleaned.strip()


def answer_badge(result) -> str:
    web_results = sum(1 for item in result.retrieved if item.document.doc_id.startswith("WEB-"))
    hallucination = evaluation_score(result, "online_hallucination_guard")
    helpfulness = evaluation_score(result, "online_helpfulness_guard")
    relevant = max((item.score for item in result.retrieved), default=0.0) >= 0.25
    if web_results:
        return "Web Search Assisted"
    if relevant and hallucination >= 0.9 and helpfulness >= 0.62:
        return "Grounded - Local Knowledge Base"
    return "Review Suggested"


def render_governance(result) -> None:
    web_results = sum(1 for item in result.retrieved if item.document.doc_id.startswith("WEB-"))
    if web_results:
        route = "Tavily Web Search"
    elif result.correction_reason and "web" in result.correction_reason:
        route = "Tavily Web Search (no usable results)"
    else:
        route = "Local KB"
    docs = result.retrieved[:5]
    hallucination = evaluation_score(result, "online_hallucination_guard")
    helpfulness = evaluation_score(result, "online_helpfulness_guard") * 5
    path = graph_path(result.corrected, web_results)

    st.markdown("### Governance Details")
    st.markdown("**Retriever Route**")
    st.markdown(f"`{route}`")

    st.markdown("**Graph Path**")
    st.markdown(f"<div class='path'>{' -> '.join(path)}</div>", unsafe_allow_html=True)

    st.markdown("**Retrieved Documents**")
    if docs:
        for item in docs:
            source = item.document.source
            source_text = f" - {source}" if source.startswith("http") else ""
            st.markdown(
                f"- `{item.document.doc_id}` - {item.document.title} "
                f"(score {item.score:.2f}){source_text}"
            )
    else:
        st.markdown("- None")

    st.markdown(
        f"""
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">Hallucination Score</div>
                <div class="metric-value">{hallucination:.2f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Helpfulness Score</div>
                <div class="metric-value">{helpfulness:.1f} / 5</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Retrieved Docs</div>
                <div class="metric-value">{len(result.retrieved)}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Input Tokens</div>
                <div class="metric-value">{result.input_tokens}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Output Tokens</div>
                <div class="metric-value">{result.output_tokens}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Tokens</div>
                <div class="metric-value">{result.total_tokens}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Latency</div>
                <div class="metric-value">{result.latency_ms / 1000:.2f} sec</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Cost</div>
                <div class="metric-value">${result.cost_usd:.6f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Web Search Results</div>
                <div class="metric-value">{web_results}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("**Audit**")
    st.markdown(
        f"""
        <div class="path">
        Audit Status: Logged<br>
        Conversation ID: {result.trace_id}<br>
        Timestamp: {result.created_at}<br>
        Model: {result.model}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_static_answer(payload: dict[str, object]) -> None:
    with st.chat_message("assistant"):
        st.markdown("<div class='assistant-card'>", unsafe_allow_html=True)
        st.markdown("<div class='answer-title'>Answer</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='answer-badge'>{html.escape(str(payload.get('badge', 'Assistant')))}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='answer-text'>{html.escape(str(payload['answer']))}</div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)


def render_answer(result, show_governance: bool) -> None:
    source_chips = []
    seen = set()
    cited_ids = set(result.citations)
    source_items = [item for item in result.retrieved if item.document.doc_id in cited_ids]
    if not source_items:
        source_items = result.retrieved[:5]
    for item in source_items:
        key = item.document.source
        if key not in seen:
            source_chips.append(source_markup(item))
            seen.add(key)

    with st.chat_message("assistant"):
        st.markdown("<div class='assistant-card'>", unsafe_allow_html=True)
        st.markdown("<div class='answer-title'>Answer</div>", unsafe_allow_html=True)
        answer_text = result.answer if show_governance else clean_user_answer(result.answer)
        if not show_governance:
            st.markdown(
                f"<div class='answer-badge'>{html.escape(answer_badge(result))}</div>",
                unsafe_allow_html=True,
            )
        st.markdown(
            f"<div class='answer-text'>{html.escape(answer_text)}</div>",
            unsafe_allow_html=True,
        )
        if source_chips:
            chips = "".join(source_chips)
            st.markdown(
                f"<div class='sources'><strong>Sources Used</strong><br>{chips}</div>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

        if show_governance:
            with st.expander("Governance Details", expanded=False):
                render_governance(result)


def ask(question: str, show_governance: bool) -> None:
    if not show_governance and is_greeting(question):
        st.session_state.messages.append({"role": "user", "content": question})
        st.session_state.messages.append({"role": "assistant", "static": greeting_response()})
        return

    pipeline = get_pipeline()
    result = pipeline.answer(question, user_id=os.getenv("CORRECTIVE_RAG_USER_ID", "streamlit-user"))
    st.session_state.messages.append({"role": "user", "content": question})
    st.session_state.messages.append({"role": "assistant", "result": result})


with st.sidebar:
    st.markdown("## ChatGPT")
    st.button("New chat", use_container_width=True, on_click=lambda: st.session_state.clear())
    st.divider()
    view_mode = st.radio(
        "View",
        ["User View", "Developer / Governance View"],
        index=0,
        help="User View hides governance metrics. Developer View shows an expandable metrics panel.",
    )
    st.divider()
    st.caption("Use Case 3 + Use Case 9")
    st.caption("Corrective RAG with Langfuse, audit logs, evals, and release gates.")

show_governance = view_mode == "Developer / Governance View"

st.markdown(
    """
    <div class="topbar">
        <div class="brand">Corrective RAG Chat</div>
        <div>Use Case 9 Observability</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    st.markdown("### Hi! How can I help you today?")
    st.markdown(
        "Ask about FastAPI, corrective RAG, Langfuse tracing, audit logs, RAGAS, or NIST governance."
    )

for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
    elif "static" in message:
        render_static_answer(message["static"])
    else:
        render_answer(message["result"], show_governance)

prompt = st.chat_input("Ask anything")
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.spinner("Thinking..."):
        ask(prompt, show_governance)
    st.rerun()
