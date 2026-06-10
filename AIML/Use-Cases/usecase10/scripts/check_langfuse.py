import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from trading_floor.config import DEFAULT_CONFIG


def mask(value: str | None) -> str:
    if not value:
        return "missing"
    return value[:6] + "..." + value[-4:]


print("LANGFUSE_HOST", DEFAULT_CONFIG.langfuse_host)
print("LANGFUSE_PUBLIC_KEY", mask(DEFAULT_CONFIG.langfuse_public_key))
print("LANGFUSE_SECRET_KEY", "configured" if DEFAULT_CONFIG.langfuse_secret_key else "missing")

if not (DEFAULT_CONFIG.langfuse_public_key and DEFAULT_CONFIG.langfuse_secret_key):
    raise SystemExit("Langfuse keys are not configured in .env")

try:
    from langfuse import Langfuse

    langfuse = Langfuse(
        public_key=DEFAULT_CONFIG.langfuse_public_key,
        secret_key=DEFAULT_CONFIG.langfuse_secret_key,
        host=DEFAULT_CONFIG.langfuse_host,
    )
    print("AUTH_CHECK", langfuse.auth_check())
    if not langfuse.auth_check():
        raise RuntimeError("Langfuse auth_check returned False. Check public/secret key pair and project region.")

    with langfuse.start_as_current_observation(
        name="usecase10_manual_connection_test",
        as_type="span",
        metadata={"component": "governance", "check": "manual_connection_test"},
    ):
        pass
    langfuse.flush()
    langfuse.shutdown()
    print("LANGFUSE_CONNECTED")
    print("Open Langfuse Cloud and search for span: usecase10_manual_connection_test")
except Exception as exc:
    print("LANGFUSE_CONNECTION_FAILED")
    print(type(exc).__name__)
    print(str(exc)[:800])
    raise SystemExit(1)
