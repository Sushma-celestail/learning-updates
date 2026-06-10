import subprocess
import tempfile

FORBIDDEN_IMPORTS = [
    "socket",
    "requests",
    "urllib",
    "http",
]

def run_python_safely(code: str):

    for item in FORBIDDEN_IMPORTS:

        if item in code:
            return f"Blocked import: {item}"

    with tempfile.NamedTemporaryFile(
        suffix=".py",
        delete=False,
        mode="w"
    ) as f:

        f.write(code)
        file_name = f.name

    try:

        result = subprocess.run(
            ["python", file_name],
            capture_output=True,
            text=True,
            timeout=5,
        )

        return result.stdout

    except subprocess.TimeoutExpired:

        return "Execution timed out after 5 seconds"