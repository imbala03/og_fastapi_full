from sqlalchemy import Column, Integer, String, Float, DateTime, func
from database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    shop_name = Column(String, nullable=False)
    owner_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    phone2 = Column(String, nullable=True)  # NEW
    address = Column(String, nullable=False)
    pincode = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)   # NEW
    longitude = Column(Float, nullable=True)  # NEW
    created_at = Column(DateTime(timezone=True), server_default=func.now())
 