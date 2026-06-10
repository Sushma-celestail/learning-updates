# AI Intern Monorepo

This repository contains **Use Case 1 - Docs Buddy**, a simple RAG (Retrieval-Augmented Generation) chatbot built over the FastAPI documentation site. The chatbot answers questions using only information from the retrieved documentation context.

## Project Structure

```
ai-intern-monorepo/
├── pyproject.toml              # Python project configuration and dependencies
├── shared/                     # Shared modules used across use cases
│   ├── config/
│   │    └── settings.py        # Central configuration settings
│   └── vectorstore/
│        └── chroma.py          # ChromaDB vector store utilities
└── uc01_docs_buddy/           # Use Case 1: Documentation chatbot
    ├── ingest.py              # Script to download and embed documentation
    ├── chain.py               # RAG chain implementation using LCEL
    ├── app.py                 # Streamlit web interface
    ├── data/
    │    └── chroma/           # Persistent vector database storage
    └── tests/
        ├── ground_truth.json  # Test questions for validation
        └── test_rag.py        # Integration and unit tests
```

## Setup Instructions

### 1. Create Virtual Environment
```powershell
# Navigate to the project directory
cd C:\Users\sushma.s\Desktop\Use-Cases\ai-intern-monorepo

# Create a Python virtual environment
python -m venv .venv

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```powershell
# Install the project in editable mode
pip install -e .

# Alternative: Install from requirements.txt
# pip install -r requirements.txt
```

### 3. Configure API Key
```powershell
# Set your Google API key (get it from https://makersuite.google.com/app/apikey)
$env:GOOGLE_API_KEY="your-actual-gemini-api-key"

# Alternative: Create a .env file with GOOGLE_API_KEY=your_key
```

## Usage

### Ingest Documentation
```powershell
# Navigate to the use case directory
cd C:\Users\sushma.s\Desktop\Use-Cases\ai-intern-monorepo\uc01_docs_buddy

# Run the ingestion script to download and embed FastAPI docs
python ingest.py
```

**⚠️ Rate Limiting Note**: The free Gemini API tier has a limit of 100 embedding requests per minute. The ingestion script automatically handles this by:
- Processing chunks in batches of 50
- Adding 65-second delays between batches
- Automatically retrying if rate limits are hit
- **Total time**: ~15-20 minutes for full ingestion

For faster processing, consider upgrading to a paid Gemini API plan.

The ingestion script:
- Downloads 50-80 pages from the FastAPI documentation sitemap
- Splits pages into 800-character chunks with 100-character overlap
- Embeds chunks using Gemini `gemini-embedding-001`
- Stores vectors in a persistent ChromaDB collection
- Is idempotent (safe to run multiple times)

### Run the Chatbot
```powershell
# Start the Streamlit web interface
cd C:\Users\sushma.s\Desktop\Use-Cases\ai-intern-monorepo\uc01_docs_buddy
streamlit run app.py
```

The chatbot will be available at `http://localhost:8501` and provides:
- Single-turn question answering about FastAPI documentation
- Answers include citations with source URLs
- Fallback response for out-of-scope questions
- Client-side chat history

### Run Tests
```powershell
# Run all tests from the project root
cd C:\Users\sushma.s\Desktop\Use-Cases\ai-intern-monorepo
pytest

# Run only unit tests (no API calls)
pytest -m "not integration"

# Run integration tests (requires API key and ingested data)
pytest -m integration
```

## Technical Implementation

### RAG Chain Architecture
The system uses LangChain Expression Language (LCEL) to build a retrieval chain:

```
User Question → Retriever → Format Context → Prompt → Gemini → Answer
```

1. **Retriever**: Searches ChromaDB for top-4 most relevant chunks
2. **Context Formatting**: Combines retrieved chunks with source URLs
3. **Prompt**: System instruction enforces docs-only answers
4. **Gemini**: `gemini-2.5-flash` generates the final response
5. **Output**: Plain text answer with citations

### Key Features
- **Strict Context Adherence**: Model only answers from retrieved documentation
- **Citation Support**: Answers include source URLs from retrieved chunks
- **Fallback Handling**: Out-of-scope questions get a configured fallback response
- **Persistent Storage**: ChromaDB stores embeddings on disk for fast startup
- **Idempotent Ingestion**: Re-running ingestion updates existing documents

## Acceptance Criteria Compliance

✅ **Criterion 1**: `python ingest.py` ingests ≥50 pages into persistent Chroma collection  
✅ **Criterion 2**: Answers 10 ground-truth questions with 8/10 including citations  
✅ **Criterion 3**: Responds with fallback phrase for 3/3 out-of-scope questions  
✅ **Criterion 4**: End-to-end latency p50 < 4s with top-k=4 retrieval  
✅ **Criterion 5**: README documents LLM/embedding provider swap in ≤5 lines  

## Swap LLM or Embedding Provider

To change the AI models, edit these lines in `shared/config/settings.py`:

```python
EMBEDDING_MODEL = "gemini-embedding-001"  # Change to different embedding model
CHAT_MODEL = "gemini-3.1-flash lite "          # Change to different chat model
```

If switching providers (e.g., from Google to OpenAI), update the LangChain classes:
- In `shared/vectorstore/chroma.py`: Replace `GoogleGenerativeAIEmbeddings`
- In `uc01_docs_buddy/chain.py`: Replace `ChatGoogleGenerativeAI`

## Stack Summary
- **Python 3.11**: Core runtime environment
- **LangChain**: Framework for building LLM applications
- **Google Gemini**: Embedding (`gemini-embedding-001`) and chat (`gemini-2.5-flash`) models
- **ChromaDB**: Vector database for similarity search
- **Streamlit**: Web framework for the chat interface
- **FastAPI Docs**: Documentation source (50-80 pages via sitemap)