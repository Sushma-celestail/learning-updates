"""Helpers for creating and opening the shared ChromaDB vector store."""
# This module centralizes ChromaDB setup to ensure consistent configuration
# across ingestion, retrieval, and testing components

from langchain_chroma import Chroma  # LangChain's ChromaDB integration for vector operations
from langchain_google_genai import GoogleGenerativeAIEmbeddings  # Google Gemini embedding client

# Import shared configuration values to maintain consistency
from shared.config.settings import CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """Return the Gemini embedding client used for documents and queries."""
    # The same embedding model must be used for both:
    # 1. Embedding documents during ingestion (ingest.py)
    # 2. Embedding user queries during retrieval (chain.py)
    # Using different models would break similarity search
    
    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL  # Uses the model specified in settings.py
        # The GOOGLE_API_KEY environment variable is automatically read by this class
    )


def get_vectorstore() -> Chroma:
    """Open the persistent ChromaDB vector store for Docs Buddy."""
    # This function provides a single point of access to the vector database
    # It ensures all components (app, ingest, tests) use the same configuration
    
    # Create the storage directory if it doesn't exist yet
    # parents=True creates parent directories, exist_ok=True prevents errors if it exists
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    
    return Chroma(
        collection_name=COLLECTION_NAME,        # Stable collection name for consistent access
        embedding_function=get_embeddings(),    # Embedding function for query vectorization
        persist_directory=str(CHROMA_DIR),      # Local directory for persistent storage
        # ChromaDB automatically handles:
        # - Creating the collection if it doesn't exist
        # - Loading existing data if the collection exists
        # - Persisting new data to disk automatically
    )