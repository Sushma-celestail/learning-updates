'''graph/supervisor.py'''
"""Supervisor node implementation.

This node receives the current `CustomerState`, extracts the latest user message
(`state["messages"][-1]["content"]`), performs a very lightweight intent
classification based on keyword matching, and updates:

* ``state["pending_intents"]`` – a list of identified intents in order.
* ``state["next_agent"]`` – the first agent to handle the first pending intent.

The implementation purposefully avoids any external LLM calls to keep the code
simple, deterministic, and easy to understand for the use‑case.
"""

from typing import List

from .state import CustomerState
from memory.long_term import InMemoryStore

_store = InMemoryStore()

# Simple keyword‑to‑agent mapping
_KEYWORD_MAP = {
    "billing": "billing",
    "invoice": "billing",
    "refund": "billing",
    "technical": "tech",
    "tech": "tech",
    "error": "tech",
    "support": "tech",
    "account": "account",
    "password": "account",
    "email": "account",
    "reset": "account",
}

def _detect_intents(message: str) -> List[str]:
    """Return a list of intent strings based on keyword matches.

    The function lower‑cases the message and checks each keyword in
    ``_KEYWORD_MAP``. Duplicate intents are removed while preserving order.
    """
    lowered = message.lower()
    found: List[str] = []
    for kw, agent in _KEYWORD_MAP.items():
        if kw in lowered and agent not in found:
            found.append(agent)
    return found

def supervisor(state: CustomerState) -> CustomerState:
    """Supervisor node.

    Args:
        state: The current ``CustomerState``.

    Returns:
        The updated ``CustomerState`` with ``pending_intents`` and
        ``next_agent`` set. If no intent is detected, ``next_agent`` is set to
        ``"END"`` to terminate the graph.
    """
    # Assume the latest user message is the last entry in ``state["messages"]``
    if not state.get("messages"):
        # No messages yet – nothing to do.
        state["next_agent"] = "END"
        return state

    latest_msg = state["messages"][-1]["content"]
    intents = _detect_intents(latest_msg)

    if intents:
        state["pending_intents"] = intents
        # The first intent determines the initial next agent.
        state["next_agent"] = intents[0]
    else:
        # No matching intent – end the conversation.
        state["pending_intents"] = []
        state["next_agent"] = "END"

    # Merge any long‑term memory that may already be present in
    # ``state["customer_context"]``.
    user_id = state.get("customer_context", {}).get("user_id", "default_user")
    
    # Load long-term memory
    ltm = _store.get(user_id)
    if ltm:
        state.setdefault("customer_context", {}).update(ltm)

    # Save a simple fact into long-term memory based on the latest intent
    if intents:
        _store.set(user_id, {"last_issue": intents[0]})
        state.setdefault("customer_context", {})["last_issue"] = intents[0]

    return state
