from __future__ import annotations

import os

import pytest

from corrective_rag.config import Settings
from corrective_rag.corpus import load_eval_dataset
from corrective_rag.pipeline import CorrectiveRAGPipeline


def test_ragas_dataset_contract_is_offline_ready(tmp_path):
    ragas = pytest.importorskip("ragas")
    datasets = pytest.importorskip("datasets")

    settings = Settings.from_env()
    settings = Settings(
        knowledge_base_path=settings.knowledge_base_path,
        eval_dataset_path=settings.eval_dataset_path,
        audit_db_path=tmp_path / "audit.sqlite3",
    )
    pipeline = CorrectiveRAGPipeline(settings)
    items = load_eval_dataset(settings.eval_dataset_path)[:3]

    rows = []
    for item in items:
        answer = pipeline.answer(item["input"])
        rows.append(
            {
                "question": item["input"],
                "answer": answer.answer,
                "contexts": [retrieved.document.text for retrieved in answer.retrieved],
                "ground_truth": item["expected_answer"],
            }
        )

    dataset = datasets.Dataset.from_list(rows)
    assert dataset.num_rows == 3
    assert {"question", "answer", "contexts", "ground_truth"}.issubset(dataset.column_names)
    assert ragas is not None


@pytest.mark.skipif(
    os.getenv("RAGAS_RUN_FULL") != "1",
    reason="Set RAGAS_RUN_FULL=1 in an environment with configured RAGAS LLM/embeddings.",
)
def test_ragas_full_metric_run(tmp_path):
    evaluate = pytest.importorskip("ragas").evaluate
    datasets = pytest.importorskip("datasets")
    metrics_module = pytest.importorskip("ragas.metrics")

    settings = Settings.from_env()
    settings = Settings(
        knowledge_base_path=settings.knowledge_base_path,
        eval_dataset_path=settings.eval_dataset_path,
        audit_db_path=tmp_path / "audit.sqlite3",
    )
    pipeline = CorrectiveRAGPipeline(settings)
    item = load_eval_dataset(settings.eval_dataset_path)[0]
    answer = pipeline.answer(item["input"])
    dataset = datasets.Dataset.from_list(
        [
            {
                "question": item["input"],
                "answer": answer.answer,
                "contexts": [retrieved.document.text for retrieved in answer.retrieved],
                "ground_truth": item["expected_answer"],
            }
        ]
    )

    result = evaluate(
        dataset,
        metrics=[
            metrics_module.faithfulness,
            metrics_module.answer_relevancy,
            metrics_module.context_precision,
            metrics_module.context_recall,
        ],
    )
    assert result is not None
