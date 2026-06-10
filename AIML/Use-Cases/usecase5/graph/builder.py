# graph/builder.py
"""Graph builder for the use‑case 5 StateGraph.

The builder creates a lightweight execution loop that mimics LangGraph's
`StateGraph`. It wires together the following nodes:

* ``supervisor`` – classifies intents from the latest user message.
* ``router`` – conditional edge that selects the next worker based on
  ``state["next_agent"]`` and handles multi‑intent chaining.
* ``billing_agent`` – mock billing worker.
* ``tech_agent`` – mock technical support worker.
* ``account_agent`` – mock account‑management worker.
* ``END`` – terminates the loop.

The ``run_graph`` function takes an initial ``CustomerState`` and executes the
nodes until ``next_agent`` becomes ``"END"``. It returns the final state.
"""

from typing import Callable, Dict

from .state import CustomerState, initial_state
from .supervisor import supervisor
from .router import router
from agents.billing_agent import billing_agent
from agents.tech_agent import tech_agent
from agents.account_agent import account_agent
from observability.langfuse_logger import log_node

# Mapping node names to callables that accept and return ``CustomerState``.
_NODE_MAP: Dict[str, Callable[[CustomerState], CustomerState]] = {
    "supervisor": supervisor,
    "router": router,  # router returns the next node name, handled separately
    "billing": billing_agent,
    "tech": tech_agent,
    "account": account_agent,
}

def run_graph(state: CustomerState) -> CustomerState:
    """Execute the StateGraph loop.

    The loop follows the pattern:
    1. ``supervisor`` – runs once at the start of a user turn.
    2. ``router`` – determines which worker node to invoke.
    3. Worker node – performs its mock work and updates ``state``.
    4. Repeat from step 2 until ``next_agent == "END"``.
    """
    # Ensure we have a proper state structure.
    if "messages" not in state:
        state["messages"] = []

    # Initial supervisor pass (classify intents).
    latest_msg = state["messages"][-1]["content"] if state.get("messages") else ""
    state = supervisor(state)
    log_node("supervisor", latest_msg, str(state.get("pending_intents", [])))

    while True:
        # Determine the next node via router.
        next_node = router(state)
        if next_node == "END" or next_node not in _NODE_MAP:
            break
        # Execute the worker node.
        state = _NODE_MAP[next_node](state)
        # Log the worker node execution
        last_response = state["messages"][-1]["content"] if state.get("messages") else ""
        log_node(next_node, latest_msg, last_response)
        # After a worker finishes, the loop returns to the router to check
        # for any remaining pending intents.
    return state
