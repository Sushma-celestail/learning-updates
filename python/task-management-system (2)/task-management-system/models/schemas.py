"""
models/schemas.py
-----------------
All Pydantic schemas (data shapes) for Users and Tasks.

WHY PYDANTIC SCHEMAS?
Pydantic schemas serve three purposes simultaneously:
  1. VALIDATION  — reject bad data before it reaches business logic
  2. SERIALIZATION — convert Python objects to/from JSON automatically
  3. DOCUMENTATION — FastAPI reads these to generate OpenAPI/Swagger docs

We use SEPARATE schemas for Create, Update, and Response so that:
- Passwords are NEVER returned in responses (security)
- Update schemas make all fields optional (partial update support)
- Response schemas can add computed/stored fields (id, created_at, etc.)

This pattern is sometimes called "schema segregation" and follows ISP.
"""

from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from models.enums import TaskStatus, TaskPriority


# ─────────────────────────────────────────────
# USER SCHEMAS
# ─────────────────────────────────────────────

class UserCreate(BaseModel):
    """
    Schema for registering a new user.
    All fields are required and validated strictly.
    """
    username: str = Field(
        ...,                          # ... means required (no default)
        min_length=3,
        max_length=30,
        description="Unique username between 3 and 30 characters"
    )
    email: EmailStr = Field(
        ...,
        description="Valid email address"
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Password must be at least 8 characters"
    )

    @field_validator("username")
    @classmethod
    def username_no_whitespace(cls, v: str) -> str:
        """Reject usernames that are only spaces."""
        if v.strip() == "":
            raise ValueError("Username cannot be empty or whitespace only")
        return v.strip()


class UserLogin(BaseModel):
    """Schema for the login endpoint — only needs credentials."""
    username: str
    password: str


class UserResponse(BaseModel):
    """
    Schema returned to clients.
    NOTE: 'password' is intentionally absent — never expose it.
    """
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        # Allow creating UserResponse from ORM/dict objects directly
        from_attributes = True


# ─────────────────────────────────────────────
# TASK SCHEMAS
# ─────────────────────────────────────────────

class TaskCreate(BaseModel):
    """Schema for creating a new task. owner is set by the service, not the client."""
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    owner: str = Field(..., description="Username of the task owner")

    @field_validator("title")
    @classmethod
    def title_not_whitespace(cls, v: str) -> str:
        if v.strip() == "":
            raise ValueError("Title cannot be empty or whitespace only")
        return v.strip()


class TaskUpdate(BaseModel):
    """
    Schema for full (PUT) updates.
    All fields are still required here — use TaskPatch for partial updates.
    """
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    priority: TaskPriority
    status: TaskStatus
    owner: str


class TaskPatch(BaseModel):
    """
    Schema for partial (PATCH) updates.
    Every field is Optional — client can send just the fields they want changed.
    """
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    owner: Optional[str] = None


class TaskResponse(BaseModel):
    """Complete task data returned to clients."""
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    owner: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# GENERIC RESPONSE SCHEMAS
# ─────────────────────────────────────────────

class ErrorResponse(BaseModel):
    """Standardized error envelope returned for all exceptions."""
    error: str       # Exception class name, e.g. "TaskNotFoundError"
    message: str     # Human-readable explanation
    status_code: int # HTTP status code mirrored in the body


class MessageResponse(BaseModel):
    """Simple success message for delete operations."""
    message: str
