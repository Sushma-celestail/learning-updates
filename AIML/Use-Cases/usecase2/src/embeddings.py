
from langchain_huggingface import HuggingFaceEmbeddings


# Using a strong, lightweight local embedding model instead of Gemini
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5"
)
