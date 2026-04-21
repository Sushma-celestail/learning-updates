from fastapi import APIRouter
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["🔐 Auth"])

@router.post("/login")
def login():
    # Dummy user (replace with DB check)
    user = {"user_id": 1, "role": "Admin", "warehouse_id": 1}
    token = create_access_token(user)
    return {"access_token": token}