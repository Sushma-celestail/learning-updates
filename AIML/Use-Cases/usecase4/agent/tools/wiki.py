"""Wikipedia lookup tool with proper error handling."""

from langchain_core.tools import tool
import wikipedia


@tool
def wikipedia_search(query: str) -> str:
    """Search Wikipedia for a topic and return a concise summary with source URL.
    Use this for historical facts, biographies, scientific concepts, or general knowledge."""
    try:
        summary = wikipedia.summary(query, sentences=5)
        page = wikipedia.page(query)
        return f"{summary}\n\nSource: {page.url}"
    except wikipedia.exceptions.DisambiguationError as e:
        options = ", ".join(e.options[:10])
        return f"Disambiguation: multiple results found. Try one of: {options}"
    except wikipedia.exceptions.PageError:
        return f"No Wikipedia page found for '{query}'. Try a different search term."
    except Exception as e:
        return f"Wikipedia error: {e}"
