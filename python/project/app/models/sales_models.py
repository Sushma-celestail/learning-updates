from sqlalchemy import Column, Integer, String, Date, ForeignKey
from app.db.sales_db import BaseSales

class Customer(BaseSales):
    __tablename__ = "customers"
    __table_args__ = {"schema": "SALES"}
    customer_id = Column(Integer, primary_key=True)
    created_date = Column(Date)
    customer_name = Column(String)

class Order(BaseSales):
    __tablename__ = "orders"
    __table_args__ = {"schema": "SALES"}
    order_id = Column(Integer, primary_key=True)
    order_date = Column(Date)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))

class Payment(BaseSales):
    __tablename__ = "payments"
    __table_args__ = {"schema": "SALES"}
    payment_id = Column(Integer, primary_key=True)
    payment_date = Column(Date)
    order_id = Column(Integer, ForeignKey("orders.order_id"))