from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, require_roles
from app.core.roles import Role
from app.schemas.shipment import ShipmentCreate, ShipmentStatusUpdate, ShipmentResponse
from app.services import shipment_service

router = APIRouter()

@router.get("/", response_model=list[ShipmentResponse])
def list_shipments(
    db: Session = Depends(get_db),
    user: dict = Depends(require_roles(Role.ADMIN, Role.MANAGER, Role.DRIVER, Role.CLERK)),
):
    return shipment_service.list_shipments(
        db, user["role"], user["user_id"], user.get("warehouse_id")
    )

@router.post("/", response_model=ShipmentResponse)
def create_shipment(
    data: ShipmentCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_roles(Role.CLERK)),
):
    return shipment_service.create_shipment(db, data)

@router.patch("/{shipment_id}/status", response_model=ShipmentResponse)
def update_status(
    shipment_id: int,
    data: ShipmentStatusUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(require_roles(Role.DRIVER)),
):
    return shipment_service.update_status(db, shipment_id, data, user["user_id"])