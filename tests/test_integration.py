import pytest


@pytest.mark.asyncio
async def test_full_checkout_flow_decrements_inventory_and_clears_cart(auth_client, db):
    from app.models import Product
    
    product_resp = await auth_client.post("/api/products", json={
        "name": "Jeans",
        "price": 500,
        "seller": "Jane",
        "whatsapp": "254700000000",
        "location": "CBD",
        "category": "Pants",
        "inventory": 10,
    })
    product_id = product_resp.json()["id"]
    
    product = await db.get(Product, product_id)
    product.approved = True
    await db.commit()
    
    await auth_client.post("/api/cart", json={"product_id": product_id, "quantity": 2})

    checkout = await auth_client.post("/api/cart/checkout", json={"payment_method": "mock"})
    assert checkout.status_code == 200
    assert "order_id" in checkout.json()

    cart_after = await auth_client.get("/api/cart")
    assert len(cart_after.json()) == 0

    product = await auth_client.get(f"/api/products/{product_id}")
    p = product.json()
    assert p["inventory"] == 8


@pytest.mark.asyncio
async def test_registration_creates_user_in_db(auth_client):
    me = await auth_client.get("/api/auth/me")
    assert me.json()["username"] == "authtest"


@pytest.mark.asyncio
async def test_admin_can_approve_product_after_creation(client, db):
    from app.models import User
    from app.security import hash_password, create_access_token
    
    admin = User(username="admintest", email="admin@test.com", password_hash=hash_password("admin123"), role="admin")
    db.add(admin)
    await db.commit()
    await db.refresh(admin)
    
    token = create_access_token({"sub": admin.username})
    client.headers["Authorization"] = f"Bearer {token}"
    
    product_resp = await client.post("/api/products", json={
        "name": "Shirt",
        "price": 250,
        "seller": "John",
        "whatsapp": "254711111111",
        "location": "Westlands",
        "category": "Tops",
    })
    pid = product_resp.json()["id"]
    assert product_resp.json()["approved"] is False
    await client.post(f"/api/admin/products/{pid}/approve")
    p = await client.get(f"/api/products/{pid}")
    assert p.json()["approved"] is True
