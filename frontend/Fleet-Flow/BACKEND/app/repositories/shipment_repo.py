from sqlalchemy.orm import Session
from app.models.shipment import Shipment
from app.schemas.shipment import ShipmentCreate

def get_all_by_warehouse(db: Session, warehouse_id: int) -> list[Shipment]:
    return db.query(Shipment).filter(
        Shipment.source_warehouse_id == warehouse_id
    ).all()

def get_all_by_driver(db: Session, driver_id: int) -> list[Shipment]:
    return db.query(Shipment).filter(Shipment.driver_id == driver_id).all()

def get_all(db: Session) -> list[Shipment]:
    return db.query(Shipment).all()

def get_by_id(db: Session, shipment_id: int) -> Shipment | None:
    return db.query(Shipment).filter(Shipment.id == shipment_id).first()

def create(db: Session, data: ShipmentCreate) -> Shipment:
    shipment = Shipment(
        source_warehouse_id=data.source_warehouse_id,
        destination_warehouse_id=data.destination_warehouse_id,
        driver_id=data.driver_id,
        status="Pending",
    )
    db.add(shipment)
    db.commit()
    db.refresh(shipment)
    return shipment

def update_status(db: Session, shipment: Shipment, status: str) -> Shipment:
    shipment.status = status
    db.commit()
    db.refresh(shipment)
    return shipment