"""
routers/user_router.py
----------------------
HTTP layer for user endpoints.

DAY 3 CHANGES:
  - Dependency now injects SQLAlchemy session + SQLAlchemyRepository
  - All endpoint logic is IDENTICAL to Day 2
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from models.schemas import UserCreate, UserLogin, UserResponse, MessageResponse
from models.db_models import UserModel
from services.user_service import UserService
from repositories.sqlalchemy_repository import SQLAlchemyRepository
from database import get_db

router = APIRouter(prefix="/users", tags=["Users"])


# ── Dependency Provider ───────────────────────────────────────────────────────

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """
    DAY 3: Inject SQLAlchemy session, build repository, return service.
    This is the ONLY place JSONRepository → SQLAlchemyRepository swap happens.
    Services and endpoints are untouched.
    """
    repo = SQLAlchemyRepository(db=db, model=UserModel)
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
    service: UserService = Depends(get_user_service),
):
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
    return service.login_user(credentials)


@router.get(
    "",
    response_model=List[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="List all users",
)
def list_users(service: UserService = Depends(get_user_service)):
    return service.get_all_users()


@router.delete(
    "/{user_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a user",
)
def delete_user(user_id: int, service: UserService = Depends(get_user_service)):
    service.delete_user(user_id)
    return MessageResponse(message=f"User {user_id} deleted successfully")
