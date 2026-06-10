
# Research Agent
#       │
#       ▼
#    TradeIdea
#       │
#       ▼
#    RiskDecision
#       │
#       ▼
# ExecutionReport
#       │
#       ▼
#    ChatTurn

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4


AgentName = Literal["research_agent", "risk_agent", "execution_agent"]
DecisionStatus = Literal["approved", "rejected", "needs_human_approval", "executed"]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

#this create by research agents 
@dataclass
class TradeIdea:
    symbol: str
    side: Literal["buy", "sell"]
    quantity: int
    price: float
    rationale: str  # it checks why the trade exists
    confidence: float = 0.65

    @property
    def notional(self) -> float:
        return round(self.quantity * self.price, 2)

#created by risk agent
@dataclass
class RiskDecision:
    status: DecisionStatus
    reason: str
    max_allowed_usd: float
    proposed_usd: float
    symbol: str


@dataclass
class ExecutionReport:
    order_id: str
    status: DecisionStatus
    symbol: str
    side: str
    quantity: int
    price: float
    notional: float
    message: str

# Research Agent
#      ↓
# ChatTurn
#      ↓
# Risk Agent
#      ↓
# ChatTurn
#      ↓
# Execution Agent


@dataclass
class ChatTurn:
    id: str = field(default_factory=lambda: str(uuid4()))
    trader_id: str = "demo_trader" #used for memory retrieval
    user_message: str = ""
    active_agent: AgentName = "research_agent"
    response: str = ""
    trade_idea: TradeIdea | None = None
    risk_decision: RiskDecision | None = None
    execution_report: ExecutionReport | None = None
    handoffs: list[str] = field(default_factory=list)
    memories_used: list[str] = field(default_factory=list)
    pending_approval: dict[str, Any] | None = None
    created_at: str = field(default_factory=utc_now)
