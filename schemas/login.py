from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class LoginBase(BaseModel):
    email: EmailStr
    password: str


class LoginCreate(LoginBase):
    name: str
    role: str


class LoginResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    status: str
    last_login: Optional[datetime] = None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
