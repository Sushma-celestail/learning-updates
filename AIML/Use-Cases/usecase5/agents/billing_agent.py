# agents/billing_agent.py
"""Billing agent – mock worker that handles billing related intents.

It uses the mock tools defined in ``tools.billing_tools`` to retrieve an invoice
or process a refund. The function receives a ``CustomerState`` and must return the
updated state.
"""

from typing import Dict, Any

from graph.state import CustomerState
from tools.billing_tools import get_invoice, refund


def billing_agent(state: CustomerState) -> CustomerState:
    """Process a billing intent.

    The supervisor has already identified the intent as ``billing`` and
    popped it from ``state['pending_intents']``. We now inspect the latest user
    message to decide which mock tool to invoke:

    * If the user explicitly mentions *refund* (e.g. "refund my order"), we call
      ``refund()``.
    * Otherwise we assume they just want invoice information and call
      ``get_invoice()``.
    The response is appended to ``state['messages']`` as an assistant message.
    """
    # Get the most recent user message (if any)
    user_msgs = [m["content"] for m in state.get("messages", []) if m.get("role") == "user"]
    user_msg = user_msgs[-1] if user_msgs else ""
    lowered = user_msg.lower()

    if "refund" in lowered:
        # User asked for a refund – invoke the refund tool.
        result = refund()
    else:
        # Default path – show the invoice.
        result = get_invoice()

    # Append assistant response.
    state.setdefault("messages", []).append({"role": "assistant", "content": result})
    state.setdefault("executed_agents", []).append("billing")

    # The router will decide the next agent.
    return state
