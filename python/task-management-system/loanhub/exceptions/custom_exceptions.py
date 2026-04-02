from fastapi import HTTPException, status

class LoanHubException(HTTPException):
    def __init__(self, status_code: int, message: str, error_type: str):
        super().__init__(status_code=status_code, detail={"message": message, "error": error_type})

class UserNotFoundError(LoanHubException):
    def __init__(self, message: str = "User not found"):
        super().__init__(status.HTTP_404_NOT_FOUND, message, "UserNotFoundError")

class DuplicateUserError(LoanHubException):
    def __init__(self, message: str = "User already exists"):
        super().__init__(status.HTTP_409_CONFLICT, message, "DuplicateUserError")

class InvalidCredentialsError(LoanHubException):
    def __init__(self, message: str = "Invalid username or password"):
        super().__init__(status.HTTP_401_UNAUTHORIZED, message, "InvalidCredentialsError")

class ForbiddenError(LoanHubException):
    def __init__(self, message: str = "Permission denied"):
        super().__init__(status.HTTP_403_FORBIDDEN, message, "ForbiddenError")

class LoanNotFoundError(LoanHubException):
    def __init__(self, message: str = "Loan not found"):
        super().__init__(status.HTTP_404_NOT_FOUND, message, "LoanNotFoundError")

class MaxPendingLoansError(LoanHubException):
    def __init__(self, message: str = "Max pending loans limit reached"):
        super().__init__(status.HTTP_422_UNPROCESSABLE_ENTITY, message, "MaxPendingLoansError")

class InvalidLoanReviewError(LoanHubException):
    def __init__(self, message: str = "Loan has already been reviewed"):
        super().__init__(status.HTTP_422_UNPROCESSABLE_ENTITY, message, "InvalidLoanReviewError")
