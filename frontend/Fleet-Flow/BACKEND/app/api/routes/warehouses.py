from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, require_roles
from app.core.roles import Role
from app.schemas.warehouse import WarehouseCreate, WarehouseResponse
from app.services import warehouse_service

router = APIRouter()
admin_only = require_roles(Role.ADMIN)

@router.post("/", response_model=WarehouseResponse)
def create_warehouse(
    data: WarehouseCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(admin_only),
):
    return warehouse_service.create_warehouse(db, data)

@router.get("/", response_model=list[WarehouseResponse])
def list_warehouses(
    db: Session = Depends(get_db),
    _: dict = Depends(require_roles(Role.ADMIN, Role.MANAGER, Role.CLERK)),
):
    return warehouse_service.list_warehouses(db)

@router.put("/{warehouse_id}", response_model=WarehouseResponse)
def update_warehouse(
    warehouse_id: int,
    data: WarehouseCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(admin_only),
):
    return warehouse_service.update_warehouse(db, warehouse_id, data)

@router.delete("/{warehouse_id}", status_code=204)
def delete_warehouse(
    warehouse_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(admin_only),
):
    warehouse_service.delete_warehouse(db, warehouse_id)
    return None