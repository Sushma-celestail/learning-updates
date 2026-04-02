"""
services/user_service.py
------------------------
Business logic for user operations.

DAY 3 CHANGES:
  - _find_by_username() uses find_by_field() for SQLAlchemy (more efficient)
  - Falls back to linear scan for JSON repo (backward compatible)
  - Everything else identical to Day 2
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
    """SHA-256 hash. In production use bcrypt."""
    return hashlib.sha256(password.encode()).hexdigest()


class UserService:
    """Encapsulates all user business logic."""

    def __init__(self, repository: BaseRepository):
        self.repo = repository

    def register_user(self, user_data: UserCreate) -> UserResponse:
        """Register a new user. Checks for duplicate username before saving."""
        existing = self._find_by_username(user_data.username)
        if existing:
            logger.warning(f"Duplicate username attempt: '{user_data.username}'")
            raise DuplicateUserError(user_data.username)

        record = {
            "username": user_data.username,
            "email": user_data.email,
            "password": _hash_password(user_data.password),
            "created_at": datetime.now(),
        }

        saved = self.repo.save(record)
        logger.info(f"User '{user_data.username}' registered with id={saved['id']}")
        return self._to_response(saved)

    def login_user(self, credentials: UserLogin) -> UserResponse:
        """Validate login credentials."""
        user = self._find_by_username(credentials.username)
        if user:
            if user["password"] == _hash_password(credentials.password):
                logger.info(f"User '{credentials.username}' logged in successfully")
                return self._to_response(user)
            else:
                logger.warning(f"Bad password attempt for '{credentials.username}'")
                raise InvalidCredentialsError()

        logger.warning(f"Login attempt for unknown user '{credentials.username}'")
        raise InvalidCredentialsError()

    def get_all_users(self) -> List[UserResponse]:
        """Return all users."""
        users = self.repo.find_all()
        return [self._to_response(u) for u in users]

    def delete_user(self, user_id: int) -> None:
        """Delete a user by ID."""
        success = self.repo.delete(user_id)
        if not success:
            logger.error(f"Delete failed: user id={user_id} not found")
            raise UserNotFoundError(user_id)
        logger.info(f"User id={user_id} deleted")

    def _find_by_username(self, username: str):
        """
        Find user by username.
        Uses find_by_field() if available (SQLAlchemy),
        falls back to linear scan (JSON repo).
        """
        if hasattr(self.repo, 'find_by_field'):
            return self.repo.find_by_field("username", username)
        users = self.repo.find_all()
        for user in users:
            if user["username"] == username:
                return user
        return None

    def _to_response(self, record: Dict[str, Any]) -> UserResponse:
        return UserResponse(
            id=record["id"],
            username=record["username"],
            email=record["email"],
            created_at=record["created_at"],
        )
