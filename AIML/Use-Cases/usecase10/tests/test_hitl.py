from trading_floor.config import GovernanceConfig
from trading_floor.orchestrator import HITLInterrupt, TradingFloorSwarm


def make_swarm(tmp_path):
    return TradingFloorSwarm(
        GovernanceConfig(
            starting_cash_usd=25000.0,
            audit_path=tmp_path / "audit.jsonl",
            memory_path=tmp_path / "memories.json",
            portfolio_path=tmp_path / "portfolio.json",
        )
    )


def test_large_mock_trade_interrupts(tmp_path):
    swarm = make_swarm(tmp_path)
    try:
        swarm.process("buy $1500 of NVDA as a paper trade", interrupt_on_hitl=True)
    except HITLInterrupt as exc:
        assert exc.payload["trade_idea"]["notional"] > 1000
    else:
        raise AssertionError("expected HITLInterrupt")


def test_human_approval_and_rejection_paths(tmp_path):
    swarm = make_swarm(tmp_path)
    turn = swarm.process("buy $1500 of NVDA as a paper trade")
    assert turn.pending_approval is not None

    rejected = swarm.approve_pending(turn.pending_approval, approved=False)
    assert "rejected" in rejected.response.lower()
    assert rejected.execution_report is None

    approved = swarm.approve_pending(turn.pending_approval, approved=True)
    assert approved.execution_report is not None
    assert approved.execution_report.status == "executed"
