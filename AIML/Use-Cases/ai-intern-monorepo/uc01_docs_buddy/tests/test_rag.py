"""
UC01 — Docs Buddy: Test suite.

Unit tests run without any API key or ingested data.
Integration tests (marked @pytest.mark.integration) require:
  - GOOGLE_API_KEY set in .env
  - ChromaDB populated by running: python uc01_docs_buddy/ingest.py

Run unit tests only:
    pytest uc01_docs_buddy/tests/ -m "not integration" -v

Run all tests (including integration):
    pytest uc01_docs_buddy/tests/ -v
"""

import json
import os
import sys
import time
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from shared.config.settings import FALLBACK_PHRASE, UC01_CHROMA_DIR

GROUND_TRUTH = Path(__file__).parent / "ground_truth.json"


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

def _load_gt():
    with open(GROUND_TRUTH, encoding="utf-8") as f:
        return json.load(f)


def _has_api_key() -> bool:
    return bool(os.getenv("GOOGLE_API_KEY"))


def _has_chroma() -> bool:
    return UC01_CHROMA_DIR.exists() and any(UC01_CHROMA_DIR.iterdir())


# ---------------------------------------------------------------------------
# Unit tests — no API key needed
# ---------------------------------------------------------------------------

def test_ground_truth_file_exists():
    """Ground truth JSON must be present in the repo."""
    assert GROUND_TRUTH.exists(), f"Missing: {GROUND_TRUTH}"


def test_ground_truth_structure():
    """JSON must have in_scope_questions and out_of_scope_questions keys."""
    data = _load_gt()
    assert "in_scope_questions"   in data
    assert "out_of_scope_questions" in data
    assert isinstance(data["in_scope_questions"],    list)
    assert isinstance(data["out_of_scope_questions"], list)


def test_ground_truth_counts():
    """Exactly 10 in-scope and 3 out-of-scope questions (AC2, AC3)."""
    data = _load_gt()
    assert len(data["in_scope_questions"])    == 10, "Need exactly 10 in-scope questions"
    assert len(data["out_of_scope_questions"]) == 3,  "Need exactly 3 out-of-scope questions"


def test_all_questions_non_empty():
    """Every question must be a non-empty string."""
    data = _load_gt()
    for q in data["in_scope_questions"] + data["out_of_scope_questions"]:
        assert isinstance(q, str) and q.strip(), f"Empty/invalid question: {q!r}"


def test_fallback_phrase_configured():
    """FALLBACK_PHRASE must be a non-empty string."""
    assert isinstance(FALLBACK_PHRASE, str) and FALLBACK_PHRASE.strip()


# ---------------------------------------------------------------------------
# Integration tests — require API key + ingested data
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_in_scope_citations(capsys):
    """
    AC2: At least 8/10 in-scope answers must include a citation block with URLs.
    """
    if not _has_api_key():
        pytest.skip("GOOGLE_API_KEY not set")
    if not _has_chroma():
        pytest.skip("ChromaDB not populated — run python uc01_docs_buddy/ingest.py")

    from uc01_docs_buddy.chain import answer_question

    questions = _load_gt()["in_scope_questions"]
    cited = 0

    for i, q in enumerate(questions, 1):
        answer = answer_question(q)
        has_section = any(kw in answer.lower() for kw in ("citation", "source", "reference"))
        has_url     = "https://" in answer
        if has_section and has_url:
            cited += 1
        print(f"  Q{i}: cited={has_section and has_url} | {q[:60]}")

    print(f"\nCitations: {cited}/10")
    assert cited >= 8, f"Only {cited}/10 answers had citations (need ≥8)"


@pytest.mark.integration
def test_out_of_scope_fallback():
    """
    AC3: All 3 out-of-scope questions must return the exact fallback phrase.
    """
    if not _has_api_key():
        pytest.skip("GOOGLE_API_KEY not set")
    if not _has_chroma():
        pytest.skip("ChromaDB not populated — run python uc01_docs_buddy/ingest.py")

    from uc01_docs_buddy.chain import answer_question

    questions = _load_gt()["out_of_scope_questions"]
    for q in questions:
        answer = answer_question(q)
        assert FALLBACK_PHRASE in answer, (
            f"Fallback phrase missing.\nQ: {q}\nA: {answer}"
        )


@pytest.mark.integration
def test_latency_under_10s():
    """
    AC4: p50 latency target is <4 s; we assert <10 s as a generous CI bound.
    """
    if not _has_api_key():
        pytest.skip("GOOGLE_API_KEY not set")
    if not _has_chroma():
        pytest.skip("ChromaDB not populated — run python uc01_docs_buddy/ingest.py")

    from uc01_docs_buddy.chain import answer_question

    t0     = time.perf_counter()
    answer = answer_question("What is FastAPI?")
    elapsed = time.perf_counter() - t0

    print(f"\nLatency: {elapsed:.2f}s")
    assert answer.strip(), "Answer must not be empty"
    assert elapsed < 10, f"Latency {elapsed:.2f}s exceeds 10 s ceiling"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
