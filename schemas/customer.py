from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CustomerCreate(BaseModel):
    shop_name: str
    owner_name: str
    phone: str
    phone2: Optional[str] = None
    address: str
    pincode: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class CustomerUpdate(BaseModel):
    """All fields optional for partial update."""
    shop_name: Optional[str] = None
    owner_name: Optional[str] = None
    phone: Optional[str] = None
    phone2: Optional[str] = None
    address: Optional[str] = None
    pincode: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class CustomerResponse(CustomerCreate):
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
