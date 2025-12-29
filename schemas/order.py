from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class OrderBase(BaseModel):
    customer_id: Optional[int] = None
    trays_holding: int = 0
    trays_returned: int = 0
    bottles_holding: int = 0
    bottles_returned: int = 0
    bottles_damaged: int = 0
    payment_status: Optional[str] = None
    delivered_by: Optional[int] = None
    review_status: Optional[str] = None


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    customer_id: Optional[int] = None
    trays_holding: Optional[int] = None
    trays_returned: Optional[int] = None
    bottles_holding: Optional[int] = None
    bottles_returned: Optional[int] = None
    bottles_damaged: Optional[int] = None
    payment_status: Optional[str] = None
    delivered_by: Optional[int] = None
    review_status: Optional[str] = None


class OrderResponse(OrderBase):
    order_id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class OrderSummaryResponse(BaseModel):
    total_orders: int
    total_trays_outside: int
    trays_received_back: int
    total_bottles_outside: int
    bottles_returned: int
    bottles_damaged: int


class AgentOrderSummaryResponse(BaseModel):
    total_orders: int
    total_trays_outside: int
    total_trays_received: int
    total_bottles_delivered: int
    total_bottles_returned: int
    total_bottles_damaged: int
