from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class OrderTempBase(BaseModel):
    customer_id: Optional[int] = None
    trays_taken: int = 0
    trays_returned: int = 0
    bottles_holding: int = 0
    bottles_returned: int = 0
    bottles_damaged: int = 0
    payment_status: Optional[str] = None
    delivered_by: Optional[int] = None
    review_status: Optional[str] = None


class OrderTempCreate(OrderTempBase):
    pass


class OrderTempUpdate(BaseModel):
    customer_id: Optional[int] = None
    trays_taken: Optional[int] = None
    trays_returned: Optional[int] = None
    bottles_holding: Optional[int] = None
    bottles_returned: Optional[int] = None
    bottles_damaged: Optional[int] = None
    payment_status: Optional[str] = None
    delivered_by: Optional[int] = None
    review_status: Optional[str] = None


class OrderTempResponse(OrderTempBase):
    order_id: int
    created_at: datetime
    trays_holding: int = 0  # Read-only: derived as trays_taken - trays_returned

    model_config = {"from_attributes": True}
