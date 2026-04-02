from sqlalchemy.orm import Session
from models.db_models import Loan, User
from models.enums import LoanStatus, LoanPurpose, EmploymentStatus
from decorators.timer import timer

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    @timer
    def get_summary(self):
        loans = self.db.query(Loan).all()
        users_count = self.db.query(User).count()
        
        if not loans:
            return {
                "total_users": users_count,
                "total_loans": 0,
                "pending_loans": 0,
                "approved_loans": 0,
                "rejected_loans": 0,
                "total_disbursed_amount": 0,
                "loans_by_purpose": {},
                "loans_by_employment": {},
                "avg_loan_amount": 0
            }

        # Requirement 10: Use comprehensions
        statuses = [l.status for l in loans]
        status_breakdown = {s.value: statuses.count(s) for s in LoanStatus}
        
        purposes = [l.purpose for l in loans]
        loans_by_purpose = {p.value: purposes.count(p) for p in LoanPurpose}
        
        employment = [l.employment_status for l in loans]
        loans_by_employment = {e.value: employment.count(e) for e in EmploymentStatus}
        
        amounts = [l.amount for l in loans]
        avg_loan_amount = sum(amounts) / len(amounts)
        
        # Total disbursed: List comprehension with conditional filter
        total_disbursed = sum([l.amount for l in loans if l.status == LoanStatus.APPROVED])
        
        return {
            "total_users": users_count,
            "total_loans": len(loans),
            "pending_loans": status_breakdown.get("pending", 0),
            "approved_loans": status_breakdown.get("approved", 0),
            "rejected_loans": status_breakdown.get("rejected", 0),
            "total_disbursed_amount": total_disbursed,
            "loans_by_purpose": loans_by_purpose,
            "loans_by_employment": loans_by_employment,
            "avg_loan_amount": avg_loan_amount
        }
