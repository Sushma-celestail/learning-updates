from fastapi import APIRouter, Depends, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from models.schemas import UserCreate, UserLogin, UserResponse, Token
from services.user_service import UserService
from exceptions.custom_exceptions import InvalidCredentialsError

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    user_service = UserService(db)
    return user_service.register_user(user_data)


@router.post("/token", response_model=Token)          # /token is what Swagger looks for
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),  # form data, not JSON body
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    
    # Convert form data to your existing UserLogin schema
    login_data = UserLogin(
        username=form_data.username,
        password=form_data.password
    )
    
    token = user_service.login(login_data)  # your login service returns a token
    return token