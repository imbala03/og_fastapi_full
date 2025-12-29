# models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Enum, func
from database import Base
import enum


class UserRole(str, enum.Enum):
    super_admin = "super_admin"
    admin = "admin"
    agent = "agent"
    customer = "customer"
    poweradmin = "poweradmin"  # Legacy role value


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)
    phone = Column(String(50), unique=True, index=True, nullable=True)
    password = Column(String(255), nullable=False)  # hashed
    role = Column(Enum(UserRole), default=UserRole.customer, nullable=False)
    status = Column(String(50), default="active", nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(
    ), onupdate=func.now(), nullable=False)
