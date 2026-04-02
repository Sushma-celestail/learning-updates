from fastapi import APIRouter, Depends, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.schemas import LoanCreate, LoanResponse
from ..models.enums import LoanStatus
from ..services.loan_service import LoanService
from ..utils.notifications import notification_service
from ..decorators.auth import jwt, SECRET_KEY, ALGORITHM # Reusing logic helper

router = APIRouter(prefix="/loans", tags=["Loans"])

# Dependency to get current user ID from token
def get_current_user_id(token: str = Depends(lambda: "")):
    # This is a placeholder since we don't have a real OAuth2 implementation
    # In a real app, this would use OAuth2PasswordBearer
    return 1 # TODO: Real extraction from token

@router.post("/", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
async def apply_for_loan(
    loan_in: LoanCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # For now, hardcoding user_id=1 for demonstration 
    # (in tests we will use appropriate IDs)
    service = LoanService(db)
    loan = service.apply_loan(user_id=1, loan_in=loan_in)
    
    # Background task logging (Requirement 6)
    msg = f"New loan application #{loan.id} by 'user1' (ID:1) for {loan.purpose.value} — ₹{loan.amount}"
    background_tasks.add_task(notification_service.notify_all, msg)
    
    return loan

@router.get("/my", response_model=List[LoanResponse])
def get_my_loans(
    status: Optional[LoanStatus] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    service = LoanService(db)
    loans = service.get_user_loans(user_id=1, status=status)
    # Manual pagination
    start = (page - 1) * limit
    return loans[start : start + limit]

@router.get("/my/{loan_id}", response_model=LoanResponse)
def get_loan_detail(loan_id: int, db: Session = Depends(get_db)):
    service = LoanService(db)
    return service.get_loan_by_id(loan_id, user_id=1)
