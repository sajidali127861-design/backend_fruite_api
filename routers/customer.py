from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.user import UserResponse
from utils.dependencies import get_current_admin


router = APIRouter(
    prefix="/customers",
    tags=["Customers"]
)


@router.get("/", response_model=list[UserResponse])
def get_customers(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    customers = db.query(User).filter(
        User.role == "customer"
    ).all()

    return customers


@router.get("/{customer_id}", response_model=UserResponse)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    customer = db.query(User).filter(
        User.id == customer_id,
        User.role == "customer"
    ).first()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return customer