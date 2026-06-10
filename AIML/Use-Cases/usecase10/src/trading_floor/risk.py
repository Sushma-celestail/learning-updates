from __future__ import annotations

from .config import GovernanceConfig
from .models import RiskDecision, TradeIdea


class RiskEngine:
    def __init__(self, config: GovernanceConfig):
        self.config = config

    def evaluate(self, idea: TradeIdea, portfolio_value: float) -> RiskDecision:
        max_allowed = round(portfolio_value * self.config.max_single_stock_pct, 2)
        if idea.notional > max_allowed:
            return RiskDecision(
                status="rejected",
                reason=(
                    f"Rejected: {idea.symbol} notional ${idea.notional:,.2f} exceeds "
                    f"the 10% single-stock limit (${max_allowed:,.2f})."
                ),
                max_allowed_usd=max_allowed,
                proposed_usd=idea.notional,
                symbol=idea.symbol,
            )
        if idea.notional > self.config.hitl_threshold_usd:
            return RiskDecision(
                status="needs_human_approval",
                reason=f"Risk gate passed, but ${idea.notional:,.2f} requires human approval.",
                max_allowed_usd=max_allowed,
                proposed_usd=idea.notional,
                symbol=idea.symbol,
            )
        return RiskDecision(
            status="approved",
            reason=f"Approved: ${idea.notional:,.2f} is within the 10% single-stock limit.",
            max_allowed_usd=max_allowed,
            proposed_usd=idea.notional,
            symbol=idea.symbol,
        )
