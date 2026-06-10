from src.vectordb import create_vectorstore

vectordb = create_vectorstore()

retriever = vectordb.as_retriever(
    search_kwargs={"k": 5}
)

query = "What is FastAPI middleware?"

docs = retriever.invoke(query)

print("\n===== RETRIEVED DOCS =====\n")

for i, doc in enumerate(docs):

    print(f"\n--- DOCUMENT {i+1} ---\n")

    print(doc.page_content[:500])