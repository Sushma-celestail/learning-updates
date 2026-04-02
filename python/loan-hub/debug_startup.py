import traceback
import logging
import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

try:
    print("Attempting to import and run app...")
    from main import app
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
except Exception as e:
    print("\n--- STARTUP ERROR DETECTED ---")
    traceback.print_exc()
    print("--- END OF TRACEBACK ---\n")
