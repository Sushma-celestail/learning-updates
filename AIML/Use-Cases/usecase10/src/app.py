from __future__ import annotations

import html
import json
import sys
import uuid
from pathlib import Path
from typing import Any

import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent))

from trading_floor import TradingFloorSwarm
from trading_floor.audit import verify_audit
from trading_floor.config import DEFAULT_CONFIG, PROJECT_ROOT
from trading_floor.tools import MOCK_PRICES


st.set_page_config(
    page_title="AI Trading Floor",
    page_icon="chart_with_upwards_trend",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Helpers (execution logic from file 1, UI helpers from file 2)
# ---------------------------------------------------------------------------

def render_text(text: str) -> str:
    """Render chat text safely (file 1 logic)."""
    text = html.escape(text or "")
    return text.replace("\n", "<br>")


def badge_for_message(item: dict[str, Any]) -> tuple[str, str]:  # retained for future use
    active = item.get("active_agent") or ""
    content = item.get("content", "")

    if item.get("role") == "user":
        return "YOU", "badge-user"
    if "Human approval" in content or "Human reviewer" in content:
        return "HITL", "badge-hitl"
    if "Risk agent:" in content or active == "risk_agent":
        return "RISK", "badge-risk"
    if "Execution agent:" in content or active == "execution_agent":
        return "EXEC", "badge-execution"
    if content.startswith("Blocked:") or active == "governance":
        return "SYSTEM", "badge-system"
    return "RESEARCH", "badge-research"


# build_flow is taken EXACTLY from file 1 (the working execution version)
def build_flow(prompt: str, turn) -> list[str]:
    if turn.response.startswith("Blocked: prompt-injection"):
        return ["User", "NeMo Guardrails", "Prompt-injection check", "Blocked"]

    if turn.response.startswith("Blocked:") or "I can only assist with" in turn.response:
        return ["User", "NeMo Guardrails", "Domain check", "Blocked"]

    if "remember that preference" in turn.response.lower():
        return ["User", "NeMo Guardrails", "Mem0 semantic memory saved", "audit.jsonl"]

    if "No trade was proposed" in turn.response:
        return ["User", "NeMo Guardrails", "Last active agent checkpoint", "Research Agent", "Mem0 memory lookup", "Web search", "Ticker lookup", "Response"]

    if turn.pending_approval:
        return ["User", "NeMo Guardrails", "Research Agent", "Risk Agent", "Output Guardrail", "Execution Agent", "interrupt()", "Human approval pending"]

    if turn.risk_decision and turn.risk_decision.status == "rejected":
        return ["User", "NeMo Guardrails", "Research Agent", "Risk Agent", "10% rule check", "Rejected", "Langfuse span", "audit.jsonl"]

    if turn.execution_report:
        return ["User", "NeMo Guardrails", "Research Agent", "Risk Agent", "Output Guardrail", "Execution Agent", "Mock Broker API", "audit.jsonl"]

    return ["User", "NeMo Guardrails", "Research Agent", "Response"]


def load_portfolio() -> dict[str, Any]:
    path = DEFAULT_CONFIG.portfolio_path
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"cash": DEFAULT_CONFIG.starting_cash_usd, "positions": {}}


def portfolio_total(portfolio: dict[str, Any]) -> float:
    total = float(portfolio.get("cash", 0.0))
    for symbol, shares in portfolio.get("positions", {}).items():
        total += float(shares) * MOCK_PRICES.get(symbol, 0.0)
    return round(total, 2)


def load_audit_entries(limit: int | None = None) -> list[dict[str, Any]]:
    path = DEFAULT_CONFIG.audit_path
    if not path.exists():
        return []
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return entries[-limit:] if limit else entries


def compute_eval_metrics() -> dict[str, Any]:
    entries = load_audit_entries()
    authorized = [
        e for e in entries
        if e.get("action") == "output_guardrail.execute_trade"
        and e.get("payload", {}).get("allowed")
    ]
    violations = [
        e for e in entries
        if e.get("action") == "output_guardrail.execute_trade"
        and not e.get("payload", {}).get("allowed")
    ]
    execute_calls = [e for e in entries if e.get("action") == "execute_trade"]
    risk_rejections = [
        e for e in entries
        if e.get("action") == "risk_decision"
        and e.get("payload", {}).get("status") == "rejected"
    ]
    input_blocks = [e for e in entries if e.get("action") == "input_guardrail.block"]

    return {
        "total_audit_entries": len(entries),
        "safety_violation_rate": round(len(violations) / max(1, len(authorized) + len(violations)), 4),
        "tool_call_accuracy": round(len(execute_calls) / max(1, len(authorized)), 4),
        "risk_rejections": len(risk_rejections),
        "input_guardrail_blocks": len(input_blocks),
    }


