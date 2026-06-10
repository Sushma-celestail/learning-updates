from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent
load_dotenv(ROOT_DIR / ".env")


def _clean(value: str | None, default: str) -> str:
    if value is None or value.strip() == "":
        return default
    return value.strip().strip('"').strip("'")


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw.strip())
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer, got {raw!r}") from exc


def _prefixes() -> tuple[str, ...]:
    raw = os.getenv(
        "DOCS_URL_PREFIXES",
        "/tutorial/,/advanced/,/reference/,/deployment/,/how-to/",
    )
    values = [part.strip() for part in raw.split(",") if part.strip()]
    return tuple(value if value.startswith("/") else f"/{value}" for value in values)


@dataclass(frozen=True)
class Settings:
    docs_base_url: str = _clean(os.getenv("DOCS_BASE_URL"), "https://fastapi.tiangolo.com")
    sitemap_url: str = _clean(os.getenv("SITEMAP_URL"), "https://fastapi.tiangolo.com/sitemap.xml")
    docs_page_limit: int = _int_env("DOCS_PAGE_LIMIT", 80)
    docs_url_prefixes: tuple[str, ...] = _prefixes()
    min_pages: int = 50
    max_pages: int = 200

    chroma_dir: Path = ROOT_DIR / _clean(os.getenv("CHROMA_DIR"), "chroma_db")
    chroma_collection: str = _clean(os.getenv("CHROMA_COLLECTION"), "fastapi_docs")

    embedding_model: str = _clean(os.getenv("EMBEDDING_MODEL"), "models/gemini-embedding-001")
    chat_model: str = _clean(os.getenv("CHAT_MODEL"), "gemini-2.5-flash")
    google_api_key: str = _clean(os.getenv("GOOGLE_API_KEY"), "")

    top_k: int = _int_env("TOP_K", 4)
    chunk_size: int = _int_env("CHUNK_SIZE", 800)
    chunk_overlap: int = _int_env("CHUNK_OVERLAP", 100)
    fallback_answer: str = _clean(
        os.getenv("FALLBACK_ANSWER"),
        "I don't know based on the provided docs",
    )

    user_agent: str = "DocsBuddyRAG/1.0 (+https://fastapi.tiangolo.com)"


settings = Settings()
