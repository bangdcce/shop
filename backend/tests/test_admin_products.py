import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.db import engine
from app.main import app
from app.models import Product, User

client = TestClient(app)
PEN = {"name": "Pen", "price": "1.10", "stock": 5}


def test_admin_creates_product(admin_headers):
    r = client.post("/products", json=PEN, headers=admin_headers)
    assert r.status_code == 201
    new_id = r.json()["id"]
    with Session(engine) as session:
        assert session.get(Product, new_id).name == "Pen"


def test_no_token_is_401():
    assert client.post("/products", json=PEN).status_code == 401


def test_customer_is_403(customer_headers):
    r = client.post("/products", json=PEN, headers=customer_headers)
    assert r.status_code == 403
    assert r.json() == {"detail": "Admins only"}


@pytest.mark.parametrize("body", [
    {"name": "", "price": "1.00", "stock": 1},
    {"name": "A", "price": "0", "stock": 1},
    {"name": "A", "price": "-1", "stock": 1},
    {"name": "A", "price": "1.999", "stock": 1},
    {"name": "A", "price": "1.00", "stock": -1},
])
def test_bad_product_is_422(body, admin_headers):
    assert client.post("/products", json=body, headers=admin_headers).status_code == 422


def test_boundary_values_are_ok(admin_headers):
    body = {"name": "A", "price": "0.01", "stock": 0}
    assert client.post("/products", json=body, headers=admin_headers).status_code == 201


def test_seed_admin_twice_creates_one_admin():
    from app.seed import seed_admin
    seed_admin()
    seed_admin()
    with Session(engine) as session:
        admins = session.exec(select(User).where(User.role == "admin")).all()
    assert len(admins) == 1
    assert admins[0].hashed_password.startswith("$argon2")
