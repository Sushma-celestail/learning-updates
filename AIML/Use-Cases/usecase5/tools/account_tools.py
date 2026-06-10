# tools/account_tools.py

"""
Mock account management tools.

These functions simulate actions that would normally interact with a user
account system. They return static responses suitable for demos and testing.
"""


def reset_password() -> str:
    """Simulate a password reset operation."""
    return (
        "Password reset request submitted successfully.\n"
        "A password reset link has been sent to your registered email address."
    )


def update_email() -> str:
    """Simulate an email update operation."""
    return (
        "Email update request submitted successfully.\n"
        "Your email address has been updated."
    )


def get_account_info() -> str:
    """Return mock account information."""
    return (
        "Account Information\n\n"
        "User ID: usr_a4f2c\n"
        "Account Status: Active\n"
        "Plan: Premium\n"
        "Registered Email: customer@example.com\n"
        "Last Login: 2026-06-03"
    )