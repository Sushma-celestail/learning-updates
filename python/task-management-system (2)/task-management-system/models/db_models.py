"""
models/db_models.py
-------------------
SQLAlchemy ORM models — these define the actual DATABASE TABLES.

DAY 3 NEW FILE.

DIFFERENCE FROM PYDANTIC SCHEMAS:
  Pydantic schemas (schemas.py) → define API request/response shapes
  SQLAlchemy models (this file)  → define database table columns

  Both exist side by side. The repository layer converts between them.

  Pydantic:    UserCreate, UserResponse  (HTTP layer)
  SQLAlchemy:  UserModel                 (DB layer)

WHY TWO SEPARATE MODELS?
  - DB models have columns like 'password' that should never appear in API responses
  - DB models have relationships (ForeignKey, back_populates) that Pydantic doesn't need
  - Keeps concerns separated: API contract vs storage structure

RELATIONSHIPS:
  UserModel has a one-to-many relationship with TaskModel.
  One user can own many tasks.
  TaskModel.owner_username is a ForeignKey to UserModel.username.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class UserModel(Base):
    """
    Maps to the 'users' table in PostgreSQL.

    __tablename__ tells SQLAlchemy what to name the table.
    Each Column() defines one column in the table.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(30), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)   # stores hashed password
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    # Relationship: one user → many tasks
    # back_populates links UserModel.tasks ↔ TaskModel.user
    tasks = relationship("TaskModel", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User id={self.id} username={self.username}>"


class TaskModel(Base):
    """
    Maps to the 'tasks' table in PostgreSQL.
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)          # Text = unlimited length string
    status = Column(String(20), nullable=False, default="pending")
    priority = Column(String(10), nullable=False, default="medium")
    owner_username = Column(
        String(30),
        ForeignKey("users.username", ondelete="CASCADE"),  # delete tasks when user deleted
        nullable=False
    )
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    # Relationship: many tasks → one user
    user = relationship("UserModel", back_populates="tasks")

    def __repr__(self):
        return f"<Task id={self.id} title={self.title} owner={self.owner_username}>"
