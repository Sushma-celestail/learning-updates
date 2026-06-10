"""ReAct agent core — uses Groq (Llama 3.3 70B) with native tool-calling."""

import os
from dotenv import load_dotenv
load_dotenv()
# Ensure GROQ_API_KEY is available for ChatGroq
os.environ.setdefault("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))
from langchain_groq import ChatGroq

from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware
from langchain.agents.middleware.model_call_limit import ModelCallLimitExceededError
from langchain_core.messages import SystemMessage

from agent.tools.search import web_search
from agent.tools.calculator import calculator
from agent.tools.python_repl import python_repl
from agent.tools.wiki import wikipedia_search
from memory.store import get_checkpointer

# --- System Prompt ---
SYSTEM_PROMPT = """You are a Personal Research Assistant. You answer multi-step factual questions
by reasoning step-by-step and calling the right tools.

You have 4 tools available:

1. **web_search** — Use this for current events, live statistics, recent news, or any
   real-world data that may change over time (populations, stock prices, sports results).

2. **calculator** — Use this for mathematical expressions. Pass a valid math expression
   string like "68170000 / 1000000" or "sqrt(144) * 8". Do NOT pass Python code here.

3. **python_repl** — Use this for small Python computations, data processing, or anything
   that needs real code execution. Keep snippets short and always print the result.

4. **wikipedia_search** — Use this for historical facts, biographies, scientific concepts,
   or well-established general knowledge.

When a question asks for the definition of a term, acronym, or concept, you must first call `wikipedia_search` with a precise query (e.g., "RAG (retrieval augmented generation)") to obtain an authoritative summary. Only after retrieving the information should you synthesize the final answer.

- **Never output any answer text before you have called all required tools.** First, think about which tool(s) you need, call them, collect the results, and only then synthesize the final answer.
- Always think about which tool is best for each sub‑question.
- Break complex questions into smaller steps.
- After getting tool results, synthesize them into a clear final answer.
- If you cannot find the answer after several attempts, say so honestly.
- Always think about which tool is best for each sub-question.
- Break complex questions into smaller steps.
- After getting tool results, synthesize them into a clear final answer.
- If you cannot find the answer after several attempts, say so honestly.

**Output format**:
When you have the final answer, output it **first** on its own line.
Immediately after the answer, output a markdown table titled **"Required tool chain"** with columns
`Step | Tool (function) | Argument | Expected result`.
List each tool you invoked in order, with the argument you passed and the expected result.

```
"""
# --- Initialize LLM ---
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

# --- Load Tools ---
tools = [web_search, calculator, python_repl, wikipedia_search]

# --- Checkpointer (memory) ---
checkpointer = get_checkpointer()

# --- Iteration Cap Middleware ---
middleware = [ModelCallLimitMiddleware(run_limit=8, exit_behavior="error")]

# --- Create Agent ---
agent = create_agent(
    model=llm,
    tools=tools,
    middleware=middleware,
    checkpointer=checkpointer,
    # debug=True,
    system_prompt=SYSTEM_PROMPT,
)


def run_agent(user_input: str, thread_id: str, callbacks=None):
    """Run the agent with memory and iteration cap.

    Args:
        user_input: The user's question.
        thread_id: Stable thread ID for multi-turn memory.
        callbacks: Optional list of LangChain callbacks (e.g. Langfuse).

    Returns:
        The agent's final answer as a string.
    """
    config = {
        "configurable": {"thread_id": thread_id},
        "callbacks": callbacks or [],
    }

    try:
        result = agent.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config=config,
        )
        content = result["messages"][-1].content
        # Handle list-type content (some models return structured blocks)
        if isinstance(content, list):
            return " ".join(
                b.get("text", "")
                for b in content
                if isinstance(b, dict) and b.get("type") == "text"
            )
        return str(content)
    except ModelCallLimitExceededError:
        return "I couldn't determine the answer within 8 steps. Try rephrasing or breaking the question into smaller parts."
    except Exception as e:
        return f"An error occurred: {e}"
