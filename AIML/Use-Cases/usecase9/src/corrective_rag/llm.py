from __future__ import annotations

import re

from corrective_rag.models import RetrievedDocument
from corrective_rag.retriever import tokenize


class LocalGroundedGenerator:
    """Extractive generator that keeps answers grounded in retrieved context."""

    def generate(
        self,
        question: str,
        contexts: list[RetrievedDocument],
        conservative: bool = False,
    ) -> str:
        if not contexts:
            return (
                "I could not find this in the local knowledge base, and web search did not return "
                "usable results. Please check that TAVILY_API_KEY is configured and that internet "
                "access is available, then try again."
            )

        query_terms = set(tokenize(question))
        selected: list[str] = []
        definition_mode = question.strip().lower().startswith("what is ")
        contexts_to_use = [
            item
            for item in contexts
            if item.score >= 0.25 and not is_noisy_document(item.document.text)
        ] or contexts[:1]
        if definition_mode and contexts and contexts[0].document.title.lower().startswith("what is "):
            contexts_to_use = contexts[:1]
        if not definition_mode and contexts_to_use:
            best = contexts_to_use[0].score
            contexts_to_use = [item for item in contexts_to_use if item.score >= best * 0.72]

        for item in contexts_to_use[:2]:
            sentences = split_sentences(item.document.text)
            ranked = rank_sentences(sentences, query_terms)
            sentence_limit = 4 if definition_mode else 5
            for sentence, overlap in ranked[:3]:
                if overlap == 0 and query_terms:
                    continue
                if is_noisy_sentence(sentence):
                    continue
                if sentence not in selected and len(selected) < sentence_limit:
                    selected.append(sentence)

        if not selected:
            return (
                "I found some related sources, but not enough relevant evidence to answer cleanly. "
                "Try asking about a specific supported topic such as FastAPI, path parameters, "
                "dependency injection, Corrective RAG, Langfuse, audit logs, or RAGAS."
            )

        prefix = ""
        if conservative:
            prefix = (
                "Based only on the retrieved project sources, the safest answer is: "
            )

        citation_contexts = contexts_to_use[:3] if definition_mode else contexts[:3]
        citation_text = " ".join(f"[{item.document.doc_id}]" for item in citation_contexts)
        url_lines = [
            f"{item.document.title}: {item.document.source}"
            for item in citation_contexts
            if item.document.doc_id.startswith("WEB-") and item.document.source.startswith("http")
        ]
        body = " ".join(selected)
        if url_lines:
            urls = "\n".join(url_lines)
            return f"{prefix}{body}\n\nSources:\n{urls}\n\nCitations: {citation_text}"
        return f"{prefix}{body} Citations: {citation_text}"


def split_sentences(text: str) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def rank_sentences(sentences: list[str], query_terms: set[str]) -> list[tuple[str, int]]:
    ranked = []
    for sentence in sentences:
        overlap = len(query_terms.intersection(tokenize(sentence)))
        ranked.append((sentence, overlap))
    return sorted(ranked, key=lambda item: (item[1], -len(item[0])), reverse=True)


def is_noisy_sentence(sentence: str) -> bool:
    lowered = sentence.lower()
    noisy_markers = [
        "table of contents",
        "about the author",
        "copyright",
        "disclaimer",
        "preface",
        "........",
    ]
    return any(marker in lowered for marker in noisy_markers)


def is_noisy_document(text: str) -> bool:
    lowered = text.lower()[:600]
    return any(
        marker in lowered
        for marker in [
            "table of contents",
            "about the author",
            "contributors",
            "disclaimer",
            "copyright",
            "preface",
        ]
    )
