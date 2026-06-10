#Loads knowledge_base.jsonl
# User Question
#       │
#       ▼
# expand_query()
#       │
#       ▼
# tokenize()
#       │
#       ▼
# BM25 Search
#       │ (gives exact docs based on keyword matching)
#       ▼
# Score Documents
#       │
#       ▼
# Apply Boosts/Penalties
#       │
#       ▼
# Sort by Score
#       │
#       ▼
# Top RetrievedDocument Objects
#       │
#       ▼
# Send to LLM

from __future__ import annotations

import math

import re
from collections import Counter

from corrective_rag.models import Document, RetrievedDocument

TOKEN_RE = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_-]*")
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "i",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "our",
    "should",
    "that",
    "the",
    "to",
    "what",
    "when",
    "where",
    "with",
    "tell",
    "me",
    "you",
    "your",
}


def tokenize(text: str) -> list[str]:
    return [
        token.lower()
        for token in TOKEN_RE.findall(text)
        if len(token) > 2 and token.lower() not in STOPWORDS
    ]

# when user question -> search documents-> 
# rank documents-> return top results
#Reward frequent matches
#Reward rare terms
#Penalize very long documents
class LocalBM25Retriever:
    """Small BM25-style retriever so the demo works without external services."""

    def __init__(self, documents: list[Document]) -> None:
        self.documents = documents
        self.doc_tokens = [tokenize(f"{doc.title} {doc.text}") for doc in documents]
        self.doc_lengths = [len(tokens) for tokens in self.doc_tokens]
        self.avg_doc_len = sum(self.doc_lengths) / max(len(self.doc_lengths), 1)
        self.doc_freq: Counter[str] = Counter()
        for tokens in self.doc_tokens:
            self.doc_freq.update(set(tokens))

    def search(self, query: str, top_k: int = 4) -> list[RetrievedDocument]:
        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        scored: list[RetrievedDocument] = []
        for doc, tokens, doc_len in zip(self.documents, self.doc_tokens, self.doc_lengths):
            token_counts = Counter(tokens)
            score = 0.0
            matched = []
            title_tokens = set(tokenize(doc.title))
            for term in query_tokens:
                if token_counts[term] == 0:
                    continue
                matched.append(term)
                idf = math.log(1 + (len(self.documents) - self.doc_freq[term] + 0.5) / (self.doc_freq[term] + 0.5))
                tf = token_counts[term]
                score += idf * ((tf * 2.2) / (tf + 1.2 * (1 - 0.75 + 0.75 * doc_len / self.avg_doc_len)))
            if score > 0:
                if set(query_tokens).issubset(title_tokens):
                    score += 2.0
                lowered_title = doc.title.lower()
                if lowered_title.startswith(("what is ", "overview", "introduction")):
                    score += 4.0
                title_matches = sum(1 for term in query_tokens if term in lowered_title)
                if title_matches:
                    score += 1.5 * title_matches
                topic = str(doc.metadata.get("topic", "")).replace("_", " ").lower()
                topic_matches = sum(1 for term in query_tokens if term in topic)
                if topic_matches:
                    score += 1.5 * topic_matches
                lowered_text_head = doc.text.lower()[:400]
                if "table of contents" in lowered_text_head or "about the author" in lowered_text_head:
                    score *= 0.45
                normalized = score / (len(query_tokens) + 1)
                scored.append(
                    RetrievedDocument(
                        document=doc,
                        score=normalized,
                        matched_terms=tuple(sorted(set(matched))),
                    )
                )

        return sorted(scored, key=lambda item: item.score, reverse=True)[:top_k]


def expand_query(query: str) -> str:
    lower = query.lower()
    expansions: list[str] = []
    if "trace" in lower or "observ" in lower:
        expansions.extend(["langfuse", "callback", "audit", "span"])
    if "halluc" in lower or "ground" in lower:
        expansions.extend(["groundedness", "citations", "evaluator"])
    if "nist" in lower or "govern" in lower or "measure" in lower:
        expansions.extend(["governance", "risk", "metric", "policy"])
    if "ragas" in lower or "offline" in lower:
        expansions.extend(["faithfulness", "context", "answer", "pytest"])
    if "dataset" in lower or "seed" in lower:
        expansions.extend(["langfuse", "item", "expected_answer"])
    return " ".join([query, *expansions])
