# tests/test_long_term_mem.py
"""Test long-term memory persistence across sessions (AC #24)."""

import os
from graph.builder import run_graph, initial_state
from memory.long_term import InMemoryStore

def test_long_term_memory():
    """Verify that a fact extracted in session 1 is available in session 2."""
    
    # We use a unique user ID for this test
    test_user_id = "test_user_999"
    
    # Session 1: User asks about billing
    state1 = initial_state()
    state1["customer_context"] = {"user_id": test_user_id}
    state1["messages"] = [{"role": "user", "content": "I have a question about my invoice."}]
    
    final_state1 = run_graph(state1)
    
    # Check that long term store actually saved 'last_issue'
    store = InMemoryStore()
    ltm = store.get(test_user_id)
    assert ltm.get("last_issue") == "billing", "Session 1 did not persist 'last_issue'."
    
    # Session 2: Same user asks about something else, or just starts a new session
    state2 = initial_state()
    state2["customer_context"] = {"user_id": test_user_id}
    state2["messages"] = [{"role": "user", "content": "I need help."}]
    
    final_state2 = run_graph(state2)
    
    # The supervisor should have loaded 'last_issue' into 'customer_context'
    assert final_state2["customer_context"].get("last_issue") == "billing", "Session 2 did not load 'last_issue' from long term memory."
