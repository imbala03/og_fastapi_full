from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum
from datetime import datetime


class UserRole(str, Enum):
    super_admin = "super_admin"
    admin = "admin"
    agent = "agent"
    customer = "customer"
    poweradmin = "poweradmin"  # Legacy role value


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str = Field(..., min_length=6)
    role: Optional[UserRole] = UserRole.customer


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6)
    role: Optional[UserRole] = None
    status: Optional[str] = None


class UserOut(BaseModel):
    id: int
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: UserRole
    status: str
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class LoginRequest(BaseModel):
    identifier: str = Field(..., description="email or phone")
    password: str


class UserPasswordResponse(BaseModel):
    id: int
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password_hash: str = Field(..., description="Bcrypt hashed password (cannot be decrypted)")
    note: str = "Passwords are hashed using bcrypt and cannot be decrypted. This is the stored hash."
    
    model_config = {
        "from_attributes": True
    }
