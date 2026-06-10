from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from corrective_rag.config import Settings
from corrective_rag.corpus import load_eval_dataset
from corrective_rag.pipeline import CorrectiveRAGPipeline


def build_report(limit: int | None = None) -> dict:
    settings = Settings.from_env()
    pipeline = CorrectiveRAGPipeline(settings)
    items = load_eval_dataset(settings.eval_dataset_path)
    if limit:
        items = items[:limit]

    rows = []
    for item in items:
        result = pipeline.answer(item["input"])
        row = result.as_report_row()
        row["expected_answer"] = item["expected_answer"]
        row["metadata"] = item.get("metadata", {})
        rows.append(row)

    total = len(rows)
    corrected = sum(1 for row in rows if row["corrected"])
    eval_scores = [
        evaluation["score"]
        for row in rows
        for evaluation in row["evaluations"]
    ]
    failures = [
        {
            "question": row["question"],
            "failed": [
                evaluation
                for evaluation in row["evaluations"]
                if not evaluation["passed"]
            ],
        }
        for row in rows
        if any(not evaluation["passed"] for evaluation in row["evaluations"])
    ]
    faithfulness = _mean_metric(rows, "online_hallucination_guard")
    answer_relevancy = _mean_metric(rows, "online_helpfulness_guard")
    context_precision = round(
        sum(min(max(row["retrieval_scores"], default=0.0), 1.0) for row in rows) / max(total, 1),
        4,
    )
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_items": total,
        "corrected_items": corrected,
        "mean_online_score": round(sum(eval_scores) / max(len(eval_scores), 1), 4),
        "faithfulness": faithfulness,
        "answer_relevancy": answer_relevancy,
        "context_precision": context_precision,
        "thresholds": {
            "faithfulness": settings.min_faithfulness,
            "answer_relevancy": settings.min_answer_relevancy,
            "context_precision": settings.min_context_precision,
        },
        "failures": failures,
        "rows": rows,
    }


def _mean_metric(rows: list[dict], name: str) -> float:
    scores = [
        evaluation["score"]
        for row in rows
        for evaluation in row["evaluations"]
        if evaluation["name"] == name
    ]
    return round(sum(scores) / max(len(scores), 1), 4)


def assert_thresholds(report: dict) -> None:
    failed = []
    thresholds = report["thresholds"]
    for metric in ("faithfulness", "answer_relevancy", "context_precision"):
        if report[metric] < thresholds[metric]:
            failed.append(f"{metric}={report[metric]} < {thresholds[metric]}")
    if failed:
        raise SystemExit("Metric gate failed: " + "; ".join(failed))


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a CI-friendly JSON eval report.")
    parser.add_argument("--out", type=Path, default=Path("reports/rag_eval_report.json"))
    parser.add_argument("--limit", type=int)
    parser.add_argument("--fail-on-thresholds", action="store_true")
    args = parser.parse_args()

    report = build_report(limit=args.limit)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if args.fail_on_thresholds:
        assert_thresholds(report)
    print(
        json.dumps(
            {
                key: report[key]
                for key in [
                    "total_items",
                    "corrected_items",
                    "mean_online_score",
                    "faithfulness",
                    "answer_relevancy",
                    "context_precision",
                ]
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
