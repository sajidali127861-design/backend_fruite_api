from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    status = Column(
        String,
        default="pending",
        nullable=False
    )

    total_amount = Column(
        Integer,
        nullable=False
    )

    shipping_name = Column(
        String,
        nullable=False
    )

    shipping_phone = Column(
        String,
        nullable=False
    )

    shipping_address = Column(
        String,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    user = relationship("User")

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(
        Integer,
        ForeignKey("orders.id"),
        nullable=False
    )

    product_variant_id = Column(
        Integer,
        ForeignKey("product_variants.id"),
        nullable=False
    )

    product_name = Column(
        String,
        nullable=False
    )

    weight = Column(
        String,
        nullable=False
    )

    price = Column(
        Integer,
        nullable=False
    )

    quantity = Column(
        Integer,
        nullable=False
    )

    item_total = Column(
        Integer,
        nullable=False
    )

    order = relationship(
        "Order",
        back_populates="items"
    )

    product_variant = relationship(
        "ProductVariant"
    )