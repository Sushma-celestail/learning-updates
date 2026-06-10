from trading_floor.config import GovernanceConfig
from trading_floor.risk import RiskEngine
from trading_floor.models import TradeIdea


def test_oversized_trade_is_rejected():
    engine = RiskEngine(GovernanceConfig(starting_cash_usd=25000.0))
    idea = TradeIdea(symbol="NVDA", side="buy", quantity=30, price=125.50, rationale="test")

    decision = engine.evaluate(idea, portfolio_value=25000.0)

    assert decision.status == "rejected"
    assert "10% single-stock limit" in decision.reason
