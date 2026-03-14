from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, cast
from sqlalchemy.types import Date
from datetime import datetime, date

from database import get_db
from models.order import Order
from models.user import User, UserRole
from schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderSummaryResponse, AgentOrderSummaryResponse, OrderLatestHoldingsResponse, CustomerTotalHoldingsResponse

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse)
def create_order(data: OrderCreate, db: Session = Depends(get_db)):
    """Create a new order"""
    try:
        # Ensure customer exists if customer_id is provided
        if data.customer_id:
            from models.customer import Customer
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

        order = Order(**order_data)
        db.add(order)
        db.commit()
        db.refresh(order)
        return order
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error creating order: {str(e)}"
        )


@router.get("/", response_model=list[OrderResponse])
def list_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()


@router.get("/by-date-range", response_model=list[OrderResponse])
def get_orders_between_dates(
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    """
    Return orders whose created_at date is between start_date and end_date (inclusive).
    """
    if end_date < start_date:
        raise HTTPException(status_code=400, detail="end_date must be on or after start_date")
    orders = (
        db.query(Order)
        .filter(
            cast(Order.created_at, Date) >= start_date,
            cast(Order.created_at, Date) <= end_date,
        )
        .order_by(Order.created_at.asc())
        .all()
    )
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get a specific order by order_id"""
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get("/customer/{id}", response_model=list[OrderResponse])
def get_customer_orders(id: int, db: Session = Depends(get_db)):
    """
    Return all orders belonging to a specific customer.
    """
    orders = db.query(Order).filter(Order.customer_id == id).all()
    return orders


@router.get("/customer/{customer_id}/latest-holdings", response_model=OrderLatestHoldingsResponse)
def get_customer_latest_holdings(customer_id: int, db: Session = Depends(get_db)):
    """
    Return the latest order (by created_at) for the given customer with
    trays_holding, bottles_holding, and bottles_damaged.
    Use this for 'last delivery' only. For customer balance use total-holdings.
    """
    order = (
        db.query(Order)
        .filter(Order.customer_id == customer_id)
        .order_by(Order.created_at.desc())
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="No orders found for this customer")
    return order


@router.get("/customer/{customer_id}/total-holdings", response_model=CustomerTotalHoldingsResponse)
def get_customer_total_holdings(customer_id: int, db: Session = Depends(get_db)):
    """
    Return cumulative trays_holding, bottles_holding, bottles_damaged across
    ALL orders for this customer. Use for customer balance (no discrepancy).
    Example: two orders (1 tray, 1 bottle) and (2 trays, 2 bottles) with nothing
    returned -> total_trays_holding=3, total_bottles_holding=3.
    """
    from models.customer import Customer
    cust = db.query(Customer).filter(Customer.id == customer_id).first()
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found")

    result = (
        db.query(
            func.count(Order.order_id).label("total_orders"),
            func.coalesce(func.sum(Order.trays_holding), 0).label("total_trays_holding"),
            func.coalesce(func.sum(Order.bottles_holding), 0).label("total_bottles_holding"),
            func.coalesce(func.sum(Order.bottles_damaged), 0).label("total_bottles_damaged"),
        )
        .filter(Order.customer_id == customer_id)
        .first()
    )
    return CustomerTotalHoldingsResponse(
        customer_id=customer_id,
        total_orders=result.total_orders or 0,
        total_trays_holding=int(result.total_trays_holding) if result.total_trays_holding is not None else 0,
        total_bottles_holding=int(result.total_bottles_holding) if result.total_bottles_holding is not None else 0,
        total_bottles_damaged=int(result.total_bottles_damaged) if result.total_bottles_damaged is not None else 0,
    )


@router.get("/delivered-by/{delivered_by}", response_model=list[OrderResponse])
def get_orders_by_delivered_by(delivered_by: int, db: Session = Depends(get_db)):
    """
    Return all orders delivered by a specific user.
    """
    orders = db.query(Order).filter(Order.delivered_by == delivered_by).all()
    return orders


@router.get("/agent/{user_id}/summary", response_model=AgentOrderSummaryResponse)
def get_agent_order_summary(user_id: int, db: Session = Depends(get_db)):
    """
    Get aggregated order statistics for a specific agent.
    Validates that the user exists and has role "agent".
    Returns sums of all order fields where delivered_by matches the user_id.
    """
    # Validate user exists and is an agent
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role != UserRole.agent:
        raise HTTPException(
            status_code=400,
            detail=f"User with ID {user_id} is not an agent. Current role: {user.role.value}"
        )
    
    # Filter orders by delivered_by
    orders_query = db.query(Order).filter(Order.delivered_by == user_id)
    
    # Aggregate the data
    result = orders_query.with_entities(
        func.count(Order.order_id).label('total_orders'),
        func.coalesce(func.sum(Order.trays_holding), 0).label('total_trays_outside'),
        func.coalesce(func.sum(Order.trays_returned), 0).label('total_trays_received'),
        func.coalesce(func.sum(Order.bottles_holding), 0).label('total_bottles_delivered'),
        func.coalesce(func.sum(Order.bottles_returned), 0).label('total_bottles_returned'),
        func.coalesce(func.sum(Order.bottles_damaged), 0).label('total_bottles_damaged')
    ).first()
    
    if not result or result.total_orders == 0:
        # Return zeros if no orders found for the agent
        return AgentOrderSummaryResponse(
            total_orders=0,
            total_trays_outside=0,
            total_trays_received=0,
            total_bottles_delivered=0,
            total_bottles_returned=0,
            total_bottles_damaged=0
        )
    
    return AgentOrderSummaryResponse(
        total_orders=result.total_orders or 0,
        total_trays_outside=int(result.total_trays_outside) if result.total_trays_outside else 0,
        total_trays_received=int(result.total_trays_received) if result.total_trays_received else 0,
        total_bottles_delivered=int(result.total_bottles_delivered) if result.total_bottles_delivered else 0,
        total_bottles_returned=int(result.total_bottles_returned) if result.total_bottles_returned else 0,
        total_bottles_damaged=int(result.total_bottles_damaged) if result.total_bottles_damaged else 0
    )


@router.get("/summary/by-date", response_model=OrderSummaryResponse)
def get_orders_summary_by_date(
    timestamp: datetime = Query(..., description="Timestamp/date to filter orders (format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"),
    db: Session = Depends(get_db)
):
    """
    Get aggregated order statistics for a specific date.
    Returns total orders count and sums of trays and bottles fields.
    """
    # Extract date from timestamp
    target_date = timestamp.date()
    
    # Filter orders by date (compare only the date part, ignoring time)
    orders_query = db.query(Order).filter(
        cast(Order.created_at, Date) == target_date
    )
    
    # Aggregate the data
    result = orders_query.with_entities(
        func.count(Order.order_id).label('total_orders'),
        func.coalesce(func.sum(Order.trays_holding), 0).label('total_trays_outside'),
        func.coalesce(func.sum(Order.trays_returned), 0).label('trays_received_back'),
        func.coalesce(func.sum(Order.bottles_holding), 0).label('total_bottles_outside'),
        func.coalesce(func.sum(Order.bottles_returned), 0).label('bottles_returned'),
        func.coalesce(func.sum(Order.bottles_damaged), 0).label('bottles_damaged')
    ).first()
    
    if not result or result.total_orders == 0:
        # Return zeros if no orders found for the date
        return OrderSummaryResponse(
            total_orders=0,
            total_trays_outside=0,
            trays_received_back=0,
            total_bottles_outside=0,
            bottles_returned=0,
            bottles_damaged=0
        )
    
    return OrderSummaryResponse(
        total_orders=result.total_orders or 0,
        total_trays_outside=int(result.total_trays_outside) if result.total_trays_outside else 0,
        trays_received_back=int(result.trays_received_back) if result.trays_received_back else 0,
        total_bottles_outside=int(result.total_bottles_outside) if result.total_bottles_outside else 0,
        bottles_returned=int(result.bottles_returned) if result.bottles_returned else 0,
        bottles_damaged=int(result.bottles_damaged) if result.bottles_damaged else 0
    )


@router.put("/{order_id}", response_model=OrderResponse)
def update_order(order_id: int, data: OrderUpdate, db: Session = Depends(get_db)):
    """Update an existing order"""
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Update fields (only provided fields)
    update_data = data.dict(exclude_unset=True)

    # Recompute trays_holding and bottles_holding (Model A)
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
def delete_order(order_id: int, db: Session = Depends(get_db)):
    """Delete an order"""
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    db.delete(order)
    db.commit()
    return {"message": "Order deleted successfully"}