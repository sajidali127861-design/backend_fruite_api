from pydantic import BaseModel

class ProductVariantCreate(BaseModel):
    weight: str
    price: int
    stock: int = 0

class ProductCreate(BaseModel):
    category_id: int
    name: str
    description: str | None = None
    image_url: str | None = None
    variants: list[ProductVariantCreate]


class ProductVariantUpdate(BaseModel):
    id: int | None = None
    weight: str
    price: int
    stock: int

class ProductUpdate(BaseModel):
    category_id: int
    name: str
    description: str | None = None
    image_url: str | None = None
    variants: list[ProductVariantUpdate]




class ProductVariantResponse(BaseModel):
    id: int
    weight: str
    price: int
    stock: int

    class Config:
        from_attributes = True


class ProductResponse(BaseModel):
    id: int
    category_id: int
    name: str
    description: str | None
    image_url: str | None
    variants: list[ProductVariantResponse]

    class Config:
        from_attributes = True