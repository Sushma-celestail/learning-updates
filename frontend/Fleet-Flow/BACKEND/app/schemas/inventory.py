from pydantic import BaseModel
from typing import Optional

class InventoryCreate(BaseModel):
    product_name: str
    quantity: int

class InventoryUpdate(BaseModel):
    product_name: Optional[str] = None
    quantity: Optional[int] = None

class InventoryResponse(BaseModel):
    id: int
    product_name: str
    quantity: int
    warehouse_id: int
    is_approved: bool

    model_config = {"from_attributes": True}