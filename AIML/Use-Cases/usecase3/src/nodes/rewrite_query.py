from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate


# =========================
# REWRITE QUERY NODE
# =========================

def rewrite_query(state):
    """
    Rewrites the current question to be better suited for a web search engine.
    Preserves all other state fields via model_copy().
    """

    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0
    )

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            (
                "You are a search query optimizer. "
                "Rewrite the given question to be clearer, more specific, "
                "and better suited for a web search engine. "
                "Return ONLY the rewritten query — no explanation, no preamble."
            ),
        ),
        ("human", "{question}"),
    ])

    chain = prompt | llm

    rewritten = chain.invoke({"question": state.question})

    return state.model_copy(
        update={"question": rewritten.content.strip()}
    )
