from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models.customer import Customer
from models.order_temp import OrderTemp
from schemas.order_temp import OrderTempCreate, OrderTempUpdate, OrderTempResponse
from schemas.order import CustomerTotalHoldingsResponse

router = APIRouter(
    prefix="/order-temp",
    tags=["Order Temp"]
)


@router.post("/", response_model=OrderTempResponse)
def create_temp_order(data: OrderTempCreate, db: Session = Depends(get_db)):
    # Ensure customer exists if customer_id is provided
    if data.customer_id:
        cust = db.query(Customer).filter(Customer.id == data.customer_id).first()
        if not cust:
            raise HTTPException(status_code=404, detail="Customer not found")

    # Derive trays_holding and bottles_holding (Model A)
    if data.trays_taken < 0 or data.trays_returned < 0:
        raise HTTPException(status_code=400, detail="Tray counts cannot be negative")
    if data.trays_returned > data.trays_taken:
        raise HTTPException(status_code=400, detail="Trays returned cannot exceed trays taken")
    if data.bottles_taken < 0 or data.bottles_returned < 0:
        raise HTTPException(status_code=400, detail="Bottle counts cannot be negative")
    if data.bottles_returned > data.bottles_taken:
        raise HTTPException(status_code=400, detail="Bottles returned cannot exceed bottles taken")

    order_data = data.dict()
    order_data["trays_holding"] = order_data["trays_taken"] - order_data["trays_returned"]
    order_data["bottles_holding"] = order_data["bottles_taken"] - order_data["bottles_returned"]

    order = OrderTemp(**order_data)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.get("/", response_model=list[OrderTempResponse])
def list_temp_orders(db: Session = Depends(get_db)):
    return db.query(OrderTemp).all()


@router.get("/{order_id}", response_model=OrderTempResponse)
def get_temp_order(order_id: int, db: Session = Depends(get_db)):
    """Get a specific temp order by order_id"""
    order = db.query(OrderTemp).filter(OrderTemp.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get("/customer/{id}", response_model=list[OrderTempResponse])
def get_customer_temp_orders(id: int, db: Session = Depends(get_db)):
    """
    Return all temp orders belonging to a specific customer.
    """
    orders = db.query(OrderTemp).filter(OrderTemp.customer_id == id).all()
    return orders


@router.get("/customer/{customer_id}/total-holdings", response_model=CustomerTotalHoldingsResponse)
def get_customer_temp_total_holdings(customer_id: int, db: Session = Depends(get_db)):
    """
    Cumulative trays_holding, bottles_holding, bottles_damaged across ALL order_temp
    rows for this customer. Use this for customer balance when using order-temp
    (e.g. after submit, show total_trays_holding / total_bottles_holding = 3,3 not 2,2).
    """
    cust = db.query(Customer).filter(Customer.id == customer_id).first()
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found")

    result = (
        db.query(
            func.count(OrderTemp.order_id).label("total_orders"),
            func.coalesce(func.sum(OrderTemp.trays_holding), 0).label("total_trays_holding"),
            func.coalesce(func.sum(OrderTemp.bottles_holding), 0).label("total_bottles_holding"),
            func.coalesce(func.sum(OrderTemp.bottles_damaged), 0).label("total_bottles_damaged"),
        )
        .filter(OrderTemp.customer_id == customer_id)
        .first()
    )
    return CustomerTotalHoldingsResponse(
        customer_id=customer_id,
        total_orders=result.total_orders or 0,
        total_trays_holding=int(result.total_trays_holding) if result.total_trays_holding is not None else 0,
        total_bottles_holding=int(result.total_bottles_holding) if result.total_bottles_holding is not None else 0,
        total_bottles_damaged=int(result.total_bottles_damaged) if result.total_bottles_damaged is not None else 0,
    )


@router.get("/delivered-by/{delivered_by}", response_model=list[OrderTempResponse])
def get_temp_orders_by_delivered_by(delivered_by: int, db: Session = Depends(get_db)):
    """
    Return all temp orders delivered by a specific user.
    """
    orders = db.query(OrderTemp).filter(OrderTemp.delivered_by == delivered_by).all()
    return orders


@router.put("/{order_id}", response_model=OrderTempResponse)
def update_temp_order(order_id: int, data: OrderTempUpdate, db: Session = Depends(get_db)):
    """Update an existing temp order"""
    order = db.query(OrderTemp).filter(OrderTemp.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Update fields (only provided fields)
    update_data = data.dict(exclude_unset=True)

    trays_taken = update_data.get("trays_taken", order.trays_taken)
    trays_returned = update_data.get("trays_returned", order.trays_returned)
    bottles_taken = update_data.get("bottles_taken", order.bottles_taken)
    bottles_returned = update_data.get("bottles_returned", order.bottles_returned)

    if trays_taken < 0 or trays_returned < 0:
        raise HTTPException(status_code=400, detail="Tray counts cannot be negative")
    if trays_returned > trays_taken:
        raise HTTPException(status_code=400, detail="Trays returned cannot exceed trays taken")
    if bottles_taken < 0 or bottles_returned < 0:
        raise HTTPException(status_code=400, detail="Bottle counts cannot be negative")
    if bottles_returned > bottles_taken:
        raise HTTPException(status_code=400, detail="Bottles returned cannot exceed bottles taken")

    update_data["trays_holding"] = trays_taken - trays_returned
    update_data["bottles_holding"] = bottles_taken - bottles_returned

    for key, value in update_data.items():
        setattr(order, key, value)
    
    db.commit()
    db.refresh(order)
    return order


@router.delete("/{order_id}")
def delete_temp_order(order_id: int, db: Session = Depends(get_db)):
    """Delete a temp order"""
    order = db.query(OrderTemp).filter(OrderTemp.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    db.delete(order)
    db.commit()
    return {"message": "Order deleted successfully"}
