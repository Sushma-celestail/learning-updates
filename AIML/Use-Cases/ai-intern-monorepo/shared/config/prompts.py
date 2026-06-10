"""
Prompt templates — shared by UC01 and UC02.

Edit the wording here once and both use-cases pick it up automatically.
"""

from langchain_core.prompts import ChatPromptTemplate

from shared.config.settings import FALLBACK_PHRASE


def get_rag_prompt() -> ChatPromptTemplate:
    """
    Strict docs-only prompt for UC01.

    Template slots:
        {question} — the user's question
        {context}  — retrieved chunks with source labels
    """
    return ChatPromptTemplate.from_messages([
        (
            "system",
            "You are Docs Buddy, a helpful documentation assistant. "
            "Answer questions ONLY using the retrieved documentation context below. "
            f"If the answer is not in the context, respond exactly: '{FALLBACK_PHRASE}' "
            "When you can answer, end your reply with a 'Citations' section "
            "listing the source URLs from the retrieved chunks. "
            "Be concise and use the exact terminology from the docs.",
        ),
        (
            "human",
            "Question: {question}\n\nDocumentation context:\n{context}",
        ),
    ])


def get_hybrid_prompt() -> ChatPromptTemplate:
    """
    Strict docs-only prompt for UC02 (hybrid pipeline).

    Template slots:
        {question} — the user's question
        {context}  — reranked chunks with source labels
    """
    return ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a precise technical assistant. "
            "Answer ONLY from the reranked documentation context provided. "
            f"If the answer is absent, say exactly: '{FALLBACK_PHRASE}' "
            "Append a 'Sources' section with the URLs of every chunk you used.",
        ),
        (
            "human",
            "Question: {question}\n\nReranked context:\n{context}",
        ),
    ])
