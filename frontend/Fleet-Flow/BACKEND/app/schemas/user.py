from pydantic import BaseModel, EmailStr
from typing import Optional
from app.core.roles import Role

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Role
    warehouse_id: Optional[int] = None

class UserUpdate(BaseModel):
    name: str
    email: EmailStr
    password: Optional[str] = None
    role: Role
    warehouse_id: Optional[int] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    warehouse_id: Optional[int]

    model_config = {"from_attributes": True}