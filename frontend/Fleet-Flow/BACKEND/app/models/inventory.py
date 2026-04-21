from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Inventory(Base):
    __tablename__ = "inventory"

    id           = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, nullable=False)
    quantity     = Column(Integer, default=0)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    is_approved  = Column(Boolean, default=False)

    warehouse = relationship("Warehouse", back_populates="inventory")