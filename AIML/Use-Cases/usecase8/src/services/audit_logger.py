import json
from datetime import datetime
from src.schemas.review_schema import ReviewDecision

AUDIT_FILE = "approvals.jsonl"


def log_event(event: dict):
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        **event
    }

    with open(AUDIT_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def log_review(decision: ReviewDecision):
    log_event({
        "type": "review_decision",
        "reviewer_id": decision.reviewer_id,
        "decision": decision.decision,
        "reason": decision.reason
    })


def log_tool_execution(tool_name: str, result: dict):
    log_event({
        "type": "tool_execution",
        "tool": tool_name,
        "result": result
    })


