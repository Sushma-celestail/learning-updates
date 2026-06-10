# Retrieve
#    ↓
# Grade Retrieval
#    ↓
# If weak:
#    Rewrite Query
#    ↓
#    Web Search
#    ↓
# Generate Answer
#    ↓
# Evaluate Hallucination
#    ↓
# Evaluate Helpfulness

#defines RAG flow
from __future__ import annotations

from corrective_rag.config import Settings
from corrective_rag.evaluators import hallucination_evaluator, helpfulness_evaluator
from corrective_rag.retriever import LocalBM25Retriever, expand_query
from corrective_rag.scope import classify_question
from corrective_rag.tracing import observe
from graph.state import GraphState
from tools.web_search import TavilyWebSearch

#@observe is used for tracing, logging, monitoring, langfuse integration
@observe(name="retrieve")
def retrieve(state: GraphState, retriever: LocalBM25Retriever, settings: Settings) -> GraphState:
    state.scope = classify_question(state.question)
    # here it list out the top 4 document with prob score
    state.documents = retriever.search(state.question, top_k=settings.retrieval_top_k)
    #grade actually select best matching document in which retrieval quality 
    state.grade = max((item.score for item in state.documents), default=0.0)
    return state

# gives highest retrieval score compare with threshhold  
@observe(name="grade_documents")
def grade_documents(state: GraphState, settings: Settings) -> GraphState:
    if state.scope == "web":
        state.documents = []
        state.grade = 0.0
        state.corrected = True
        state.correction_reason = "web_required"
        return state
    state.grade = max((item.score for item in state.documents), default=0.0)
    #if the grade is 4.5 means correct = False no need of correction reason 
    if state.grade < settings.min_retrieval_score:
        state.corrected = True
        state.correction_reason = "retrieval_score_below_threshold"
    return state

#if weak retrieval -> improve the query
@observe(name="rewrite_query")
def rewrite_query(state: GraphState) -> GraphState:
    state.iterations += 1
    state.rewritten_question = expand_query(state.question)
    return state

# if the local docs not enough -> search internet
@observe(name="web_search")
def web_search(state: GraphState, web_searcher: TavilyWebSearch) -> GraphState:
    state.web_documents = web_searcher.search(state.rewritten_question or state.question)
    if state.scope == "web" and not state.web_documents:
        state.documents = []
        state.grade = 0.0
        state.correction_reason = "web_search_unavailable"
        return state
    existing_ids = {item.document.doc_id for item in state.documents}
    state.documents.extend(
        item for item in state.web_documents if item.document.doc_id not in existing_ids
    )
    state.grade = max((item.score for item in state.documents), default=0.0)
    return state

# question + documents -> LLM -> answer
@observe(name="generate")
def generate(state: GraphState, generator, settings: Settings) -> GraphState:
    state.generation = generator.generate(state.question, state.documents)
    state.evaluations = [
        hallucination_eval(state, settings),
        helpfulness_eval(state, settings),
    ]
    return state


@observe(name="hallucination_eval")
def hallucination_eval(state: GraphState, settings: Settings):
    return hallucination_evaluator(
        state.generation,
        state.documents,
        settings.min_hallucination_score,
    )


@observe(name="helpfulness_eval")
def helpfulness_eval(state: GraphState, settings: Settings):
    return helpfulness_evaluator(
        state.question,
        state.generation,
        state.documents,
        settings.min_helpfulness_score,
    )
