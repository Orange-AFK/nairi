from fastapi.testclient import TestClient

from nairi_api.main import create_app


def test_health_endpoint_returns_service_status() -> None:
    client = TestClient(create_app())

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "nairi-api",
        "version": "0.1.0",
    }
