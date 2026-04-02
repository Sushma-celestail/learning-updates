from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from ..repositories.sqlalchemy_repository import SQLAlchemyRepository
from ..models.db_models import Loan, User
from ..models.schemas import LoanCreate, LoanReview
from ..models.enums import LoanStatus
from ..exceptions.custom_exceptions import (
    MaxPendingLoansError, LoanNotFoundError, 
    InvalidLoanReviewError, ForbiddenError
)
from ..decorators.timer import timer
from ..utils.notifications import notification_service

class LoanService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = SQLAlchemyRepository(db)

    @timer
    def apply_loan(self, user_id: int, loan_in: LoanCreate) -> Loan:
        # Business Rule: Max 3 pending loans
        pending_loans = self.repo.find_all(Loan, user_id=user_id, status=LoanStatus.PENDING)
        if len(pending_loans) >= 3:
            raise MaxPendingLoansError()

        new_loan = Loan(
            user_id=user_id,
            amount=loan_in.amount,
            purpose=loan_in.purpose,
            tenure_months=loan_in.tenure_months,
            employment_status=loan_in.employment_status,
            status=LoanStatus.PENDING
        )
        loan = self.repo.save(new_loan)
        
        # Background task simulation (Requirement 6)
        # In a real FastAPI app, this would be passed to BackgroundTasks
        # For now, we'll trigger it here for demonstration or the router will handle it.
        return loan

    def get_user_loans(self, user_id: int, status: Optional[LoanStatus] = None) -> List[Loan]:
        filters = {"user_id": user_id}
        if status:
            filters["status"] = status
        return self.repo.find_all(Loan, **filters)

    def get_loan_by_id(self, loan_id: int, user_id: Optional[int] = None) -> Loan:
        loan = self.repo.find_by_id(Loan, loan_id)
        if not loan:
            raise LoanNotFoundError()
        if user_id and loan.user_id != user_id:
            raise LoanNotFoundError("Loan not found for this user")
        return loan

    def get_all_loans(self, **filters) -> List[Loan]:
        return self.repo.find_all(Loan, **filters)

    @timer
    def review_loan(self, loan_id: int, admin_name: str, review_in: LoanReview) -> Loan:
        """
        Atomic review operation (Requirement 4).
        """
        loan = self.repo.find_by_id(Loan, loan_id)
        if not loan:
            raise LoanNotFoundError()
        
        # Rule: Only pending loans can be reviewed
        if loan.status != LoanStatus.PENDING:
            raise InvalidLoanReviewError()

        # Update fields atomically
        loan.status = review_in.status
        loan.admin_remarks = review_in.admin_remarks
        loan.reviewed_by = admin_name
        loan.reviewed_at = datetime.utcnow()
        loan.updated_at = datetime.utcnow()

        # Save updates
        updated_loan = self.repo.update(loan)
        
        return updated_loan
