"""
routers/user_router.py
----------------------
HTTP layer for user endpoints. This file ONLY handles:
  - Receiving HTTP requests
  - Calling the service
  - Returning HTTP responses

It contains NO business logic and NO file I/O.

DEPENDENCY INJECTION with FastAPI Depends():
  FastAPI's Depends() system works like this:
    1. FastAPI sees that an endpoint parameter is annotated with Depends(get_user_service)
    2. It calls get_user_service() to build the dependency
    3. It injects the result into the endpoint function

  This is how we achieve DIP: the router doesn't import or create
  JSONRepository or UserService directly — it just declares what it needs.

WHY SPLIT ROUTERS INTO SEPARATE FILES?
  OCP: Adding a new resource (e.g. Projects) means adding a new router file.
  We never need to touch user_router.py to add project endpoints.
"""

from fastapi import APIRouter, Depends, status
from typing import List

from models.schemas import UserCreate, UserLogin, UserResponse, MessageResponse
from services.user_service import UserService
from repositories.json_repository import JSONRepository
from config import settings

# APIRouter is like a mini FastAPI app — it groups related endpoints.
# The prefix and tags appear in the OpenAPI docs.
router = APIRouter(prefix="/users", tags=["Users"])


# ── Dependency provider ───────────────────────────────────────────────────────

def get_user_service() -> UserService:
    """
    Factory function used by FastAPI's Depends() system.

    This is the ONLY place in the codebase where we wire together
    the concrete JSONRepository with the UserService.

    If we ever want to switch to SQLiteRepository, we change ONE line here.
    The rest of the codebase is untouched.
    """
    repo = JSONRepository(file_path=settings.users_file, collection="users")
    return UserService(repository=repo)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service),  # FastAPI injects this
):
    """
    Register a new user account.
    - Username must be unique (3-30 chars)
    - Email must be a valid format
    - Password must be at least 8 characters
    """
    return service.register_user(user_data)


@router.post(
    "/login",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Login with credentials",
)
def login_user(
    credentials: UserLogin,
    service: UserService = Depends(get_user_service),
):
    """
    Validate login credentials. Returns user info on success.
    In a real system, this would return a JWT token.
    """
    return service.login_user(credentials)


@router.get(
    "",
    response_model=List[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="List all users",
)
def list_users(
    service: UserService = Depends(get_user_service),
):
    """Return all registered users (passwords excluded)."""
    return service.get_all_users()


@router.delete(
    "/{user_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a user",
)
def delete_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
):
    """Delete a user by ID. Returns 404 if user doesn't exist."""
    service.delete_user(user_id)
    return MessageResponse(message=f"User {user_id} deleted successfully")
