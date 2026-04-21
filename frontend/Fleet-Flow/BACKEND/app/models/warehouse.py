from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base

class Warehouse(Base):
    __tablename__ = "warehouses"

    id       = Column(Integer, primary_key=True, index=True)
    name     = Column(String, nullable=False)
    location = Column(String, nullable=False)

    users     = relationship("User", back_populates="warehouse")
    inventory = relationship("Inventory", back_populates="warehouse")
    shipments_source = relationship("Shipment", back_populates="source_warehouse", foreign_keys="Shipment.source_warehouse_id")
    shipments_destination = relationship("Shipment", back_populates="destination_warehouse", foreign_keys="Shipment.destination_warehouse_id")