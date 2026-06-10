import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from trading_floor import TradingFloorSwarm


PROMPTS = [
    "Remember that I prefer tech stocks but want conservative paper trades.",
    "Research NVDA and buy 2 shares as a paper trade.",
    "Buy $5000 of NVDA as a paper trade.",
    "Buy $1500 of MSFT as a paper trade.",
    "Continue with a small AAPL paper trade using what you remember about me.",
]

swarm = TradingFloorSwarm()
pending = None
for idx, prompt in enumerate(PROMPTS, start=1):
    print(f"\nPROMPT {idx}: {prompt}")
    turn = swarm.process(prompt, trader_id="demo_trader")
    print("ACTIVE:", turn.active_agent)
    print("HANDOFFS:", " | ".join(turn.handoffs) or "none")
    print(turn.response)
    if turn.pending_approval:
        pending = turn.pending_approval
        print("HITL: interrupt fired; approving this one for demo continuity")
        resumed = swarm.approve_pending(pending, approved=True, trader_id="demo_trader")
        print(resumed.response)
