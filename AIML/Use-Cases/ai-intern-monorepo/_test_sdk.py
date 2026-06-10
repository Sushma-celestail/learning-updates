"""Test google-genai SDK directly with explicit timeout."""
import sys, os, time
sys.path.insert(0, '.')
from shared.config.settings import load_env_file
load_env_file()

key = os.getenv('GOOGLE_API_KEY')
print(f"Key: {key[:8]}...  len={len(key)}")

from google import genai
from google.genai.types import HttpOptions

# Use explicit timeout and http options
client = genai.Client(
    api_key=key,
    http_options=HttpOptions(timeout=10000)  # 10 second timeout
)

print("Calling embed_content with 10s timeout ...")
t0 = time.perf_counter()
try:
    result = client.models.embed_content(
        model="models/gemini-embedding-001",
        contents="What is FastAPI?",
    )
    print(f"✅ SUCCESS  dims={len(result.embeddings[0].values)}  time={time.perf_counter()-t0:.2f}s")
except Exception as e:
    print(f"❌ FAILED after {time.perf_counter()-t0:.2f}s: {type(e).__name__}: {e}")
