# tools/billing_tools.py
"""Mock billing tools.

These functions simulate external calls to a billing system. They return static
strings that are easy to test.
"""

def get_invoice() -> str:
    """Return a fake invoice summary."""
    return "Invoice #12345: $99.99 due on 2026-07-01"


def refund() -> str:
    """Simulate a refund operation and return a confirmation message."""
    return "Refund of $99.99 processed successfully"
