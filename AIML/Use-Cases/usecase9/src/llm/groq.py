from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from corrective_rag.llm import LocalGroundedGenerator
from corrective_rag.models import RetrievedDocument
from corrective_rag.tracing import observe, update_current_span


class GroqGenerator:
    """Groq-backed generator with local grounded fallback."""

    def __init__(self, model: str = "llama-3.1-8b-instant", api_key: str | None = None) -> None:
        self.model = model
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.fallback = LocalGroundedGenerator()

    @observe(name="groq-generation")
    def generate(
        self,
        question: str,
        contexts: list[RetrievedDocument],
        conservative: bool = False,
    ) -> str:
        update_current_span(
            input={
                "question": question,
                "context_doc_ids": [item.document.doc_id for item in contexts],
            },
            metadata={"provider": "groq", "model": self.model},
        )
        if not self.api_key:
            output = self.fallback.generate(question, contexts, conservative)
            update_current_span(output=output, metadata={"provider": "local-fallback"})
            return output

        context_block = "\n\n".join(
            f"[{item.document.doc_id}] {item.document.title}: {item.document.text}"
            for item in contexts
        )
        instruction = (
            "Answer only from the supplied context. Include bracket citations. "
            "If evidence is insufficient, say so clearly."
        )
        if conservative:
            instruction += " Be conservative and omit any claim not directly supported."
        payload = json.dumps(
            {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": instruction},
                    {
                        "role": "user",
                        "content": f"Question: {question}\n\nContext:\n{context_block}",
                    },
                ],
                "temperature": 0.1,
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                data = json.loads(response.read().decode("utf-8"))
            output = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            update_current_span(
                output=output,
                metadata={
                    "provider": "groq",
                    "model": self.model,
                    "usage": usage,
                },
            )
            return output
        except (KeyError, urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            output = self.fallback.generate(question, contexts, conservative)
            update_current_span(
                output=output,
                metadata={"provider": "local-fallback", "reason": "groq_unavailable"},
            )
            return output
