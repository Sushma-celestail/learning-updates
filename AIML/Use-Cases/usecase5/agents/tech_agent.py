# agents/tech_agent.py

from graph.state import CustomerState
from tools.rag_retriever import retrieve


def tech_agent(state: CustomerState) -> CustomerState:
    """
    Process technical support requests using the RAG retriever.
    """

    # Get latest user message
    user_msgs = [
        msg["content"]
        for msg in state.get("messages", [])
        if msg.get("role") == "user"
    ]

    user_msg = user_msgs[-1] if user_msgs else ""

    # Retrieve documentation
    answer = retrieve(user_msg)

    # Handle empty results
    if not answer or not answer.strip():
        answer = (
            "I couldn't find relevant technical documentation for your query.\n\n"
            "You can ask about:\n"
            "• Product features\n"
            "• Installation steps\n"
            "• Configuration\n"
            "• Troubleshooting\n"
            "• API usage"
        )

    # Add assistant response
    state.setdefault("messages", []).append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    return state