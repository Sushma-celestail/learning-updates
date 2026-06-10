from langgraph.graph import StateGraph, END

from src.graph.state import GraphState

from src.nodes.retrieve import retrieve
from src.nodes.grade_documents import grade_documents
from src.nodes.rewrite_query import rewrite_query
from src.nodes.web_search import web_search
from src.nodes.generate import generate

from src.graph.edges import decide_route

# =========================
# BUILD GRAPH
# =========================

def build_graph():

    workflow = StateGraph(GraphState)

    # =========================
    # NODES
    # =========================

    workflow.add_node("retrieve", retrieve)

    workflow.add_node(
        "grade_documents",
        grade_documents
    )

    workflow.add_node(
        "rewrite_query",
        rewrite_query
    )

    workflow.add_node(
        "web_search",
        web_search
    )

    workflow.add_node(
        "generate",
        generate
    )

    from langgraph.graph import START
    
    # =========================
    # ENTRY
    # =========================

    workflow.add_edge(START, "retrieve")

    # =========================
    # FLOW
    # =========================

    workflow.add_edge(
        "retrieve",
        "grade_documents"
    )

    workflow.add_conditional_edges(
        "grade_documents",
        decide_route,
        {
            "generate": "generate",
            "rewrite": "rewrite_query",
        }
    )

    workflow.add_edge(
        "rewrite_query",
        "web_search"
    )

    workflow.add_edge(
        "web_search",
        "grade_documents"
    )

    workflow.add_edge(
        "generate",
        END
    )

    return workflow.compile()