from sqlalchemy.orm import Session
from app.repositories import warehouse_repo
from app.schemas.warehouse import WarehouseCreate
from app.models.warehouse import Warehouse

def create_warehouse(db: Session, data: WarehouseCreate) -> Warehouse:
    if not data.name.strip() or not data.location.strip():
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Name and location are required")
    return warehouse_repo.create(db, data)

def list_warehouses(db: Session) -> list[Warehouse]:
    return warehouse_repo.get_all(db)

def update_warehouse(db: Session, warehouse_id: int, data: WarehouseCreate) -> Warehouse:
    if not data.name.strip() or not data.location.strip():
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Name and location are required")
    db_warehouse = warehouse_repo.get_by_id(db, warehouse_id)
    if not db_warehouse:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return warehouse_repo.update(db, db_warehouse, data)

def delete_warehouse(db: Session, warehouse_id: int) -> None:
    db_warehouse = warehouse_repo.get_by_id(db, warehouse_id)
    if not db_warehouse:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Warehouse not found")
    warehouse_repo.delete(db, db_warehouse)