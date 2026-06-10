"""RAG chain implementation using LangChain Expression Language (LCEL)."""


import time    
import sys     
from pathlib import Path  

# LangChain components for building the RAG chain
from langchain_core.output_parsers import StrOutputParser   # Converts LLM output to plain string
from langchain_core.prompts import ChatPromptTemplate        # Builds system + user prompt
from langchain_core.runnables import RunnableLambda, RunnablePassthrough  # LCEL helpers
from langchain_google_genai import ChatGoogleGenerativeAI   # Gemini chat model client

# Add project root to Python path so shared modules can be imported
PROJECT_ROOT = Path(__file__).resolve().parents[1]   # ai-intern-monorepo/
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Project imports
from shared.config.settings import CHAT_MODEL, FALLBACK_PHRASE, RETRIEVAL_K
from shared.vectorstore.chroma import get_vectorstore
from shared.logger import get_logger   # Shared logger writes to file + console

# Module-level logger — every log line from this file shows "chain" as the source
log = get_logger("chain")


# ---------------------------------------------------------------------------
# Helper: format retrieved documents into context text
# ---------------------------------------------------------------------------

def format_docs(docs):
    """Convert retrieved chunks into context text with source citations."""
    log.debug("[STEP 3] Formatting %d retrieved chunks into context", len(docs))

    # If 0 chunks came back the embedding API call failed silently
    # (exhausted quota returns empty results instead of raising an error).
    # Raise explicitly so the UI shows a clear message instead of the fallback phrase.
    if not docs:
        log.error(
            "[STEP 3] 0 chunks retrieved — embedding API likely quota-exhausted. "
            "Update GOOGLE_API_KEY with a fresh key."
        )
        raise RuntimeError(
            "No documentation chunks were retrieved for your question.\n\n"
            "This usually means the embedding API quota is exhausted on the current key.\n"
            "Please update GOOGLE_API_KEY in the .env file with a fresh API key from "
            "https://aistudio.google.com/app/apikey and restart the app."
        )

    formatted_chunks = []

    for index, doc in enumerate(docs, start=1):
        source = doc.metadata.get("source", "Unknown source")
        chunk_preview = doc.page_content[:80].replace("\n", " ")
        log.debug("  Chunk %d | source: %s | preview: %s...", index, source, chunk_preview)
        formatted_chunks.append(f"[Source {index}: {source}]\n{doc.page_content}")

    context = "\n\n".join(formatted_chunks)
    log.debug("[STEP 3] Context assembled — total characters: %d", len(context))
    return context


# ---------------------------------------------------------------------------
# Helper: build the strict docs-only prompt
# ---------------------------------------------------------------------------

def build_prompt() -> ChatPromptTemplate:
    """
    Create the ChatPromptTemplate that enforces docs-only answers.

    The system message does three things:
    1. Restricts the model to answer only from retrieved context.
    2. Defines the exact fallback phrase for out-of-scope questions.
    3. Requires a Citations block listing source URLs.

    Returns
    -------
    ChatPromptTemplate
        Ready-to-use prompt template with {question} and {context} slots.
    """
    log.debug("[STEP 4] Building prompt template")

    return ChatPromptTemplate.from_messages([
        (
            "system",
            # Strict context adherence — prevents hallucination
            "You are Docs Buddy, a helpful documentation question-answering assistant. "
            "You must answer questions ONLY using information from the retrieved "
            "documentation context below. "
            # Fallback phrase — tested by acceptance criteria
            f"If the answer is not clearly available in the provided context, "
            f"you must respond exactly with: '{FALLBACK_PHRASE}' "
            # Citation requirement — tested by acceptance criteria
            "When you can answer from the context, include a 'Citations' section "
            "at the end listing the source URLs you used from the retrieved chunks. "
            "Be concise but complete. Use the exact terminology from the documentation."
        ),
        (
            "human",
            "Question: {question}\n\nRetrieved documentation context:\n{context}"
        ),
    ])


# ---------------------------------------------------------------------------
# Main chain builder
# ---------------------------------------------------------------------------

def build_chain():
    """
    Assemble the complete LCEL retrieval-augmented generation chain.

    Pipeline steps
    --------------
    1. Receive user question (str)
    2. Embed question → search ChromaDB → return top-k Document objects
    3. Format documents into context string with source citations
    4. Inject question + context into the prompt template
    5. Send prompt to Gemini → receive generated text
    6. Parse Gemini output to plain string

    Returns
    -------
    Runnable
        An LCEL chain that accepts a question string and returns an answer string.
    """
    log.debug("[STEP 1] Building RAG chain components")

    # --- Retriever --------------------------------------------------------
    log.debug("  Opening ChromaDB vector store")
    vectorstore = get_vectorstore()   # Opens the persisted Chroma collection on disk

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": RETRIEVAL_K}   # Return top-4 most similar chunks
    )
    log.debug("  Retriever ready — top_k=%d", RETRIEVAL_K)

    # --- Language model ---------------------------------------------------
    log.debug("  Initialising Gemini chat model: %s", CHAT_MODEL)
    llm = ChatGoogleGenerativeAI(
        model=CHAT_MODEL,
        temperature=0   # Deterministic output for reproducible answers
    )

    # --- Prompt -----------------------------------------------------------
    prompt = build_prompt()

    # --- Assemble LCEL pipeline -------------------------------------------
    # The | operator chains runnables left-to-right.
    # The dict at the start runs retriever and passthrough in parallel,
    # then merges their outputs as {context} and {question} for the prompt.
    chain = (
        {
            "context":  retriever | RunnableLambda(format_docs),  # retrieve → format
            "question": RunnablePassthrough(),                     # pass question unchanged
        }
        | prompt            # fill {question} and {context} slots
        | llm               # call Gemini API
        | StrOutputParser() # extract plain text from the AIMessage object
    )

    log.debug("[STEP 1] RAG chain assembled successfully")
    return chain


# ---------------------------------------------------------------------------
# Public interface used by app.py and tests
# ---------------------------------------------------------------------------

def answer_question(question: str) -> str:
    """
    Run the full RAG pipeline for a single user question and return the answer.

    This is the only function that app.py and the test suite call.
    It logs every step with timestamps so the complete trace from
    question to answer is visible in rag_pipeline.log.

    Parameters
    ----------
    question : str
        The user's natural-language question.

    Returns
    -------
    str
        The generated answer, including a Citations block when the question
        is in scope, or the configured fallback phrase when it is not.
    """
    # ------------------------------------------------------------------
    # STEP 1 — Receive and log the incoming question
    # ------------------------------------------------------------------
    log.info("=" * 70)
    log.info("[STEP 1] USER QUESTION RECEIVED")
    log.info("  Question : %s", question)
    t_start = time.perf_counter()   # Start total latency timer

    # ------------------------------------------------------------------
    # STEP 2 — Build the chain (opens vector store, initialises LLM)
    # ------------------------------------------------------------------
    log.info("[STEP 2] Building RAG chain (vector store + LLM)")
    t2 = time.perf_counter()
    chain = build_chain()
    log.info("[STEP 2] Chain ready — %.3fs", time.perf_counter() - t2)

    # ------------------------------------------------------------------
    # STEP 3 — Retrieval (happens inside chain.invoke via format_docs)
    # STEP 4 — Prompt construction (happens inside chain.invoke)
    # STEP 5 — LLM generation (happens inside chain.invoke)
    # ------------------------------------------------------------------
    log.info("[STEP 3-5] Running retrieval → prompt → LLM generation")
    t3 = time.perf_counter()

    try:
        answer = chain.invoke(question)   # Executes the full LCEL pipeline
        llm_latency = time.perf_counter() - t3
        log.info("[STEP 3-5] Pipeline completed — %.3fs", llm_latency)

    except Exception as exc:
        # Log the full error so it appears in the log file
        log.error("[STEP 3-5] Pipeline error: %s", exc, exc_info=True)
        raise   # Re-raise so app.py can show a user-friendly error message

    # ------------------------------------------------------------------
    # STEP 6 — Classify and log the answer type
    # ------------------------------------------------------------------
    total_latency = time.perf_counter() - t_start

    if FALLBACK_PHRASE in answer:
        log.info("[STEP 6] ANSWER TYPE  : OUT-OF-SCOPE (fallback phrase returned)")
    elif "Citations" in answer and "https://" in answer:
        log.info("[STEP 6] ANSWER TYPE  : IN-SCOPE with citations ✅")
    else:
        log.info("[STEP 6] ANSWER TYPE  : IN-SCOPE (no citation block detected)")

    log.info("[STEP 6] ANSWER PREVIEW : %s...", answer[:120].replace("\n", " "))
    log.info("[STEP 6] TOTAL LATENCY  : %.3f seconds", total_latency)
    log.info("=" * 70)

    return answer
