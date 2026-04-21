from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, require_roles
from app.core.roles import Role
from app.schemas.user import UserCreate, UserResponse
from app.services import user_service

router = APIRouter()
admin_only = require_roles(Role.ADMIN)

@router.post("/", response_model=UserResponse)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(admin_only),
):
    return user_service.create_user(db, data)

from app.schemas.user import UserCreate, UserUpdate, UserResponse

@router.get("/", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    user: dict = Depends(require_roles(Role.ADMIN, Role.MANAGER, Role.CLERK)),
):
    return user_service.list_users(db)

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(admin_only),
):
    return user_service.update_user(db, user_id, data)

@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(admin_only),
):
    user_service.delete_user(db, user_id)
    return None