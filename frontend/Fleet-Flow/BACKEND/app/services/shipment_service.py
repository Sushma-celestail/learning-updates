from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories import shipment_repo, user_repo, warehouse_repo
from app.schemas.shipment import ShipmentCreate, ShipmentStatusUpdate
from app.models.shipment import Shipment
from app.core.roles import Role

VALID_TRANSITIONS = {
    "Pending": ["In Transit"],
    "In Transit": ["Delivered"],
    "Delivered": [],
}

def create_shipment(db: Session, data: ShipmentCreate) -> Shipment:
    if not warehouse_repo.get_by_id(db, data.source_warehouse_id):
        raise HTTPException(status_code=404, detail="Source warehouse not found")
    if not warehouse_repo.get_by_id(db, data.destination_warehouse_id):
        raise HTTPException(status_code=404, detail="Destination warehouse not found")
    driver = user_repo.get_by_id(db, data.driver_id)
    if not driver or driver.role != Role.DRIVER:
        raise HTTPException(status_code=400, detail="Invalid driver")
    return shipment_repo.create(db, data)

def update_status(db: Session, shipment_id: int, data: ShipmentStatusUpdate, driver_id: int) -> Shipment:
    shipment = shipment_repo.get_by_id(db, shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    if shipment.driver_id != driver_id:
        raise HTTPException(status_code=403, detail="Not your shipment")
    if data.status not in VALID_TRANSITIONS.get(shipment.status, []):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot transition from {shipment.status} to {data.status}",
        )
    return shipment_repo.update_status(db, shipment, data.status)

def list_shipments(db: Session, role: str, user_id: int, warehouse_id: int | None) -> list[Shipment]:
    if role == Role.ADMIN:
        return shipment_repo.get_all(db)
    if role in [Role.MANAGER, Role.CLERK]:
        return shipment_repo.get_all_by_warehouse(db, warehouse_id)
    if role == Role.DRIVER:
        return shipment_repo.get_all_by_driver(db, user_id)
    return []