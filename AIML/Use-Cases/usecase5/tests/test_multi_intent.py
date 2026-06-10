# tests/test_multi_intent.py
"""Test multi-intent chaining (AC #23)."""

from graph.builder import run_graph, initial_state

def test_multi_intent_refund_and_reset():
    """Verify that 'Refund AND reset password' triggers billing then account agent."""
    state = initial_state()
    state["messages"] = [{"role": "user", "content": "I need a refund and reset my password."}]
    
    final_state = run_graph(state)
    
    # Check that both billing and account responses are in the messages
    messages = [m["content"] for m in final_state.get("messages", []) if m["role"] == "assistant"]
    
    assert len(messages) >= 2, "Expected at least 2 assistant messages for multi-intent."
    
    # We expect one message to be about refund (billing) and one about password (account)
    has_billing = any("Refund" in m or "Invoice" in m for m in messages)
    has_account = any("Password" in m or "Email" in m for m in messages)
    
    assert has_billing, "Billing agent response not found."
    assert has_account, "Account agent response not found."
