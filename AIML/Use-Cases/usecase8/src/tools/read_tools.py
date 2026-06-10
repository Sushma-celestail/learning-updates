from langchain.tools import tool

@tool
def read_file(path: str) -> str:
    """Read file contents."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

