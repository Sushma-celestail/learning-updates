"""
UC01 — Docs Buddy: LCEL retrieval chain.

Pipeline:
    question
      → ChromaDB retriever (top-k=4)
      → format retrieved chunks into context string
      → prompt (system + context + question)
      → Gemini gemini-2.5-flash
      → plain string answer

Usage:
    from uc01_docs_buddy.chain import answer_question
    answer = answer_question("What is dependency injection in FastAPI?")
"""

import sys
from pathlib import Path

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from shared.config.prompts import get_rag_prompt
from shared.config.settings import (
    RETRIEVAL_K,
    UC01_CHROMA_DIR,
    UC01_COLLECTION,
)
from shared.llm.gemini import GeminiChat
from shared.vectorstore.chroma import get_vectorstore


def _format_docs(docs) -> str:
    """
    Convert retrieved Document objects into a numbered context string.
    Each chunk is prefixed with its source URL so the LLM can cite it.
    Raises RuntimeError if no chunks came back (quota exhausted).
    """
    if not docs:
        raise RuntimeError(
            "No documentation chunks were retrieved.\n"
            "The embedding API quota may be exhausted. "
            "Update GOOGLE_API_KEY in .env with a fresh key from "
            "https://aistudio.google.com/app/apikey and restart."
        )

    parts = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "unknown")
        parts.append(f"[Source {i}: {source}]\n{doc.page_content}")

    return "\n\n".join(parts)


def _build_chain():
    """
    Assemble the LCEL chain.
    Returns a Runnable: question str → answer str.
    """
    vs        = get_vectorstore(UC01_CHROMA_DIR, UC01_COLLECTION)
    retriever = vs.as_retriever(search_kwargs={"k": RETRIEVAL_K})
    prompt    = get_rag_prompt()

    # The dict runs retriever and passthrough in parallel, then merges results
    chain = (
        {
            "context":  retriever | RunnableLambda(_format_docs),
            "question": RunnablePassthrough(),
        }
        | prompt
        | GeminiChat
        | StrOutputParser()
    )
    return chain


def answer_question(question: str) -> str:
    """
    Run the full RAG pipeline for one question.

    Returns the answer string with a Citations block,
    or the fallback phrase if the question is out of scope.
    """
    chain = _build_chain()
    return chain.invoke(question)
