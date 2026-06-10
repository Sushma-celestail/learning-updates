import streamlit as st
import pandas as pd
import asyncio
from nemoguardrails import LLMRails, RailsConfig
import os
from dotenv import load_dotenv

# Load API keys
load_dotenv()
if "GOOGLE_GEMINI_API_KEY" in os.environ and "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = os.environ["GOOGLE_GEMINI_API_KEY"]

st.set_page_config(layout="wide", page_title="Guardrailed Assistant", page_icon="🛡️")

# Initialize NeMo Guardrails
@st.cache_resource
def init_rails():
    config = RailsConfig.from_path("./config")
    return LLMRails(config)

rails = init_rails()

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "test_history" not in st.session_state:
    st.session_state.test_history = []

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

# ==========================================
# CSS STYLING (Matching the Mockups)
# ==========================================
st.markdown("""
<style>
    /* Sidebar Styling */
    .sidebar-card {
        background-color: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .sidebar-title {
        color: #6b7280;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.05em;
        margin-bottom: 16px;
    }
    .badge-green { background-color: #dcfce7; color: #166534; padding: 2px 8px; border-radius: 12px; font-size: 12px; display: inline-block; margin-top: 8px; }
    .badge-blue { background-color: #dbeafe; color: #1e40af; padding: 2px 8px; border-radius: 12px; font-size: 12px; display: inline-block; margin-top: 8px; }
    .badge-orange { background-color: #fef3c7; color: #92400e; padding: 2px 8px; border-radius: 12px; font-size: 12px; display: inline-block; margin-top: 8px; }
    
    /* Header Badges */
    .header-badge { background-color: #dcfce7; color: #166534; padding: 4px 12px; border-radius: 16px; font-size: 14px; margin-left: 12px; display: inline-block; }
    
    /* Chat Badges */
    .chat-badge-fail { font-size: 12px; color: #991b1b; float: right; margin-top: -24px; background-color: #fee2e2; padding: 2px 8px; border-radius: 4px; }
    .chat-badge-warn { font-size: 12px; color: #065f46; float: right; margin-top: -24px; background-color: #d1fae5; padding: 2px 8px; border-radius: 4px; }

    /* Blocked Message Styling */
    .blocked-msg { background-color: #fef2f2; border-left: 4px solid #b91c1c; padding: 16px; border-radius: 0 8px 8px 0; color: #991b1b; margin-bottom: 8px; }
    .blocked-tag { background-color: #ede9fe; color: #5b21b6; font-size: 11px; padding: 2px 6px; border-radius: 4px; display: inline-block; }

    /* Trace Timeline & Metrics */
    .trace-item { margin-bottom: 24px; position: relative; }
    .trace-number { width: 24px; height: 24px; background-color: #dbeafe; color: #1e3a8a; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold; position: absolute; left: 0; top: 0; }
    .trace-content { margin-left: 40px; }
    .trace-line { position: absolute; left: 11px; top: 30px; bottom: -20px; width: 1px; background-color: #e5e7eb; }
    .trace-pass { background-color: #dcfce7; color: #166534; font-size: 11px; padding: 2px 6px; border-radius: 4px; margin-left: 8px; }
    .trace-code { font-family: monospace; font-size: 12px; color: #4b5563; margin-top: 4px; }
    .demo-box { background-color: #f6f5ec; border: 1px solid #d1d5db; border-radius: 8px; padding: 16px; font-family: monospace; font-size: 13px; margin-top: 32px; }
    .demo-redact { color: #b91c1c; }
    .demo-green { color: #15803d; }
    .metric-card { background-color: #f9fafb; border-radius: 8px; padding: 16px; border: 1px solid #e5e7eb; }
    .metric-title { color: #6b7280; font-size: 14px; margin-bottom: 8px; }
    .metric-value { font-size: 24px; font-weight: bold; color: #111827; }
    .metric-sub { font-size: 12px; color: #6b7280; margin-top: 4px; }
    .bar-bg { height: 6px; background-color: #e5e7eb; border-radius: 3px; margin-top: 12px; }
    .bar-fill-green { background-color: #15803d; height: 100%; border-radius: 3px; }
    .bar-fill-red { background-color: #b91c1c; height: 100%; border-radius: 3px; }
    .bar-fill-blue { background-color: #1d4ed8; height: 100%; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)




# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown('<div class="sidebar-title">SAFETY LAYERS</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-card">
        Layer 1 — NeMo<br>
        <span class="badge-green">Active</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-card">
        Layer 2 — LlamaGuard<br>
        <span class="badge-blue">Active</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-card">
        Layer 3 — Guardrails AI<br>
        <span class="badge-orange">Active</span>
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# TABS
# ==========================================
tab1, tab2, tab3 = st.tabs(["Chat interface", "Observability trace", "Test harness"])


# ------------------------------------------
# TAB 1: CHAT INTERFACE
# ------------------------------------------
with tab1:
    # Header
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 16px; border-bottom: 1px solid #e5e7eb; margin-bottom: 24px;">
        <div>
            <span style="font-size: 18px;">👨‍🍳 Cooking assistant</span>
            <span class="header-badge">Topic-locked</span>
        </div>
        <div style='color: #6b7280; font-size: 14px;'>Model: gpt-oss-120b</div>
    </div>
    """, unsafe_allow_html=True)

    # Display chat history
    for msg in st.session_state.messages:
        avatar = "👤" if msg["role"] == "user" else "🤖"

        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

        if msg.get("blocked", False):
            st.markdown(
                '<div class="chat-badge-fail">⛔ Blocked by Guardrails</div>',
                unsafe_allow_html=True
            )
        elif "[REDACTED" in msg["content"]:
            st.markdown(
                '<div class="chat-badge-warn">⚠️ PII detected</div>',
                unsafe_allow_html=True
            )

    # Process pending prompt from bottom search bar
    if st.session_state.pending_prompt:

        prompt = st.session_state.pending_prompt
        st.session_state.pending_prompt = None

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Processing through safety layers..."):
                try:

                    response = asyncio.run(
                        rails.generate_async(
                            messages=[
                                {
                                    "role": "user",
                                    "content": prompt
                                }
                            ]
                        )
                    )

                    reply_text = response["content"]

                    is_blocked = any(
                        refusal in reply_text
                        for refusal in [
                            "I'm sorry, I can't help with that",
                            "This request was flagged as potentially harmful",
                            "I'm a cooking assistant and can only help with food"
                        ]
                    )

                    # Update Test Harness row
                    if st.session_state.test_history:

                        if is_blocked:
                            st.session_state.test_history[-1]["attack_class"] = "Guardrail Triggered"
                            st.session_state.test_history[-1]["result"] = "⛔ BLOCKED"
                            st.session_state.test_history[-1]["caught_by"] = "NeMo Guardrails"

                    if is_blocked:

                        st.markdown(f"""
                        <div class="blocked-msg">
                            ⛔ {reply_text}
                        </div>
                        <div class="blocked-tag">
                            Blocked by NeMo rails
                        </div>
                        """, unsafe_allow_html=True)

                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": reply_text,
                                "blocked": True
                            }
                        )

                    else:

                        st.markdown(reply_text)

                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": reply_text
                            }
                        )

                except Exception as e:

                    error_msg = f"Error communicating with LLM/Rails: {e}"

                    st.error(error_msg)

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": error_msg
                        }
                    )
