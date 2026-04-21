from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Shipment(Base):
    __tablename__ = "shipments"

    id                       = Column(Integer, primary_key=True, index=True)
    source_warehouse_id      = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    destination_warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    driver_id                = Column(Integer, ForeignKey("users.id"), nullable=False)
    status                   = Column(String, default="Pending")

    driver = relationship("User", back_populates="shipments", foreign_keys=[driver_id])
    source_warehouse = relationship("Warehouse", back_populates="shipments_source", foreign_keys=[source_warehouse_id])
    destination_warehouse = relationship("Warehouse", back_populates="shipments_destination", foreign_keys=[destination_warehouse_id])