"""seed.py: put sample products into the database. Run:  uv run python -m app.seed
Safe to run many times: it only adds products when the table is empty (idempotent)."""

from decimal import Decimal

from sqlmodel import Session, select

from app.db import engine
from app.models import Product


def sample_products() -> list[Product]:
    return [
        Product(name="Blue T-shirt", price=Decimal("12.50"), stock=10),
        Product(name="Coffee mug", price=Decimal("7.00"), stock=0),
        Product(name="Notebook", price=Decimal("3.25"), stock=42),
    ]


def seed() -> None:
    with Session(engine) as session:
        if session.exec(select(Product)).first() is not None:
            print("product table already has data: nothing added")
            return
        products = sample_products()
        session.add_all(products)
        session.commit()
        print(f"added {len(products)} products")


if __name__ == "__main__":
    seed()
