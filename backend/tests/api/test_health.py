"""NFR-1: helsesjekken svarer uten innlogging."""

from fastapi.testclient import TestClient

from rbe.main import create_app


def test_nfr1_health_returns_ok() -> None:
    client = TestClient(create_app())
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
