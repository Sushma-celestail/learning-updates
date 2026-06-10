import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from trading_floor import TradingFloorSwarm


swarm = TradingFloorSwarm()
status = swarm.strict_stack_status()
print(json.dumps(status, indent=2, sort_keys=True))

if not status["google_api_key_configured"]:
    raise SystemExit("GOOGLE_API_KEY is not configured in .env")
if not all(status["packages"].values()):
    missing = [name for name, installed in status["packages"].items() if not installed]
    raise SystemExit(f"Missing packages: {missing}")

swarm.compile_gemini_swarm()
print("Strict Gemini LangGraph swarm compiled successfully.")
