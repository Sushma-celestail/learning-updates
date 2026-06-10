import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from trading_floor.audit import verify_audit
from trading_floor.config import DEFAULT_CONFIG


parser = argparse.ArgumentParser(description="Verify the hash chain in audit.jsonl.")
parser.add_argument("path", nargs="?", default=str(DEFAULT_CONFIG.audit_path))
args = parser.parse_args()

ok, message = verify_audit(Path(args.path))
print(message)
raise SystemExit(0 if ok else 1)
