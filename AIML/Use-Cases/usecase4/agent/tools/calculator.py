from langchain_core.tools import tool
import numexpr

@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression. Input must be a valid math expression string."""
    try:
        return str(numexpr.evaluate(expression).item())
    except Exception as e:
        return f"Error: {e}"
