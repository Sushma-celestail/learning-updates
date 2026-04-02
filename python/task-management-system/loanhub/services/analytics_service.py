from sqlalchemy.orm import Session
from ..repositories.sqlalchemy_repository import SQLAlchemyRepository
from ..models.db_models import Loan, User
from ..models.enums import LoanStatus
from ..decorators.timer import timer

class AnalyticsService:
    def __init__(self, db: Session):
        self.repo = SQLAlchemyRepository(db)

    @timer
    def get_summary(self):
        """
        Analytics dashboard using comprehensions (Requirement 10).
        """
        all_loans = self.repo.find_all(Loan)
        all_users = self.repo.find_all(User)

        # Status breakdown: Dictionary comprehension
        status_counts = {status.value: len([l for l in all_loans if l.status == status]) 
                         for status in LoanStatus}

        # Loans by purpose: Dictionary comprehension
        # First get unique purposes from active applications
        purposes = set(l.purpose.value for l in all_loans)
        purpose_counts = {p: len([l for l in all_loans if l.purpose.value == p]) for p in purposes}

        # Loans by employment: Dictionary comprehension
        employments = set(l.employment_status.value for l in all_loans)
        employment_counts = {e: len([l for l in all_loans if l.employment_status.value == e]) 
                             for e in employments}

        # Average loan amount: List comprehension
        amounts = [l.amount for l in all_loans]
        avg_amount = sum(amounts) / len(amounts) if amounts else 0

        # Total disbursed: List comprehension with conditional filter
        disbursed_total = sum([l.amount for l in all_loans if l.status == LoanStatus.APPROVED])

        return {
            "total_users": len(all_users),
            "total_loans": len(all_loans),
            "pending_loans": status_counts.get("pending", 0),
            "approved_loans": status_counts.get("approved", 0),
            "rejected_loans": status_counts.get("rejected", 0),
            "total_disbursed_amount": disbursed_total,
            "loans_by_purpose": purpose_counts,
            "loans_by_employment": employment_counts,
            "avg_loan_amount": avg_amount
        }
