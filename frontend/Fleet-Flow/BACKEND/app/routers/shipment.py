from fastapi import APIRouter, Depends
from app.core.security import require_role

router = APIRouter(prefix="/shipments", tags=["🚚 Shipments"])

#  Clerk creates shipment
@router.post("/")
def create_shipment(user=Depends(require_role(["Inventory Clerk"]))):
    return {"message": "Shipment created"}


#  Driver updates status
@router.patch("/{id}/status")
def update_status(user=Depends(require_role(["Driver"]))):
    return {"message": "Status updated"}