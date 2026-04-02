from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional
import re
from .enums import UserRole, LoanPurpose, EmploymentStatus, LoanStatus

# --- User Schemas ---

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    phone: str
    monthly_income: int = Field(..., ge=0)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username must be alphanumeric or underscores only")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if not re.match(r"^\d{10,15}$", v):
            raise ValueError("Phone must be 10-15 digits only")
        return v

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# --- Loan Schemas ---

class LoanBase(BaseModel):
    amount: int = Field(..., gt=0, le=1000000)
    purpose: LoanPurpose
    tenure_months: int = Field(..., ge=6, le=360)
    employment_status: EmploymentStatus

class LoanCreate(LoanBase):
    pass

class LoanReview(BaseModel):
    status: LoanStatus
    admin_remarks: str = Field(..., min_length=5, max_length=500)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v == LoanStatus.PENDING:
            raise ValueError("Cannot review a loan to PENDING status")
        return v

class LoanResponse(LoanBase):
    id: int
    user_id: int
    status: LoanStatus
    admin_remarks: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    applied_at: datetime
    updated_at: datetime
    credit_score: Optional[int] = None

    class Config:
        from_attributes = True

# --- Bulk Check Schema ---
class BulkEligibilityCheck(BaseModel):
    loan_ids: list[int]
