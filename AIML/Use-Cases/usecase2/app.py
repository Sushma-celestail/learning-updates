# STREAMLIT APPLICATION
# Goal:
# User Query → Hybrid Retrieval → Rerank → LLM Answer

import streamlit as st
from dotenv import load_dotenv
from langfuse.langchain import CallbackHandler

from langchain_core.documents import Document

from src.vectordb import get_vectorstore
from src.retriever import (
    create_bm25,
    create_ensemble_retriever
)
from src.reranker import rerank
from src.chain import create_rag_chain

load_dotenv()

# UI CONFIG

st.set_page_config(
    page_title="Hybrid RAG Assistant",
    page_icon="🚀",
    layout="wide"
)

st.title("Hybrid RAG Assistant 🚀")

# SESSION MEMORY

if "messages" not in st.session_state:
    st.session_state.messages = []
# RAG PIPELINE SETUP (runs once)

@st.cache_resource
def setup_rag():

   # STEP 1: LOAD VECTOR DATABASE (ChromaDB)

    vectordb = get_vectorstore()

# STEP 2: EXTRACT STORED DOCUMENTS
    # WHY?
    # BM25 needs RAW TEXT (not embeddings)
 
    all_data = vectordb.get()

    docs = []

    for text, meta in zip(
        all_data["documents"],
        all_data["metadatas"]
    ):
        docs.append(
            Document(
                page_content=text,
                metadata=meta
            )
        )

 # STEP 3: VECTOR RETRIEVER (semantic search)

    vector_retriever = vectordb.as_retriever(
        search_kwargs={"k": 10}
    )
# STEP 4: BM25 RETRIEVER (keyword search)

    bm25_retriever = create_bm25(docs)

# STEP 5: ENSEMBLE RETRIEVER
# COMBINES BM25 + VECTOR
 
    ensemble = create_ensemble_retriever(
        bm25_retriever,
        vector_retriever
    )

   # STEP 6: FINAL RAG CHAIN
    # ensemble → rerank → LLM
 
    rag_chain = create_rag_chain(
        ensemble,
        rerank
    )

    return rag_chain


# Initialize pipeline
rag_chain = setup_rag()

# CHAT HISTORY DISPLAY

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# USER INPUT SECTION

if rag_chain:

    query = st.chat_input("Ask something...")

    if query:

        # store user message
        st.session_state.messages.append({
            "role": "user",
            "content": query
        })

        with st.chat_message("user"):
            st.markdown(query)

        langfuse_handler = CallbackHandler()

       # STEP 1: RETRIEVE (BM25 + VECTOR)
        # STEP 2: RERANK
        # STEP 3: GENERATE ANSWER
      
        with st.spinner("Thinking..."):

            answer, docs = rag_chain(
                query,
                callbacks=[langfuse_handler]
            )

      # SHOW RESPONSE
      
        with st.chat_message("assistant"):

            st.markdown(answer)

          # SOURCES DISPLAY
       
            st.markdown("## Sources")

            seen = set()

            for doc in docs:

                source = doc.metadata.get("source", "Unknown")

                if source not in seen:
                    seen.add(source)

                    if source.startswith("http"):
                        st.markdown(f"- 🌐 {source}")
                    else:
                        st.markdown(f"- 📄 {source}")

       # SHOW RETRIEVED CHUNKS
   
            with st.expander("🔍 Retrieved Chunks"):

                for i, doc in enumerate(docs):

                    st.markdown(f"### Chunk {i+1}")
                    st.markdown(f"Source: {doc.metadata.get('source')}")
                    st.code(doc.page_content[:800])

        # save chat
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })