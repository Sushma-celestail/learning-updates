"""
Verify all API keys before running ingest.
Uses the custom GeminiEmbeddings class (bypasses the hanging LangChain wrapper).
Run: python _verify_keys.py
"""
import sys, os, time
sys.path.insert(0, '.')
from shared.config.settings import (
    load_env_file, EMBEDDING_MODEL, CHAT_MODEL,
    LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST,
)
load_env_file()

print("=" * 55)
print("API Key Verification")
print("=" * 55)

google_key = os.getenv("GOOGLE_API_KEY", "")
print(f"\nGOOGLE_API_KEY   : {'✅ set' if google_key else '❌ MISSING'} (len={len(google_key)})")
print(f"LANGFUSE_PUBLIC  : {'✅ set' if LANGFUSE_PUBLIC_KEY else '⚠️  not set (optional)'}")
print(f"LANGFUSE_SECRET  : {'✅ set' if LANGFUSE_SECRET_KEY else '⚠️  not set (optional)'}")
print(f"LANGFUSE_HOST    : {LANGFUSE_HOST}")
print(f"\nEMBEDDING_MODEL  : {EMBEDDING_MODEL}")
print(f"CHAT_MODEL       : {CHAT_MODEL}")

# ── Test 1: Embedding via custom GeminiEmbeddings (bypasses LangChain wrapper) ──
print("\n--- Test 1: Gemini Embedding (custom SDK client) ---")
try:
    from shared.vectorstore.chroma import GeminiEmbeddings
    t0  = time.perf_counter()
    emb = GeminiEmbeddings(model=EMBEDDING_MODEL, timeout=15)
    vec = emb.embed_query("FastAPI dependency injection test")
    t1  = time.perf_counter()
    print(f"✅ Embedding works!  dims={len(vec)}  time={t1-t0:.2f}s")
except Exception as e:
    print(f"❌ Embedding FAILED: {type(e).__name__}: {e}")

# ── Test 2: Chat model (Gemini) ──────────────────────────────────────────────
print("\n--- Test 2: Gemini Chat (gemini-2.5-flash) ---")
try:
    from shared.llm.gemini import GeminiChat
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    t0    = time.perf_counter()
    chain = ChatPromptTemplate.from_messages([("human", "{q}")]) | GeminiChat | StrOutputParser()
    resp  = chain.invoke({"q": "Reply with just: OK"})
    t1    = time.perf_counter()
    print(f"✅ Chat works!  response='{resp.strip()}'  time={t1-t0:.2f}s")
except Exception as e:
    print(f"❌ Chat FAILED: {type(e).__name__}: {e}")

# ── Test 3: Langfuse callback ────────────────────────────────────────────────
print("\n--- Test 3: Langfuse Observability ---")
try:
    from shared.observability.langfuse_cb import get_langfuse_handler
    handler = get_langfuse_handler()
    if handler:
        print("✅ Langfuse handler created — tracing enabled")
    else:
        print("⚠️  Langfuse keys not set — tracing disabled (optional)")
except Exception as e:
    print(f"❌ Langfuse FAILED: {type(e).__name__}: {e}")

print("\n" + "=" * 55)
print("If all tests pass → run: python uc02_hybrid_search/ingest.py")
print("=" * 55)
