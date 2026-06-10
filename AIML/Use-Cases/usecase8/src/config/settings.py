from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-1.5-flash")

CHECKPOINT_DB = "checkpoints.db"
AUDIT_FILE = "approvals.jsonl"


