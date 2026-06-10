from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate


# =========================
# GENERATE NODE
# =========================

def generate(state):
    """
    Generates the final answer from the current documents and question.

    Bug fixed
    ---------
    Was returning `{**state, ...}` which fails on a Pydantic model.
    Now uses model_copy() consistently with the other nodes.
    """

    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0
    )

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            (
                "You are a helpful assistant. "
                "Answer the question using ONLY the provided context. "
                "If the context does not contain enough information, say so honestly. "
                "Be concise and precise."
            ),
        ),
        (
            "human",
            "Context:\n{documents}\n\nQuestion: {question}"
        ),
    ])

    chain = prompt | llm

    result = chain.invoke({
        "question": state.question,
        "documents": "\n\n---\n\n".join(state.documents) if state.documents else "No context available.",
    })

    return state.model_copy(
        update={"generation": result.content}
    )
