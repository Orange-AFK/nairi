from fastapi.testclient import TestClient

from nairi_api.config import Settings
from nairi_api.main import create_app


def build_client() -> TestClient:
    settings = Settings(
        api_tokens={
            "settings-reader-token": ["settings:read"],
            "posts-reader-token": ["posts:read"],
            "admin-token": ["admin:all"],
        }
    )
    return TestClient(create_app(settings=settings))


def test_protected_endpoint_rejects_missing_token() -> None:
    client = build_client()

    response = client.get("/api/v1/mdx-components")

    assert response.status_code == 401
    assert response.json() == {
        "code": "unauthorized",
        "message": "Missing bearer token",
        "details": {},
        "requestId": "unavailable",
    }


def test_protected_endpoint_rejects_invalid_token() -> None:
    client = build_client()

    response = client.get(
        "/api/v1/mdx-components",
        headers={"Authorization": "Bearer unknown-token"},
    )

    assert response.status_code == 401
    assert response.json() == {
        "code": "unauthorized",
        "message": "Invalid bearer token",
        "details": {},
        "requestId": "unavailable",
    }


def test_protected_endpoint_rejects_missing_scope() -> None:
    client = build_client()

    response = client.get(
        "/api/v1/mdx-components",
        headers={"Authorization": "Bearer posts-reader-token"},
    )

    assert response.status_code == 403
    assert response.json() == {
        "code": "forbidden",
        "message": "Missing required scope",
        "details": {"requiredScope": "settings:read"},
        "requestId": "unavailable",
    }


def test_protected_endpoint_accepts_required_scope() -> None:
    client = build_client()

    response = client.get(
        "/api/v1/mdx-components",
        headers={"Authorization": "Bearer settings-reader-token"},
    )

    assert response.status_code == 200
    assert response.json() == {"items": []}


def test_protected_endpoint_accepts_admin_all_scope() -> None:
    client = build_client()

    response = client.get(
        "/api/v1/mdx-components",
        headers={"Authorization": "Bearer admin-token"},
    )

    assert response.status_code == 200
    assert response.json() == {"items": []}
