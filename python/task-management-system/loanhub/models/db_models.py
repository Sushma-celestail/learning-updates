from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base
from .enums import UserRole, LoanPurpose, EmploymentStatus, LoanStatus

class User(Base):
    """
    SQLAlchemy model for Users.
    Includes both regular users and admins.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    phone = Column(String(15), nullable=False)
    monthly_income = Column(Integer, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to loans
    loans = relationship("Loan", back_populates="user")

    def __repr__(self):
        return f"<User(username={self.username}, role={self.role})>"

class Loan(Base):
    """
    SQLAlchemy model for Loan Applications.
    """
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    purpose = Column(SQLEnum(LoanPurpose), nullable=False)
    tenure_months = Column(Integer, nullable=False)
    employment_status = Column(SQLEnum(EmploymentStatus), nullable=False)
    status = Column(SQLEnum(LoanStatus), default=LoanStatus.PENDING, nullable=False)
    admin_remarks = Column(Text, nullable=True)
    reviewed_by = Column(String(50), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    applied_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # New column for Requirement 5 (Alembic migration exercise)
    credit_score = Column(Integer, nullable=True)

    # Relationship to user
    user = relationship("User", back_populates="loans")

    def __repr__(self):
        return f"<Loan(id={self.id}, user_id={self.user_id}, status={self.status})>"
