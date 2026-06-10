from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone

from audit.database import get_connection


def save_conversation(
    user_id: str,
    question: str,
    answer: str,
    doc_ids: list[str],
    model: str,
    cost: float,
    latency: float,
    eval_scores: dict[str, float],
    input_tokens: int = 0,
    output_tokens: int = 0,
    total_tokens: int = 0,
) -> None:
    with get_connection() as conn:
        hallucination_score = eval_scores.get("hallucination", eval_scores.get("online_hallucination_guard", 0.0))
        helpfulness_score = eval_scores.get("helpfulness", eval_scores.get("online_helpfulness_guard", 0.0))
        conn.execute(
            """
            INSERT INTO rag_audit_log (
              trace_id, user_id, created_at, question, answer, model, cost, latency,
              input_tokens, output_tokens, total_tokens, hallucination_score, helpfulness_score,
              citations_json, retrieval_json, evaluations_json, corrected, correction_reason
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"manual-{datetime.now(timezone.utc).timestamp()}",
                user_id,
                datetime.now(timezone.utc).isoformat(),
                question,
                answer,
                model,
                cost,
                latency,
                input_tokens,
                output_tokens,
                total_tokens,
                hallucination_score,
                helpfulness_score,
                json.dumps(doc_ids),
                json.dumps([{"doc_id": doc_id} for doc_id in doc_ids]),
                json.dumps(
                    [
                        {
                            "name": name,
                            "score": score,
                            "passed": True,
                            "rationale": "Saved through audit.logger.save_conversation.",
                        }
                        for name, score in eval_scores.items()
                    ]
                ),
                0,
                None,
            ),
        )
