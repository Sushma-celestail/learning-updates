from pydantic import BaseModel

class ShipmentCreate(BaseModel):
    source_warehouse_id: int
    destination_warehouse_id: int
    driver_id: int

class ShipmentStatusUpdate(BaseModel):
    status: str  # "In Transit" | "Delivered"

class ShipmentResponse(BaseModel):
    id: int
    source_warehouse_id: int
    destination_warehouse_id: int
    driver_id: int
    status: str

    model_config = {"from_attributes": True}