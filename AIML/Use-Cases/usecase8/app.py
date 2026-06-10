import streamlit as st
import json
import uuid
from datetime import datetime

from langgraph.types import Command
from src.graph.checkpointer import get_checkpointer
from src.graph.graph_builder import build_graph
from src.services.audit_logger import log_event
from src.schemas.review_schema import ReviewDecision


# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Safe Agent",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─────────────────────────────────────────
# CUSTOM CSS — dark terminal aesthetic
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Syne:wght@400;600;700;800&display=swap');

/* ── Root Variables ── */
:root {
    --bg:       #0d0f14;
    --surface:  #13161e;
    --border:   #1e2330;
    --accent:   #4ade80;
    --accent2:  #facc15;
    --danger:   #f87171;
    --muted:    #4b5563;
    --text:     #e2e8f0;
    --text-dim: #64748b;
    --user-bg:  #1a2235;
    --agent-bg: #111827;
    --radius:   12px;
}

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'JetBrains Mono', monospace !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
    padding: 0 !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }

/* ── Main area ── */
.main .block-container { padding: 0 !important; }

/* ── Chat container ── */
.chat-wrapper {
    display: flex;
    flex-direction: column;
    height: 100vh;
    overflow: hidden;
}

.chat-header {
    padding: 16px 28px;
    border-bottom: 1px solid var(--border);
    background: var(--surface);
    display: flex;
    align-items: center;
    gap: 12px;
    flex-shrink: 0;
}

.chat-header .title {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800;
    font-size: 18px;
    color: var(--accent);
    letter-spacing: -0.3px;
}

.status-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--accent);
    box-shadow: 0 0 8px var(--accent);
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.4; }
}

/* ── Messages ── */
.messages-area {
    flex: 1;
    overflow-y: auto;
    padding: 28px;
    display: flex;
    flex-direction: column;
    gap: 20px;
    scrollbar-width: thin;
    scrollbar-color: var(--border) transparent;
}

.msg-row {
    display: flex;
    gap: 14px;
    align-items: flex-start;
    animation: fadeUp 0.3s ease;
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}

.msg-row.user  { flex-direction: row-reverse; }

.avatar {
    width: 34px; height: 34px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px;
    flex-shrink: 0;
    border: 1px solid var(--border);
}

