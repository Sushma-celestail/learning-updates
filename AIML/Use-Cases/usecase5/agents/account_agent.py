from graph.state import CustomerState
from tools.account_tools import reset_password, update_email


def account_agent(state: CustomerState) -> CustomerState:

    user_msgs = [
        m["content"]
        for m in state.get("messages", [])
        if m.get("role") == "user"
    ]

    user_msg = user_msgs[-1] if user_msgs else ""
    lowered = user_msg.lower()

    if "reset" in lowered or "password" in lowered:
        result = reset_password()

    elif "email" in lowered or "update" in lowered:
        result = update_email()

    elif (
        "account" in lowered
        or "profile" in lowered
        or "account info" in lowered
        or "account information" in lowered
    ):
        result = """
Account Information

User ID: usr_a4f2c
Status: Active
Plan: Premium
Email: customer@example.com
Last Login: 2026-06-03
"""

    else:
        result = """
I can help with:
• Password reset
• Email update
• Account information
"""

    state.setdefault("messages", []).append(
        {
            "role": "assistant",
            "content": result
        }
    )

    return state