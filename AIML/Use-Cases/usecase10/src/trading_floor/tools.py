# Research Agent
#      │
#      ▼
# Tools.py
#  ├── normalize_symbol()
#  ├── ticker_lookup()
#  ├── web_search_market_brief()
#  ├── infer_quantity()
#  │
#  ▼
# TradeIdea
#  │
#  ▼
# Risk Agent
#  │
#  ▼
# mock_broker_execute()
#  │
#  ▼
# portfolio.json

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import quote_plus
from uuid import uuid4

from .models import ExecutionReport, TradeIdea


MOCK_PRICES = {
    "AAPL": 195.10,
    "AMZN": 182.25,
    "GOOGL": 176.40,
    "MSFT": 430.20,
    "NVDA": 125.50,
    "TSLA": 178.75,
    "KO" :62.50,
}


MOCK_BRIEFS = {
    "NVDA": "AI accelerator demand remains the main growth narrative; valuation risk is elevated.",
    "MSFT": "Cloud and AI platform revenue continue to support a resilient large-cap profile.",
    "AAPL": "Services revenue is steady while device-cycle growth remains more muted.",
    "TSLA": "Execution risk and pricing pressure remain material for the EV narrative.",
    "KO": "Coca-Cola has a defensive consumer-staples profile with dividend income appeal and slower growth.",
}


COMPANY_ALIASES = {
    "NVIDIA": "NVDA",
    "MICROSOFT": "MSFT",
    "AMAZON": "AMZN",
    "APPLE": "AAPL",
    "TESLA": "TSLA",
    "GOOGLE": "GOOGL",
    "ALPHABET": "GOOGL",
    "COCA-COLA": "KO",
    "COCA COLA": "KO",
    "COKE": "KO",
}


def normalize_symbol(message: str) -> str:
    upper = message.upper()
    for symbol in MOCK_PRICES:
        if symbol in upper:
            return symbol
    for company, symbol in COMPANY_ALIASES.items():
        if company in upper:
            return symbol
    if "TECH" in upper or "AI" in upper:
        return "NVDA"
    return "MSFT"

def ticker_lookup(symbol: str) -> dict:
    price = MOCK_PRICES.get(symbol.upper(), 100.0)
    return {"symbol": symbol.upper(), "price": price, "source": "mock_ticker_lookup"}


def _mock_market_brief(symbol: str) -> str:
    return MOCK_BRIEFS.get(symbol.upper(), "Using a conservative fallback market brief for this ticker.")


def live_web_search_market_brief(symbol: str, timeout_seconds: int = 8) -> str | None:
    """Use DuckDuckGo HTML search for a lightweight live market brief.

    This keeps the project API-key-free for web search. If the network is blocked,
    the caller falls back to the deterministic mock brief.
    """
    try:
        import requests

        query = quote_plus(f"{symbol} stock latest market news analyst brief")
        url = f"https://duckduckgo.com/html/?q={query}"
        response = requests.get(
            url,
            timeout=timeout_seconds,
            headers={"User-Agent": "Mozilla/5.0 trading-floor-demo"},
        )
        response.raise_for_status()
        page = response.text
        snippets = re.findall(r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>', page, flags=re.S)
        if not snippets:
            snippets = re.findall(r'<div[^>]+class="result__snippet"[^>]*>(.*?)</div>', page, flags=re.S)
        cleaned: list[str] = []
        for snippet in snippets[:3]:
            text = re.sub(r"<.*?>", " ", snippet)
            text = html.unescape(re.sub(r"\s+", " ", text)).strip()
            if text:
                cleaned.append(text)
        if cleaned:
            return "Live web search summary: " + " ".join(cleaned[:2])
    except Exception:
        return None
    return None


def web_search_market_brief(symbol: str) -> str:
    live = live_web_search_market_brief(symbol)
    if live:
        return live
    return _mock_market_brief(symbol) + " (Fallback brief; live web search unavailable.)"


def infer_quantity(message: str, price: float) -> int:
    digits = [int(token.strip("$,").replace(",", "")) for token in message.split() if token.strip("$,. ").replace(",", "").isdigit()]
    if digits:
        number = max(digits)
        if "$" in message or number > 50:
            return max(1, int(number / price))
        return max(1, number)
    return 3


def mock_broker_execute(idea: TradeIdea, portfolio_path: Path) -> ExecutionReport:
    portfolio_path.parent.mkdir(parents=True, exist_ok=True)
    if portfolio_path.exists():
        portfolio = json.loads(portfolio_path.read_text(encoding="utf-8"))
    else:
        portfolio = {"cash": 10000.0, "positions": {}}
    cost = idea.notional if idea.side == "buy" else -idea.notional
    portfolio["cash"] = round(portfolio.get("cash", 0.0) - cost, 2)
    positions = portfolio.setdefault("positions", {})
    positions[idea.symbol] = positions.get(idea.symbol, 0) + idea.quantity
    portfolio_path.write_text(json.dumps(portfolio, indent=2, sort_keys=True), encoding="utf-8")
    return ExecutionReport(
        order_id=f"MOCK-{uuid4().hex[:10].upper()}",
        status="executed",
        symbol=idea.symbol,
        side=idea.side,
        quantity=idea.quantity,
        price=idea.price,
        notional=idea.notional,
        message="Mock broker accepted the paper trade.",
    )
