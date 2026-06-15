import pytest
import pytest_asyncio
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_security_headers_pent(client):
    resp = await client.get("/api/health")
    assert resp.headers["x-content-type-options"] == "nosniff"
    assert resp.headers["x-frame-options"] == "DENY"
    assert resp.headers.get("x-xss-protection") == "1; mode=block"


@pytest.mark.asyncio
async def test_xss_in_product_name_blocked(auth_client):
    resp = await auth_client.post("/api/products", json={
        "name": "<script>alert(1)</script>",
        "price": 100,
        "seller": "Evil",
        "whatsapp": "2547",
        "location": "X",
        "category": "Other",
    })
    assert resp.status_code == 400
