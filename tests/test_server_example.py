from fastapi.testclient import TestClient

from examples.server.app import app


def test_health_endpoint_returns_ok() -> None:
    response = TestClient(app).get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
