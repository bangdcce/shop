import time

import jwt
import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.db import engine
from app.main import app
from sqlalchemy import text

AN = {"email": "an@example.com", "password": "an-pass-123"}

client = TestClient(app)


def register(body=AN):
    return client.post("/auth/register", json=body)


def test_password_is_stored_as_argon2_hash():
    register()
    with engine.connect() as conn:
        stored = conn.execute(text('SELECT hashed_password FROM "user"')).scalar_one()
    assert stored.startswith("$argon2")
    assert "an-pass-123" not in stored


def login(email="an@example.com", password="an-pass-123"):
    return client.post("/auth/login", data={"username": email, "password": password})


def test_me_with_token():
    register()
    token = login().json()["access_token"]
    r = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == "an@example.com"


# ---- SHOP-007: register ----
def test_register_returns_201_without_password():  # AC1
    r = register()
    assert r.status_code == 201
    assert r.json() == {"id": 1, "email": "an@example.com", "role": "customer"}


def test_register_same_email_twice_is_409():  # AC2
    register()
    r = register()
    assert r.status_code == 409
    assert r.json() == {"detail": "Email already registered"}


@pytest.mark.parametrize(
    "body, status",
    [
        ({"email": "an@example.com", "password": "1234567"}, 422),  # 7 chars: just below the edge
        ({"email": "an@example.com", "password": "12345678"}, 201),  # 8 chars: exactly the edge
        ({"email": "not-an-email", "password": "12345678"}, 422),
    ],
)
def test_register_validation_edges(body, status):  # AC3
    assert register(body).status_code == status


def test_cannot_register_as_admin():  # AC5
    r = register({**AN, "role": "admin"})
    assert r.json()["role"] == "customer"


# ---- SHOP-008: login + /auth/me ----
def test_login_returns_bearer_token():  # AC1
    register()
    r = login()
    assert r.status_code == 200
    assert r.json()["token_type"] == "bearer"


@pytest.mark.parametrize("email, password", [("an@example.com", "wrong-pass"), ("nobody@example.com", "an-pass-123")])
def test_login_failures_share_one_message(email, password):  # AC2: no user enumeration
    register()
    r = login(email, password)
    assert r.status_code == 401
    assert r.json() == {"detail": "Wrong email or password"}


def test_me_rejects_missing_tampered_and_expired_tokens():  # AC4
    register()
    token = login().json()["access_token"]
    expired = jwt.encode({"sub": "1", "exp": int(time.time()) - 10}, settings.secret_key, algorithm="HS256")
    for headers in ({}, {"Authorization": f"Bearer {token[:-2]}xx"}, {"Authorization": f"Bearer {expired}"}):
        assert client.get("/auth/me", headers=headers).status_code == 401


def test_secret_key_is_long_enough():  # AC5
    assert len(settings.secret_key) >= 32
