from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# =========================
# PATH SETUP
# =========================

BASE_DIR = Path(__file__).resolve().parent.parent

CHROMA_DIR = BASE_DIR / "chroma_db"

print("RETRIEVE DB:", CHROMA_DIR.resolve())

# =========================
# EMBEDDINGS
# =========================

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# =========================
# LOAD EXISTING CHROMA DB
# =========================

vectorstore = Chroma(
    collection_name="crag_corpus",
    embedding_function=embeddings,
    persist_directory=str(CHROMA_DIR)
)

# =========================
# RETRIEVE NODE
# =========================

def retrieve(state):

    question = state.question

    docs_and_scores = vectorstore.similarity_search_with_score(
        question,
        k=4
    )

    documents = []
    relevance_scores = []

    for doc, distance in docs_and_scores:

        documents.append(doc.page_content)

        score = round(1 / (1 + distance), 4)

        relevance_scores.append(score)

    avg_score = (
        round(sum(relevance_scores) / len(relevance_scores), 4)
        if relevance_scores else 0.0
    )

    return state.model_copy(
        update={
            "documents": documents,
            "scores": relevance_scores,
            "avg_score": avg_score,
            "source": "chroma",
            "grade": "unknown"
        }
    )