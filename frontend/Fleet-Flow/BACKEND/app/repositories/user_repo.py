from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password

def get_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def get_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

def get_all(db: Session) -> list[User]:
    return db.query(User).all()

def create(db: Session, data: UserCreate) -> User:
    user = User(
        name=data.name,
        email=data.email,
        password=hash_password(data.password),
        role=data.role,
        warehouse_id=data.warehouse_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update(db: Session, db_user: User, data: UserCreate) -> User:
    db_user.name = data.name
    db_user.email = data.email
    db_user.role = data.role
    db_user.warehouse_id = data.warehouse_id
    if data.password:
        db_user.password = hash_password(data.password)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete(db: Session, db_user: User) -> None:
    db.delete(db_user)
    db.commit()