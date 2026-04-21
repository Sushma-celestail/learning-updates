from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.auth import (
    LoginRequest, TokenResponse, ForgotPasswordRequest, 
    VerifyOTPRequest, ResetPasswordRequest
)
from app.services import auth_service

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    token = auth_service.login(db, data)
    return TokenResponse(access_token=token)

@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    return await auth_service.forgot_password(db, data)

@router.post("/verify-otp")
def verify_otp(data: VerifyOTPRequest, db: Session = Depends(get_db)):
    return auth_service.verify_otp(db, data)

@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    return auth_service.reset_password(db, data)