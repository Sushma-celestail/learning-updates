"""
models/enums.py
---------------
Enum definitions for TaskStatus and TaskPriority.

WHY ENUMS?
Enums restrict a field to a fixed set of valid values.
Without enums, a user could send status="done" or priority="urgent" —
values our system doesn't understand. Enums enforce correctness at the
Pydantic validation layer before any business logic runs.

Python's str + Enum combination makes FastAPI serialize them as plain
strings in JSON responses (e.g., "pending" not "TaskStatus.pending").
"""

from enum import Enum


class TaskStatus(str, Enum):
    """
    Allowed lifecycle states for a task.
    Inheriting from str means JSON serialization gives "pending" not 0.
    """
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """
    Urgency levels for a task.
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
