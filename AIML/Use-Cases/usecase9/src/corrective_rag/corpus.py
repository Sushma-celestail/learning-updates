
#read these files in order
from __future__ import annotations

import json
from pathlib import Path

from corrective_rag.models import Document


def load_jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def load_documents(path: Path) -> list[Document]:
    rows = load_jsonl(path)
    return [
        Document(
            doc_id=row["doc_id"],
            title=row["title"],
            text=row["text"],
            source=row["source"],
            metadata=row.get("metadata", {}),
        )
        for row in rows
    ]


def load_eval_dataset(path: Path) -> list[dict]:
    return load_jsonl(path)
