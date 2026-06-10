import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from trading_floor.config import DEFAULT_CONFIG


parser = argparse.ArgumentParser(description="Compute daily governance evals from audit.jsonl.")
parser.add_argument("path", nargs="?", default=str(DEFAULT_CONFIG.audit_path))
args = parser.parse_args()

path = Path(args.path)
entries = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()] if path.exists() else []
blocks = [e for e in entries if e["action"] in {"input_guardrail.block", "risk_decision"} and e.get("payload", {}).get("status") == "rejected"]
execute_calls = [e for e in entries if e["action"] == "execute_trade"]
authorized = [e for e in entries if e["action"] == "output_guardrail.execute_trade" and e["payload"].get("allowed")]
violations = [e for e in entries if e["action"] == "output_guardrail.execute_trade" and not e["payload"].get("allowed")]

metrics = {
    "total_audit_entries": len(entries),
    "safety_violation_rate": round(len(violations) / max(1, len(authorized) + len(violations)), 4),
    "tool_call_accuracy": round(len(execute_calls) / max(1, len(authorized)), 4),
    "risk_or_input_blocks": len(blocks),
}
print(json.dumps(metrics, indent=2, sort_keys=True))
