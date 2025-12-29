from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CustomerCreate(BaseModel):
    shop_name: str
    owner_name: str
    phone: str
    phone2: Optional[str] = None         # NEW
    address: str
    pincode: Optional[str] = None
    latitude: Optional[float] = None     # NEW
    longitude: Optional[float] = None    # NEW


class CustomerResponse(CustomerCreate):
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
