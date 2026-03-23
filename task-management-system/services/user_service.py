"""
services/user_service.py
------------------------
Business logic layer for user operations.

SOLID PRINCIPLES APPLIED:
  SRP: UserService ONLY handles user-related business rules.
       It does NOT touch HTTP (that's the router) or files (that's the repo).

  DIP: UserService depends on BaseRepository (abstraction), not JSONRepository.
       The concrete repo is injected via FastAPI's Depends() — the service
       never creates its own repository instance.

  OCP: To add a new user feature (e.g. email verification), we add a method
       here without touching any other file.

WHAT IS "BUSINESS LOGIC"?
Business logic = rules that define HOW your system works:
  - "Usernames must be unique" → checked here, not in the router
  - "Passwords are hashed before storage" → done here
  - "Login validates credentials" → done here

We use a simple hash for passwords (not bcrypt) to keep dependencies minimal,
but in production you'd always use bcrypt or argon2.
"""

import hashlib
import logging
from datetime import datetime
from typing import Any, Dict, List

from repositories.base_repository import BaseRepository
from models.schemas import UserCreate, UserLogin, UserResponse
from exceptions.custom_exceptions import (
    UserNotFoundError,
    DuplicateUserError,
    InvalidCredentialsError,
)

logger = logging.getLogger(__name__)


def _hash_password(password: str) -> str:
    """
    Simple SHA-256 hash of the password.
    In production: use bcrypt or passlib.
    We hash so that the raw password is never stored in the JSON file.
    """
    return hashlib.sha256(password.encode()).hexdigest()


class UserService:
    """
    Encapsulates all user business logic.

    The repository is injected via the constructor — this is
    Dependency Injection, which enables DIP.
    """

    def __init__(self, repository: BaseRepository):
        # We store a reference to the abstraction, not the concrete class
        self.repo = repository

    def register_user(self, user_data: UserCreate) -> UserResponse:
        """
        Register a new user.
        Rules:
          1. Username must not already exist (DuplicateUserError if it does)
          2. Password is hashed before storage
          3. created_at timestamp is assigned here (not by the client)
        """
        # Rule 1: Check for duplicate username
        existing_users = self.repo.find_all()
        for user in existing_users:
            if user["username"] == user_data.username:
                logger.warning(f"Duplicate username attempt: '{user_data.username}'")
                raise DuplicateUserError(user_data.username)

        # Rule 2 & 3: Build the record dict to persist
        record = {
            "username": user_data.username,
            "email": user_data.email,
            "password": _hash_password(user_data.password),  # never store plaintext
            "created_at": datetime.now().isoformat(),
        }

        saved = self.repo.save(record)
        logger.info(f"User '{user_data.username}' registered with id={saved['id']}")
        return self._to_response(saved)

    def login_user(self, credentials: UserLogin) -> UserResponse:
        """
        Validate login credentials.
        Rules:
          - Username must exist
          - Password hash must match stored hash
        Returns the UserResponse (no token in this simple system).
        """
        users = self.repo.find_all()
        for user in users:
            if user["username"] == credentials.username:
                if user["password"] == _hash_password(credentials.password):
                    logger.info(f"User '{credentials.username}' logged in successfully")
                    return self._to_response(user)
                else:
                    logger.warning(f"Bad password attempt for '{credentials.username}'")
                    raise InvalidCredentialsError()

        # Username not found — same error as bad password (don't reveal which)
        logger.warning(f"Login attempt for unknown user '{credentials.username}'")
        raise InvalidCredentialsError()

    def get_all_users(self) -> List[UserResponse]:
        """Return all users (passwords excluded via UserResponse schema)."""
        users = self.repo.find_all()
        return [self._to_response(u) for u in users]

    def delete_user(self, user_id: int) -> None:
        """
        Delete a user by ID.
        Raises UserNotFoundError if the ID doesn't exist.
        """
        success = self.repo.delete(user_id)
        if not success:
            logger.error(f"Delete failed: user id={user_id} not found")
            raise UserNotFoundError(user_id)
        logger.info(f"User id={user_id} deleted")

    # ── Private helpers ───────────────────────────────────────────────

    def _to_response(self, record: Dict[str, Any]) -> UserResponse:
        """
        Convert a raw dict (from JSON storage) to a UserResponse Pydantic model.
        Pydantic will coerce the string datetime back to a datetime object.
        """
        return UserResponse(
            id=record["id"],
            username=record["username"],
            email=record["email"],
            created_at=record["created_at"],
        )
