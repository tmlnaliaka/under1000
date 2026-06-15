import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import tempfile
import pytest
import pytest_asyncio
from decimal import Decimal
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.main import create_app
from app.database import Base
from app.models import User, DiscountCode, Product
from app.services import ProductService, CartService, CheckoutService
from app.schemas import ProductCreate, CheckoutRequest
from app.security import hash_password


@pytest.mark.asyncio
async def test_cart_total_math(db):
    svc = ProductService(db)
    user = User(username="mathu", email="m@t.com", password_hash="x")
    db.add(user)
    await db.commit()
    await db.refresh(user)

    p1 = await svc.create(ProductCreate(name="A", price=Decimal("100"), seller="s", whatsapp="254700000000", location="Nairobi", category="Tops"), "mathu")
    p2 = await svc.create(ProductCreate(name="B", price=Decimal("300"), seller="s", whatsapp="254700000000", location="Nairobi", category="Shoes"), "mathu")
    p1.approved = True
    p2.approved = True
    await db.commit()
    await db.refresh(p1)
    await db.refresh(p2)

    cart = CartService(db)
    await cart.get_or_create_cart_item(user.id, p1)
    await cart.get_or_create_cart_item(user.id, p2)

    checkout = CheckoutService(db)
    result = await checkout.process_checkout(user.id, CheckoutRequest(payment_method="mock"))
    assert Decimal(str(result["subtotal"])) == Decimal("400.00")
    assert Decimal(str(result["tax"])) == Decimal("64.00")
    assert Decimal(str(result["total"])) == Decimal("464.00")


@pytest.mark.asyncio
async def test_empty_cart_raises(db):
    user = User(username="empty", email="e@t.com", password_hash="x")
    db.add(user)
    await db.commit()
    await db.refresh(user)
    checkout = CheckoutService(db)
    with pytest.raises(Exception):
        await checkout.process_checkout(user.id, CheckoutRequest(payment_method="mock"))


@pytest.mark.asyncio
async def test_checkout_reduces_inventory(db):
    svc = ProductService(db)
    user = User(username="inv", email="i@t.com", password_hash="x")
    db.add(user)
    await db.commit()
    await db.refresh(user)

    p1 = await svc.create(ProductCreate(name="Limited", price=Decimal("500"), seller="s", whatsapp="254700000000", location="Nairobi", category="Hats", inventory=3), "inv")
    p1.approved = True
    await db.commit()
    await db.refresh(p1)
    assert p1.inventory == 3

    cart = CartService(db)
    await cart.get_or_create_cart_item(user.id, p1)
    checkout = CheckoutService(db)
    await checkout.process_checkout(user.id, CheckoutRequest(payment_method="mock"))
    await db.refresh(p1)
    assert p1.inventory == 2


@pytest.mark.asyncio
async def test_discount_code_reduces_total(db):
    user = User(username="dcu", email="d@t.com", password_hash="x")
    db.add(user)
    db.add(DiscountCode(code="SAVE10", percentage=10, active=True))
    await db.commit()
    await db.refresh(user)

    svc = ProductService(db)
    p1 = await svc.create(ProductCreate(name="X", price=Decimal("200"), seller="s", whatsapp="254700000000", location="Nairobi", category="Accessories"), "dcu")
    p1.approved = True
    await db.commit()
    await db.refresh(p1)

    cart = CartService(db)
    await cart.get_or_create_cart_item(user.id, p1)
    checkout = CheckoutService(db)
    result = await checkout.process_checkout(user.id, CheckoutRequest(payment_method="mock", discount_code="SAVE10"))
    assert Decimal(str(result["discount_amount"])) == Decimal("20.00")
