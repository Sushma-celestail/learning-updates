"""Integration tests for the agent."""

import os
import sys
import uuid
import pytest
from dotenv import load_dotenv

# Load env and set up path
load_dotenv()
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent.core import run_agent


class TestAgentBasic:
    """Basic agent integration tests."""

    def test_simple_factual_question(self):
        """Agent should return a non-empty answer for a simple question."""
        thread_id = str(uuid.uuid4())
        answer = run_agent("What is the capital of France?", thread_id)
        assert isinstance(answer, str)
        assert len(answer) > 0
        assert "paris" in answer.lower()

    def test_iteration_cap(self):
        """Agent should gracefully stop on unanswerable questions."""
        thread_id = str(uuid.uuid4())
        answer = run_agent(
            "Search the web repeatedly to find the secret codename of the person "
            "who bought the exactly 1000th ticket to the 1994 World Cup final, "
            "then look up their high school math teacher's favorite color. "
            "You MUST use the search tool repeatedly until you find the exact color, "
            "do not stop or give up.",
            thread_id,
        )
        assert isinstance(answer, str)
        # Should either hit the iteration cap or explain it can't find the answer
        assert "8 steps" in answer.lower() or "couldn't" in answer.lower() or "cannot" in answer.lower() or "unable" in answer.lower()

    def test_multiturn_memory(self):
        """Follow-up question should use the previous turn's answer."""
        thread_id = str(uuid.uuid4())

        # First question
        answer1 = run_agent(
            "What is the population of France?",
            thread_id,
        )
        assert isinstance(answer1, str)
        assert len(answer1) > 0

        # Follow-up in the same thread
        answer2 = run_agent(
            "And what is that number divided by 1 million?",
            thread_id,
        )
        assert isinstance(answer2, str)
        assert len(answer2) > 0
