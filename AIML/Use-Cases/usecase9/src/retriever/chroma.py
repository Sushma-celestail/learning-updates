from __future__ import annotations

from pathlib import Path

from corrective_rag.models import Document, RetrievedDocument
from corrective_rag.retriever import LocalBM25Retriever


class ChromaRetriever:
    """Optional Chroma retriever with a local BM25 fallback for offline runs."""

    def __init__(
        self,
        documents: list[Document],
        persist_directory: str | Path = ".chroma",
        collection_name: str = "corrective_rag",
    ) -> None:
        self.documents = documents
        self.fallback = LocalBM25Retriever(documents)
        self.persist_directory = str(persist_directory)
        self.collection_name = collection_name
        self.collection = None
        self._init_chroma()

    def _init_chroma(self) -> None:
        try:
            import chromadb
        except Exception:
            return

        client = chromadb.PersistentClient(path=self.persist_directory)
        self.collection = client.get_or_create_collection(self.collection_name)
        existing = set(self.collection.get(include=[])["ids"])
        ids = [doc.doc_id for doc in self.documents if doc.doc_id not in existing]
        if not ids:
            return
        docs_by_id = {doc.doc_id: doc for doc in self.documents}
        self.collection.add(
            ids=ids,
            documents=[docs_by_id[doc_id].text for doc_id in ids],
            metadatas=[
                {
                    "title": docs_by_id[doc_id].title,
                    "source": docs_by_id[doc_id].source,
                    **docs_by_id[doc_id].metadata,
                }
                for doc_id in ids
            ],
        )

    def search(self, query: str, top_k: int = 4) -> list[RetrievedDocument]:
        if self.collection is None:
            return self.fallback.search(query, top_k)

        result = self.collection.query(query_texts=[query], n_results=top_k)
        ids = result.get("ids", [[]])[0]
        distances = result.get("distances", [[]])[0] or [0.0 for _ in ids]
        docs_by_id = {doc.doc_id: doc for doc in self.documents}
        retrieved = []
        for doc_id, distance in zip(ids, distances):
            if doc_id not in docs_by_id:
                continue
            retrieved.append(
                RetrievedDocument(
                    document=docs_by_id[doc_id],
                    score=1.0 / (1.0 + float(distance)),
                    matched_terms=(),
                )
            )
        return retrieved
