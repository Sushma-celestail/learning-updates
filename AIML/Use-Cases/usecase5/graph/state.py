# graph/state.py
"""State definitions shared across nodes."""

from typing import TypedDict, Literal, List, Dict, Any

class CustomerState(TypedDict, total=False):
    """State passed between graph nodes.
    
    - next_agent: which worker should handle the next intent.
    - customer_context: arbitrary dict storing user facts.
    - pending_intents: list of intents to resolve.
    """
    next_agent: Literal["billing", "tech", "account", "END"]
    customer_context: Dict[str, Any]
    pending_intents: List[str]

# Initial empty state helper
def initial_state() -> CustomerState:
    return CustomerState(
        next_agent="END",
        customer_context={},
        pending_intents=[],
    )
