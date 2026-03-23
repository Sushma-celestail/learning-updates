"""
exceptions/custom_exceptions.py
--------------------------------
Domain-specific exception classes for the Task Management system.

WHY CUSTOM EXCEPTIONS?
Using plain ValueError or Exception everywhere makes it impossible to
distinguish "task not found" from "user not found" programmatically.
Custom exceptions let global handlers map each exception type to the
correct HTTP status code and error message automatically.

This also follows SRP: exception classes only carry error information,
not handling logic (that lives in main.py's exception handlers).
"""


class AppBaseException(Exception):
    """
    Base class for all application exceptions.
    Carries a human-readable message that is safe to expose to clients.
    """
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class UserNotFoundError(AppBaseException):
    """Raised when a user_id or username lookup returns nothing."""
    def __init__(self, identifier):
        super().__init__(f"User '{identifier}' not found")


class TaskNotFoundError(AppBaseException):
    """Raised when a task_id lookup returns nothing."""
    def __init__(self, task_id: int):
        super().__init__(f"Task with id {task_id} not found")


class DuplicateUserError(AppBaseException):
    """Raised when registration tries to use an already-taken username."""
    def __init__(self, username: str):
        super().__init__(f"Username '{username}' is already registered")


class InvalidCredentialsError(AppBaseException):
    """Raised when login credentials don't match stored records."""
    def __init__(self):
        super().__init__("Invalid username or password")


class StorageError(AppBaseException):
    """Raised when reading/writing the JSON file fails unexpectedly."""
    def __init__(self, detail: str):
        super().__init__(f"Storage error: {detail}")
