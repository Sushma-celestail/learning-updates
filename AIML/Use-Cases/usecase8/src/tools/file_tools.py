from langchain.tools import tool

@tool
def write_file(path: str, content: str) -> str:
    """Write content to file."""
    with open(path, "w") as f:
        f.write(content)

    return f"Written to {path}"

