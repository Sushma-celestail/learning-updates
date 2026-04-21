from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories import inventory_repo, warehouse_repo
from app.schemas.inventory import InventoryCreate, InventoryUpdate
from app.models.inventory import Inventory

def add_inventory(db: Session, data: InventoryCreate, warehouse_id: int) -> Inventory:
    wh = warehouse_repo.get_by_id(db, warehouse_id)
    if not wh:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return inventory_repo.create(db, data, warehouse_id)

def update_inventory(db: Session, item_id: int, data: InventoryUpdate, warehouse_id: int) -> Inventory:
    item = inventory_repo.get_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.warehouse_id != warehouse_id:
        raise HTTPException(status_code=403, detail="Not your warehouse")
    return inventory_repo.update(db, item, data)

def approve_inventory(db: Session, item_id: int, warehouse_id: int) -> Inventory:
    item = inventory_repo.get_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.warehouse_id != warehouse_id:
        raise HTTPException(status_code=403, detail="Not your warehouse")
    return inventory_repo.approve(db, item)

def list_inventory(db: Session, warehouse_id: int | None, is_admin: bool) -> list[Inventory]:
    if is_admin:
        return inventory_repo.get_all(db)
    return inventory_repo.get_all_by_warehouse(db, warehouse_id)