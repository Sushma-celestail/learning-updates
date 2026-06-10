from langchain.tools import tool

@tool
def execute_sql(query: str) -> str:
    """
    Mock SQL execution.
    """

    return f"Executed SQL: {query}"