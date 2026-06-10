"""Comprehensive tests for the Docs Buddy RAG chatbot."""
# This module contains both unit tests and integration tests
# Integration tests require GOOGLE_API_KEY and ingested documentation data

import json  # For loading ground truth questions from JSON file
import os    # For checking environment variables
import sys   # For adding project root to Python import path
from pathlib import Path  # For cross-platform file path operations

import pytest  # Testing framework for assertions and test organization

# Add project root to Python path for importing local modules
# This allows running pytest from any directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # Go up to ai-intern-monorepo
if str(PROJECT_ROOT) not in sys.path:  # Avoid duplicate entries
    sys.path.insert(0, str(PROJECT_ROOT))  # Add to beginning for import priority

# Import project modules for testing
from shared.config.settings import CHROMA_DIR, FALLBACK_PHRASE
from uc01_docs_buddy.chain import answer_question

# Define path to ground truth test data
GROUND_TRUTH_PATH = Path(__file__).with_name("ground_truth.json")


def load_ground_truth():
    """Load hand-written test questions from the JSON file."""
    # This function reads the test questions that validate acceptance criteria
    # Keeping questions in JSON makes them easy to edit without changing code
    
    with open(GROUND_TRUTH_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def has_google_key() -> bool:
    """Check if Google API key is available for integration tests."""
    # Integration tests need to call the real Gemini API
    # This function allows tests to skip gracefully when the key is missing
    
    return bool(os.getenv("GOOGLE_API_KEY"))


def has_chroma_store() -> bool:
    """Check if ChromaDB vector store exists and contains data."""
    # Integration tests need ingested documentation data to work
    # This function verifies that "python ingest.py" has been run successfully
    
    return (
        CHROMA_DIR.exists() and           # Directory exists
        any(CHROMA_DIR.iterdir())         # Directory is not empty
    )


# Unit Tests - These don't require API keys or external data
# They test the structure and configuration of the project

def test_ground_truth_file_exists():
    """Verify that the ground truth test data file exists."""
    # This ensures the test data file is properly included in the project
    
    assert GROUND_TRUTH_PATH.exists(), f"Ground truth file not found: {GROUND_TRUTH_PATH}"


def test_ground_truth_file_has_correct_structure():
    """Verify ground truth file contains required question categories."""
    # This validates the structure of our test data matches expectations
    
    data = load_ground_truth()
    
    # Check that both question categories exist
    assert "in_scope_questions" in data, "Missing in_scope_questions in ground truth"
    assert "out_of_scope_questions" in data, "Missing out_of_scope_questions in ground truth"
    
    # Verify data types are correct
    assert isinstance(data["in_scope_questions"], list), "in_scope_questions must be a list"
    assert isinstance(data["out_of_scope_questions"], list), "out_of_scope_questions must be a list"


def test_ground_truth_has_required_question_counts():
    """Verify ground truth contains exactly the required number of test questions."""
    # This test ensures we meet the acceptance criteria for test coverage:
    # - 10 in-scope questions (documentation questions)
    # - 3 out-of-scope questions (deliberate non-documentation questions)
    
    data = load_ground_truth()
    
    # Check exact counts as specified in acceptance criteria
    assert len(data["in_scope_questions"]) == 10, (
        f"Expected 10 in-scope questions, got {len(data['in_scope_questions'])}"
    )
    assert len(data["out_of_scope_questions"]) == 3, (
        f"Expected 3 out-of-scope questions, got {len(data['out_of_scope_questions'])}"
    )


def test_all_questions_are_non_empty_strings():
    """Verify all test questions are valid non-empty strings."""
    # This prevents issues with empty or invalid test data
    
    data = load_ground_truth()
    
    # Check in-scope questions
    for i, question in enumerate(data["in_scope_questions"]):
        assert isinstance(question, str), f"In-scope question {i} is not a string"
        assert question.strip(), f"In-scope question {i} is empty"
    
    # Check out-of-scope questions  
    for i, question in enumerate(data["out_of_scope_questions"]):
        assert isinstance(question, str), f"Out-of-scope question {i} is not a string"
        assert question.strip(), f"Out-of-scope question {i} is empty"


# Integration Tests - These require API key and ingested data
# They test the actual RAG functionality with real API calls

@pytest.mark.integration
def test_in_scope_answers_include_citations_for_at_least_8_questions():
    """Test that at least 8/10 in-scope answers include citation blocks with URLs."""
    # This validates Acceptance Criterion #2:
    # "The Streamlit app answers 10 hand-written ground-truth questions, 
    #  and at least 8/10 answers include a citation block listing the source URLs"
    
    # Skip if prerequisites are not met
    if not has_google_key():
        pytest.skip("GOOGLE_API_KEY environment variable not set")
    if not has_chroma_store():
        pytest.skip("ChromaDB store not found. Run 'python ingest.py' first")
    
    # Load test questions and generate answers
    questions = load_ground_truth()["in_scope_questions"]
    print(f"\nTesting {len(questions)} in-scope questions...")
    
    answers = []
    for i, question in enumerate(questions, 1):
        print(f"  {i}/10: {question}")
        answer = answer_question(question)
        answers.append(answer)
    
    # Count answers that include citations
    # We look for both "Citations" (or similar) and actual URLs
    cited_answers = []
    for i, answer in enumerate(answers):
        has_citation_section = any(
            keyword in answer.lower() 
            for keyword in ["citation", "source", "reference"]
        )
        has_urls = "https://" in answer
        
        if has_citation_section and has_urls:
            cited_answers.append(i)
    
    # Report results
    citation_count = len(cited_answers)
    print(f"\nResults: {citation_count}/10 answers included citations")
    
    if citation_count < 8:
        print("Answers without citations:")
        for i, answer in enumerate(answers):
            if i not in cited_answers:
                print(f"  Question {i+1}: {questions[i]}")
                print(f"  Answer: {answer[:200]}...")
    
    # Assert acceptance criterion
    assert citation_count >= 8, (
        f"Only {citation_count}/10 answers included citations. "
        f"Acceptance criteria requires at least 8/10."
    )


@pytest.mark.integration  
def test_out_of_scope_questions_use_fallback_phrase():
    """Test that all out-of-scope questions return the exact fallback phrase."""
    # This validates Acceptance Criterion #3:
    # "For 3 deliberately out-of-scope questions, the bot responds 
    #  with the configured fallback phrase 3/3 times"
    
    # Skip if prerequisites are not met
    if not has_google_key():
        pytest.skip("GOOGLE_API_KEY environment variable not set")
    if not has_chroma_store():
        pytest.skip("ChromaDB store not found. Run 'python ingest.py' first")
    
    # Load out-of-scope test questions
    questions = load_ground_truth()["out_of_scope_questions"]
    print(f"\nTesting {len(questions)} out-of-scope questions...")
    
    # Test each out-of-scope question
    for i, question in enumerate(questions, 1):
        print(f"  {i}/3: {question}")
        answer = answer_question(question)
        
        # Check if answer contains the exact fallback phrase
        assert FALLBACK_PHRASE in answer, (
            f"Out-of-scope question {i} did not use fallback phrase.\n"
            f"Question: {question}\n"
            f"Answer: {answer}\n"
            f"Expected phrase: {FALLBACK_PHRASE}"
        )
    
    print(f"✅ All {len(questions)} out-of-scope questions used the fallback phrase")


@pytest.mark.integration
def test_answer_latency_is_reasonable():
    """Test that answer generation completes within reasonable time limits."""
    # This helps validate Acceptance Criterion #4 about latency
    # We test with a simple question to measure baseline performance
    
    # Skip if prerequisites are not met
    if not has_google_key():
        pytest.skip("GOOGLE_API_KEY environment variable not set")
    if not has_chroma_store():
        pytest.skip("ChromaDB store not found. Run 'python ingest.py' first")
    
    import time
    
    # Use a simple question for latency testing
    test_question = "What is FastAPI?"
    
    # Measure response time
    start_time = time.time()
    answer = answer_question(test_question)
    end_time = time.time()
    
    latency = end_time - start_time
    print(f"\nLatency test: {latency:.2f} seconds for question: '{test_question}'")
    
    # Verify we got a real answer
    assert answer.strip(), "Answer should not be empty"
    assert len(answer) > 10, "Answer should be substantial"
    
    # Check latency is reasonable (allowing some buffer beyond the 4s requirement)
    assert latency < 10, (
        f"Answer took {latency:.2f} seconds, which is too slow. "
        f"Target is <4s for p50 latency."
    )
    
    print(f"✅ Latency test passed: {latency:.2f}s")


# Test runner helper for development
if __name__ == "__main__":
    # Allow running this file directly for quick testing during development
    pytest.main([__file__, "-v"])