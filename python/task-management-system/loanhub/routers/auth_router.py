from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.schemas import UserCreate, UserLogin, UserResponse
from ..services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    service = UserService(db)
    return service.register_user(user_in)

@router.post("/login")
def login(login_in: UserLogin, db: Session = Depends(get_db)):
    service = UserService(db)
    return service.authenticate_user(login_in)
