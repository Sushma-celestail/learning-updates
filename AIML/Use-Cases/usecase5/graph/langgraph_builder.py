# graph/langgraph_builder.py
"""LangGraph StateGraph definition for Use‑Case 5.

This file creates a real ``StateGraph`` (from the *langgraph* library) that
mirrors the lightweight loop implemented in ``graph/builder.py``.  The graph
contains the following nodes and edges:

* **supervisor** – classifies intents from the latest user message.
* **router** – looks at ``state["next_agent"]`` and routes to the appropriate
  worker (``billing``, ``tech`` or ``account``).  If ``next_agent`` is ``END``
  the graph terminates.
* **billing**, **tech**, **account** – the three mock worker agents.
* After each worker the execution returns to **router** to handle any remaining
  pending intents.
* The final node is ``END`` which simply returns the state.

Usage example::

    from graph.langgraph_builder import run_graph, initial_state
    state = initial_state()
    state["messages"].append({"role": "user", "content": "Can you show me my invoice?"})
    final_state = run_graph(state)

The ``run_graph`` helper compiles the graph on first call and then invokes it.
"""

from __future__ import annotations

from typing import Callable, Literal

from langgraph.graph import StateGraph, END

from .state import CustomerState, initial_state
from .supervisor import supervisor
from .router import router
from agents.billing_agent import billing_agent
from agents.tech_agent import tech_agent
from agents.account_agent import account_agent


def _build_graph() -> StateGraph[CustomerState]:
    """Construct and return the StateGraph.

    The graph mirrors the execution flow described in the project docs:
    ``supervisor -> router -> worker -> router -> … -> END``.
    """
    graph = StateGraph(CustomerState)

    # Nodes
    graph.add_node("supervisor", supervisor)  # type: ignore[arg-type]
    graph.add_node("router", router)  # type: ignore[arg-type]
    graph.add_node("billing", billing_agent)  # type: ignore[arg-type]
    graph.add_node("tech", tech_agent)  # type: ignore[arg-type]
    graph.add_node("account", account_agent)  # type: ignore[arg-type]

    # Edges
    graph.add_edge("supervisor", "router")

    # Conditional routing based on the ``next_agent`` set by the router.
    def _router_conditional(state: CustomerState) -> Literal["billing", "tech", "account", END]:
        return state.get("next_agent", END)  # type: ignore[return-value]

    graph.add_conditional_edges(
        "router",
        condition=_router_conditional,
        mapping={
            "billing": "billing",
            "tech": "tech",
            "account": "account",
            END: END,
        },
    )

    # After a worker we go back to the router for any remaining intents.
    graph.add_edge("billing", "router")
    graph.add_edge("tech", "router")
    graph.add_edge("account", "router")

    graph.set_entry_point("supervisor")
    return graph

# Cache compiled graph.
_GRAPH: StateGraph[CustomerState] | None = None

def _get_graph() -> StateGraph[CustomerState]:
    global _GRAPH
    if _GRAPH is None:
        _GRAPH = _build_graph()
    return _GRAPH


def run_graph(state: CustomerState) -> CustomerState:
    """Execute the LangGraph pipeline and return the final state."""
    return _get_graph().invoke(state)

__all__ = ["run_graph", "initial_state"]
