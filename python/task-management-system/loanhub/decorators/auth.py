from fastapi import Request
from jose import jwt, JWTError
from .custom_exceptions import ForbiddenError, InvalidCredentialsError
from ..models.enums import UserRole
import functools

SECRET_KEY = "loan-hub-secret-key" # In production, this would be in .env
ALGORITHM = "HS256"

def require_role(role: UserRole):
    """
    Decorator/Dependency to check if user has the required role. (Day 3 Requirement)
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # This is a simplified version. In a real FastAPI app, 
            # we would use Depends() in the router.
            # However, for the requirement of a decorator:
            request: Request = kwargs.get("request")
            if not request:
                # If not in kwargs, might be in args
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            
            if not request:
                raise ForbiddenError("Request context missing")

            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise InvalidCredentialsError("Not authenticated")

            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                user_role = payload.get("role")
                if user_role != role:
                    raise ForbiddenError(f"Required role: {role}")
            except JWTError:
                raise InvalidCredentialsError("Invalid token")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