def render_message(item: dict[str, Any]) -> None:
    role = item.get("role", "assistant")
    content = render_text(item.get("content", ""))
    badge, badge_class = badge_for_message(item)

    if role == "user":
        st.markdown(
            f"""
            <div class="chat-row user">
                <div class="chat-bubble bubble-user">
                    <span class="agent-badge {badge_class}">{badge}</span><br>{content}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="chat-row assistant">
                <div class="chat-bubble bubble-agent">
                    <span class="agent-badge {badge_class}">{badge}</span><br>{content}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if item.get("handoffs"):
            st.markdown(
                "<div class='meta-row'>"
                + " ".join(
                    f"<span class='agent-chip'>{html.escape(h)}</span>"
                    for h in item["handoffs"]
                )
                + "</div>",
                unsafe_allow_html=True,
            )

        if item.get("flow"):
            with st.expander("Flow"):
                for step in item["flow"]:
                    st.write(step)


# ---------------------------------------------------------------------------
# CSS (from file 2)
# ---------------------------------------------------------------------------

st.markdown(
    """
<style>
.stApp {
    background: #0a0e1a;
    color: #e2e8f0;
}

.main .block-container {
    padding-top: 22px;
    padding-bottom: 110px;
}

[data-testid="stSidebar"] {
    background: #0f172a;
    border-right: 1px solid #1e293b;
}

[data-testid="stSidebar"] * {
    color: #e2e8f0;
}

.trading-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 24px 32px;
    margin-bottom: 22px;
    position: relative;
    overflow: hidden;
}

.trading-header:before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #6366f1, #22d3ee, #6366f1);
}

.trading-header h1 {
    font-size: 28px;
    font-weight: 700;
    color: #e2e8f0;
    margin: 0;
    letter-spacing: 0;
}

.trading-header p {
    color: #94a3b8;
    margin: 6px 0 0 0;
    font-size: 14px;
}

.chat-row {
    display: flex;
    width: 100%;
    margin: 14px 0;
}

.chat-row.user {
    justify-content: flex-end;
}

.chat-row.assistant {
    justify-content: flex-start;
}

.chat-bubble {
    max-width: 78%;
    border-radius: 10px;
    padding: 14px 18px;
    font-size: 15px;
    line-height: 1.6;
    border: 1px solid;
    overflow-wrap: anywhere;
    letter-spacing: 0;
}

.bubble-user {
    background: #1e293b;
    border-color: #334155;
    color: #e2e8f0;
}

.bubble-agent {
    background: #0f172a;
    border-color: #1e293b;
    color: #e2e8f0;
}

.agent-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.05em;
    margin-bottom: 7px;
}

