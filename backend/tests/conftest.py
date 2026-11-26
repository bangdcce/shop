import os
from dotenv import dotenv_values

test_url = os.environ.get("TEST_DATABASE_URL") or dotenv_values(".env").get(
    "TEST_DATABASE_URL"
)
if not test_url:
    raise RuntimeError(
        "Thiếu TEST_DATABASE_URL trong .env, không chạy test để tránh đụng shop_dev"
    )
os.environ["DATABASE_URL"] = test_url

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text

from fastapi.testclient import TestClient

from app.config import settings
from app.db import engine
from app.main import app
from app.seed import seed, seed_admin

client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def migrate_test_db():
    command.upgrade(Config("alembic.ini"), "head")


@pytest.fixture(autouse=True)
def fresh_products():
    with engine.begin() as conn:
        conn.execute(text('TRUNCATE product, "user" RESTART IDENTITY'))  # ✅
    seed()


def login_headers(email: str, password: str) -> dict:
    r = client.post("/auth/login", data={"username": email, "password": password})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
def admin_headers():
    seed_admin()
    return login_headers(settings.admin_email, settings.admin_password)


@pytest.fixture
def customer_headers():
    client.post("/auth/register", json={"email": "cus@example.com", "password": "cus-pass-123"})
    return login_headers("cus@example.com", "cus-pass-123")
