from __future__ import annotations

import hashlib
import re
import sys
import time
import xml.etree.ElementTree as ET
from collections.abc import Iterable
from urllib.parse import urlparse

import requests
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import settings

SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
IMPORTANT_PATH_HINTS = (
    "/tutorial/first-steps/",
    "/tutorial/path-params/",
    "/tutorial/query-params/",
    "/tutorial/body/",
    "/tutorial/response-model/",
    "/tutorial/handling-errors/",
    "/tutorial/dependencies/",
    "/tutorial/bigger-applications/",
    "/tutorial/background-tasks/",
    "/tutorial/metadata/",
)


def _require_api_key() -> None:
    if not settings.google_api_key:
        raise RuntimeError("GOOGLE_API_KEY is required in .env")


def _fetch_xml(url: str) -> ET.Element:
    response = requests.get(
        url,
        timeout=30,
        headers={"User-Agent": settings.user_agent},
    )
    response.raise_for_status()
    return ET.fromstring(response.content)


def _loc_values(root: ET.Element, path: str) -> list[str]:
    return [loc.text.strip() for loc in root.findall(path, SITEMAP_NS) if loc.text]


def discover_sitemap_urls(sitemap_url: str) -> list[str]:
    """Return all page URLs from a sitemap or sitemap index."""
    seen_sitemaps: set[str] = set()
    urls: list[str] = []

    def walk(url: str) -> None:
        if url in seen_sitemaps:
            return
        seen_sitemaps.add(url)
        root = _fetch_xml(url)
        tag = root.tag.lower()
        if tag.endswith("sitemapindex"):
            for child_sitemap in _loc_values(root, "sm:sitemap/sm:loc"):
                walk(child_sitemap)
            return
        urls.extend(_loc_values(root, "sm:url/sm:loc"))

    walk(sitemap_url)
    return urls


def _is_selected_doc_url(url: str) -> bool:
    parsed_url = urlparse(url)
    parsed_base = urlparse(settings.docs_base_url)
    if parsed_url.netloc != parsed_base.netloc:
        return False
    return any(parsed_url.path.startswith(prefix) for prefix in settings.docs_url_prefixes)


def select_doc_urls(urls: Iterable[str]) -> list[str]:
    page_limit = max(settings.min_pages, min(settings.docs_page_limit, settings.max_pages))
    candidates = sorted({url for url in urls if _is_selected_doc_url(url)})
    selected: list[str] = []

    for hint in IMPORTANT_PATH_HINTS:
        for url in candidates:
            if hint in url and url not in selected:
                selected.append(url)
                break

    for prefix in settings.docs_url_prefixes:
        prefix_urls = [url for url in candidates if urlparse(url).path.startswith(prefix)]
        for url in prefix_urls[: max(10, page_limit // max(len(settings.docs_url_prefixes), 1))]:
            if len(selected) >= page_limit:
                break
            if url not in selected:
                selected.append(url)

    for url in candidates:
        if len(selected) >= page_limit:
            break
        if url not in selected:
            selected.append(url)

    if len(selected) < settings.min_pages:
        raise RuntimeError(
            f"Only found {len(selected)} matching docs pages. "
            f"Need at least {settings.min_pages}. Check DOCS_URL_PREFIXES in .env."
        )
    return selected[:page_limit]


def load_pages(urls: list[str]):
    loader = WebBaseLoader(
        web_paths=urls,
        requests_per_second=2,
        header_template={"User-Agent": settings.user_agent},
        continue_on_failure=True,
    )
    docs = loader.load()
    cleaned = []
    for doc in docs:
        text = re.sub(r"\s+", " ", doc.page_content).strip()
        if len(text) < 200:
            continue
        doc.page_content = text
        doc.metadata["source"] = doc.metadata.get("source") or doc.metadata.get("url")
        doc.metadata["title"] = doc.metadata.get("title", "FastAPI documentation")
        cleaned.append(doc)
    if len(cleaned) < settings.min_pages:
        raise RuntimeError(f"Loaded only {len(cleaned)} usable pages; expected at least {settings.min_pages}.")
    return cleaned


def split_pages(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        add_start_index=True,
    )
    chunks = splitter.split_documents(docs)
    source_counts: dict[str, int] = {}
    ids: list[str] = []
    for chunk in chunks:
        source = chunk.metadata.get("source", "unknown-source")
        chunk_index = source_counts.get(source, 0)
        source_counts[source] = chunk_index + 1
        chunk.metadata["chunk_index"] = chunk_index
        stable_key = f"{source}|{chunk_index}"
        ids.append(hashlib.sha256(stable_key.encode("utf-8")).hexdigest())
    return chunks, ids


def _batched(items: list, size: int):
    for start in range(0, len(items), size):
        yield items[start : start + size]


def get_vector_store() -> Chroma:
    embeddings = GoogleGenerativeAIEmbeddings(
        model=settings.embedding_model,
        google_api_key=settings.google_api_key,
    )
    return Chroma(
        collection_name=settings.chroma_collection,
        embedding_function=embeddings,
        persist_directory=str(settings.chroma_dir),
    )


def existing_ids(vector_store: Chroma, ids: list[str]) -> set[str]:
    found: set[str] = set()
    for batch in _batched(ids, 500):
        result = vector_store.get(ids=batch)
        found.update(result.get("ids", []))
    return found


def persist_if_supported(vector_store: Chroma) -> None:
    persist = getattr(vector_store, "persist", None)
    if callable(persist):
        persist()


def main() -> int:
    _require_api_key()
    started = time.perf_counter()
    settings.chroma_dir.mkdir(parents=True, exist_ok=True)

    print(f"Discovering docs from {settings.sitemap_url}")
    all_urls = discover_sitemap_urls(settings.sitemap_url)
    urls = select_doc_urls(all_urls)
    print(f"Selected {len(urls)} pages")

    docs = load_pages(urls)
    print(f"Loaded {len(docs)} pages")

    chunks, ids = split_pages(docs)
    print(f"Prepared {len(chunks)} chunks")

    vector_store = get_vector_store()
    already_present = existing_ids(vector_store, ids)
    new_docs = []
    new_ids = []
    for doc, doc_id in zip(chunks, ids, strict=True):
        if doc_id not in already_present:
            new_docs.append(doc)
            new_ids.append(doc_id)

    if new_docs:
        for doc_batch, id_batch in zip(_batched(new_docs, 128), _batched(new_ids, 128), strict=True):
            vector_store.add_documents(documents=doc_batch, ids=id_batch)
        persist_if_supported(vector_store)

    elapsed = time.perf_counter() - started
    total = vector_store._collection.count()
    print(f"Added {len(new_docs)} new chunks; skipped {len(chunks) - len(new_docs)} existing chunks")
    print(f"Chroma collection '{settings.chroma_collection}' now has {total} chunks")
    print(f"Done in {elapsed:.1f}s")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Ingestion failed: {exc}", file=sys.stderr)
        raise

