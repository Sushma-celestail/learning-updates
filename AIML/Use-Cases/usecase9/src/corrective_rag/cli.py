from __future__ import annotations

import argparse
import json
from pathlib import Path

from corrective_rag.pipeline import CorrectiveRAGPipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the corrective RAG chatbot locally.")
    parser.add_argument("question", nargs="*", help="Question to ask the chatbot.")
    parser.add_argument("--json", action="store_true", help="Print the full JSON response.")
    parser.add_argument("--audit-limit", type=int, default=0, help="Show latest audit rows and exit.")
    parser.add_argument("--out", type=Path, help="Write JSON response to a file.")
    args = parser.parse_args()

    pipeline = CorrectiveRAGPipeline()
    if args.audit_limit:
        print(json.dumps(pipeline.audit_logger.latest(args.audit_limit), indent=2))
        return

    question = " ".join(args.question).strip()
    if not question:
        question = input("Question: ").strip()

    result = pipeline.answer(question)
    payload = result.as_report_row()
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(result.answer)
        print(f"\nTrace: {result.trace_id}")
        print(f"Corrected: {result.corrected}")
        print(
            "Scores: "
            + ", ".join(f"{item.name}={item.score:.2f}" for item in result.evaluations)
        )


if __name__ == "__main__":
    main()
