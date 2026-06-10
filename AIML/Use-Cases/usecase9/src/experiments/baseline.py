from __future__ import annotations

import argparse
import json
from pathlib import Path

from corrective_rag.config import Settings
from observability.langfuse_config import get_langfuse_client


METRICS = ("faithfulness", "answer_relevancy", "context_precision")


def compare_with_baseline(
    current_report_path: Path,
    baseline_report_path: Path | None = None,
    max_drop: float = 0.10,
) -> dict:
    settings = Settings.from_env()
    baseline_path = baseline_report_path or settings.baseline_report_path
    current = json.loads(current_report_path.read_text(encoding="utf-8"))
    if not baseline_path.exists():
        baseline_path.parent.mkdir(parents=True, exist_ok=True)
        baseline_path.write_text(json.dumps(current, indent=2), encoding="utf-8")
        result = {
            "status": "baseline_created",
            "baseline": str(baseline_path),
            "metrics": {metric: current.get(metric, 0.0) for metric in METRICS},
        }
        record_langfuse_experiment(result, current)
        return result

    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    comparisons = {}
    failures = []
    for metric in METRICS:
        base_value = float(baseline.get(metric, 0.0))
        current_value = float(current.get(metric, 0.0))
        drop = base_value - current_value
        comparisons[metric] = {
            "baseline": base_value,
            "current": current_value,
            "drop": round(drop, 4),
            "passed": drop <= max_drop,
        }
        if drop > max_drop:
            failures.append(metric)

    status = "failed" if failures else "passed"
    result = {"status": status, "max_drop": max_drop, "comparisons": comparisons}
    record_langfuse_experiment(result, current)
    return result


def record_langfuse_experiment(result: dict, current_report: dict) -> None:
    client = get_langfuse_client()
    if client is None:
        return
    try:
        trace = client.trace(
            name="langfuse-experiment-baseline-comparison",
            metadata={
                "experiment": "current_model_vs_baseline_model",
                "result": result,
                "report_generated_at": current_report.get("generated_at"),
            },
            tags=["usecase9", "baseline-comparison", "experiment"],
        )
        for metric in METRICS:
            trace.score(name=metric, value=float(current_report.get(metric, 0.0)))
        client.flush()
    except Exception:
        return


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare current report with baseline metrics.")
    parser.add_argument("--current", type=Path, default=Path("reports/rag_eval_report.json"))
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--max-drop", type=float, default=0.10)
    parser.add_argument("--fail", action="store_true")
    args = parser.parse_args()

    result = compare_with_baseline(args.current, args.baseline, args.max_drop)
    print(json.dumps(result, indent=2))
    if args.fail and result["status"] == "failed":
        raise SystemExit("Baseline regression gate failed.")


if __name__ == "__main__":
    main()
