from trading_floor.config import GovernanceConfig
from trading_floor.orchestrator import TradingFloorSwarm


def test_last_active_agent_resumes_on_next_turn(tmp_path):
    swarm = TradingFloorSwarm(
        GovernanceConfig(
            starting_cash_usd=25000.0,
            audit_path=tmp_path / "audit.jsonl",
            memory_path=tmp_path / "memories.json",
            portfolio_path=tmp_path / "portfolio.json",
        )
    )
    first = swarm.process("buy 2 shares of MSFT as a paper trade")
    assert first.active_agent == "execution_agent"

    second = swarm.process("buy 1 share of AAPL as a paper trade")
    assert second.handoffs[0].startswith("execution_agent -> research_agent")
    assert second.active_agent == "execution_agent"
