from fastapi import APIRouter, Depends
from app.core.security import require_role

router = APIRouter(prefix="/users", tags=["👑 Admin"])

@router.post("/")
def create_user(user=Depends(require_role(["Admin"]))):
    return {"message": "User created"}

@router.get("/")
def get_users(user=Depends(require_role(["Admin"]))):
    return {"message": "All users"}