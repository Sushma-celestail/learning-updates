import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories import user_repo
from app.core.security import verify_password, create_access_token, hash_password
from app.schemas.auth import LoginRequest, ForgotPasswordRequest, VerifyOTPRequest, ResetPasswordRequest
from app.core.config import settings
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True if settings.MAIL_USERNAME else False,
    VALIDATE_CERTS=True
)

async def send_otp_email(email: str, otp: str):
    if not settings.MAIL_USERNAME or not settings.MAIL_PASSWORD:
        print(f"DEBUG: Skipping real email (no credentials). OTP {otp} sent to console for {email}")
        return

    message = MessageSchema(
        subject="Precision Flow - Genetic Access Recovery",
        recipients=[email],
        body=f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #030305; color: #ffffff; padding: 20px;">
                <div style="max-width: 600px; margin: auto; background-color: #0D0D15; padding: 40px; border-radius: 16px; border: 1px solid #ffffff14;">
                    <h1 style="color: #8b5cf6;">Access Recovery Protocol</h1>
                    <p>A request has been made to reset the access key for your node.</p>
                    <div style="background-color: #ffffff0a; padding: 20px; border-radius: 12px; text-align: center; margin: 30px 0;">
                        <span style="font-size: 32px; font-weight: bold; letter-spacing: 10px; color: #ffffff;">{otp}</span>
                    </div>
                    <p style="color: #64748b; font-size: 12px;">This code will expire in 10 minutes. If you did not request this, please secure your terminal immediately.</p>
                </div>
            </body>
        </html>
        """,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)

def login(db: Session, data: LoginRequest) -> str:
    user = user_repo.get_by_email(db, data.email)
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = create_access_token({
        "user_id": user.id,
        "role": user.role,
        "warehouse_id": user.warehouse_id,
        "name": user.name,
        "email": user.email
    })
    return token

async def forgot_password(db: Session, data: ForgotPasswordRequest):
    user = user_repo.get_by_email(db, data.email)
    print(f"DEBUG: Processing forgot_password for {data.email}")
    print(f"DEBUG: MAIL_USERNAME is '{settings.MAIL_USERNAME}'")
    
    if not user:
        # We don't want to reveal if a user exists or not for security
        return {"message": "If this email is registered, you will receive an OTP."}
    
    otp = str(random.randint(100000, 999999))
    user.otp_code = otp
    user.otp_expires_at = datetime.utcnow() + timedelta(minutes=10)
    db.commit()
    
    await send_otp_email(data.email, otp)
    
    return {
        "message": "OTP sent to your email. Please check your inbox."
    }

def verify_otp(db: Session, data: VerifyOTPRequest):
    user = user_repo.get_by_email(db, data.email)
    if not user or user.otp_code != data.otp or (user.otp_expires_at and user.otp_expires_at < datetime.utcnow()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP",
        )
    return {"message": "OTP verified successfully."}

def reset_password(db: Session, data: ResetPasswordRequest):
    user = user_repo.get_by_email(db, data.email)
    if not user or user.otp_code != data.otp or (user.otp_expires_at and user.otp_expires_at < datetime.utcnow()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP",
        )
    
    user.password = hash_password(data.new_password)
    user.otp_code = None
    user.otp_expires_at = None
    db.commit()
    
    return {"message": "Password reset successfully. Please login with your new password."}