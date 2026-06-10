"""Central settings for the Docs Buddy project."""

import os
from pathlib import Path

# Project root = ai-intern-monorepo/  (two levels up from shared/config/)
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# .env file in project root
ENV_FILE = PROJECT_ROOT / ".env"


def load_env_file():
    """Load KEY=VALUE lines from .env into environment variables."""
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key   = key.replace("$env:", "").strip()
        value = value.strip().strip('"').strip("'")
        os.environ[key] = value


# Load .env before any API clients are created
load_env_file()

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
USE_CASE_ROOT = PROJECT_ROOT / "usecase_01"          # active use-case folder
CHROMA_DIR    = USE_CASE_ROOT / "data" / "chroma"    # ChromaDB storage on disk

# ---------------------------------------------------------------------------
# ChromaDB
# ---------------------------------------------------------------------------
COLLECTION_NAME = "fastapi_docs_buddy"

# ---------------------------------------------------------------------------
# Documentation source
# ---------------------------------------------------------------------------
DOCS_SITEMAP_URL = "https://fastapi.tiangolo.com/sitemap.xml"
DOCS_URL_PREFIX  = "https://fastapi.tiangolo.com/"

# ---------------------------------------------------------------------------
# Ingestion limits 
# ---------------------------------------------------------------------------
MIN_PAGES = 50
MAX_PAGES = 80 

# Quick-test mode — set True to ingest only TEST_PAGES pages
QUICK_TEST_MODE = False
TEST_PAGES      = 10

# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------
CHUNK_SIZE    = 800
CHUNK_OVERLAP = 100

# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------
RETRIEVAL_K = 4

# ---------------------------------------------------------------------------
# AI models  — change these two lines to swap provider
# ---------------------------------------------------------------------------
EMBEDDING_MODEL = "gemini-embedding-001"   # Gemini embedding model
CHAT_MODEL      = "gemini-2.5-flash"       # Gemini chat model

# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------
FALLBACK_PHRASE = "I don't know based on the provided docs"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_DIR  = USE_CASE_ROOT / "logs"
LOG_FILE = LOG_DIR / "rag_pipeline.log"
