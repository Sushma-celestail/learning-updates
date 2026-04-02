from fastapi import APIRouter, Depends, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from database import get_db
from models.schemas import LoanResponse, LoanReview
from models.enums import LoanStatus, UserRole, LoanPurpose, EmploymentStatus
from services.loan_service import LoanService
from routers.loan_router import get_current_user
from decorators.auth import require_role
from decorators.timer import timer
from utils.notifications import send_notifications
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional
import time

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/loans", response_model=List[LoanResponse])
def list_all_loans(
    status: Optional[LoanStatus] = None,
    user_id: Optional[int] = None,
    purpose: Optional[LoanPurpose] = None,
    employment_status: Optional[EmploymentStatus] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db),
    admin=Depends(require_role(UserRole.ADMIN))
):
    loan_service = LoanService(db)
    filters = {
        "status": status,
        "user_id": user_id,
        "purpose": purpose,
        "employment_status": employment_status
    }
    # Filter out None values
    filters = {k: v for k, v in filters.items() if v is not None}
    
    loans = loan_service.get_all_loans_admin(**filters)
    start = (page - 1) * limit
    return loans[start : start + limit]

@router.get("/loans/{loan_id}", response_model=LoanResponse)
def view_loan_detail(
    loan_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_role(UserRole.ADMIN))
):
    loan_service = LoanService(db)
    return loan_service.get_loan_detail(loan_id, admin)

@router.patch("/loans/{loan_id}/review", response_model=LoanResponse)
def review_loan(
    loan_id: int,
    review_data: LoanReview,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    admin=Depends(require_role(UserRole.ADMIN))
):
    loan_service = LoanService(db)
    loan = loan_service.review_loan(loan_id, review_data, admin.username)
    
    # Requirement 6: Background task for async notifications
    background_tasks.add_task(
        send_notifications, 
        loan.id, loan.user.username, loan.status.value
    )
    
    return loan

# Requirement 3: ThreadPoolExecutor for bulk check
def compute_eligibility(loan_id: int, income: int, amount: int):
    # Simulate I/O or heavy computation
    time.sleep(0.1)
    ratio = income / (amount / 12) if amount > 0 else 0
    return {"loan_id": loan_id, "eligibility_score": round(ratio, 2), "status": "eligible" if ratio > 2 else "risky"}

@router.post("/loans/bulk-check")
@timer
def bulk_check_eligibility(
    loan_ids: List[int],
    db: Session = Depends(get_db),
    admin=Depends(require_role(UserRole.ADMIN))
):
    loan_service = LoanService(db)
    tasks = []
    for lid in loan_ids:
        loan = loan_service.repo.get_by_id(lid)
        if loan:
            tasks.append((loan.id, loan.user.monthly_income, loan.amount))
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(lambda p: compute_eligibility(*p), tasks))
        
    return {"results": results}
