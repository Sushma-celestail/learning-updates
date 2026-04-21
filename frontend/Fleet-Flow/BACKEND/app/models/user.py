from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True, nullable=False)
    password = Column(String)
    role = Column(String)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=True)
    otp_code = Column(String, nullable=True)
    otp_expires_at = Column(DateTime, nullable=True)

    warehouse = relationship("Warehouse", back_populates="users")
    shipments = relationship("Shipment", back_populates="driver", foreign_keys="Shipment.driver_id")