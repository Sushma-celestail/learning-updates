from sqlalchemy.orm import Session
from app.models.warehouse import Warehouse
from app.schemas.warehouse import WarehouseCreate

def get_all(db: Session) -> list[Warehouse]:
    return db.query(Warehouse).all()

def get_by_id(db: Session, warehouse_id: int) -> Warehouse | None:
    return db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()

def create(db: Session, data: WarehouseCreate) -> Warehouse:
    wh = Warehouse(name=data.name, location=data.location)
    db.add(wh)
    db.commit()
    db.refresh(wh)
    return wh

def update(db: Session, db_warehouse: Warehouse, data: WarehouseCreate) -> Warehouse:
    db_warehouse.name = data.name
    db_warehouse.location = data.location
    db.commit()
    db.refresh(db_warehouse)
    return db_warehouse

def delete(db: Session, db_warehouse: Warehouse) -> None:
    db.delete(db_warehouse)
    db.commit()