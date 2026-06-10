from __future__ import annotations

import json
import statistics
import sys

from config import ROOT_DIR, settings
from rag import answer_question

QUESTIONS_PATH = ROOT_DIR / "data" / "eval_questions.json"


def has_citation_block(answer: str) -> bool:
    return "\nSources:\n" in answer and "https://fastapi.tiangolo.com" in answer


def main() -> int:
    questions = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    docs_questions = questions["in_scope"]
    oos_questions = questions["out_of_scope"]

    docs_results = []
    oos_results = []

    print("Running in-scope questions")
    for item in docs_questions:
        response = answer_question(item["question"])
        docs_results.append(response)
        citation = "yes" if has_citation_block(response.answer) else "no"
        print(f"- citation={citation} latency={response.latency_seconds:.2f}s :: {item['question']}")

    print("\nRunning out-of-scope questions")
    for question in oos_questions:
        response = answer_question(question)
        oos_results.append(response)
        fallback = "yes" if response.answer.strip() == settings.fallback_answer else "no"
        print(f"- fallback={fallback} latency={response.latency_seconds:.2f}s :: {question}")

    citation_count = sum(has_citation_block(result.answer) for result in docs_results)
    fallback_count = sum(result.answer.strip() == settings.fallback_answer for result in oos_results)
    latencies = [result.latency_seconds for result in docs_results + oos_results]
    p50_latency = statistics.median(latencies) if latencies else 0.0

    print("\nSummary")
    print(f"Citations: {citation_count}/10")
    print(f"Fallbacks: {fallback_count}/3")
    print(f"p50 latency: {p50_latency:.2f}s")

    ok = citation_count >= 8 and fallback_count == 3 and p50_latency < 4.0
    if not ok:
        print("Acceptance smoke check did not pass yet.", file=sys.stderr)
        return 1
    print("Acceptance smoke check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
