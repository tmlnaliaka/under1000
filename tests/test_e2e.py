import pytest


@pytest.mark.asyncio
async def test_e2e_customer_journey(client, db):
    await client.post("/api/auth/register", json={"username": "journey", "email": "j@t.com", "password": "pass1234"})
    login = await client.post("/api/auth/login", data={"username": "journey", "password": "pass1234"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/products/", json={
        "name": "Sneakers",
        "price": 800,
        "seller": "Kiosk",
        "whatsapp": "254700000000",
        "location": "CBD",
        "category": "Shoes",
        "inventory": 5,
    }, headers=headers)

    product_id = resp.json()["id"]
    
    from app.models import Product
    product = await db.get(Product, product_id)
    product.approved = True
    await db.commit()

    listing = await client.get("/api/products/?search=Sneakers", headers=headers)
    assert len(listing.json()) == 1

    pid = listing.json()[0]["id"]
    await client.post("/api/cart/", json={"product_id": pid, "quantity": 1}, headers=headers)

    checkout = await client.post("/api/cart/checkout", json={"payment_method": "mpesa"}, headers=headers)
    assert checkout.status_code == 200

    orders = await client.get("/api/orders/", headers=headers)
    assert len(orders.json()) == 1


@pytest.mark.asyncio
async def test_sql_injection_blocked(client):
    payload = {"username": "admin' OR '1'='1", "email": "a@a.com", "password": "x"}
    resp = await client.post("/api/auth/register", json=payload)
    assert resp.status_code in (400, 422)
