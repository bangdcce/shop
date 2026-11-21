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
