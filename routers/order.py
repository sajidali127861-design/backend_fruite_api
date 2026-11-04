from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.order import Order, OrderItem
from models.cart import Cart
from models.user import User

from schemas.order import (
    CheckoutRequest,
    OrderResponse,
    OrderStatusUpdate
)

from utils.dependencies import (
    get_current_user,
    get_current_admin
)
router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)
@router.post("/checkout")
def checkout(
    checkout_data: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Find user's cart
    cart = db.query(Cart).filter(
        Cart.user_id == current_user.id
    ).first()

    if not cart or not cart.items:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty"
        )

    # Calculate total
    total_amount = 0

    for cart_item in cart.items:
        variant = cart_item.product_variant

        # Check stock
        if variant.stock < cart_item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for {variant.product.name}"
            )

        total_amount += (
            variant.price * cart_item.quantity
        )

    # Create order
    new_order = Order(
        user_id=current_user.id,
        status="pending",
        total_amount=total_amount,
        shipping_name=checkout_data.shipping_name,
        shipping_phone=checkout_data.shipping_phone,
        shipping_address=checkout_data.shipping_address
    )

    db.add(new_order)
    db.flush()

    # Create order items and reduce stock
    for cart_item in cart.items:

        variant = cart_item.product_variant
        product = variant.product

        item_total = (
            variant.price * cart_item.quantity
        )

        order_item = OrderItem(
            order_id=new_order.id,
            product_variant_id=variant.id,
            product_name=product.name,
            weight=variant.weight,
            price=variant.price,
            quantity=cart_item.quantity,
            item_total=item_total
        )

        db.add(order_item)

        # Reduce stock
        variant.stock -= cart_item.quantity

    # Remove cart items
    for cart_item in cart.items:
        db.delete(cart_item)

    db.commit()
    db.refresh(new_order)

    return {
        "message": "Order placed successfully",
        "order_id": new_order.id,
        "total_amount": new_order.total_amount,
        "status": new_order.status
    }
@router.get("/my-orders", response_model=list[OrderResponse])
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    orders = db.query(Order).filter(
        Order.user_id == current_user.id
    ).order_by(
        Order.created_at.desc()
    ).all()

    return orders
@router.get("/{order_id}", response_model=OrderResponse)
def get_my_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return order
@router.get("/admin/all", response_model=list[OrderResponse])
def get_all_orders(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    orders = db.query(Order).order_by(
        Order.created_at.desc()
    ).all()

    return orders

@router.put("/admin/{order_id}/status")
def update_order_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    allowed_transitions = {
        "pending": ["confirmed", "cancelled"],
        "confirmed": ["shipped", "cancelled"],
        "shipped": ["delivered"],
        "delivered": [],
        "cancelled": []
    }

    current_status = order.status
    new_status = status_data.status

    # Check if the new status is valid
    if new_status not in allowed_transitions:
        raise HTTPException(
            status_code=400,
            detail="Invalid order status"
        )

    # Check if this status change is allowed
    if new_status not in allowed_transitions[current_status]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot change order status from "
                   f"{current_status} to {new_status}"
        )

    # Update status
    order.status = new_status

    db.commit()
    db.refresh(order)

    return {
        "message": "Order status updated successfully",
        "order_id": order.id,
        "status": order.status
    }