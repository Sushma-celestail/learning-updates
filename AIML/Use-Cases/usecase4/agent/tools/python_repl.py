"""Sandboxed Python REPL tool with timeout enforcement."""

from langchain_core.tools import tool
import subprocess
import sys


@tool
def python_repl(code: str) -> str:
    """Run a small Python snippet and return stdout. A 5-second timeout is enforced.
    Use this for computations, data manipulation, or quick scripts.
    Do NOT use this for infinite loops or long-running processes."""
    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True, text=True, timeout=5
        )
        output = result.stdout or result.stderr
        # Truncate output at 2000 characters to prevent runaway responses
        if len(output) > 2000:
            output = output[:2000] + "\n... (output truncated)"
        return output
    except subprocess.TimeoutExpired:
        return "Timeout: execution exceeded 5 seconds."
    except Exception as e:
        return f"Execution error: {e}"