.badge-user { background: #111827; color: #e5e7eb; border: 1px solid #374151; }
.badge-research { background: #1e3a8a; color: #93c5fd; border: 1px solid #3b82f6; }
.badge-risk { background: #4c1d95; color: #c4b5fd; border: 1px solid #8b5cf6; }
.badge-execution { background: #064e3b; color: #6ee7b7; border: 1px solid #10b981; }
.badge-system { background: #1e1e2e; color: #cbd5e1; border: 1px solid #475569; }
.badge-hitl { background: #78350f; color: #fde68a; border: 1px solid #f59e0b; }

.agent-chip {
    display: inline-block;
    padding: 4px 9px;
    border-radius: 999px;
    background: #111827;
    color: #cbd5e1;
    border: 1px solid #334155;
    margin-right: 6px;
    margin-top: 6px;
    font-size: 12px;
}

.meta-row {
    max-width: 960px;
    margin: -8px 0 12px 0;
}

.metric-card {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 8px;
    padding: 14px;
    text-align: center;
}

.metric-value {
    font-size: 24px;
    font-weight: 700;
    color: #22d3ee;
}

.metric-label {
    color: #94a3b8;
    font-size: 12px;
    text-transform: uppercase;
    margin-top: 4px;
}

.audit-ok { color: #22c55e; font-weight: 700; }
.audit-bad { color: #f87171; font-weight: 700; }

[data-testid="stChatInput"] textarea {
    background: #1e293b !important;
    color: #e2e8f0 !important;
    border: 1px solid #334155 !important;
    border-radius: 10px !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 8px;
    color: #cbd5e1;
    padding: 8px 14px;
}

[data-testid="stExpander"] {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 8px;
}

pre, code {
    color: #e2e8f0 !important;
}
</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Session state init (file 1 pattern, extended with file 2 fields)
# ---------------------------------------------------------------------------

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]
if "swarm" not in st.session_state:
    st.session_state.swarm = TradingFloorSwarm()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_approval" not in st.session_state:
    st.session_state.pending_approval = None


# ---------------------------------------------------------------------------
# Sidebar (UI from file 2, stack-status expander from file 1)
# ---------------------------------------------------------------------------

with st.sidebar:
    # Session
    st.markdown("### Session")
    trader_id = st.text_input("Trader ID", value="demo_trader")
    st.write(f"Session: `{st.session_state.session_id}`")
    active_agent = st.session_state.swarm._last_active_agent(trader_id) if hasattr(st.session_state.swarm, "_last_active_agent") else "research_agent"
    st.write(f"Active Agent: `{active_agent}`")

    st.divider()

    # Portfolio
    st.markdown("### Portfolio")
    try:
        portfolio = load_portfolio()
        cash = float(portfolio.get("cash", 0.0))
        total = portfolio_total(portfolio)
        col1, col2 = st.columns(2)
        col1.metric("Cash", f"${cash:,.0f}")
        col2.metric("Total Value", f"${total:,.0f}")

        positions = portfolio.get("positions", {})
        if positions:
            st.markdown("**Positions**")
            for symbol, shares in positions.items():
                value = float(shares) * MOCK_PRICES.get(symbol, 0.0)
                st.write(f"{symbol}: {shares} share(s) — ${value:,.2f}")
        else:
            st.caption("No open positions")
    except Exception as exc:
        st.caption(f"Portfolio unavailable: {exc}")

    st.divider()

    # Risk Controls
    st.markdown("### Risk Controls")
    st.write("Max single-stock limit: **10%**")
    st.write("HITL threshold: **$1,000**")

    st.divider()

    # Governance
    st.markdown("### Governance")
    ok, _ = verify_audit(DEFAULT_CONFIG.audit_path)
    st.write(f"Audit: **{'Verified ✓' if ok else 'Failed ✗'}**")

    stack_status = st.session_state.swarm.strict_stack_status()
    langfuse_ok = stack_status.get("langfuse_configured", False)
    st.write(f"Langfuse: **{'Configured ✓' if langfuse_ok else 'Not configured'}**")

    memory_backend = stack_status.get("memory", {}).get("backend", "local")
    st.write(f"Memory: **{memory_backend}**")

# ---------------------------------------------------------------------------
# Main area header (file 2 UI)
# ---------------------------------------------------------------------------

st.markdown(
    """
<div class="trading-header">
  <h1>Multi-Agent Trading Floor</h1>
  <p>Research Agent | Risk Agent | Execution Agent | Memory | Safety | Governance | HITL</p>
</div>
""",
    unsafe_allow_html=True,
)

tab_chat, tab_diagram, tab_audit, tab_eval = st.tabs(
    ["Trading Chat", "Swarm Diagram", "Audit Log", "Evaluation"]
)


# ---------------------------------------------------------------------------
# Tab: Trading Chat
# Execution logic is taken EXACTLY from file 1.
# UI rendering (render_message, badges) is from file 2.
# ---------------------------------------------------------------------------

with tab_chat:
    # ---- Exact rendering loop from file 1 ----
    for item in st.session_state.messages:
        role = item["role"]
        content = render_text(item["content"])

        st.markdown(
            f"""
            <div class="chat-row {html.escape(role)}">
                <div class="chat-bubble">{content}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if item.get("handoffs"):
            st.markdown(
                "<div class='meta-row'>"
                + " ".join([f"<span class='agent-chip'>{html.escape(h)}</span>" for h in item["handoffs"]])
                + "</div>",
                unsafe_allow_html=True,
            )
        if item.get("flow"):
            with st.expander("Flow"):
                for step in item["flow"]:
                    st.write(step)

    # Quick-prompt handler (sidebar buttons) — uses same file 1 execution path
    if "quick_prompt" in st.session_state:
        prompt = st.session_state.quick_prompt
        del st.session_state.quick_prompt

        st.session_state.messages.append({"role": "user", "content": prompt})
        turn = st.session_state.swarm.process(prompt, trader_id=trader_id)
        st.session_state.pending_approval = turn.pending_approval
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": turn.response,
                "handoffs": turn.handoffs,
                "memories": [],
                "flow": build_flow(prompt, turn),
            }
        )
        st.rerun()

    # ---- Exact HITL block from file 1 ----
    if st.session_state.pending_approval:
        st.warning("Human approval required before this mock trade can execute.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Approve trade", type="primary"):
                turn = st.session_state.swarm.approve_pending(st.session_state.pending_approval, True, trader_id)
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": turn.response,
                        "handoffs": turn.handoffs,
                        "memories": [],
                        "flow": ["Human reviewer", "Execution Agent", "Mock Broker API", "audit.jsonl"],
                    }
                )
                st.session_state.pending_approval = None
                st.rerun()
        with col2:
            if st.button("Reject trade"):
                turn = st.session_state.swarm.approve_pending(st.session_state.pending_approval, False, trader_id)
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": turn.response,
                        "handoffs": turn.handoffs,
                        "memories": [],
                        "flow": ["Human reviewer", "Execution Agent", "Broker call skipped", "audit.jsonl"],
                    }
                )
                st.session_state.pending_approval = None
                st.rerun()

    # ---- Exact chat input block from file 1 ----
    prompt = st.chat_input("Ask for research, risk review, or a mock paper trade")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        turn = st.session_state.swarm.process(prompt, trader_id=trader_id)
        st.session_state.pending_approval = turn.pending_approval
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": turn.response,
                "handoffs": turn.handoffs,
                "memories": [],
                "flow": build_flow(prompt, turn),
            }
        )
        st.rerun()


# ---------------------------------------------------------------------------
# Tab: Swarm Diagram (file 2 UI)
# ---------------------------------------------------------------------------

with tab_diagram:
    st.markdown("### Swarm Architecture Diagram")

    png_path = PROJECT_ROOT / "assets" / "swarm_diagram.png"
    mmd_path = PROJECT_ROOT / "assets" / "swarm_diagram.mmd"

    if png_path.exists():
        st.image(str(png_path), use_container_width=True)
    else:
        st.info("Diagram PNG not found.")

    if mmd_path.exists():
        with st.expander("Mermaid Source"):
            st.code(mmd_path.read_text(encoding="utf-8"), language="mermaid")

    st.markdown("### Agent Responsibilities")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
**Research Agent**

- Web search market brief
- Ticker lookup
- Trade idea generation
- Handoff to Risk Agent
"""
        )

    with col2:
        st.markdown(
            """
**Risk Agent**

- 10% single-stock limit
- HITL threshold check
- Risk rejection span
- Handoff to Execution Agent
"""
        )

    with col3:
        st.markdown(
            """
**Execution Agent**

- Output guardrail
- LangGraph interrupt()
- Human approval/rejection
- Mock broker execution
"""
        )


# ---------------------------------------------------------------------------
# Tab: Audit Log (file 2 UI)
# ---------------------------------------------------------------------------

with tab_audit:
    st.markdown("### Immutable Audit Log")

    ok, chain_msg = verify_audit(DEFAULT_CONFIG.audit_path)
    if ok:
        st.success(chain_msg)
    else:
        st.error(chain_msg)

    entries = load_audit_entries(limit=50)
    st.metric("Showing Entries", len(entries))

    if entries:
        for entry in reversed(entries):
            timestamp = entry.get("timestamp", "")[:19]
            action = entry.get("action", "unknown")
            actor = entry.get("actor", "unknown")
            entry_hash = entry.get("hash", "")[:12]
            payload = entry.get("payload", {})

            with st.expander(f"{timestamp} | {action} | {actor} | {entry_hash}..."):
                st.json(payload)
                st.caption(f"previous_hash: {entry.get('previous_hash')}")
                st.caption(f"hash: {entry.get('hash')}")
    else:
        st.info("No audit entries yet. Start chatting to generate audit logs.")


# ---------------------------------------------------------------------------
# Tab: Evaluation (file 2 UI)
# ---------------------------------------------------------------------------

with tab_eval:
    st.markdown("### Daily Evaluation Report")

    if st.button("Refresh Metrics"):
        st.rerun()

    # Always recompute fresh from disk on every render
    metrics = compute_eval_metrics()

    col1, col2 = st.columns(2)
    col1.metric("Audit Entries", metrics["total_audit_entries"])
    col2.metric("Tool Call Accuracy", f"{metrics['tool_call_accuracy']:.1%}")

    st.markdown("### Evaluation Details")
    display_metrics = {
        "total_audit_entries": metrics["total_audit_entries"],
        "tool_call_accuracy": metrics["tool_call_accuracy"],
        "input_guardrail_blocks": metrics["input_guardrail_blocks"],
    }
    st.json(display_metrics)

    st.caption("Metrics recompute fresh from audit.jsonl on each render. Click Refresh Metrics to force an update.")