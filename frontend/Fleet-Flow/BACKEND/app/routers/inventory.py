from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import require_role
from app.db import get_db
from app.services.inventory_service import (
    fetch_inventory,
    add_inventory,
    approve_inventory_service
)
from app.schemas.inventory_schema import InventoryCreate

router = APIRouter(prefix="/inventory", tags=["📦 Inventory"])


# 👑 Admin + Manager + Clerk
@router.get("/")
def get_inventory(
    user=Depends(require_role(["Admin", "Warehouse Manager", "Inventory Clerk"])),
    db: Session = Depends(get_db)
):
    return fetch_inventory(db, user)


# 📋 Clerk only
@router.post("/")
def create_inventory(
    data: InventoryCreate,
    user=Depends(require_role(["Inventory Clerk"])),
    db: Session = Depends(get_db)
):
    return add_inventory(db, data)


# 🏭 Manager approval (NOW FULLY WORKING)
@router.patch("/approve/{inventory_id}")
def approve_inventory(
    inventory_id: int,
    user=Depends(require_role(["Warehouse Manager"])),
    db: Session = Depends(get_db)
):
    item = approve_inventory_service(db, inventory_id)

    if not item:
        raise HTTPException(status_code=404, detail="Inventory not found")

    return {
        "message": "Inventory approved",
        "inventory_id": item.id,
        "is_approved": item.is_approved
    }