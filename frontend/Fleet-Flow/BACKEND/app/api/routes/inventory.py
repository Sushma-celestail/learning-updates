from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, require_roles, get_current_user
from app.core.roles import Role
from app.schemas.inventory import InventoryCreate, InventoryUpdate, InventoryResponse
from app.services import inventory_service

router = APIRouter()

@router.get("/", response_model=list[InventoryResponse])
def list_inventory(
    db: Session = Depends(get_db),
    user: dict = Depends(require_roles(Role.ADMIN, Role.MANAGER, Role.CLERK)),
):
    is_admin = user["role"] == Role.ADMIN
    return inventory_service.list_inventory(db, user.get("warehouse_id"), is_admin)

@router.post("/", response_model=InventoryResponse)
def add_inventory(
    data: InventoryCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(require_roles(Role.CLERK)),
):
    return inventory_service.add_inventory(db, data, user["warehouse_id"])

@router.put("/{item_id}", response_model=InventoryResponse)
def update_inventory(
    item_id: int,
    data: InventoryUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(require_roles(Role.CLERK)),
):
    return inventory_service.update_inventory(db, item_id, data, user["warehouse_id"])

@router.patch("/approve/{item_id}", response_model=InventoryResponse)
def approve_inventory(
    item_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_roles(Role.MANAGER)),
):
    return inventory_service.approve_inventory(db, item_id, user["warehouse_id"])