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

from app.db import engine
from app.seed import seed


@pytest.fixture(scope="session", autouse=True)
def migrate_test_db():
    command.upgrade(Config("alembic.ini"), "head")


@pytest.fixture(autouse=True)
def fresh_products():
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE product RESTART IDENTITY"))
    seed()
