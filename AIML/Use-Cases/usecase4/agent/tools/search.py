"""Web search tool with Tavily / DuckDuckGo toggle."""

import os
from langchain_core.tools import tool


def _get_search_backend():
    """Always use DuckDuckGo as the search backend.
    This avoids failures when Tavily API keys are missing.
    """
    from duckduckgo_search import DDGS

    def _ddg_search(query: str) -> str:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        if not results:
            return "No results found."
        parts = []
        for r in results:
            parts.append(f"Title: {r['title']}\nContent: {r['body']}\n")
        return "\n".join(parts)

    return _ddg_search


_search_fn = _get_search_backend()


@tool
def web_search(query: str) -> str:
    """Search the web for current information, facts, statistics, or news.
    Use this tool when you need up-to-date or real-world factual data."""
    try:
        return _search_fn(query)
    except Exception as e:
        return f"Error during web search: {e}"
