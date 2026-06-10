from __future__ import annotations

import json
from typing import Any

from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph_swarm import create_handoff_tool, create_swarm

from .config import DEFAULT_CONFIG, GovernanceConfig
from .llm import build_gemini_llm
from .risk import RiskEngine
from .tools import MOCK_PRICES, ticker_lookup, web_search_market_brief


@tool
def web_search(query: str) -> str:
    """Search for a short market brief about a stock, sector, or ticker."""
    symbol = query.upper().strip().split()[-1]
    for known in MOCK_PRICES:
        if known in query.upper():
            symbol = known
            break
    return web_search_market_brief(symbol)


@tool
def lookup_ticker(symbol: str) -> str:
    """Look up the latest configured mock quote for a ticker symbol."""
    return json.dumps(ticker_lookup(symbol), sort_keys=True)


@tool
def risk_gate(symbol: str, quantity: int, price: float, portfolio_value: float = 25000.0) -> str:
    """Evaluate a proposed trade against the 10 percent single-stock portfolio limit."""
    from .models import TradeIdea

    idea = TradeIdea(symbol=symbol.upper(), side="buy", quantity=int(quantity), price=float(price), rationale="swarm risk gate")
    decision = RiskEngine(DEFAULT_CONFIG).evaluate(idea, portfolio_value=float(portfolio_value))
    return json.dumps(decision.__dict__, sort_keys=True)


@tool
def execute_trade_authorized(symbol: str, quantity: int, price: float, risk_status: str) -> str:
    """Prepare a mock broker order only when the risk agent says approved or needs_human_approval."""
    status = risk_status.lower().strip()
    if status not in {"approved", "needs_human_approval"}:
        return json.dumps({"status": "blocked", "reason": "risk gate did not authorize execution"})
    notional = round(int(quantity) * float(price), 2)
    if notional > DEFAULT_CONFIG.hitl_threshold_usd:
        return json.dumps({"status": "needs_human_approval", "notional": notional})
    return json.dumps({"status": "ready_for_mock_broker", "symbol": symbol.upper(), "quantity": int(quantity), "price": float(price), "notional": notional})


class GeminiSwarmRuntime:
    """Strict-stack LangGraph Swarm runtime with last-active-agent checkpointing."""

    def __init__(self, config: GovernanceConfig = DEFAULT_CONFIG):
        self.config = config
        self.checkpointer = InMemorySaver()
        self.graph = None

    def compile(self):
        llm = build_gemini_llm(self.config)

        to_research = create_handoff_tool(
            agent_name="research_agent",
            description="Transfer to Research when ticker research or trade ideation is needed.",
        )
        to_risk = create_handoff_tool(
            agent_name="risk_agent",
            description="Transfer to Risk before any trade can be executed.",
        )
        to_execution = create_handoff_tool(
            agent_name="execution_agent",
            description="Transfer to Execution only after the risk gate approves or requests HITL.",
        )

        research_agent = create_react_agent(
            llm,
            tools=[web_search, lookup_ticker, to_risk, to_execution],
            name="research_agent",
            prompt=(
                "You are the Research agent on a paper-trading floor. Use web_search and lookup_ticker "
                "to produce a concise trade idea. Never execute. Handoff to risk_agent for approval."
            ),
        )
        risk_agent = create_react_agent(
            llm,
            tools=[risk_gate, to_research, to_execution],
            name="risk_agent",
            prompt=(
                "You are the Risk agent. Evaluate every proposed trade with risk_gate. Reject trades "
                "above the 10 percent single-stock limit. Handoff to execution_agent only for approved "
                "or needs_human_approval decisions."
            ),
        )
        execution_agent = create_react_agent(
            llm,
            tools=[execute_trade_authorized, to_risk, to_research],
            name="execution_agent",
            prompt=(
                "You are the Execution agent. You may only prepare a mock broker order with "
                "execute_trade_authorized after a risk-agent approval. If the notional exceeds $1,000, "
                "request human approval instead of claiming execution."
            ),
        )

        self.graph = create_swarm(
            agents=[research_agent, risk_agent, execution_agent],
            default_active_agent="research_agent",
        ).compile(checkpointer=self.checkpointer)
        return self.graph

    def invoke(self, message: str, trader_id: str = "demo_trader") -> dict[str, Any]:
        graph = self.graph or self.compile()
        return graph.invoke(
            {"messages": [{"role": "user", "content": message}]},
            config={"configurable": {"thread_id": trader_id}},
        )