.avatar.agent { background: #1a2640; }
.avatar.user  { background: #1a2a1a; }

.bubble {
    max-width: 72%;
    padding: 12px 16px;
    border-radius: var(--radius);
    font-size: 13.5px;
    line-height: 1.65;
    border: 1px solid var(--border);
    word-break: break-word;
}

.bubble.agent { background: var(--agent-bg); color: var(--text); border-color: var(--border); }
.bubble.user  { background: var(--user-bg);  color: var(--text); border-color: #2a3a55; }

.bubble .ts {
    font-size: 10px;
    color: var(--text-dim);
    margin-top: 6px;
}

/* ── Pause banner ── */
.pause-banner {
    margin: 0 28px 12px;
    padding: 10px 16px;
    border-radius: 8px;
    background: #1c1400;
    border: 1px solid #854d0e;
    color: var(--accent2);
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ── Input bar ── */
.input-bar {
    padding: 16px 28px;
    border-top: 1px solid var(--border);
    background: var(--surface);
    flex-shrink: 0;
}

/* ── Override Streamlit inputs ── */
textarea, input[type="text"], input[type="number"] {
    background: #0d0f14 !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
}

textarea:focus, input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(74,222,128,0.15) !important;
}

/* ── Buttons ── */
.stButton > button {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    padding: 8px 20px !important;
    transition: all 0.2s !important;
    border: 1px solid var(--border) !important;
}

.stButton > button[kind="primary"],
.stButton > button:first-child {
    background: var(--accent) !important;
    color: #000 !important;
    border-color: var(--accent) !important;
}

.stButton > button:hover {
    filter: brightness(1.15) !important;
    transform: translateY(-1px) !important;
}

/* ── Selectbox ── */
[data-baseweb="select"] > div {
    background: #0d0f14 !important;
    border-color: var(--border) !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* ── Sidebar sections ── */
.sidebar-header {
    padding: 20px 20px 12px;
    border-bottom: 1px solid var(--border);
}

.sidebar-logo {
    font-family: 'Syne', sans-serif !important;
    font-size: 22px;
    font-weight: 800;
    color: var(--accent);
    letter-spacing: -0.5px;
}

.sidebar-sub {
    font-size: 10px;
    color: var(--text-dim);
    margin-top: 2px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

.thread-card {
    margin: 8px 12px;
    padding: 10px 14px;
    border-radius: 8px;
    background: var(--bg);
    border: 1px solid var(--border);
    font-size: 11px;
}

.thread-id {
    color: var(--accent);
    font-weight: 600;
    font-size: 11px;
    letter-spacing: 0.3px;
}

.thread-meta {
    color: var(--text-dim);
    font-size: 10px;
    margin-top: 3px;
}

.approval-section {
    margin: 8px 12px;
    padding: 14px;
    border-radius: 8px;
    background: #1a1200;
    border: 1px solid #854d0e;
}

.approval-title {
    font-family: 'Syne', sans-serif !important;
    font-size: 13px;
    font-weight: 700;
    color: var(--accent2);
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 6px;
}

.tool-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    background: #1e1000;
    border: 1px solid #92400e;
    color: var(--accent2);
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.5px;
}

.divider {
    height: 1px;
    background: var(--border);
    margin: 12px 0;
}

.section-label {
    font-size: 10px;
    color: var(--text-dim);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 6px;
}

/* ── JSON display ── */
.stJson {
    background: #0a0c10 !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-size: 11px !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

/* ── Approve / Reject button overrides ── */
.approve-btn > button {
    background: #14532d !important;
    color: var(--accent) !important;
    border-color: #166534 !important;
}

.reject-btn > button {
    background: #450a0a !important;
    color: var(--danger) !important;
    border-color: #7f1d1d !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────
if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"thread-{uuid.uuid4().hex[:8]}"

if "messages" not in st.session_state:
    st.session_state.messages = []   # list of {"role","content","ts"}

if "graph" not in st.session_state:
    @st.cache_resource
    def load_graph():
        from src.graph.checkpointer import get_checkpointer
        from src.graph.graph_builder import build_graph
        cp = get_checkpointer()
        return build_graph(cp)
    st.session_state.graph = load_graph()

graph = st.session_state.graph
thread_id = st.session_state.thread_id
config = {"configurable": {"thread_id": thread_id}}


# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────
def extract_text(message):
    if not message:
        return ""
    content = getattr(message, "content", "") if not isinstance(message, dict) else message.get("content", "")
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and "text" in item:
                parts.append(item["text"])
            elif hasattr(item, "text"):
                parts.append(item.text)
        return "\n".join(parts)
    return str(content)

def now_ts():
    return datetime.now().strftime("%H:%M")

def add_message(role, content):
    st.session_state.messages.append({
        "role": role,
        "content": content,
        "ts": now_ts()
    })


# ─────────────────────────────────────────
# ── SIDEBAR ──────────────────────────────
# ─────────────────────────────────────────
with st.sidebar:

    # Logo
    st.markdown("""
    <div class="sidebar-header">
        <div class="sidebar-logo">🛡️ SafeAgent</div>
        <div class="sidebar-sub">Human-in-the-Loop · v1.0</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Thread Info
    st.markdown('<div class="section-label" style="padding:0 12px">Active Thread</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="thread-card">
        <div class="thread-id">⬡ {thread_id}</div>
        <div class="thread-meta">Started {datetime.now().strftime("%b %d, %Y · %H:%M")}</div>
    </div>
    """, unsafe_allow_html=True)

    # New thread button
    st.markdown("<div style='padding:0 12px'>", unsafe_allow_html=True)
    if st.button("＋ New Thread", use_container_width=True):
        st.session_state.thread_id = f"thread-{uuid.uuid4().hex[:8]}"
        st.session_state.messages = []
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="divider" style="margin:14px 12px"></div>', unsafe_allow_html=True)

    # ── APPROVAL PANEL ───────────────────
    state = graph.get_state(config)

    if state.next:
        messages_state = state.values.get("messages", [])
        last_ai = messages_state[-1] if messages_state else None
        tool_call = None

        if last_ai and hasattr(last_ai, "tool_calls") and last_ai.tool_calls:
            tool_call = last_ai.tool_calls[0]

        if tool_call:
            st.markdown(f"""
            <div class="approval-title">
                ⚠ Approval Required
            </div>
            <div style="margin-bottom:8px">
                <span class="tool-badge">🔧 {tool_call['name']}</span>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("Tool Args", expanded=True):
                st.json(tool_call["args"])

            st.markdown('<div class="section-label" style="margin-top:10px">Reviewer</div>', unsafe_allow_html=True)
            reviewer_id = st.text_input("", placeholder="your-name", label_visibility="collapsed", key="reviewer")

            st.markdown('<div class="section-label">Decision</div>', unsafe_allow_html=True)
            decision_str = st.selectbox(
                "",
                ["approve", "edit", "reject"],
                label_visibility="collapsed",
                key="decision_select"
            )

            st.markdown('<div class="section-label">Reason (optional)</div>', unsafe_allow_html=True)
            reason = st.text_area("", placeholder="Why this decision?", label_visibility="collapsed",
                                  height=70, key="reason_text")

            if decision_str == "edit":
                st.markdown('<div class="section-label">Edit Args (JSON)</div>', unsafe_allow_html=True)
                edited_args_text = st.text_area(
                    "",
                    value=json.dumps(tool_call["args"], indent=2),
                    height=110,
                    label_visibility="collapsed",
                    key="edited_args"
                )
            else:
                edited_args_text = json.dumps(tool_call["args"], indent=2)

            col1, col2 = st.columns(2)

            with col1:
                resume_clicked = st.button(
                    "✓ Resume",
                    use_container_width=True,
                    type="primary",
                    key="resume_btn"
                )

            with col2:
                quick_reject = st.button(
                    "✕ Reject",
                    use_container_width=True,
                    key="quick_reject"
                )

            # Handle quick reject
            if quick_reject:
                decision_str = "reject"
                resume_clicked = True

            if resume_clicked:
                if not reviewer_id:
                    st.error("Enter reviewer name.")
                    st.stop()

                decision = ReviewDecision(
                    reviewer_id=reviewer_id,
                    decision=decision_str,
                    reason=reason or None
                )

                log_event({
                    "type": "review",
                    "reviewer": reviewer_id,
                    "decision": decision.decision,
                    "payload": tool_call
                })

                if decision.decision == "reject":
                    result = graph.invoke(
                        Command(resume={
                            "decisions": [{"decision": "reject", "edited_args": None}],
                            "tool_call": tool_call
                        }),
                        config=config,
                    )
                    response_text = extract_text(result["messages"][-1])
                    add_message("agent", f"❌ Tool rejected. {response_text}")

                elif decision.decision == "edit":
                    try:
                        edited_args = json.loads(edited_args_text)
                    except Exception:
                        st.error("Invalid JSON in edited args.")
                        st.stop()
                    final_tc = {**tool_call, "args": edited_args}
                    result = graph.invoke(
                        Command(resume={
                            "decisions": [{"decision": "edit", "edited_args": edited_args}],
                            "tool_call": final_tc
                        }),
                        config=config,
                    )
                    response_text = extract_text(result["messages"][-1])
                    add_message("agent", f"✏️ Tool executed with edited args. {response_text}")

                else:  # approve
                    final_tc = {**tool_call}
                    result = graph.invoke(
                        Command(resume={
                            "decisions": [{"decision": "approve", "edited_args": None}],
                            "tool_call": final_tc
                        }),
                        config=config,
                    )
                    response_text = extract_text(result["messages"][-1])
                    add_message("agent", f"✅ Tool approved & executed. {response_text}")

                st.rerun()

    else:
        st.markdown("""
        <div style="padding:0 12px">
            <div style="padding:12px 14px; border-radius:8px; background:#0d1a0d;
                        border:1px solid #166534; font-size:12px; color:#4ade80;">
                ✓ No pending approvals
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Stats at bottom
    st.markdown("<div style='flex:1'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="padding:12px; margin-top:20px; border-top:1px solid #1e2330; font-size:10px; color:#4b5563;">
        <div>Messages: {len(st.session_state.messages)}</div>
        <div style="margin-top:3px">Thread: ...{thread_id[-6:]}</div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────
# ── MAIN CHAT AREA ───────────────────────
# ─────────────────────────────────────────

# Header
state = graph.get_state(config)
status_color = "#facc15" if state.next else "#4ade80"
status_label = "AWAITING APPROVAL" if state.next else "READY"

st.markdown(f"""
<div class="chat-header">
    <div class="status-dot" style="background:{status_color}; box-shadow:0 0 8px {status_color}"></div>
    <div class="title">Safe Autonomous Agent</div>
    <div style="margin-left:auto; font-size:10px; color:{status_color};
                letter-spacing:1.5px; text-transform:uppercase;">{status_label}</div>
</div>
""", unsafe_allow_html=True)

# Pause banner
if state.next:
    st.markdown("""
    <div class="pause-banner">
        ⏸ Agent paused — review the tool request in the sidebar and approve, edit, or reject to continue.
    </div>
    """, unsafe_allow_html=True)

# Messages
st.markdown('<div class="messages-area" id="chat-messages">', unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("""
    <div style="text-align:center; padding:60px 20px; color:#374151;">
        <div style="font-size:36px; margin-bottom:12px">🛡️</div>
        <div style="font-family:'Syne',sans-serif; font-size:18px; font-weight:700; color:#4b5563">
            Safe Autonomous Agent
        </div>
        <div style="font-size:12px; color:#374151; margin-top:6px; max-width:340px; margin-inline:auto; line-height:1.6">
            Send a request. Dangerous actions (file writes, SQL, emails) will pause for your approval before executing.
        </div>
    </div>
    """, unsafe_allow_html=True)

for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]
    ts = msg.get("ts", "")
    avatar = "🧑" if role == "user" else "🤖"
    bubble_cls = "user" if role == "user" else "agent"
    row_cls = "user" if role == "user" else ""

    st.markdown(f"""
    <div class="msg-row {row_cls}">
        <div class="avatar {bubble_cls}">{avatar}</div>
        <div class="bubble {bubble_cls}">
            {content}
            <div class="ts">{ts}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)


# ── Input ──────────────────────────────
st.markdown('<div class="input-bar">', unsafe_allow_html=True)

col_input, col_btn = st.columns([5, 1])

with col_input:
    user_input = st.text_input(
        "",
        placeholder="Type a request… e.g. Send status email to team",
        label_visibility="collapsed",
        key="chat_input",
        disabled=state.next,  # disable while waiting for approval
    )

with col_btn:
    send = st.button("Send →", type="primary", disabled=state.next, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)


# ── Send handler ──
if send and user_input.strip():
    add_message("user", user_input.strip())

    current_state = graph.get_state(config)
    if current_state.next:
        add_message("agent", "⚠️ There's a pending approval. Please resolve it in the sidebar first.")
        st.rerun()

    with st.spinner("Agent thinking…"):
        result = graph.invoke(
            {"messages": [("user", user_input.strip())]},
            config=config,
        )

    new_state = graph.get_state(config)

    if new_state.next:
        add_message("agent", "⏸ I need to perform a sensitive action. Please review and approve it in the sidebar.")
    else:
        response_text = extract_text(result["messages"][-1])
        add_message("agent", response_text or "Done.")

    st.rerun()

# Auto-scroll script
st.markdown("""
<script>
    const area = document.getElementById('chat-messages');
    if (area) area.scrollTop = area.scrollHeight;
</script>
""", unsafe_allow_html=True)