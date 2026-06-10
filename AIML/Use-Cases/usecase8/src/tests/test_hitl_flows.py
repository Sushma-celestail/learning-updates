# src/tests/test_hitl_flows.py
import json
import os
from pathlib import Path

import pytest
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

# Project imports
from src.graph.graph_builder import build_graph
from src.services.audit_logger import log_event

# ----------------------------------------------------------------------
# Helper to resume the graph with a decision payload
# ----------------------------------------------------------------------
def resume_graph(graph, config, decision, tool_call, edited_args=None):
    """Send a resume command to the graph.

    ``decision`` must be one of "approve", "edit" or "reject".
    ``edited_args`` is only used when ``decision`` is "edit".
    """
    decisions = [
        {
            "decision": decision,
            "edited_args": edited_args if decision == "edit" else None,
        }
    ]
    payload = Command(resume={"decisions": decisions, "tool_call": tool_call})
    return graph.invoke(payload, config=config)

# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------
@pytest.fixture
def graph():
    # In‑memory checkpointer keeps each test isolated
    cp = MemorySaver()
    return build_graph(cp)

@pytest.fixture
def config():
    return {"configurable": {"thread_id": "test-thread"}}

@pytest.fixture
def dummy_write_tool_call(tmp_path):
    """A minimal tool call payload for ``write_file``.

    The path is a temporary file within the test's ``tmp_path`` directory.
    """
    return {
        "name": "write_file",
        "args": {"path": str(tmp_path / "output.txt"), "content": "original content"},
        "id": "tool-123",
        "type": "tool",
    }

# ----------------------------------------------------------------------
# 1️⃣ Approve flow
# ----------------------------------------------------------------------
def test_approve_flow(graph, config, dummy_write_tool_call):
    result = resume_graph(
        graph,
        config,
        decision="approve",
        tool_call=dummy_write_tool_call,
    )
    # The file should have been written
    target = Path(dummy_write_tool_call["args"]["path"])
    assert target.read_text() == "original content"
    # Graph returns a normal message (not a ToolMessage)
    last_msg = result["messages"][-1]
    assert "content" in last_msg
    assert "Tool executed" in last_msg["content"] or "Completed" in last_msg["content"]
    # Verify an audit entry was created (optional safety check)
    log_file = Path(__file__).parents[2] / "approvals.jsonl"
    if log_file.exists():
        with open(log_file) as f:
            entries = [json.loads(l) for l in f.readlines()]
        latest = entries[-1]
        assert latest["decision"] == "approve"
        assert latest["payload"]["name"] == "write_file"

# ----------------------------------------------------------------------
# 2️⃣ Edit flow
# ----------------------------------------------------------------------
def test_edit_flow(graph, config, dummy_write_tool_call):
    # Change the content via the edit path
    edited_args = {
        "path": dummy_write_tool_call["args"]["path"],
        "content": "edited content",
    }
    result = resume_graph(
        graph,
        config,
        decision="edit",
        tool_call=dummy_write_tool_call,
        edited_args=edited_args,
    )
    target = Path(dummy_write_tool_call["args"]["path"])
    assert target.read_text() == "edited content"
    last_msg = result["messages"][-1]
    assert "content" in last_msg
    assert "Tool executed" in last_msg["content"]
    log_file = Path(__file__).parents[2] / "approvals.jsonl"
    if log_file.exists():
        with open(log_file) as f:
            entries = [json.loads(l) for l in f.readlines()]
        latest = entries[-1]
        assert latest["decision"] == "edit"
        assert latest["payload"]["name"] == "write_file"

# ----------------------------------------------------------------------
# 3️⃣ Reject flow
# ----------------------------------------------------------------------
def test_reject_flow(graph, config, dummy_write_tool_call):
    result = resume_graph(
        graph,
        config,
        decision="reject",
        tool_call=dummy_write_tool_call,
    )
    # The file must NOT exist because the tool never ran
    target = Path(dummy_write_tool_call["args"]["path"])
    assert not target.exists()
    # The graph should return a ToolMessage indicating rejection
    last_msg = result["messages"][-1]
    # ToolMessage objects are dict‑like with a "content" field that contains the rejection reason
    assert "Rejected by human" in last_msg.get("content", "")
    log_file = Path(__file__).parents[2] / "approvals.jsonl"
    if log_file.exists():
        with open(log_file) as f:
            entries = [json.loads(l) for l in f.readlines()]
        latest = entries[-1]
        assert latest["decision"] == "reject"
        assert latest["payload"]["name"] == "write_file"
