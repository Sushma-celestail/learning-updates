from dataclasses import dataclass
from pathlib import Path
import os


PROJECT_ROOT = Path(__file__).resolve().parents[2]

try:
    from dotenv import load_dotenv

    load_dotenv(PROJECT_ROOT / ".env", override=True)
except Exception:
    pass


DATA_DIR = Path(os.getenv("TRADING_FLOOR_DATA_DIR", PROJECT_ROOT / "data"))
if not DATA_DIR.is_absolute():
    DATA_DIR = PROJECT_ROOT / DATA_DIR

#Makes config read-only.
@dataclass(frozen=True)
class GovernanceConfig:
    max_single_stock_pct: float = 0.10  # the amount should satisfies 10% of the share value 
    hitl_threshold_usd: float = 1000.0
    starting_cash_usd: float = 100000.0
    audit_path: Path = DATA_DIR / "audit.jsonl"
    memory_path: Path = DATA_DIR / "memories.json"
    portfolio_path: Path = DATA_DIR / "portfolio.json"
    google_api_key: str | None = os.getenv("GOOGLE_API_KEY")
    model_name: str = os.getenv("MODEL_NAME", "gemini-1.5-flash")
    use_gemini_swarm: bool = os.getenv("TRADING_FLOOR_USE_GEMINI_SWARM", "true").lower() == "true"
    langfuse_public_key: str | None = os.getenv("LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: str | None = os.getenv("LANGFUSE_SECRET_KEY")
    langfuse_host: str | None = os.getenv("LANGFUSE_HOST") or os.getenv("LANGFUSE_BASE_URL")


DEFAULT_CONFIG = GovernanceConfig()


