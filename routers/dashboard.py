from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models.user import User
from models.category import Category
from models.product import Product
from models.order import Order
from utils.dependencies import get_current_admin


router = APIRouter(
    prefix="/admin/dashboard",
    tags=["Admin Dashboard"]
)


@router.get("/")
def get_dashboard(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    total_customers = db.query(User).filter(
        User.role == "customer"
    ).count()

    total_categories = db.query(Category).count()

    total_products = db.query(Product).count()

    total_orders = db.query(Order).count()

    total_sales = db.query(
        func.coalesce(func.sum(Order.total_amount), 0)
    ).filter(
        Order.status != "cancelled"
    ).scalar()

    pending_orders = db.query(Order).filter(
        Order.status == "pending"
    ).count()

    return {
        "total_customers": total_customers,
        "total_categories": total_categories,
        "total_products": total_products,
        "total_orders": total_orders,
        "total_sales": total_sales,
        "pending_orders": pending_orders
    }