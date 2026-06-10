"""
Gemini chat client — shared by UC01 and UC02.

Uses the google-genai SDK directly with an explicit timeout.
Implements LangChain's Runnable interface as a simple callable
so it works in LCEL chains: prompt | GeminiChat() | StrOutputParser()
"""

import os
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import AIMessage
from langchain_core.prompt_values import PromptValue

from shared.config.settings import CHAT_MODEL


def _call_gemini(prompt_value: PromptValue) -> AIMessage:
    """
    Call Gemini via the google-genai SDK with a 30-second timeout.
    Accepts a LangChain PromptValue, returns an AIMessage.
    """
    from google import genai
    from google.genai.types import HttpOptions

    client = genai.Client(
        api_key=os.environ.get("GOOGLE_API_KEY", ""),
        http_options=HttpOptions(timeout=30000),  # 30 seconds in ms
    )

    # Convert PromptValue messages to a single string
    messages = prompt_value.to_messages()
    parts = []
    for msg in messages:
        role    = getattr(msg, "type", "human")
        content = msg.content
        if role == "system":
            parts.append(f"Instructions:\n{content}")
        else:
            parts.append(content)

    prompt_text = "\n\n".join(parts)

    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=prompt_text,
    )

    return AIMessage(content=response.text or "")


# GeminiChat is a RunnableLambda — works in any LCEL chain
# Usage: prompt | GeminiChat | StrOutputParser()
GeminiChat = RunnableLambda(_call_gemini)
