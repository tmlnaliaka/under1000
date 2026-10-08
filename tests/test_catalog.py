import json
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_seeded_products_have_direct_seller_evidence():
    products = json.loads((ROOT / "products.json").read_text(encoding="utf-8"))

    assert products
    assert len(products) < 100
    assert all(0 < product["price"] <= 1000 for product in products)
    assert all(product["approved"] for product in products)
    assert all(product["source_url"].startswith("https://www.instagram.com/") for product in products)
    assert all(product["source_date"] and product["media_type"] for product in products)
    assert all(product["media_type"] == "video" for product in products)
    assert all("image_url" not in product for product in products)
    assert all("jumia" not in product["source_url"].lower() for product in products)
    assert all("kilimall" not in product["source_url"].lower() for product in products)


def test_storefront_displays_seller_source_and_availability_notice():
    spec = importlib.util.spec_from_file_location("under1000_storefront", ROOT / "app.py")
    storefront = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(storefront)

    response = storefront.app.test_client().get("/")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Confirm price and availability with the seller." in page
    assert all(
        product["source_url"].rstrip("/") + "/embed/" in page
        for product in json.loads((ROOT / "products.json").read_text(encoding="utf-8"))
    )
