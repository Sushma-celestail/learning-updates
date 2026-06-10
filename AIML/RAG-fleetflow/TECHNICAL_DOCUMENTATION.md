# Technical Documentation: RAG Chatbot Implementation

## 📋 Table of Contents
1. [System Architecture](#system-architecture)
2. [Code Flow Overview](#code-flow-overview)
3. [Component Deep Dive](#component-deep-dive)
4. [RAG Pipeline Execution](#rag-pipeline-execution)
5. [Data Flow Diagrams](#data-flow-diagrams)
6. [Key Algorithms](#key-algorithms)
7. [API Integration](#api-integration)
8. [Error Handling](#error-handling)

---

## 🏗️ System Architecture

### High-Level Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Query    │───▶│   Streamlit     │───▶│   RAG Chain     │
│                 │    │   Interface     │    │   (LCEL)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Final Answer  │◀───│   Gemini LLM    │◀───│   Retriever     │
│   with Citations│    │   Generation    │    │   (ChromaDB)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Project Structure Explained
```
ai-intern-monorepo/
├── shared/                    # Shared utilities across use cases
│   ├── config/
│   │   └── settings.py       # Central configuration management
│   └── vectorstore/
│       └── chroma.py         # ChromaDB vector store utilities
└── uc01_docs_buddy/          # Use Case 1: Documentation chatbot
    ├── ingest.py             # Document ingestion pipeline
    ├── chain.py              # RAG chain implementation (LCEL)
    ├── app.py                # Streamlit web interface
    ├── quick_test.py         # Development testing script
    └── tests/                # Test suite
        ├── test_rag.py       # Integration and unit tests
        └── ground_truth.json # Test questions and expected behavior
```

---

## 🔄 Code Flow Overview

### 1. Configuration Layer (`shared/config/settings.py`)
**Purpose**: Centralized configuration management
**Key Responsibilities**:
- Environment variable loading
- Model configuration (embedding + chat models)
- Path management
- Rate limiting parameters

```python
# Core configuration flow
load_env_file()  # Load .env variables
↓
Define paths (PROJECT_ROOT, CHROMA_DIR, etc.)
↓
Set model configurations (EMBEDDING_MODEL, CHAT_MODEL)
↓
Configure ingestion parameters (MIN_PAGES, MAX_PAGES, etc.)
```

### 2. Vector Store Layer (`shared/vectorstore/chroma.py`)
**Purpose**: ChromaDB integration and embedding management
**Key Functions**:

```python
get_embeddings() → GoogleGenerativeAIEmbeddings
    ├── Creates Gemini embedding client
    ├── Uses EMBEDDING_MODEL from settings
    └── Handles API authentication via GOOGLE_API_KEY

get_vectorstore() → Chroma
    ├── Creates/opens persistent ChromaDB collection
    ├── Links embedding function for query vectorization
    └── Manages local storage at CHROMA_DIR
```

### 3. Ingestion Pipeline (`uc01_docs_buddy/ingest.py`)
**Purpose**: Download, process, and store documentation
**Execution Flow**:

```python
ingest() → ingest_with_rate_limiting()
    ├── check_api_key()           # Verify Gemini API access
    ├── load_docs()               # Download FastAPI documentation
    │   ├── SitemapLoader()       # Load from sitemap.xml
    │   ├── Filter by URL prefix  # Keep only FastAPI docs
    │   └── Clean text content    # Normalize whitespace
    ├── split_docs()              # Chunk documents
    │   └── RecursiveCharacterTextSplitter(chunk_size=800, overlap=100)
    ├── make_id()                 # Create stable document IDs
    │   └── SHA-256 hash of (index + source + content)
    └── Batch processing with rate limiting
        ├── Process 50 chunks per batch
        ├── 65-second delays between batches
        └── Automatic retry on rate limit errors
```

### 4. RAG Chain (`uc01_docs_buddy/chain.py`)
**Purpose**: Retrieval-Augmented Generation using LangChain Expression Language
**Core Components**:

```python
build_chain() → LCEL Pipeline
    ├── Retriever: vectorstore.as_retriever(k=4)
    ├── Context Formatter: format_docs()
    ├── Prompt Template: build_prompt()
    ├── LLM: ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    └── Output Parser: StrOutputParser()
```

### 5. Web Interface (`uc01_docs_buddy/app.py`)
**Purpose**: Streamlit chat interface
**User Interaction Flow**:

```python
Streamlit App Lifecycle:
    ├── Initialize session state (chat history)
    ├── Display previous messages
    ├── Handle new user input
    │   ├── Add user message to history
    │   ├── Call answer_question(user_input)
    │   ├── Display assistant response
    │   └── Add response to history
    └── Persist state across interactions
```

---

## 🔍 Component Deep Dive

### A. Document Ingestion Process

#### Step 1: Document Loading
```python
# Location: ingest.py → load_docs()
loader = SitemapLoader(
    web_path="https://fastapi.tiangolo.com/sitemap.xml",
    filter_urls=["https://fastapi.tiangolo.com/"]
)
docs = loader.load()  # Downloads all FastAPI documentation pages
```

**What happens internally**:
1. Fetches XML sitemap from FastAPI website
2. Extracts all documentation URLs
3. Downloads HTML content for each page
4. Converts HTML to plain text
5. Filters out empty or invalid pages

#### Step 2: Text Chunking
```python
# Location: ingest.py → split_docs()
splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,      # Maximum characters per chunk
    chunk_overlap=100    # Overlapping characters between chunks
)
chunks = splitter.split_documents(docs)
```

**Chunking Strategy**:
- **Recursive splitting**: Tries to split on paragraphs, then sentences, then words
- **Overlap preservation**: 100 characters overlap maintains context between chunks
- **Size optimization**: 800 characters fit well in embedding models and LLM context

#### Step 3: Stable ID Generation
```python
# Location: ingest.py → make_id()
def make_id(index, source, text):
    raw_text = f"{index}|{source}|{text}"
    return hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
```

**Why stable IDs matter**:
- **Idempotent ingestion**: Re-running ingestion updates existing chunks instead of duplicating
- **Version control**: Same content always gets same ID
- **Efficient updates**: Only changed content gets re-embedded

### B. RAG Chain Architecture

#### LCEL Pipeline Structure
```python
# Location: chain.py → build_chain()
chain = (
    {
        "context": retriever | RunnableLambda(format_docs),
        "question": RunnablePassthrough(),
    }
    | prompt
    | llm
    | StrOutputParser()
)
```

**Pipeline Breakdown**:

1. **Input Processing**:
   ```python
   {
       "context": retriever | format_docs,  # Retrieve and format relevant chunks
       "question": RunnablePassthrough()    # Pass user question unchanged
   }
   ```

2. **Retrieval Step**:
   ```python
   retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
   # Finds 4 most similar chunks using cosine similarity
   ```

3. **Context Formatting**:
   ```python
   def format_docs(docs):
       formatted_chunks = []
       for index, doc in enumerate(docs, start=1):
           source = doc.metadata.get("source", "Unknown source")
           formatted_chunks.append(f"[Source {index}: {source}]\n{doc.page_content}")
       return "\n\n".join(formatted_chunks)
   ```

4. **Prompt Construction**:
   ```python
   ChatPromptTemplate.from_messages([
       ("system", "You are Docs Buddy... Answer only from retrieved context..."),
       ("human", "Question: {question}\n\nRetrieved context:\n{context}")
   ])
   ```

5. **LLM Generation**:
   ```python
   ChatGoogleGenerativeAI(
       model="gemini-2.5-flash",
       temperature=0  # Deterministic responses
   )
   ```

### C. Vector Store Operations

#### Embedding Process
```python
# Location: vectorstore/chroma.py → get_embeddings()
embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
```

**How embeddings work**:
1. **Text → Vector**: Converts text chunks into 768-dimensional vectors
2. **Semantic representation**: Similar concepts have similar vectors
3. **Similarity search**: Uses cosine similarity to find relevant chunks

#### ChromaDB Storage
```python
# Location: vectorstore/chroma.py → get_vectorstore()
vectorstore = Chroma(
    collection_name="fastapi_docs_buddy",
    embedding_function=get_embeddings(),
    persist_directory=str(CHROMA_DIR)
)
```

**Storage structure**:
- **Collections**: Named containers for related documents
- **Persistence**: Automatic saving to disk for fast startup
- **Metadata**: Stores source URLs, chunk indices, and other metadata

---

## 🚀 RAG Pipeline Execution

### Query Processing Flow

#### 1. User Input Processing
```python
# Location: app.py → User submits question
question = st.chat_input("Ask about FastAPI docs")
if question:
    answer = answer_question(question)  # Calls RAG chain
```

#### 2. Vector Similarity Search
```python
# Location: chain.py → Retrieval step
user_question → embed_query() → vector_search() → top_k_chunks
```

**Detailed process**:
1. **Query embedding**: User question converted to vector using same embedding model
2. **Similarity calculation**: Cosine similarity between query vector and all stored vectors
3. **Ranking**: Chunks sorted by similarity score
4. **Top-k selection**: Returns 4 most relevant chunks

#### 3. Context Assembly
```python
# Location: chain.py → format_docs()
retrieved_chunks → format_with_sources() → structured_context
```

**Context format**:
```
[Source 1: https://fastapi.tiangolo.com/tutorial/path-params/]
Path parameters are variable parts of the URL path...

[Source 2: https://fastapi.tiangolo.com/tutorial/query-params/]
Query parameters are optional parameters that appear after...
```

#### 4. Prompt Construction
```python
# Location: chain.py → ChatPromptTemplate
system_message + user_question + retrieved_context → final_prompt
```

#### 5. LLM Generation
```python
# Location: chain.py → ChatGoogleGenerativeAI
final_prompt → gemini_api_call() → generated_response
```

#### 6. Response Processing
```python
# Location: chain.py → StrOutputParser
generated_response → parse_to_string() → final_answer
```

---

## 📊 Data Flow Diagrams

### Ingestion Data Flow
```
FastAPI Sitemap
       ↓
   SitemapLoader
       ↓
  Raw HTML Pages
       ↓
  Text Extraction
       ↓
   Clean Text Docs
       ↓
RecursiveCharacterTextSplitter
       ↓
   Text Chunks (800 chars)
       ↓
  Stable ID Generation
       ↓
  Gemini Embedding API
       ↓
   Vector Embeddings
       ↓
   ChromaDB Storage
```

### Query Data Flow
```
User Question
       ↓
  Streamlit Interface
       ↓
   RAG Chain (LCEL)
       ↓
  Query Embedding
       ↓
  Vector Similarity Search
       ↓
  Top-4 Relevant Chunks
       ↓
  Context Formatting
       ↓
  Prompt Construction
       ↓
  Gemini Chat API
       ↓
  Generated Answer
       ↓
  Streamlit Display
```

---

## 🔧 Key Algorithms

### 1. Recursive Text Splitting Algorithm
```python
# Splitting hierarchy (RecursiveCharacterTextSplitter)
1. Try splitting on double newlines (\n\n) - paragraphs
2. If chunks still too large, split on single newlines (\n) - lines
3. If still too large, split on sentences (. ! ?)
4. If still too large, split on words (spaces)
5. If still too large, split on characters
```

### 2. Cosine Similarity for Retrieval
```python
# Vector similarity calculation
similarity = dot_product(query_vector, document_vector) / 
            (magnitude(query_vector) * magnitude(document_vector))

# Range: -1 to 1 (1 = identical, 0 = orthogonal, -1 = opposite)
```

### 3. Rate Limiting Algorithm — Why 65 Seconds?

#### The Free Tier Quota
The Gemini Embedding API (free tier) enforces a hard limit:

```
Quota: 100 embedding requests per minute per user per project
```

Every single chunk sent to the Gemini embedding API counts as **1 request**.
With 1831 total chunks (80 pages), sending them all at once would immediately
trigger a 429 RESOURCE_EXHAUSTED error after the 100th request.

#### The Math Behind 65 Seconds

```
Free Tier Limit  = 100 requests / minute
Batch Size       = 50 chunks
Each chunk       = 1 API call
─────────────────────────────────────────
Calls used       = 50 (in ~5 seconds)
Remaining quota  = 50 calls left in that same 60-second window

Problem: If we start the next batch immediately, we only have
         50 calls left before hitting the limit again.

Solution: Wait for the current 60-second window to fully expire,
          then start fresh with 100 calls available again.

Wait time = 60 seconds (full minute reset)
          +  5 seconds (safety buffer for clock drift)
          = 65 seconds total
```

#### Why Not Just 60 Seconds?
The Gemini API rate limit window is a **rolling 60-second window**, not a
fixed clock minute. If batch 1 finishes at second 5, the window resets at
second 65 (not second 60). Waiting exactly 60 seconds risks landing inside
the same window and hitting the limit again. The 5-second buffer guarantees
we are safely in a new window.

#### Why Batch Size = 50 (Not 100)?
```
Option A: batch_size = 100 (use full quota per batch)
  ✅ Fewer batches needed
  ❌ Any single failure wastes the entire minute
  ❌ No headroom for retries within the same window

Option B: batch_size = 50 (use half quota per batch)
  ✅ Leaves 50 calls as retry headroom
  ✅ Safer on unstable connections
  ✅ Consistent, predictable timing
  ❌ Slightly more total wait time
```

Batch size 50 was chosen for reliability over raw speed.

#### Why 70 Seconds on Retry?
```
Normal delay  = 65 seconds (planned wait between batches)
Retry delay   = 70 seconds (used only after a 429 error)

The extra 5 seconds on retry accounts for:
- The API error itself consuming time in the window
- Network latency adding unpredictable overhead
- Ensuring the rate limit window has fully cleared
```

#### Full Rate Limiting Flow
```
Batch 1 (50 chunks) → ~5 seconds to process
       ↓
  ⏳ Wait 65 seconds  ← new 60s window guaranteed
       ↓
Batch 2 (50 chunks) → ~5 seconds to process
       ↓
  ⏳ Wait 65 seconds
       ↓
  ... repeat ...
       ↓
Last Batch → no wait needed
```

#### Total Ingestion Time Estimate
```
Batches needed   = ceil(1831 / 50) = 37 batches
Processing time  = 37 × 5 seconds  = ~3 minutes
Wait time        = 36 × 65 seconds = ~39 minutes
─────────────────────────────────────────────────
Total estimate   = ~42 minutes for full 80-page ingestion

Quick test (10 pages, 220 chunks):
Batches needed   = ceil(220 / 50) = 5 batches
Wait time        = 4 × 65 seconds = ~4 minutes
Total estimate   = ~5 minutes ✅
```

#### Code Implementation
```python
# Location: ingest.py → ingest_with_rate_limiting()

batch_size = 50          # Half of free tier limit (100/min) for safety
delay      = 65          # 60s window reset + 5s safety buffer
retry_delay = 70         # Extra 5s on top of delay for error recovery

for batch_num in range(total_batches):
    try:
        vectorstore.add_documents(batch_chunks, ids=batch_ids)

        if batch_num < total_batches - 1:   # Skip delay after last batch
            time.sleep(65)                  # Wait for rate limit window to reset

    except Exception as e:
        if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
            time.sleep(70)                  # Longer wait after hitting the limit
            vectorstore.add_documents(batch_chunks, ids=batch_ids)  # Retry once
```

#### How to Speed This Up
If you have a **paid Gemini API plan**, you can increase the batch size and
remove the delays entirely by editing `ingest.py`:

```python
# For paid tier (higher quota)
batch_size = 500   # Process more chunks per batch
delay      = 0     # No delay needed
```

Or switch to a different embedding provider that has higher free limits:
```python
# In shared/config/settings.py — swap in 5 lines
EMBEDDING_MODEL = "text-embedding-3-small"  # OpenAI example
# Then update shared/vectorstore/chroma.py to use OpenAIEmbeddings
```

---

## 🌐 API Integration

### Google Gemini API Integration

#### Authentication
```python
# Environment variable based authentication
os.environ["GOOGLE_API_KEY"] = "your-api-key"
# Automatically used by langchain-google-genai
```

#### Embedding API Calls
```python
# Location: GoogleGenerativeAIEmbeddings.embed_documents()
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent
{
    "model": "models/gemini-embedding-001",
    "content": {"parts": [{"text": "chunk content"}]},
    "taskType": "RETRIEVAL_DOCUMENT"
}
```

#### Chat API Calls
```python
# Location: ChatGoogleGenerativeAI.invoke()
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent
{
    "contents": [
        {"role": "user", "parts": [{"text": "system + user prompt"}]}
    ],
    "generationConfig": {"temperature": 0}
}
```

### Rate Limiting Details
- **Free Tier**: 100 embedding requests per minute
- **Batch Strategy**: 50 chunks per batch = 50 API calls
- **Safety Margin**: 65-second delays ensure staying under limit
- **Error Handling**: Automatic retry with longer delays on 429 errors

---

## ⚠️ Error Handling

### 1. API Error Handling
```python
# Location: ingest.py → ingest_with_rate_limiting()
try:
    vectorstore.add_documents(batch_chunks, ids=batch_ids)
except Exception as e:
    if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
        # Rate limit hit - wait and retry
        time.sleep(70)
        vectorstore.add_documents(batch_chunks, ids=batch_ids)
    else:
        # Other error - log and continue or fail
        print(f"Unexpected error: {e}")
```

### 2. Configuration Validation
```python
# Location: ingest.py → check_api_key()
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("Please set GOOGLE_API_KEY environment variable")
```

### 3. Data Validation
```python
# Location: ingest.py → load_docs()
docs = [doc for doc in docs if doc.page_content.strip()]  # Filter empty docs
if len(docs) < MIN_PAGES:
    raise ValueError(f"Only loaded {len(docs)} pages, need at least {MIN_PAGES}")
```

### 4. Graceful Degradation
```python
# Location: app.py → Streamlit error handling
try:
    answer = answer_question(question)
except Exception as e:
    answer = (
        "❌ Sorry, I encountered an error. Please check:\n"
        "- Documentation has been ingested\n"
        "- GOOGLE_API_KEY is set\n"
        f"- Error: {str(e)}"
    )
```

---

## 🧪 Testing Strategy

### Test Categories
1. **Unit Tests**: Individual function testing
2. **Integration Tests**: Full RAG pipeline testing
3. **Acceptance Tests**: Ground truth question validation

### Key Test Files
- `test_rag.py`: Main test suite
- `ground_truth.json`: Test questions and expected behavior

### Test Execution
```python
# Run all tests
pytest

# Run only unit tests (no API calls)
pytest -m "not integration"

# Run integration tests (requires API key)
pytest -m integration
```

This documentation provides a complete technical overview of how the RAG chatbot works, from high-level architecture to low-level implementation details. Each component is explained with its purpose, key functions, and how it integrates with other parts of the system.