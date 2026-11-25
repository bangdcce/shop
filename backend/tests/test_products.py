from decimal import Decimal
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.db import engine
from app.main import app
from app.models import Product
import pytest

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


def test_detail_not_found():
    r = client.get("/products/999")
    assert r.status_code == 404
    assert r.json() == {"detail": "Product not found"}


def test_min_greater_than_max_is_400():
    r = client.get("/products", params={"min_price": "10", "max_price": "5"})
    assert r.status_code == 400
    assert r.json() == {"detail": "min_price must be <= max_price"}


def names(params):
    return [p["name"] for p in client.get("/products", params=params).json()]


def test_min_and_max_include_both_edges():
    assert names({"min_price": "5", "max_price": "12.50"}) == [
        "Coffee mug",
        "Blue T-shirt",
    ]


@pytest.mark.parametrize(
    "params, expected",
    [
        ({"max_price": "7.00"}, ["Notebook", "Coffee mug"]),
        ({"max_price": "6.99"}, ["Notebook"]),
    ],
)
def test_price_boundaries(params, expected):
    assert names(params) == expected


def test_detail_found():  # SHOP-005 AC1
    r = client.get("/products/1")
    assert r.status_code == 200
    assert r.json()["name"] == "Blue T-shirt"


def test_detail_id_not_a_number_is_422():  # SHOP-005 AC3
    assert client.get("/products/abc").status_code == 422


def test_in_stock_hides_sold_out():  # SHOP-006 AC3: Coffee mug has stock 0
    assert names({"in_stock": "true"}) == ["Notebook", "Blue T-shirt"]


def test_no_match_is_empty_list_not_404():  # SHOP-006 AC4
    r = client.get("/products", params={"min_price": "100"})
    assert r.status_code == 200
    assert r.json() == []


def test_min_equals_max_is_allowed():  # SHOP-006 AC6
    assert names({"min_price": "7", "max_price": "7"}) == ["Coffee mug"]
