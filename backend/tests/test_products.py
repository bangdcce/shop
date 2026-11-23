from decimal import Decimal
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.db import engine
from app.main import app
from app.models import Product

client = TestClient(app)


def test_returns_3_products():
    r = client.get("/products")

    assert r.status_code == 200

    assert len(r.json()) == 3


def test_order_product_by_price():
    list_products_from_client = client.get("/products").json()
    names = [product["name"] for product in list_products_from_client]
    assert names == ["Notebook", "Coffee mug", "Blue T-shirt"]


def test_price_is_character():
    list_products_from_client = client.get("/products").json()
    shirt = next(p for p in list_products_from_client if p["name"] == "Blue T-shirt")
    assert shirt["price"] == "12.50"


def test_same_price_smaller_id_first():
    with Session(engine) as session:
        for new_id in (100, 99):
            session.add(
                Product(
                    id=new_id,
                    name=f"Same price {new_id}",
                    price=Decimal("5.00"),
                    stock=1,
                ),
            )
            session.commit()
    list_products = client.get("/products").json()
    list_id = [p["id"] for p in list_products if p["id"] >= 99]
    assert list_id == [99, 100]
