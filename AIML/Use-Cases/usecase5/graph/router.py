'''graph/router.py'''
"""Router node for the use‑case 5 StateGraph.

The router reads ``state['next_agent']`` and ``state['pending_intents']``.
It implements the multi‑intent chaining logic described in the specification:

* If there are pending intents, pop the first one, set ``state['next_agent']`` to that intent, and return the intent name.
* If no pending intents remain, set ``state['next_agent']`` to ``"END"`` and return ``"END"``.

The function returns the name of the next node that the ``builder`` will invoke.
"""

from typing import Literal

from .state import CustomerState

def router(state: CustomerState) -> Literal["billing", "tech", "account", "END"]:
    """Conditional routing based on pending intents.

    Args:
        state: The current ``CustomerState``.

    Returns:
        The name of the next worker node (or ``"END"``).
    """
    # Ensure the pending_intents list exists.
    pending = state.get("pending_intents", [])
    if pending:
        # Pop the first pending intent and set it as the next agent.
        next_intent = pending.pop(0)
        state["pending_intents"] = pending
        state["next_agent"] = next_intent
        return next_intent
    else:
        # No more intents – terminate the graph.
        state["next_agent"] = "END"
        return "END"
