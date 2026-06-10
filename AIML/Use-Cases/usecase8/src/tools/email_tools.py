import re
from langchain.tools import tool

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"

def validate_email(email: str) -> bool:
    return re.match(EMAIL_REGEX, email) is not None


@tool
def send_email(
    to: str,
    subject: str,
    body: str,
) -> str:
    """
    Mock email sender with validation.
    """

    # ✅ 1. Validate email before sending
    if not validate_email(to):
        raise ValueError(f"Invalid email address: {to}")

    # ✅ 2. (optional) validate fields
    if not subject.strip():
        raise ValueError("Subject cannot be empty")

    if not body.strip():
        raise ValueError("Body cannot be empty")

    # ✅ 3. Simulated sending
    return f"Email sent to {to}"

