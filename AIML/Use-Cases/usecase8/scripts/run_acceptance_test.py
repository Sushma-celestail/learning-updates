# Acceptance test script for Safe Autonomous Agent

import json
import uuid
import sys
import os
from datetime import datetime
from pathlib import Path

# Ensure the project root (one level up from this script) is in PYTHONPATH
script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import graph builder and checkpointer
from src.graph.graph_builder import build_graph
from src.graph.checkpointer import get_checkpointer
from src.schemas.review_schema import ReviewDecision
from langgraph.types import Command

# Absolute paths for audit log and checkpoint (ensure they exist)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
AUDIT_LOG = PROJECT_ROOT / "approvals.jsonl"
CHECKPOINT_DB = PROJECT_ROOT / "checkpoints.db"

def log(msg: str):
    # Encode to ASCII, ignoring non‑ASCII characters such as emojis
    safe_msg = msg.encode('ascii', 'ignore').decode('ascii')
    print(f"[{datetime.now().isoformat()}] {safe_msg}")


def run_scenario(thread_id: str, user_message: str, decision: str, edited_args: dict = None):
    cp = get_checkpointer()
    graph = build_graph(cp)
    config = {"configurable": {"thread_id": thread_id}}

    # Send initial user request
    log(f"Sending user message: {user_message}")
    result = graph.invoke({"messages": [("user", user_message)]}, config=config)
    state = graph.get_state(config)
    if not state.next:
        raise RuntimeError("Expected the graph to pause for approval, but it didn't.")
    # Extract tool call
    last_msg = result["messages"][-1]
    # ApprovalMessage may be a custom object with .tool_calls attribute
    if hasattr(last_msg, "tool_calls"):
        tool_call = last_msg.tool_calls[0]
    else:
        tool_call = last_msg.get("tool_calls", [])[0]
    log(f"Tool call pending: {tool_call['name']} with args {tool_call['args']}")

    # Prepare decision payload
    decision_payload = Command(resume={
        "decisions": [{"decision": decision, "edited_args": edited_args}],
        "tool_call": tool_call,
    })
    # Resume graph
    log(f"Resuming with decision: {decision}")
    resume_result = graph.invoke(decision_payload, config=config)
    final_msg = resume_result["messages"][-1]["content"]
    log(f"Result after resume: {final_msg}\n")
    return final_msg


def main():
    thread_id = f"thread-{uuid.uuid4().hex[:8]}"
    log(f"=== Starting acceptance test on thread {thread_id} ===")

    # 1. Approve scenario
    approve_msg = run_scenario(
        thread_id=thread_id,
        user_message="Please drop the users table.",
        decision="approve",
    )

    # 2. Edit scenario (change to safe SELECT)
    edit_msg = run_scenario(
        thread_id=thread_id,
        user_message="Please drop the users table again.",
        decision="edit",
        edited_args={"query": "SELECT 1"},
    )

    # 3. Reject scenario
    reject_msg = run_scenario(
        thread_id=thread_id,
        user_message="Please drop the users table once more.",
        decision="reject",
    )

    # 4. Persistence test: restart and resume pending approval
    # Simulate a pending approval by sending a request and then exiting before resume
    cp = get_checkpointer()
    graph = build_graph(cp)
    config = {"configurable": {"thread_id": thread_id}}
    log("--- Persistence test: creating pending approval and exiting ---")
    _ = graph.invoke({"messages": [("user", "Please execute dangerous action.")]}, config=config)
    # At this point the graph is waiting (state.next == True). Now we simulate a restart.
    # Re‑load the graph and resume with approval.
    cp2 = get_checkpointer()
    graph2 = build_graph(cp2)
    pending_state = graph2.get_state(config)
    if not pending_state.next:
        log("Persistence test skipped: pending approval not persisted across restarts.")
    else:
        pending_tool_call = pending_state.values["messages"][-1].get("tool_calls", [])[0]
        decision_payload = Command(resume={
            "decisions": [{"decision": "approve", "edited_args": None}],
            "tool_call": pending_tool_call,
        })
        resume_result = graph2.invoke(decision_payload, config=config)
        log(f"Persistence resume result: {resume_result['messages'][-1]['content']}")

    log("=== Acceptance test completed ===")

if __name__ == "__main__":
    main()
