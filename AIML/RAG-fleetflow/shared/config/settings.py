"""Central settings for the Docs Buddy project."""
# This module keeps all configurable values in one easy-to-find place
# Making changes here affects the entire application consistently

import os  # os module provides access to environment variables and system functions
from pathlib import Path  # Path creates cross-platform file and directory paths safely

# Calculate the project root directory by going up two levels from this file
# __file__ is the current file path, resolve() makes it absolute, parents[2] goes up two directories
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # Points to ai-intern-monorepo folder

# Define the path to the optional .env file in the project root
ENV_FILE = PROJECT_ROOT / ".env"  # Uses Path division operator for cross-platform paths


def load_env_file():
    """Load environment variables from .env file if it exists."""
    # This function provides simple .env file support without requiring python-dotenv dependency
    # It manually parses KEY=VALUE lines and sets them as environment variables
    
    if not ENV_FILE.exists():  # Check if .env file exists before trying to read it
        return  # Exit early if no .env file is found (this is optional)
    
    # Read the entire .env file content as text with UTF-8 encoding
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()  # Remove leading/trailing whitespace from each line
        
        # Skip empty lines, comments (starting with #), and invalid lines without =
        if not line or line.startswith("#") or "=" not in line:
            continue  # Move to the next line
        
        # Split the line into key and value at the first = character
        key, value = line.split("=", 1)  # 1 means split only at first =, preserving = in values
        
        # Clean up the key by removing PowerShell-style $env: prefix and whitespace
        key = key.replace("$env:", "").strip()
        
        # Clean up the value by removing whitespace and optional quotes
        value = value.strip().strip('"').strip("'")
        
        # Set the environment variable, overriding any existing value
        os.environ[key] = value


# Load environment variables immediately when this module is imported
# This ensures API keys are available before any Gemini clients are created
load_env_file()

# Project structure paths - these define where different components are stored
USE_CASE_ROOT = PROJECT_ROOT / "usecase_01"  # Root directory for Use Case 1
CHROMA_DIR = USE_CASE_ROOT / "data" / "chroma"    # Where ChromaDB stores vector data on disk

# ChromaDB collection configuration
COLLECTION_NAME = "fastapi_docs_buddy"  # Stable name for the vector collection (enables updates)

# Documentation source configuration
DOCS_SITEMAP_URL = "https://fastapi.tiangolo.com/sitemap.xml"  # FastAPI sitemap with all doc URLs
DOCS_URL_PREFIX = "https://fastapi.tiangolo.com/"             # Filter to keep only FastAPI docs

# Document ingestion limits (per acceptance criteria)
MIN_PAGES = 50   # Minimum number of pages required by acceptance criteria
MAX_PAGES = 80   # Maximum to keep demo manageable while staying in 50-200 range

# Quick test mode - set to True for faster testing with fewer documents
QUICK_TEST_MODE = False  # Set to True to ingest only 10 pages for quick testing
TEST_PAGES = 10         # Number of pages for quick testing

# Text chunking configuration (per requirements)
CHUNK_SIZE = 800     # Maximum characters per chunk (required specification)
CHUNK_OVERLAP = 100  # Overlapping characters between chunks (required specification)

# Retrieval configuration
RETRIEVAL_K = 4  # Number of most relevant chunks to retrieve per question

# AI model configuration - change these to swap providers
EMBEDDING_MODEL = "gemini-embedding-001"  # Gemini embedding model for document vectors
CHAT_MODEL = "gemini-2.5-flash"          # Gemini chat model for answer generation

# Response configuration
FALLBACK_PHRASE = "I don't know based on the provided docs"  # Exact phrase for out-of-scope questions

# Logging configuration
LOG_DIR  = USE_CASE_ROOT / "logs"          # Directory where log files are stored
LOG_FILE = LOG_DIR / "rag_pipeline.log"   # Main log file for the full RAG pipeline trace