#Searches the loaded chunks
# Question
#     ↓
# Retrieve
#     ↓
# Grade
#     ↓
# Bad?
#  ┌───────┐
#  │ Yes   │
#  └───┬───┘
#      ↓
# Rewrite Query
#      ↓
# Retrieve Again
#      ↓
# Web Search
#      ↓
# Generate
# here it reduces hallucinations, missing context, retrieval failures



from __future__ import annotations

from corrective_rag.config import Settings
from corrective_rag.retriever import LocalBM25Retriever
from graph.nodes import generate, grade_documents, retrieve, rewrite_query, web_search
# retrieve-> retrive top docs
#grade_doc-> retrived_docs-> evaluate quality it checks relevance,coverage, confidence
#rewrite_query()-> original_query->better_query
# example : How does tracing work?
#         : How does LangFuse tracing and observability work?
# web_search() -> local docs insufficient -> seaches on internet
#generate()-> context-> LLM-> answer
#graph state : stores everything happening in the workflow
from graph.state import GraphState
#websearch tool wrapper around tavily search API
#used when local knowledge is insufficient
from tools.web_search import TavilyWebSearch

#RAG workflow
class CorrectiveRAGWorkflow:
    """Corrective RAG graph: retrieve -> grade -> rewrite/web_search when weak -> generate."""

    def __init__(
        self,
        retriever: LocalBM25Retriever, 
        generator,   # LLM wrapper groq
        settings: Settings,
        web_searcher: TavilyWebSearch | None = None,
    ) -> None:
        self.retriever = retriever
        self.generator = generator  #store LLM 
        self.settings = settings
        self.web_searcher = web_searcher or TavilyWebSearch()
    # the output should contain documents, answer, citations, evaluations 
    def run(self, question: str) -> GraphState:
        state = GraphState(question=question)
        state = retrieve(state, self.retriever, self.settings)
        state = grade_documents(state, self.settings)
        if state.corrected:
            state = rewrite_query(state)
            if state.scope == "local":
                state.documents = self.retriever.search(
                    state.rewritten_question,
                    top_k=self.settings.retrieval_top_k,
                )
            state = web_search(state, self.web_searcher)
        state = generate(state, self.generator, self.settings)
        return state