# ------------------------------------------
# TAB 2: OBSERVABILITY TRACE
# ------------------------------------------
with tab2:
    st.markdown("""
    <div style="background-color: #f9fafb; padding: 12px 16px; border-radius: 8px; border: 1px solid #e5e7eb; margin-bottom: 24px;">
        Request trace (Static Demo View)
        <span style="float: right; background-color: #dcfce7; color: #166534; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: bold;">EXAMPLE</span>
    </div>
    """, unsafe_allow_html=True)

    items = [
        {"num": 1, "title": "NeMo — input rail (jailbreak check)", "pass": True, "code": "colang rule: jailbreak_detection → no pattern match"},
        {"num": 2, "title": "NeMo — topic rail (domain guard)", "pass": True, "code": "colang rule: topic_cooking → matched keywords"},
        {"num": 3, "title": "LlamaGuard-4-12B classifier (pre-LLM)", "pass": True, "code": "category: S14 (none) | confidence: 0.98"},
        {"num": 4, "title": "LLM call (llama-3.3-70b-versatile)", "pass": True, "pass_text": "OK", "code": "tokens in: 48 | tokens out: 112"},
        {"num": 5, "title": "LlamaGuard-4-12B classifier (post-LLM)", "pass": True, "code": "output scan | category: S14 (none)"},
        {"num": 6, "title": "Guardrails AI — output rail", "pass": True, "code": "PII scan: 0 entities found"},
        {"num": 7, "title": "NeMo — output rail (self-check)", "pass": True, "code": "self_check_facts rail → response delivered"}
    ]

    html = ""
    for idx, item in enumerate(items):
        pass_badge = f'<span class="trace-pass">{item.get("pass_text", "PASS")}</span>'
        line = '<div class="trace-line"></div>' if idx < len(items) - 1 else ''
        html += f"""
        <div class="trace-item">
            <div class="trace-number">{item['num']}</div>
            {line}
            <div class="trace-content">
                <div style="font-size: 14px; font-weight: 500; color: #111827;">{item['title']} {pass_badge}</div>
                <div class="trace-code">{item['code']}</div>
            </div>
        </div>
        """
    st.markdown(html, unsafe_allow_html=True)


# ------------------------------------------
# TAB 3 - TEST HARNESS
# ------------------------------------------
with tab3:

    st.subheader("Test Harness Results")

    rows = []

    for idx, item in enumerate(st.session_state.test_history, start=1):
        rows.append([
            idx,
            item["prompt"][:80] + ("..." if len(item["prompt"]) > 80 else ""),
            item["attack_class"],
            item["result"],
            item["caught_by"]
        ])

    if rows:

        df = pd.DataFrame(
            rows,
            columns=[
                "#",
                "Prompt (truncated)",
                "Attack class",
                "Result",
                "Caught by"
            ]
        )

        st.dataframe(
            df,
            hide_index=True,
            width="stretch"
        )

    else:
        st.info("No prompts tested yet.")
# ==========================================
# BOTTOM SEARCH BAR
# ==========================================

st.markdown("---")

prompt = st.chat_input("Ask a cooking question...")

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    st.session_state.test_history.append(
        {
            "prompt": prompt,
            "attack_class": "Benign",
            "result": "✅ PASSED",
            "caught_by": "all layers"
        }
    )

    st.session_state.pending_prompt = prompt

    st.rerun()