from __future__ import annotations

import json

from corrective_rag.config import Settings
from corrective_rag.corpus import load_eval_dataset
from corrective_rag.pipeline import CorrectiveRAGPipeline
from corrective_rag.report import build_report
from corrective_rag.seed_langfuse import validate_dataset


def test_corrective_rag_answers_with_citations(tmp_path):
    settings = Settings.from_env()
    settings = Settings(
        knowledge_base_path=settings.knowledge_base_path,
        eval_dataset_path=settings.eval_dataset_path,
        audit_db_path=tmp_path / "audit.sqlite3",
    )
    pipeline = CorrectiveRAGPipeline(settings)

    result = pipeline.answer("How does this project map to NIST AI RMF MEASURE?")

    assert result.answer
    assert result.citations
    assert any(item.document.doc_id == "NIST-02" for item in result.retrieved)
    assert all(evaluation.passed for evaluation in result.evaluations)


def test_low_retrieval_query_abstains_and_is_audited(tmp_path):
    settings = Settings.from_env()
    settings = Settings(
        knowledge_base_path=settings.knowledge_base_path,
        eval_dataset_path=settings.eval_dataset_path,
        audit_db_path=tmp_path / "audit.sqlite3",
    )
    pipeline = CorrectiveRAGPipeline(settings)

    result = pipeline.answer("What is the cafeteria menu on Mars next Tuesday?")
    latest = pipeline.audit_logger.latest(1)

    assert "not have enough grounded" in result.answer.lower()
    assert result.corrected
    assert latest[0]["trace_id"] == result.trace_id
    assert json.loads(latest[0]["evaluations_json"])


def test_dataset_has_required_langfuse_seed_count():
    settings = Settings.from_env()
    items = load_eval_dataset(settings.eval_dataset_path)

    validate_dataset(items)
    assert len(items) >= 30


def test_ci_report_shape(tmp_path, monkeypatch):
    settings = Settings.from_env()
    monkeypatch.setenv("CORRECTIVE_RAG_DB", str(tmp_path / "audit.sqlite3"))
    report = build_report(limit=3)

    assert report["total_items"] == 3
    assert "mean_online_score" in report
    assert all("evaluations" in row for row in report["rows"])
