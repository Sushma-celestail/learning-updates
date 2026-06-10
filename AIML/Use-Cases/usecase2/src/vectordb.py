from langchain_chroma import Chroma
from src.embeddings import embeddings

DB_DIR = "chroma_db"

def create_vectorstore():

    vectordb = Chroma(
        persist_directory=DB_DIR,
        embedding_function=embeddings,
        collection_name="hybrid_rag"
    )

    return vectordb


def get_vectorstore():

    vectordb = Chroma(
        embedding_function=embeddings,
        persist_directory=DB_DIR,
        collection_name="hybrid_rag"
    )

    return vectordb