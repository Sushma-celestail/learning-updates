from fastapi import APIRouter, Depends, status, Query, BackgroundTasks, Request
from sqlalchemy.orm import Session
from database import get_db
from models.schemas import LoanCreate, LoanResponse
from models.enums import LoanStatus, UserRole
from services.loan_service import LoanService
from services.user_service import UserService
from utils.notifications import log_new_application
from exceptions.custom_exceptions import ForbiddenError, UserNotFoundError
from typing import List, Optional
from services.loan_service import LoanService  

router = APIRouter(prefix="/loans", tags=["loans"])

# Mock Auth Dependency: Extract username from header for simplicity in this project
def get_current_user(request: Request, db: Session = Depends(get_db)):
    username = request.headers.get("X-User")
    if not username:
        # For testing, we might want a default or fail
        raise ForbiddenError("Authentication record missing (Use X-User header)")
    
    user_service = UserService(db)
    try:
        user = user_service.get_user_by_username(username)
        request.state.user = user
        return user
    except UserNotFoundError:
        raise ForbiddenError("Invalid user in session")

@router.post("", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
def apply_loan(
    loan_data: LoanCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db), 
    user=Depends(get_current_user)
):
    loan_service = LoanService(db)
    loan = loan_service.apply_loan(user, loan_data)
    
    # Requirement 6: Background log
    background_tasks.add_task(
        log_new_application, 
        loan.id, user.username, loan.purpose.value, loan.amount
    )
    
    return loan

@router.get("/my", response_model=List[LoanResponse])
def get_my_loans(
    status: Optional[LoanStatus] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    loan_service = LoanService(db)
    loans = loan_service.get_my_loans(user.id, status)
    # Simple pagination
    start = (page - 1) * limit
    return loans[start : start + limit]

@router.get("/my/{loan_id}", response_model=LoanResponse)
def get_loan_detail(
    loan_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    loan_service = LoanService(db)
    return loan_service.get_loan_detail(loan_id, user)
