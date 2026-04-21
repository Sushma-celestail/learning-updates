from sqlalchemy.orm import Session
from app.models.inventory import Inventory
from app.schemas.inventory import InventoryCreate, InventoryUpdate

def get_all_by_warehouse(db: Session, warehouse_id: int) -> list[Inventory]:
    return db.query(Inventory).filter(Inventory.warehouse_id == warehouse_id).all()

def get_all(db: Session) -> list[Inventory]:
    return db.query(Inventory).all()

def get_by_id(db: Session, item_id: int) -> Inventory | None:
    return db.query(Inventory).filter(Inventory.id == item_id).first()

def create(db: Session, data: InventoryCreate, warehouse_id: int) -> Inventory:
    item = Inventory(
        product_name=data.product_name,
        quantity=data.quantity,
        warehouse_id=warehouse_id,
        is_approved=False,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

def update(db: Session, item: Inventory, data: InventoryUpdate) -> Inventory:
    if data.product_name is not None:
        item.product_name = data.product_name
    if data.quantity is not None:
        item.quantity = data.quantity
    db.commit()
    db.refresh(item)
    return item

def approve(db: Session, item: Inventory) -> Inventory:
    item.is_approved = True
    db.commit()
    db.refresh(item)
    return item