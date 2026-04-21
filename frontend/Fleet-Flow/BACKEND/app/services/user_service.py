from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories import user_repo
from app.schemas.user import UserCreate, UserUpdate
from app.models.user import User

def create_user(db: Session, data: UserCreate) -> User:
    if not data.name.strip() or not data.email.strip() or not data.password.strip():
        raise HTTPException(status_code=400, detail="Name, email, and password are required")
    
    if data.role in ['Manager', 'Clerk', 'Driver'] and not data.warehouse_id:
        raise HTTPException(status_code=400, detail=f"Warehouse assignment is required for {data.role} role")

    existing = user_repo.get_by_email(db, data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_repo.create(db, data)

def list_users(db: Session) -> list[User]:
    return user_repo.get_all(db)

def update_user(db: Session, user_id: int, data: UserUpdate) -> User:
    if not data.name.strip() or not data.email.strip():
        raise HTTPException(status_code=400, detail="Name and email are required")
    
    if data.role in ['Manager', 'Clerk', 'Driver'] and not data.warehouse_id:
        raise HTTPException(status_code=400, detail=f"Warehouse assignment is required for {data.role} role")
    
    db_user = user_repo.get_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if db_user.email != data.email:
        existing = user_repo.get_by_email(db, data.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
            
    return user_repo.update(db, db_user, data)

def delete_user(db: Session, user_id: int) -> None:
    db_user = user_repo.get_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    user_repo.delete(db, db_user)