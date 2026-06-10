"""
UC02 — Download sample HTML source files for ingestion.

Run this ONCE before running ingest.py if you don't have your own PDFs/HTML.

What it does:
    Downloads the same FastAPI documentation pages that UC01 used,
    saves each one as an .html file into uc02_hybrid_search/data/raw/
    so ingest.py can load them.

Run:
    python uc02_hybrid_search/download_sample_data.py
"""

import os
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("USER_AGENT", "uc02-sample-downloader/1.0")

import requests
from langchain_community.document_loaders import SitemapLoader

from shared.config.settings import UC01_SITEMAP_URL, UC01_URL_PREFIX, UC02_DATA_DIR

# How many pages to download (keep low to stay within free API quota)
MAX_PAGES = 60


def download_html_files() -> None:
    """Fetch FastAPI docs pages and save each as an HTML file."""
    UC02_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Check if files already exist
    existing = list(UC02_DATA_DIR.glob("*.html"))
    if existing:
        print(f"✅ {len(existing)} HTML files already in {UC02_DATA_DIR}")
        print("   Delete them and re-run if you want to refresh.")
        return

    print(f"Fetching sitemap: {UC01_SITEMAP_URL}")
    loader = SitemapLoader(
        web_path=UC01_SITEMAP_URL,
        filter_urls=[UC01_URL_PREFIX],
    )
    docs = loader.load()
    docs = [d for d in docs if d.page_content.strip()]
    docs = docs[:MAX_PAGES]
    print(f"Pages fetched: {len(docs)}")

    saved = 0
    for doc in docs:
        # Build a safe filename from the URL path
        url  = doc.metadata.get("source", "")
        slug = url.replace("https://fastapi.tiangolo.com/", "").strip("/")
        slug = slug.replace("/", "_") or "index"
        filename = UC02_DATA_DIR / f"{slug}.html"

        # Write the page content as a minimal HTML file
        html = f"<html><body>{doc.page_content}</body></html>"
        filename.write_text(html, encoding="utf-8")
        saved += 1

    print(f"✅ Saved {saved} HTML files to {UC02_DATA_DIR}")
    print("   Now run: python uc02_hybrid_search/ingest.py")


if __name__ == "__main__":
    download_html_files()
