from pydantic import BaseModel

class CartItemCreate(BaseModel):
    product_variant_id: int
    quantity: int = 1


class CartItemUpdate(BaseModel):
    quantity: int


class CartItemResponse(BaseModel):
    id: int
    product_variant_id: int
    quantity: int

    class Config:
        from_attributes = True