# tools/rag_retriever.py

import os
from typing import List

_DOC_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "docs",
    "product_docs.txt"
)


def _load_docs() -> List[str]:
    try:
        with open(_DOC_PATH, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []


_DOC_LINES = _load_docs()


def retrieve(query: str) -> str:

    if not query:
        return "Please provide more details."

    query = query.lower()

    # Technical queries
    if any(word in query for word in [
        "tech",
        "technical",
        "troubleshoot",
        "troubleshooting",
        "crash",
        "error",
        "bug"
    ]):
        matches = [
            line
            for line in _DOC_LINES
            if "technical" in line.lower()
            or "troubleshooting" in line.lower()
        ]

        if matches:
            return "\n".join(matches)

    # Password queries
    if any(word in query for word in [
        "password",
        "reset"
    ]):
        matches = [
            line
            for line in _DOC_LINES
            if "password" in line.lower()
        ]

        if matches:
            return "\n".join(matches)

    # Billing queries
    if any(word in query for word in [
        "bill",
        "billing",
        "invoice",
        "payment"
    ]):
        matches = [
            line
            for line in _DOC_LINES
            if "billing" in line.lower()
            or "invoice" in line.lower()
        ]

        if matches:
            return "\n".join(matches)

    # Email queries
    if any(word in query for word in [
        "email",
        "update"
    ]):
        matches = [
            line
            for line in _DOC_LINES
            if "email" in line.lower()
        ]

        if matches:
            return "\n".join(matches)

    # Documentation queries
    if any(word in query for word in [
        "documentation",
        "docs",
        "document",
        "help"
    ]):
        return "\n".join(_DOC_LINES)

    return (
        "Sorry, I couldn't find relevant information "
        "in the product documentation."
    )