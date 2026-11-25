from decimal import Decimal

from fastapi.testclient import TestClient
from hypothesis import HealthCheck, assume, given, settings, strategies as st
from sqlalchemy import text
from sqlmodel import Session

from app.db import engine
from app.main import app
from app.models import Product

client = TestClient(app)

money = st.decimals(min_value=Decimal("0.01"), max_value=Decimal("999.99"), places=2)

product = st.fixed_dictionaries(
    {"price": money, "stock": st.integers(min_value=0, max_value=5)}
)


@settings(
    max_examples=60,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@given(
    rows=st.lists(product, max_size=12), low=money, high=money, in_stock=st.booleans()
)
def test_filter_matches_simple_rule(rows, low, high, in_stock):
    assume(low <= high)

    # Arrange: đổ dữ liệu máy vừa sinh vào shop_test
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE product RESTART IDENTITY"))
    with Session(engine) as session:
        session.add_all(
            [
                Product(name=f"P{i}", price=r["price"], stock=r["stock"])
                for i, r in enumerate(rows)
            ]
        )
        session.commit()

    # Act: hỏi API
    params = {
        "min_price": str(low),
        "max_price": str(high),
        "in_stock": str(in_stock).lower(),
    }
    got = [p["id"] for p in client.get("/products", params=params).json()]

    # Assert: tự tính đáp án bằng luật Python đơn giản, rồi so
    expected = sorted(
        (r["price"], i + 1)
        for i, r in enumerate(rows)
        if low <= r["price"] <= high and (not in_stock or r["stock"] > 0)
    )
    assert got == [product_id for _, product_id in expected]
