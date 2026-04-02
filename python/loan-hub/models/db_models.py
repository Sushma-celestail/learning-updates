from sqlalchemy import Column, Integer, String, Enum as SQLEnum, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from models.enums import UserRole, LoanPurpose, EmploymentStatus, LoanStatus


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "loan_db"}

    id             = Column(Integer, primary_key=True, index=True)
    username       = Column(String(50), unique=True, index=True, nullable=False)
    email          = Column(String(120), unique=True, index=True, nullable=False)
    password       = Column(String(255), nullable=False)
    phone          = Column(String(15), nullable=False)
    monthly_income = Column(Integer, nullable=False)
    role           = Column(
                        SQLEnum(
                            UserRole,
                            name="userrole",
                            schema="loan_db",
                            values_callable=lambda x: [e.value for e in x]
                        ),
                        default=UserRole.USER,
                        nullable=False
                    )
    is_active      = Column(Boolean, default=True)
    created_at     = Column(DateTime(timezone=True), server_default=func.now())

    loans = relationship("Loan", back_populates="user")

    def __repr__(self):
        return f"<User(username={self.username}, role={self.role})>"


class Loan(Base):
    __tablename__ = "loans"
    __table_args__ = {"schema": "loan_db"}

    id                = Column(Integer, primary_key=True, index=True)
    user_id           = Column(Integer, ForeignKey("loan_db.users.id"), nullable=False)
    amount            = Column(Integer, nullable=False)
    purpose           = Column(
                            SQLEnum(
                                LoanPurpose,
                                name="loanpurpose",
                                schema="loan_db",
                                values_callable=lambda x: [e.value for e in x]
                            ),
                            nullable=False
                        )
    tenure_months     = Column(Integer, nullable=False)
    employment_status = Column(
                            SQLEnum(
                                EmploymentStatus,
                                name="employmentstatus",
                                schema="loan_db",
                                values_callable=lambda x: [e.value for e in x]
                            ),
                            nullable=False
                        )
    status            = Column(
                            SQLEnum(
                                LoanStatus,
                                name="loanstatus",
                                schema="loan_db",
                                values_callable=lambda x: [e.value for e in x]
                            ),
                            default=LoanStatus.PENDING,
                            nullable=False
                        )
    credit_score      = Column(Integer, nullable=True)
    admin_remarks     = Column(Text, nullable=True)
    reviewed_by       = Column(String(50), nullable=True)
    reviewed_at       = Column(DateTime(timezone=True), nullable=True)
    applied_at        = Column(DateTime(timezone=True), server_default=func.now())
    updated_at        = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="loans")

    def __repr__(self):
        return f"<Loan(id={self.id}, user_id={self.user_id}, status={self.status})>"