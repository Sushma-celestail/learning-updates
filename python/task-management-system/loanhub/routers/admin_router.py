from fastapi import APIRouter, Depends, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor
import time
from ..database import get_db
from ..models.schemas import LoanResponse, LoanReview, BulkEligibilityCheck
from ..models.enums import LoanStatus
from ..services.loan_service import LoanService
from ..utils.notifications import notification_service
from ..decorators.timer import timer

router = APIRouter(prefix="/admin/loans", tags=["Admin Management"])

# Helper function for bulk check (Requirement 3)
def calculate_score(loan_id: int):
    # Simulate IO / computation
    time.sleep(0.5)
    return {"loan_id": loan_id, "score": 750}

@router.get("/", response_model=List[LoanResponse])
def list_all_loans(
    user_id: Optional[int] = None,
    status: Optional[LoanStatus] = None,
    purpose: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    service = LoanService(db)
    filters = {}
    if user_id: filters["user_id"] = user_id
    if status: filters["status"] = status
    if purpose: filters["purpose"] = purpose
    
    loans = service.get_all_loans(**filters)
    start = (page - 1) * limit
    return loans[start : start + limit]

@router.patch("/{loan_id}/review", response_model=LoanResponse)
async def review_loan_application(
    loan_id: int,
    review_in: LoanReview,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    service = LoanService(db)
    # Hardcoded admin username for now
    admin_name = "admin"
    loan = service.review_loan(loan_id, admin_name, review_in)
    
    # Background task (Requirement 6)
    msg = f"Loan #{loan.id} for user ID:{loan.user_id} has been {loan.status.value} — notification sent"
    background_tasks.add_task(notification_service.notify_all, msg)
    
    return loan

@router.post("/bulk-check")
@timer
def bulk_check_loans(check_in: BulkEligibilityCheck):
    """
    Demonstrate ThreadPoolExecutor for concurrent IO (Requirement 3).
    """
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(calculate_score, check_in.loan_ids))
    return {"results": results}
