from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict, model_validator
from datetime import datetime
from typing import Optional, List, Literal
from models.enums import UserRole, LoanPurpose, EmploymentStatus, LoanStatus
import re


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str
    phone: str = Field(..., pattern=r"^\d{10,15}$")
    monthly_income: int = Field(..., ge=0)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r"^\w+$", v):
            raise ValueError("Username must be alphanumeric and underscores only")
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v or "." not in v:
            raise ValueError("Email must contain @ and .")
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


BLOCKED_PURPOSES = {"personal", "example", "test", "demo", "sample"}

VALID_PURPOSES = {"home", "education", "business", "vehicle", "medical", "other"}


class LoanBase(BaseModel):
    amount: float = Field(
        ...,
        gt=0,
        le=1000000,
        description="Loan amount must be greater than 0"
    )
    employment_status: Literal[
        "EMPLOYED",
        "SELF_EMPLOYED",
        "UNEMPLOYED"
    ] = Field(..., description="Employment status: EMPLOYED, SELF_EMPLOYED, or UNEMPLOYED")
    purpose: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Loan purpose: home, education, business, vehicle, medical, other"
    )
    tenure_months: int = Field(
        ...,
        ge=6,
        le=120,
        description="Loan tenure in months (6 to 120)"
    )


class LoanCreate(LoanBase):

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Please enter your actual loan amount. Amount must be greater than 0")
        if v < 1000:
            raise ValueError("Minimum loan amount is 1000")
        return v

    @field_validator("purpose")
    @classmethod
    def validate_purpose(cls, v: str) -> str:
        cleaned = v.strip().lower()
        if cleaned in BLOCKED_PURPOSES:
            raise ValueError(
                f"'{v}' is a placeholder. Please enter a real purpose: "
                "home, education, business, vehicle, medical, or other"
            )
        if cleaned not in VALID_PURPOSES:
            raise ValueError(
                f"'{v}' is not a valid purpose. Choose from: "
                "home, education, business, vehicle, medical, other"
            )
        return cleaned

    @field_validator("tenure_months")
    @classmethod
    def validate_tenure(cls, v: int) -> int:
        if v < 6:
            raise ValueError("Minimum tenure is 6 months")
        if v > 120:
            raise ValueError("Maximum tenure is 120 months")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "amount": 25000,
                "employment_status": "EMPLOYED",
                "purpose": "home",
                "tenure_months": 24
            }
        }


class LoanService(BaseModel):
    status: LoanStatus
    admin_remarks: str = Field(..., min_length=5, max_length=500)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: LoanStatus) -> LoanStatus:
        if v == LoanStatus.PENDING:
            raise ValueError("Status must be approved or rejected, not pending")
        return v


class LoanResponse(BaseModel):
    id: int
    user_id: int
    amount: float
    purpose: str
    tenure_months: int
    employment_status: str
    status: str
    admin_remarks: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    applied_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


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


class TokenData(BaseModel):
    username: str | None = None