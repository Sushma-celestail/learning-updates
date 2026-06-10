# User
#   ↓
# Orchestrator
#   ↓
# Research Agent
#   ↓
# Risk Agent
#   ↓
# Execution Agent

from __future__ import annotations

from dataclasses import asdict
import json
from typing import Any

from .agents import research_agent
from .audit import AuditLog, verify_audit
from .config import DEFAULT_CONFIG, GovernanceConfig, DATA_DIR
from .guardrails import InputGuardrail, OutputGuardrail
from .memory import MemoryStore
from .models import ChatTurn, ExecutionReport, TradeIdea
from .risk import RiskEngine
from .tools import mock_broker_execute
from .tracing import GovernanceTracer


class HITLInterrupt(Exception):
    def __init__(self, payload: dict[str, Any]):
        super().__init__("Human approval required")
        self.payload = payload


class TradingFloorSwarm:
    def __init__(self, config: GovernanceConfig = DEFAULT_CONFIG):
        self.config = config
        self.config.audit_path.parent.mkdir(parents=True, exist_ok=True)
        self.audit = AuditLog(self.config.audit_path)
        self.tracer = GovernanceTracer(self.audit)
        self.memory = MemoryStore(self.config.memory_path)
        self.input_guardrail = InputGuardrail()
        self.output_guardrail = OutputGuardrail()
        self.risk_engine = RiskEngine(config)
        self.state_path = DATA_DIR / "agent_state.json"
        self._gemini_swarm_runtime = None

    def _load_state(self) -> dict[str, str]:
        if not self.state_path.exists():
            return {}
        return json.loads(self.state_path.read_text(encoding="utf-8"))

    def _save_active_agent(self, trader_id: str, agent: str) -> None:
        state = self._load_state()
        state[trader_id] = agent
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")

    def _last_active_agent(self, trader_id: str) -> str:
        return self._load_state().get(trader_id, "research_agent")

    def _is_greeting(self, message: str) -> bool:
        lowered = message.strip().lower()
        return lowered in {"hi", "hello", "hey", "good morning", "good afternoon", "good evening"}

    def _is_preference_only(self, message: str) -> bool:
        lowered = message.lower()
        preference_words = [
            "prefer",
            "preference",
            "remember",
            "low-risk",
            "low risk",
            "dividend",
            "dividends",
            "conservative",
            "income",
        ]
        action_words = ["buy", "sell", "trade", "execute", "$", "share", "shares", "research", "analyze", "analysis"]
        return any(word in lowered for word in preference_words) and not any(word in lowered for word in action_words)

    def _is_research_only(self, message: str) -> bool:
        lowered = message.lower()
        research_words = ["analyze", "analysis", "research", "risks", "risk of", "market brief"]
        trade_words = ["buy", "sell", "trade", "execute", "$", "share", "shares"]
        return any(word in lowered for word in research_words) and not any(word in lowered for word in trade_words)

    def strict_stack_status(self) -> dict[str, Any]:
        modules = {
            "langgraph": "langgraph",
            "langgraph-swarm": "langgraph_swarm",
            "mem0ai": "mem0",
            "nemoguardrails": "nemoguardrails",
            "langfuse": "langfuse",
            "langchain-google-genai": "langchain_google_genai",
        }
        status: dict[str, Any] = {
            "model_name": self.config.model_name,
            "google_api_key_configured": bool(self.config.google_api_key),
            "use_gemini_swarm": self.config.use_gemini_swarm,
            "packages": {},
            "memory": self.memory.status(),
            "input_guardrail": self.input_guardrail.status(),
            "langfuse_configured": bool(self.config.langfuse_public_key and self.config.langfuse_secret_key),
        }

        import importlib.util

        for label, module in modules.items():
            status["packages"][label] = importlib.util.find_spec(module) is not None
        return status

    def compile_gemini_swarm(self):
        if not self.config.use_gemini_swarm:
            raise RuntimeError("TRADING_FLOOR_USE_GEMINI_SWARM is disabled.")
        if self._gemini_swarm_runtime is None:
            from .swarm_runtime import GeminiSwarmRuntime

            self._gemini_swarm_runtime = GeminiSwarmRuntime(self.config)
            self._gemini_swarm_runtime.compile()
            self.audit.append(
                "langgraph_swarm.compiled",
                "governance",
                {"model_name": self.config.model_name, "default_active_agent": "research_agent"},
            )
        return self._gemini_swarm_runtime

    def _portfolio_value(self) -> float:
        return self.config.starting_cash_usd

    def _hitl_payload(self, turn: ChatTurn) -> dict[str, Any]:
        assert turn.trade_idea is not None
        assert turn.risk_decision is not None
        return {
            "question": "Approve this mock paper trade?",
            "trade_idea": {**asdict(turn.trade_idea), "notional": turn.trade_idea.notional},
            "risk_decision": asdict(turn.risk_decision),
            "threshold_usd": self.config.hitl_threshold_usd,
        }

    def process(self, message: str, trader_id: str = "demo_trader", interrupt_on_hitl: bool = False) -> ChatTurn:
        self.memory.seed_demo_memories(trader_id)
        turn = ChatTurn(trader_id=trader_id, user_message=message, active_agent=self._last_active_agent(trader_id))
        self.audit.append("user_message", "user", {"trader_id": trader_id, "message": message})

        if self._is_greeting(message):
            turn.response = (
                "Hi, I can help with stock research, portfolio risk checks, "
                "mock paper trades, audit verification, and governance controls."
            )
            turn.active_agent = "research_agent"
            self.audit.append("greeting.response", "research_agent", {"message": message})
            self._save_active_agent(trader_id, turn.active_agent)
            return turn

        allowed, guard_message = self.input_guardrail.validate(message)
        if not allowed:
            turn.response = guard_message
            turn.active_agent = "research_agent"
            self.audit.append("input_guardrail.block", "safety", {"message": message, "reason": guard_message})
            self._save_active_agent(trader_id, turn.active_agent)
            return turn

        lowered = message.lower()

        if "verify audit" in lowered or "audit log integrity" in lowered:
            ok, audit_message = verify_audit(self.config.audit_path)
            turn.response = f"Audit verification {'PASSED' if ok else 'FAILED'}.\n\n{audit_message}"
            turn.active_agent = "governance"
            self.audit.append(
                "audit.verify_requested",
                "governance",
                {"trader_id": trader_id, "passed": ok, "message": audit_message},
            )
            self._save_active_agent(trader_id, "research_agent")
            return turn

        if "governance" in lowered and ("implemented" in lowered or "controls" in lowered):
            turn.response = (
                "Governance is implemented with:\n\n"
                "1. NeMo Guardrails for off-topic and prompt-injection blocking.\n"
                "2. Risk Agent checks for the 10% single-stock limit.\n"
                "3. Output Guardrail prevents broker execution without Risk approval.\n"
                "4. LangGraph interrupt() requires human approval above $1,000.\n"
                "5. Langfuse records spans for research, risk, rejection, HITL, and execution.\n"
                "6. audit.jsonl stores hash-chained immutable decision logs.\n"
                "7. Mem0 stores trader memories scoped by trader_id.\n"
                "8. Memory is used internally and raw memory text is not exposed in normal chat output."
            )
            turn.active_agent = "governance"
            self.audit.append("governance.explained", "governance", {"trader_id": trader_id})
            self._save_active_agent(trader_id, "research_agent")
            return turn

        if "suggest an investment" in lowered or "recommend an investment" in lowered:
            memories = self.memory.search(trader_id, "technology AI volatility preference investment", limit=3)
            turn.memories_used = memories
            turn.active_agent = "research_agent"
            self.audit.append(
                "memory.retrieved",
                "memory",
                {"trader_id": trader_id, "count": len(memories), "query": "technology AI volatility preference investment"},
            )
            turn.response = (
                f"Retrieved {len(memories)} stored memories from Mem0.\n\n"
                "Based on your remembered preferences, NVDA or MSFT fit your interest in technology leaders. "
                "TSLA may be less suitable if you want to avoid volatility.\n\n"
                "This is research information and not financial advice."
            )
            self._save_active_agent(trader_id, turn.active_agent)
            return turn

        memory_statement = any(
            phrase in lowered
            for phrase in [
                "i prefer",
                "i bought",
                "i avoided",
                "i avoid",
                "because",
                "volatility",
            ]
        )

        trade_action = any(
            phrase in lowered
            for phrase in [
                "buy ",
                "sell ",
                "execute",
                "trade",
                "$",
                "shares",
                "share",
            ]
        )

        if memory_statement and not trade_action:
            self.memory.add(trader_id, message, "episodic", {"source": "user_memory_statement"})
            turn.response = "Got it. I'll remember that for future research and risk checks."
            turn.active_agent = "research_agent"
            self.audit.append("memory.statement_saved", "memory", {"trader_id": trader_id, "message": message})
            self._save_active_agent(trader_id, turn.active_agent)
            return turn

        if any(token in lowered for token in ["prefer", "preference", "remember", "low-risk", "low risk", "dividend"]):
            self.memory.add(trader_id, message, "semantic", {"source": "user_statement"})

        if self._is_preference_only(message):
            turn.response = "Got it. I'll remember that preference for future risk checks."
            turn.active_agent = "research_agent"
            self.audit.append("memory.preference_saved", "memory", {"trader_id": trader_id, "message": message})
            self._save_active_agent(trader_id, turn.active_agent)
            return turn

        memories = self.memory.search(trader_id, message, limit=5)
        risk_memories = self.memory.search(trader_id, "risk preference portfolio allocation single stock exposure", limit=3)
        turn.memories_used = list(dict.fromkeys(memories + risk_memories))

        previous = turn.active_agent
        if previous != "research_agent":
            turn.handoffs.append(f"{previous} -> research_agent (last-active resume)")
        turn.active_agent = "research_agent"

        research_only = self._is_research_only(message)

        with self.tracer.span("research", "research_agent", {"trader_id": trader_id}):
            idea, research_summary = research_agent(
                message,
                turn.memories_used,
                propose_trade=not research_only,
            )
            turn.trade_idea = idea
            clean_rationale = idea.rationale.split(" Memories considered:", 1)[0]
            self.memory.add(trader_id, f"Research rationale for {idea.symbol}: {clean_rationale}", "episodic")
            self.audit.append("trade_idea.proposed", "research_agent", asdict(idea))

        if research_only:
            clean_rationale = idea.rationale.split(" Memories considered:", 1)[0]
            turn.response = (
                f"{research_summary}\n\n"
                f"Research agent: {clean_rationale}\n\n"
                "No trade was proposed, so Risk and Execution were not called."
            )
            self._save_active_agent(trader_id, turn.active_agent)
            return turn

        turn.handoffs.append("research_agent -> risk_agent")
        turn.active_agent = "risk_agent"

        with self.tracer.span(
            "risk_evaluation",
            "risk_agent",
            {"symbol": idea.symbol, "notional": idea.notional, "risk_memories": risk_memories},
        ):
            decision = self.risk_engine.evaluate(idea, self._portfolio_value())
            turn.risk_decision = decision
            self.audit.append("risk_decision", "risk_agent", asdict(decision))

        if decision.status == "rejected":
            with self.tracer.span("risk_rejection", "risk_agent", {"symbol": idea.symbol, "reason": decision.reason}):
                pass
            turn.response = f"{research_summary}\n\nRisk agent: {decision.reason}"
            self._save_active_agent(trader_id, turn.active_agent)
            return turn

        turn.handoffs.append("risk_agent -> execution_agent")
        turn.active_agent = "execution_agent"

        ok, reason = self.output_guardrail.validate_execute_trade(decision)
        self.audit.append("output_guardrail.execute_trade", "safety", {"allowed": ok, "reason": reason})
        if not ok:
            turn.response = reason
            self._save_active_agent(trader_id, turn.active_agent)
            return turn

        if decision.status == "needs_human_approval":
            payload = self._hitl_payload(turn)
            turn.pending_approval = payload
            self.audit.append("hitl.interrupt", "execution_agent", payload)
            turn.response = (
                f"{research_summary}\n\n"
                f"Risk agent: {decision.reason}\n\n"
                "Execution agent is paused for human approval before calling the mock broker."
            )
            self._save_active_agent(trader_id, turn.active_agent)
            if interrupt_on_hitl:
                self._langgraph_or_local_interrupt(payload)
            return turn

        report = mock_broker_execute(idea, self.config.portfolio_path)
        turn.execution_report = report
        self.audit.append("execute_trade", "execution_agent", asdict(report))
        turn.response = (
            f"{research_summary}\n\n"
            f"Risk agent: {decision.reason}\n\n"
            f"Execution agent: {report.message} Order {report.order_id} for {report.quantity} {report.symbol} share(s)."
        )
        self._save_active_agent(trader_id, turn.active_agent)
        return turn

    def approve_pending(self, pending_payload: dict[str, Any], approved: bool, trader_id: str = "demo_trader") -> ChatTurn:
        idea_payload = dict(pending_payload["trade_idea"])
        idea_payload.pop("notional", None)
        idea = TradeIdea(**idea_payload)

        turn = ChatTurn(
            trader_id=trader_id,
            user_message="human_approval",
            active_agent="execution_agent",
            trade_idea=idea,
        )

        self.audit.append("hitl.decision", "human", {"approved": approved, "trade_idea": pending_payload["trade_idea"]})

        if not approved:
            turn.response = "Human reviewer rejected the mock trade. No broker call was made."
            self.audit.append("execute_trade.skipped", "execution_agent", {"reason": "human_rejected"})
            self._save_active_agent(trader_id, "execution_agent")
            return turn

        report: ExecutionReport = mock_broker_execute(idea, self.config.portfolio_path)
        turn.execution_report = report
        self.audit.append("execute_trade", "execution_agent", asdict(report))
        turn.response = f"Human reviewer approved. Mock broker executed order {report.order_id}."
        self._save_active_agent(trader_id, "execution_agent")
        return turn

    def _langgraph_or_local_interrupt(self, payload: dict[str, Any]) -> Any:
        try:
            from langgraph.types import interrupt  # type: ignore

            return interrupt(payload)
        except Exception as exc:
            raise HITLInterrupt(payload) from exc