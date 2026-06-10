# User
#   │
#   ▼
# Input Guardrail
#   │
#   ▼
# Research Agent
#   │
#   ▼
# Risk Agent
#   │
#   ▼
# Output Guardrail
#   │
#   ▼
# Execution Agent
#to prevent bad inputs 
#to prevent unauthorized executions


from __future__ import annotations

from .config import PROJECT_ROOT
from .models import RiskDecision

#The assistant only supports trading-related conversations.
TRADING_TERMS = {
    "stock", "trade", "ticker", "portfolio", "risk", "risks", "buy", "sell",
    "invest", "market", "shares", "share", "allocation", "paper", "broker",
    "tech", "etf", "approval", "research", "analyze", "analysis",
    "preference", "prefer", "remember", "low-risk", "dividend", "dividends",
    "income", "company", "valuation", "earnings", "exposure",
    "nvda", "msft", "aapl", "googl", "amzn", "tsla", "ko",
    "nvidia", "microsoft", "amazon", "apple", "tesla", "google", "alphabet",
    "coca-cola", "coca", "cola", "coke","audit", "integrity", "verify", "verification", "governance",
"implemented", "controls", "memory", "suggest", "recommendation",
"investment", "avoid", "avoided", "bought", "volatility",
}

#these are jailbreak attempts it blocks unrelated questions
INJECTION_TERMS = {
"ignore all previous", "ignore all rules", "ignore all",
"without risk agent", "without risk approval", "without risk-agent",
"execute_trade", "bypass risk", "skip risk", "skip approval",
"force execute", "execute the trade immediately",
}

#validate user messages before agents see them
class InputGuardrail:
    def __init__(self) -> None:
        self._rails = None
        self.backend = "local_rules"
        try:
            from nemoguardrails import LLMRails, RailsConfig  # type: ignore

            config = RailsConfig.from_path(str(PROJECT_ROOT / "guardrails" / "trading_floor"))
            self._rails = LLMRails(config)
            self.backend = "nemo_guardrails"
        except Exception:
            self._rails = None
            self.backend = "local_rules"

    def status(self) -> dict[str, str | bool]:
        return {"backend": self.backend, "live_nemo": self._rails is not None}

    def validate(self, message: str) -> tuple[bool, str]:
        # The deterministic checks remain first so known bad prompts are blocked even if the LLM guardrail is unavailable.
        lowered = message.lower()
        if any(term in lowered for term in INJECTION_TERMS):
            return False, "Blocked: prompt-injection or policy-bypass language was detected."
        words = {word.strip(".,:;!?").lower() for word in message.split()}
        if words and not (words & TRADING_TERMS):
            return False, "Blocked: this assistant only supports paper-trading research, risk, and execution."
        return True, "allowed"

#even if agents misbehave its protect execution layer 
# research agent -> risk agent-> execution agent before execution outputguardrail checks permission
class OutputGuardrail:
    def validate_execute_trade(self, risk_decision: RiskDecision | None) -> tuple[bool, str]:
        if risk_decision is None:
            return False, "Execution blocked: missing risk-agent decision."
        if risk_decision.status not in {"approved", "needs_human_approval"}:
            return False, f"Execution blocked by risk gate: {risk_decision.reason}"
        return True, "execution authorized by risk gate"

