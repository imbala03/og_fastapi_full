from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from database import Base


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    trays_holding = Column(Integer, default=0, nullable=False)
    trays_returned = Column(Integer, default=0, nullable=False)
    bottles_holding = Column(Integer, default=0, nullable=False)
    bottles_returned = Column(Integer, default=0, nullable=False)
    bottles_damaged = Column(Integer, default=0, nullable=False)
    payment_status = Column(String(50), nullable=True)
    delivered_by = Column(Integer, nullable=True)
    review_status = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
