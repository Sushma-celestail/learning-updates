from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

class LoanHubException(Exception):
    def __init__(self, message: str, status_code: int, error_code: str):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code

class UserNotFoundError(LoanHubException):
    def __init__(self, message="User not found"):
        super().__init__(message, 404, "UserNotFoundError")

class DuplicateUserError(LoanHubException):
    def __init__(self, message="Username or email already exists"):
        super().__init__(message, 409, "DuplicateUserError")

class InvalidCredentialsError(LoanHubException):
    def __init__(self, message="Invalid username or password"):
        super().__init__(message, 401, "InvalidCredentialsError")

class ForbiddenError(LoanHubException):
    def __init__(self, message="Access denied"):
        super().__init__(message, 403, "ForbiddenError")

class LoanNotFoundError(LoanHubException):
    def __init__(self, message="Loan not found or access denied"):
        super().__init__(message, 404, "LoanNotFoundError")

class MaxPendingLoansError(LoanHubException):
    def __init__(self, message="You already have 3 pending loans"):
        super().__init__(message, 422, "MaxPendingLoansError")

class InvalidLoanReviewError(LoanHubException):
    def __init__(self, message="Cannot review an already processed loan"):
        super().__init__(message, 422, "InvalidLoanReviewError")

async def loanhub_exception_handler(request: Request, exc: LoanHubException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "message": exc.message,
            "status_code": exc.status_code
        }
    )

async def validation_exception_handler(request: Request, exc: Exception):
    # This will be used in main.py to handle Pydantic validation errors
    return JSONResponse(
        status_code=422,
        content={
            "error": "ValidationError",
            "message": str(exc),
            "status_code": 422
        }
    )
