from pathlib import Path
import shutil

from dotenv import load_dotenv

load_dotenv()

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# =========================
# PATH SETUP
# =========================

BASE_DIR = Path(__file__).resolve().parent.parent

PDF_DIR = BASE_DIR / "corpus" / "pdfs"
CHROMA_DIR = BASE_DIR / "chroma_db"

print("=" * 60)
print("PDF DIRECTORY :", PDF_DIR)
print("CHROMA DB     :", CHROMA_DIR)
print("=" * 60)

# =========================
# INGEST FUNCTION
# =========================

def ingest():

    # =====================================
    # STEP 0 → DELETE OLD BROKEN DB
    # =====================================

    if CHROMA_DIR.exists():
        print("\n🗑 Removing old Chroma DB...")
        shutil.rmtree(CHROMA_DIR)

    # =====================================
    # STEP 1 → LOAD PDFs
    # =====================================

    loader = PyPDFDirectoryLoader(str(PDF_DIR))

    docs = loader.load()

    print(f"\n📄 Loaded PDF pages: {len(docs)}")

    if len(docs) == 0:
        raise ValueError(f"No PDFs found in: {PDF_DIR}")

    # =====================================
    # STEP 2 → SPLIT DOCUMENTS
    # =====================================

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]
    )

    chunks = splitter.split_documents(docs)

    print(f"✂ Generated chunks: {len(chunks)}")

    # =====================================
    # STEP 3 → CLEAN CHUNKS
    # =====================================

    clean_chunks = []

    for i, chunk in enumerate(chunks):

        text = chunk.page_content.strip()

        # skip empty chunks
        if len(text) < 40:
            continue

        chunk.metadata["chunk_id"] = i

        clean_chunks.append(chunk)

    print(f"🧹 Clean chunks kept: {len(clean_chunks)}")

    # =====================================
    # STEP 4 → EMBEDDINGS
    # =====================================

    print("\n🧠 Loading embedding model...")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

    # =====================================
    # STEP 5 → CREATE CHROMA DB
    # =====================================

    print("\n💾 Creating Chroma vector DB...")

    vectorstore = Chroma.from_documents(
        documents=clean_chunks,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR),
        collection_name="crag_corpus",
        ids=[f"chunk_{i}" for i in range(len(clean_chunks))]
    )

    print("\n✅ INGESTION COMPLETE")
    print(f"Stored chunks: {len(clean_chunks)}")

    # =====================================
    # STEP 6 → VALIDATION TEST
    # =====================================

    print("\n🔎 Running retrieval test...")

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )

    test_query = "What is FastAPI?"

    results = retriever.invoke(test_query)

    print(f"\nQuery: {test_query}")
    print(f"Results returned: {len(results)}")

    for i, doc in enumerate(results):

        print("\n" + "-" * 50)

        print(f"Result {i+1}")

        print(doc.page_content[:300])

        print("\nMetadata:", doc.metadata)

    print("\n🎉 ChromaDB validated successfully")


# =========================
# MAIN
# =========================

if __name__ == "__main__":
    ingest()