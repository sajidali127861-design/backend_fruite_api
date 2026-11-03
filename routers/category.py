from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.category import Category
from models.product import Product
from schemas.category import CategoryCreate, CategoryResponse
from models.user import User
from utils.dependencies import get_current_admin


router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


# Create category - Admin only
@router.post(
    "/",
    response_model=CategoryResponse
)
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
@router.get(
    "/",
    response_model=list[CategoryResponse]
)
def get_categories(
    db: Session = Depends(get_db)
):
    return db.query(Category).all()


# Get single category
@router.get(
    "/{category_id}",
    response_model=CategoryResponse
)
def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
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
    print(f"category_id:{category_id}")
    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=400,
            detail="Category not found"
        )
    has_products=db.query(Product).filter(Product.category_id==category_id).first()
    if has_products:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete category with existing products"
        )
    print(f"category:{category}")
    db.delete(category)
    db.commit()

    return {
        "message": "Category deleted successfully"
    }