from pydantic import BaseModel
from datetime import datetime
class CheckoutRequest(BaseModel):
    shipping_name: str
    shipping_phone: str
    shipping_address: str

class OrderItemResponse(BaseModel):
    id: int
    product_variant_id: int
    product_name: str
    weight: str
    price: int
    quantity: int
    item_total: int

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    status: str
    total_amount: int
    shipping_name: str
    shipping_phone: str
    shipping_address: str
    created_at: datetime

    items: list[OrderItemResponse]

    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    status: str