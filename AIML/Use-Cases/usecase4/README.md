# Use‑Case 4 – Personal Research Assistant

This agent uses **native tool‑calling**: the LLM directly invokes registered Python functions (e.g., `search_web`, `calculator`, `python_repl`, `wikipedia_search`). The runtime sends a structured call to the function instead of parsing a textual "Thought:/Action:/Observation:" chain as the older ReAct pattern did. Native calls are type‑safe, automatically logged to Langfuse, and avoid brittle string‑parsing, resulting in more reliable multi‑step reasoning.
