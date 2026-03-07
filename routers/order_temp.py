from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.order_temp import OrderTemp
from schemas.order_temp import OrderTempCreate, OrderTempUpdate, OrderTempResponse

router = APIRouter(
    prefix="/order-temp",
    tags=["Order Temp"]
)


@router.post("/", response_model=OrderTempResponse)
def create_temp_order(data: OrderTempCreate, db: Session = Depends(get_db)):
    # Ensure customer exists if customer_id is provided
    if data.customer_id:
        from models.customer import Customer
        cust = db.query(Customer).filter(Customer.id == data.customer_id).first()
        if not cust:
            raise HTTPException(status_code=404, detail="Customer not found")

    # Derive trays_holding using Model A for temp orders as well
    if data.trays_taken < 0 or data.trays_returned < 0:
        raise HTTPException(status_code=400, detail="Tray counts cannot be negative")
    if data.trays_returned > data.trays_taken:
        raise HTTPException(status_code=400, detail="Trays returned cannot exceed trays taken")

    order_data = data.dict()
    order_data["trays_holding"] = order_data["trays_taken"] - order_data["trays_returned"]

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

    if trays_taken < 0 or trays_returned < 0:
        raise HTTPException(status_code=400, detail="Tray counts cannot be negative")
    if trays_returned > trays_taken:
        raise HTTPException(status_code=400, detail="Trays returned cannot exceed trays taken")

    update_data["trays_holding"] = trays_taken - trays_returned

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
