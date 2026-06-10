from __future__ import annotations

from .config import GovernanceConfig


def build_gemini_llm(config: GovernanceConfig):
    """Create the Gemini chat model used by the LangGraph swarm."""
    if not config.google_api_key:
        raise RuntimeError("GOOGLE_API_KEY is not configured. Add it to .env before using Gemini agents.")

    from langchain_google_genai import ChatGoogleGenerativeAI

    return ChatGoogleGenerativeAI(
        model=config.model_name,
        google_api_key=config.google_api_key,
        temperature=0,
    )
