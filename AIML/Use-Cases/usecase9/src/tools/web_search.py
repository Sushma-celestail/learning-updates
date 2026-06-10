from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from corrective_rag.env import load_local_env
from corrective_rag.models import Document, RetrievedDocument


class TavilyWebSearch:
    """Tavily search node used only when retrieval needs correction."""

    def __init__(self, api_key: str | None = None, max_results: int = 3) -> None:
        load_local_env()
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        self.max_results = max_results

    def search(self, query: str) -> list[RetrievedDocument]:
        if not self.api_key:
            return []
        payload = json.dumps(
            {
                "query": query,
                "search_depth": "basic",
                "max_results": self.max_results,
                "include_answer": True,
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            "https://api.tavily.com/search",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=8) as response:
                data = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            return []

        raw_results = data.get("results", [])
        first_result_url = next(
            (item.get("url") for item in raw_results if item.get("url")),
            "",
        )
        results = []
        answer = data.get("answer")
        if answer and first_result_url:
            document = Document(
                doc_id="WEB-ANSWER",
                title="Tavily answer",
                text=answer,
                source=first_result_url,
                metadata={"category": "web_search", "kind": "answer", "url": first_result_url},
            )
            results.append(
                RetrievedDocument(document=document, score=0.9, matched_terms=("web",))
            )
        for index, item in enumerate(raw_results, start=1):
            text = item.get("content") or item.get("snippet") or ""
            if not text:
                continue
            url = item.get("url") or "tavily"
            document = Document(
                doc_id=f"WEB-{index}",
                title=item.get("title") or "Tavily web result",
                text=text,
                source=url,
                metadata={"category": "web_search", "url": url},
            )
            results.append(
                RetrievedDocument(document=document, score=0.18, matched_terms=("web",))
            )
        return results
