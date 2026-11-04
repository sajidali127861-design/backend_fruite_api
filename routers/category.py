from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.category import Category
from models.product import Product
from models.order import OrderItem
from models.cart import CartItem
from models.user import User
from schemas.category import CategoryCreate, CategoryResponse
from utils.dependencies import get_current_admin


router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)

# ------------------------------------------------------------------
# IMPORTANT: apne models ke mutabiq naam yahan likho.
# models/order.py ke OrderItem aur models/cart.py ke CartItem mein
# jis column mein ForeignKey("product_variants.id") hai, uska naam.
# Common naam: product_variant_id
# ------------------------------------------------------------------
ORDER_ITEM_VARIANT_COL = OrderItem.product_variant_id
CART_ITEM_VARIANT_COL = CartItem.product_variant_id


# Create category - Admin only
@router.post("/", response_model=CategoryResponse)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    existing_category = db.query(Category).filter(
        Category.name == category.name
    ).first()

    if existing_category:
        raise HTTPException(
            status_code=400,
            detail="Category already exists"
        )

    new_category = Category(
        name=category.name,
        description=category.description,
        image_url=category.image_url
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category


# Get all categories
@router.get("/", response_model=list[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()


# Get single category
@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    return category


# Delete category - Admin only
@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    variant_ids = [
        v.id for p in category.products for v in p.variants
    ]

    if variant_ids:
        # Agar kisi order mein hai to delete nahi hogi
        in_order = db.query(OrderItem).filter(
            ORDER_ITEM_VARIANT_COL.in_(variant_ids)
        ).first()
        if in_order:
            raise HTTPException(
                status_code=400,
                detail="Is category ke products orders mein hain, delete nahi ho sakti"
            )

        # Cart items saaf kar do
        db.query(CartItem).filter(
            CART_ITEM_VARIANT_COL.in_(variant_ids)
        ).delete(synchronize_session=False)

    db.delete(category)
    db.commit()

    return {"message": "Category deleted successfully"}