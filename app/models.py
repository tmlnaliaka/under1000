from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Numeric,
    Text,
    Index,
)
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="buyer")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False, index=True)
    seller = Column(String(100), nullable=False, index=True)
    whatsapp = Column(String(20), nullable=False)
    instagram = Column(String(50), nullable=True)
    tiktok = Column(String(50), nullable=True)
    location = Column(String(100), nullable=False)
    image_url = Column(String(500), nullable=True)
    category = Column(String(50), nullable=False, index=True)
    approved = Column(Boolean, default=False, index=True)
    inventory = Column(Integer, default=1, nullable=False)
    submitted_by = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


Index("ix_products_approved_price", Product.approved, Product.price)


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    quantity = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


Index("ix_cart_user_product", CartItem.user_id, CartItem.product_id, unique=True)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    total = Column(Numeric(10, 2), nullable=False)
    tax = Column(Numeric(10, 2), default=0, nullable=False)
    discount_code = Column(String(30), nullable=True)
    discount_amount = Column(Numeric(10, 2), default=0, nullable=False)
    status = Column(String(20), default="pending", index=True)
    payment_method = Column(String(30), default="mock")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)


class DiscountCode(Base):
    __tablename__ = "discount_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(30), unique=True, nullable=False, index=True)
    percentage = Column(Integer, nullable=False)
    active = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
