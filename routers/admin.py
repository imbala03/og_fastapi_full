from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models.customer import Customer
from models.order import Order

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])


@router.get("/metrics")
def metrics(db: Session = Depends(get_db)):
    """
    Get admin dashboard metrics.
    Returns total counts of customers and orders.
    """
    try:
        total_customers = db.query(Customer).count()
        total_orders = db.query(Order).count()
        
        # Calculate orders by payment status
        orders_by_payment = db.query(
            Order.payment_status,
            func.count(Order.order_id).label('count')
        ).group_by(Order.payment_status).all()
        
        payment_status_summary = {
            status: count for status, count in orders_by_payment if status
        }
        
        return {
            "total_customers": total_customers,
            "total_orders": total_orders,
            "payment_status_summary": payment_status_summary
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching metrics: {str(e)}"
        )
