from src.schemas.review_schema import ReviewDecision


def review_tool(tool_call, reviewer_id: str) -> ReviewDecision:

    email = tool_call["args"].get("to", "")

    # ❌ FIXED TYPO + validation
    if "gmail.com" not in email:
        return ReviewDecision(
            reviewer_id=reviewer_id,
            decision="reject",
            reason="Invalid email domain"
        )

    # extra safety check
    if not email or "@" not in email:
        return ReviewDecision(
            reviewer_id=reviewer_id,
            decision="reject",
            reason="Malformed email address"
        )

    return ReviewDecision(
        reviewer_id=reviewer_id,
        decision="approve",
        reason=None
    )