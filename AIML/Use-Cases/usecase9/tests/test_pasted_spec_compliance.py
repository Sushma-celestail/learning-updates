from __future__ import annotations

import sqlite3
from pathlib import Path

from corrective_rag.config import Settings
from corrective_rag.pipeline import CorrectiveRAGPipeline
from corrective_rag.report import assert_thresholds, build_report
from datasets.exporter import export_approved_conversations


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_requested_folder_structure_exists():
    expected = [
        "src/graph/state.py",
        "src/graph/nodes.py",
        "src/graph/workflow.py",
        "src/retriever/chroma.py",
        "src/llm/groq.py",
        "src/tools/web_search.py",
        "src/observability/langfuse_config.py",
        "src/observability/callbacks.py",
        "src/evaluations/online/hallucination.py",
        "src/evaluations/online/helpfulness.py",
        "src/audit/database.py",
        "src/audit/logger.py",
        "src/datasets/exporter.py",
        "docs/GOVERNANCE_POLICY.md",
    ]
    for relative_path in expected:
        assert (PROJECT_ROOT / relative_path).exists(), relative_path


def test_audit_logs_view_exposes_required_fields(tmp_path, monkeypatch):
    monkeypatch.setenv("CORRECTIVE_RAG_DB", str(tmp_path / "audit.sqlite3"))
    monkeypatch.setenv("CORRECTIVE_RAG_LLM", "local")
    pipeline = CorrectiveRAGPipeline(Settings.from_env())
    pipeline.answer("What does the online hallucination evaluator check?", user_id="test-user")

    with sqlite3.connect(tmp_path / "audit.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM audit_logs LIMIT 1").fetchone()

    assert row["user_id"] == "test-user"
    assert row["prompt"]
    assert row["response"]
    assert row["retrieved_doc_ids"]
    assert row["model"]
    assert row["latency"] >= 0


def test_ci_threshold_report_and_exporter(tmp_path, monkeypatch):
    monkeypatch.setenv("CORRECTIVE_RAG_DB", str(tmp_path / "audit.sqlite3"))
    monkeypatch.setenv("CORRECTIVE_RAG_LLM", "local")

    report = build_report(limit=3)
    assert_thresholds(report)
    exported = export_approved_conversations(dry_run=True, limit=3)

    assert exported["exportable"] >= 1
