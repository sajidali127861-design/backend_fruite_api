from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.cart import Cart, CartItem
from models.product import ProductVariant
from models.user import User
from schemas.cart import CartItemCreate,CartItemUpdate
from utils.dependencies import get_current_user


router = APIRouter(
    prefix="/cart",
    tags=["Cart"]
)


@router.post("/items")
def add_to_cart(
    item: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check product variant
    variant = db.query(ProductVariant).filter(
        ProductVariant.id == item.product_variant_id
    ).first()

    if not variant:
        raise HTTPException(
            status_code=404,
            detail="Product variant not found"
        )

    # Check quantity
    if item.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than 0"
        )

    # Find user's cart
    cart = db.query(Cart).filter(
        Cart.user_id == current_user.id
    ).first()

    # Create cart if user doesn't have one
    if not cart:
        cart = Cart(
            user_id=current_user.id
        )

        db.add(cart)
        db.commit()
        db.refresh(cart)

    # Check whether this variant is already in cart
    existing_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_variant_id == item.product_variant_id
    ).first()

    if existing_item:
        existing_item.quantity += item.quantity
    else:
        new_item = CartItem(
            cart_id=cart.id,
            product_variant_id=item.product_variant_id,
            quantity=item.quantity
        )

        db.add(new_item)

    db.commit()

    return {
        "message": "Product added to cart"
    }

@router.get("/")
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart = db.query(Cart).filter(
        Cart.user_id == current_user.id
    ).first()

    if not cart:
        return {
            "items": [],
            "total": 0
        }

    items = []
    cart_total = 0

    for item in cart.items:
        variant = item.product_variant
        product = variant.product

        item_total = variant.price * item.quantity
        cart_total += item_total

        items.append({
            "cart_item_id": item.id,
            "product_id": product.id,
            "product_name": product.name,
            "image_url": product.image_url,
            "weight": variant.weight,
            "price": variant.price,
            "quantity": item.quantity,
            "item_total": item_total
        })

    return {
        "items": items,
        "total": cart_total
    }
@router.put("/items/{item_id}")
def update_cart_item(
    item_id: int,
    item: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if item.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than 0"
        )

    cart = db.query(Cart).filter(
        Cart.user_id == current_user.id
    ).first()

    if not cart:
        raise HTTPException(
            status_code=404,
            detail="Cart not found"
        )

    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id
    ).first()

    if not cart_item:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found"
        )

    cart_item.quantity = item.quantity

    db.commit()

    return {
        "message": "Cart item updated successfully"
    }
@router.delete("/items/{item_id}")
def remove_cart_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    cart = db.query(Cart).filter(
        Cart.user_id == current_user.id
    ).first()

    if not cart:
        raise HTTPException(
            status_code=404,
            detail="Cart not found"
        )

    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id
    ).first()

    if not cart_item:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found"
        )

    db.delete(cart_item)
    db.commit()

    return {
        "message": "Item removed from cart"
    }