from __future__ import annotations

import time
from dataclasses import dataclass
from operator import itemgetter

from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from config import settings


@dataclass(frozen=True)
class RagResponse:
    answer: str
    sources: list[str]
    latency_seconds: float


SYSTEM_INSTRUCTION = """You are Docs Buddy, a careful documentation assistant.
Use only the retrieved FastAPI documentation context to answer.
If the answer is not directly supported by the context, reply exactly: {fallback_answer}
Do not use outside knowledge. Do not guess. Keep answers concise.
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_INSTRUCTION),
        (
            "human",
            "Question:\n{question}\n\nRetrieved documentation context:\n{context}",
        ),
    ]
)


OUT_OF_SCOPE_TERMS = (
    "weather",
    "temperature today",
    "forecast",
    "stock price",
    "sports score",
    "latest cricket",
    "latest news",
    "current time",
)


def _require_api_key() -> None:
    if not settings.google_api_key:
        raise RuntimeError("GOOGLE_API_KEY is required in .env")


def get_vector_store() -> Chroma:
    _require_api_key()
    embeddings = GoogleGenerativeAIEmbeddings(
        model=settings.embedding_model,
        google_api_key=settings.google_api_key,
    )
    return Chroma(
        collection_name=settings.chroma_collection,
        embedding_function=embeddings,
        persist_directory=str(settings.chroma_dir),
    )


def collection_count() -> int:
    vector_store = get_vector_store()
    return vector_store._collection.count()


def format_docs(docs) -> str:
    formatted = []
    for index, doc in enumerate(docs, start=1):
        source = doc.metadata.get("source", "unknown source")
        title = doc.metadata.get("title", "FastAPI documentation")
        formatted.append(
            f"[{index}] Source: {source}\nTitle: {title}\nContent: {doc.page_content}"
        )
    return "\n\n".join(formatted)


def citation_block(docs) -> tuple[str, list[str]]:
    sources: list[str] = []
    for doc in docs:
        source = doc.metadata.get("source")
        if source and source not in sources:
            sources.append(source)
    if not sources:
        return "", []
    lines = ["", "Sources:"] + [f"- {source}" for source in sources]
    return "\n".join(lines), sources


def _is_obviously_out_of_scope(question: str) -> bool:
    lowered = question.lower()
    return any(term in lowered for term in OUT_OF_SCOPE_TERMS)


def _is_fallback(answer: str) -> bool:
    normalized_answer = " ".join(answer.lower().strip().split())
    normalized_fallback = " ".join(settings.fallback_answer.lower().strip().split())
    return normalized_fallback in normalized_answer


def build_rag_chain():
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": settings.top_k})
    llm = ChatGoogleGenerativeAI(
        model=settings.chat_model,
        google_api_key=settings.google_api_key,
        temperature=0,
    )

    answer_chain = (
        {
            "context": itemgetter("docs") | RunnableLambda(format_docs),
            "question": itemgetter("question"),
            "fallback_answer": lambda _: settings.fallback_answer,
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return (
        RunnablePassthrough.assign(docs=itemgetter("question") | retriever)
        | RunnablePassthrough.assign(answer=answer_chain)
    )


def answer_question(question: str) -> RagResponse:
    started = time.perf_counter()
    clean_question = question.strip()
    if not clean_question:
        return RagResponse(settings.fallback_answer, [], 0.0)

    if _is_obviously_out_of_scope(clean_question):
        return RagResponse(
            settings.fallback_answer,
            [],
            time.perf_counter() - started,
        )

    chain = build_rag_chain()
    result = chain.invoke({"question": clean_question})
    raw_answer = result["answer"].strip()
    docs = result.get("docs", [])

    if _is_fallback(raw_answer):
        answer = settings.fallback_answer
        sources: list[str] = []
    else:
        block, sources = citation_block(docs)
        answer = f"{raw_answer}\n{block}" if block else raw_answer

    return RagResponse(answer, sources, time.perf_counter() - started)
