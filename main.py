from fastapi import FastAPI
from database import engine,Base
from routers.auth import router as auth_router
from models.user import User
from models.category import Category
from models.product import Product, ProductVariant
from models.cart import Cart, CartItem
from models.order import Order, OrderItem
from routers.category import router as category_router
from routers.product import router as product_router
from routers.cart import router as cart_router
from routers.order import router as order_router
from routers.customer import router as customer_router
from routers.dashboard import router as dashboard_router
from routers.upload import router as upload_router
print("Database URL:", engine.url.render_as_string(hide_password=True))
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")
app = FastAPI()
app.include_router(auth_router)
app.include_router(category_router)
app.include_router(product_router)
app.include_router(cart_router)
app.include_router(order_router)
app.include_router(customer_router)
app.include_router(dashboard_router)
app.include_router(upload_router)
@app.get("/")
def root():
    return {"message": "FastAPI is running"}