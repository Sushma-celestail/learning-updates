import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from trading_floor.config import DEFAULT_CONFIG
from trading_floor.llm import build_gemini_llm

try:
    response = build_gemini_llm(DEFAULT_CONFIG).invoke("Reply with exactly: OK")
    text = getattr(response, "content", str(response))
    if isinstance(text, list):
        text = " ".join(str(part.get("text", "")) if isinstance(part, dict) else str(part) for part in text)
    print("GEMINI_CALL_OK")
    print(str(text).strip()[:20])
except Exception as exc:
    print("GEMINI_CALL_FAILED")
    print(type(exc).__name__)
    print(str(exc)[:500])
    raise SystemExit(1)
