from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.product import Product, ProductVariant
from models.category import Category
from schemas.product import ProductCreate,ProductUpdate ,ProductResponse
from models.user import User
from models.order import OrderItem
from models.cart import CartItem
from utils.dependencies import get_current_admin


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


# Create product - Admin only
@router.post(
    "/",
    response_model=ProductResponse
)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    # Check category
    category = db.query(Category).filter(
        Category.id == product.category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    # Create product
    new_product = Product(
        category_id=product.category_id,
        name=product.name,
        description=product.description,
        image_url=product.image_url
    )

    db.add(new_product)
    db.flush()

    # Add variants
    for variant in product.variants:

        new_variant = ProductVariant(
            product_id=new_product.id,
            weight=variant.weight,
            price=variant.price,
            stock=variant.stock
        )

        db.add(new_variant)

    db.commit()
    db.refresh(new_product)

    return new_product


# Get all products
@router.get(
    "/",
    response_model=list[ProductResponse]
)
def get_products(
    db: Session = Depends(get_db)
):
    return db.query(Product).all()


# Get single product
@router.get(
    "/{product_id}",
    response_model=ProductResponse
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )
    # Check category
    category = db.query(Category).filter(
        Category.id == product_data.category_id
    ).first()
    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )
    # Update product information
    product.category_id = product_data.category_id
    product.name = product_data.name
    product.description = product_data.description
    product.image_url = product_data.image_url
    # --------------------------------
    # Update / Add variants
    # --------------------------------
    for variant_data in product_data.variants:
        # Existing variant
        if variant_data.id is not None:
            variant = db.query(ProductVariant).filter(
                ProductVariant.id == variant_data.id,
                ProductVariant.product_id == product_id
            ).first()
            if not variant:
                raise HTTPException(
                    status_code=404,
                    detail=f"Variant {variant_data.id} not found for this product"
                )
            # Update existing variant
            variant.weight = variant_data.weight
            variant.price = variant_data.price
            variant.stock = variant_data.stock
        # New variant
        else:
            new_variant = ProductVariant(
                product_id=product_id,
                weight=variant_data.weight,
                price=variant_data.price,
                stock=variant_data.stock
            )
            db.add(new_variant)
    db.commit()
    db.refresh(product)
    return product
# Delete product - Admin only
# Delete product - Admin only
@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    variant_ids = [v.id for v in product.variants]

    if variant_ids:
        # Agar kisi order mein hai to delete mat karo
        in_order = db.query(OrderItem).filter(
            OrderItem.product_variant_id.in_(variant_ids)
        ).first()
        if in_order:
            raise HTTPException(
                status_code=400,
                detail="Is product ke orders maujood hain, delete nahi ho sakta"
            )

        # Cart items saaf kar do
        db.query(CartItem).filter(
            CartItem.product_variant_id.in_(variant_ids)
        ).delete(synchronize_session=False)

    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}