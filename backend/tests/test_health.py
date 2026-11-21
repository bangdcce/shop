"""The example test of the team. Every new endpoint gets tests in the same style:
Arrange (data) -> Act (call the API) -> Assert (check status AND body)."""

from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine

from app.db import get_session
from app.main import app

client = TestClient(app)  # calls the app in memory: no server, no port needed


def test_health_says_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "database": "ok"}


def test_health_fails_when_database_is_down():
    # Arrange: give /health a session whose database address has nothing listening (port 1)
    # connect_timeout=1: on Windows a refused connection is retried for a long time; give up after 1 second
    dead_engine = create_engine("postgresql+psycopg://x:x@127.0.0.1:1/x?connect_timeout=1")

    def dead_session():
        with Session(dead_engine) as session:
            yield session

    app.dependency_overrides[get_session] = dead_session
    try:
        # Act: raise_server_exceptions=False -> we get the 500 a real user would get
        r = TestClient(app, raise_server_exceptions=False).get("/health")
    finally:
        app.dependency_overrides.clear()  # never leak the fake into other tests
    # Assert (AC2): never say "ok" when the database is dead
    assert r.status_code == 500
