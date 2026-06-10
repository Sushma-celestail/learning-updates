# observability/langfuse_logger.py
"""Very lightweight Langfuse‑style logger.

The real Langfuse SDK is not required for this demo. Instead we write a JSON line
per node invocation to ``logs/langfuse.log``. Each entry contains:

* ``timestamp`` – ISO‑8601 UTC time
* ``node`` – name of the graph node (e.g. "supervisor", "billing")
* ``prompt_tokens`` – naive token count of the input (word count)
* ``completion_tokens`` – naive token count of the node's output (word count)
* ``total_tokens`` – sum of the two above
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

_LOG_DIR = Path(__file__).resolve().parents[1] / "logs"
_LOG_DIR.mkdir(parents=True, exist_ok=True)
_LOG_FILE = _LOG_DIR / "langfuse.log"

def _write(entry: Dict) -> None:
    with _LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def _token_count(text: str) -> int:
    """Very naive token estimator – count whitespace‑separated words."""
    return len(text.split())

def log_node(node_name: str, prompt: str, completion: str) -> int:
    """Record a single node execution and return total tokens."""
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "node": node_name,
        "prompt_tokens": _token_count(prompt),
        "completion_tokens": _token_count(completion),
    }
    entry["total_tokens"] = entry["prompt_tokens"] + entry["completion_tokens"]
    _write(entry)
    return entry["total_tokens"]

def compare_costs(messages: List[str]) -> None:
    """Compare multi-agent cost to a single-agent baseline.
    
    This function simulates the cost (in tokens) of processing the same
    set of messages using the multi-agent graph vs a single-agent baseline.
    """
    print("\n=== Cost Comparison Report ===")
    print(f"{'Message':<60} | {'Multi-Agent':<12} | {'Single-Agent':<12} | {'Overhead'}")
    print("-" * 105)
    
    total_multi = 0
    total_single = 0
    
    for msg in messages:
        # Simulate multi-agent tokens (supervisor + 1 or more agents)
        # We estimate using word counts just to show the overhead logic.
        words = _token_count(msg)
        
        # Multi-agent overhead: Supervisor runs (system prompt + msg) + Agent runs
        # We'll simulate 2.5x overhead on average for multi-intent
        multi_agent_tokens = words * 5 + 50
        
        # Single-agent: one giant prompt with all tools
        single_agent_tokens = words * 2 + 20
        
        overhead = multi_agent_tokens / single_agent_tokens if single_agent_tokens else 1
        
        total_multi += multi_agent_tokens
        total_single += single_agent_tokens
        
        trunc_msg = msg[:57] + "..." if len(msg) > 60 else msg
        print(f"{trunc_msg:<60} | {multi_agent_tokens:<12} | {single_agent_tokens:<12} | {overhead:.2f}x")
        
    print("-" * 105)
    total_overhead = total_multi / total_single if total_single else 1
    print(f"{'TOTAL':<60} | {total_multi:<12} | {total_single:<12} | {total_overhead:.2f}x")
    print("==============================\n")
