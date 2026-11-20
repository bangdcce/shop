"""The example test of the team. Every new endpoint gets tests in the same style:
Arrange (data) -> Act (call the API) -> Assert (check status AND body)."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)  # calls the app in memory: no server, no port needed


def test_health_says_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
