from fastapi import Request, Depends
from models.enums import UserRole
from exceptions.custom_exceptions import ForbiddenError
import functools

def require_role(required_role: UserRole):
    """
    FastAPI dependency to enforce role-based access control.
    Can also be used as a decorator if needed, but dependency injection is preferred in FastAPI.
    """
    def role_checker(request: Request):
        # In a real app, user would be retrieved from a token/session
        # For this project, we assume the user object is attached to the request state
        # by an authentication middleware or dependency.
        user = getattr(request.state, "user", None)
        if not user or user.role != required_role:
            raise ForbiddenError(f"Operation restricted to {required_role} only")
        return user
    return role_checker

# Example of a decorator version for service layer if required
def role_required(required_role: UserRole):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Logic to check role from args/kwargs or context
            pass
        return wrapper
    return decorator
