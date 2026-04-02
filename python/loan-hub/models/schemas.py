from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from datetime import datetime
from typing import Optional, List
import re
from models.enums import UserRole, LoanPurpose, EmploymentStatus, LoanStatus

# User Schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    phone: str
    monthly_income: int = Field(..., ge=0)

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not re.match(r'^\w+$', v):
            raise ValueError('Username must be alphanumeric or underscores only')
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if not re.match(r'^\d{10,15}$', v):
            raise ValueError('Phone must be 10-15 digits only')
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

    model_config = ConfigDict(from_attributes=True)

# Loan Schemas
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

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v == LoanStatus.PENDING:
            raise ValueError('Review status must be approved or rejected')
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

    model_config = ConfigDict(from_attributes=True)

# Analytics Schema
class AnalyticsSummary(BaseModel):
    total_users: int
    total_loans: int
    pending_loans: int
    approved_loans: int
    rejected_loans: int
    total_disbursed_amount: int
    loans_by_purpose: dict
    loans_by_employment: dict
    avg_loan_amount: float
class Token(BaseModel):
    access_token: str
    token_type: str