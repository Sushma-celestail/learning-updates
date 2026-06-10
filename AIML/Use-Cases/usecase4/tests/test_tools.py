"""Unit tests for individual tools."""

import os
import sys
import pytest
from dotenv import load_dotenv

# Load env and set up path
load_dotenv()
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class TestCalculator:
    """Tests for the calculator tool."""

    def test_power(self):
        from agent.tools.calculator import calculator
        result = calculator.invoke({"expression": "2 ** 10"})
        assert "1024" in result

    def test_division(self):
        from agent.tools.calculator import calculator
        result = calculator.invoke({"expression": "100 / 4"})
        assert "25" in result

    def test_invalid_expression(self):
        from agent.tools.calculator import calculator
        result = calculator.invoke({"expression": "foo + bar"})
        assert "Error" in result


class TestPythonRepl:
    """Tests for the python_repl tool."""

    def test_simple_print(self):
        from agent.tools.python_repl import python_repl
        result = python_repl.invoke({"code": "print('hello')"})
        assert "hello" in result

    def test_math_computation(self):
        from agent.tools.python_repl import python_repl
        result = python_repl.invoke({"code": "print(sum(range(1, 101)))"})
        assert "5050" in result

    def test_timeout(self):
        from agent.tools.python_repl import python_repl
        result = python_repl.invoke({"code": "while True: pass"})
        assert "Timeout" in result


class TestWikipedia:
    """Tests for the wikipedia_search tool."""

    def test_known_topic(self):
        from agent.tools.wiki import wikipedia_search
        result = wikipedia_search.invoke({"query": "Python (programming language)"})
        assert "wikipedia.org" in result.lower() or "python" in result.lower()

    def test_disambiguation(self):
        from agent.tools.wiki import wikipedia_search
        result = wikipedia_search.invoke({"query": "Mercury"})
        # Could be a disambiguation or a valid page — both are acceptable
        assert len(result) > 0


class TestWebSearch:
    """Tests for the web_search tool."""

    def test_basic_search(self):
        from agent.tools.search import web_search
        result = web_search.invoke({"query": "capital of France"})
        assert "paris" in result.lower() or "france" in result.lower()
