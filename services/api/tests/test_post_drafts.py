import re

from fastapi.testclient import TestClient

from nairi_api.config import Settings
from nairi_api.main import create_app


def build_client() -> TestClient:
    settings = Settings(
        api_tokens={
            "post-writer-token": ["posts:write"],
            "post-reader-token": ["posts:read"],
            "admin-token": ["admin:all"],
        }
    )
    return TestClient(create_app(settings=settings))


def draft_payload() -> dict[str, object]:
    return {
        "title": "First Nairi draft",
        "slug": "first-nairi-draft",
        "contentFormat": "markdown",
        "content": "# First Nairi draft\n\nA short draft body.",
        "summary": "A short draft summary.",
        "tags": [],
        "categoryId": None,
        "seriesId": None,
        "metadata": {"source": "route-test"},
    }


def test_create_post_draft_rejects_missing_token() -> None:
    client = build_client()

    response = client.post("/api/v1/posts", json=draft_payload())

    assert response.status_code == 401
    assert response.json() == {
        "code": "unauthorized",
        "message": "Missing bearer token",
        "details": {},
        "requestId": "unavailable",
    }


def test_create_post_draft_rejects_missing_scope() -> None:
    client = build_client()

    response = client.post(
        "/api/v1/posts",
        json=draft_payload(),
        headers={"Authorization": "Bearer post-reader-token"},
    )

    assert response.status_code == 403
    assert response.json() == {
        "code": "forbidden",
        "message": "Missing required scope",
        "details": {"requiredScope": "posts:write"},
        "requestId": "unavailable",
    }


def test_create_post_draft_accepts_posts_write_scope() -> None:
    client = build_client()

    response = client.post(
        "/api/v1/posts",
        json=draft_payload(),
        headers={"Authorization": "Bearer post-writer-token"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["postId"] == "draft-first-nairi-draft"
    assert body["status"] == "draft"
    assert body["revisionId"] == "revision-first-nairi-draft-1"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", body["createdAt"])
    assert body["createdAt"] != "1970-01-01T00:00:00Z"


def test_create_post_draft_accepts_admin_all_scope() -> None:
    client = build_client()

    response = client.post(
        "/api/v1/posts",
        json=draft_payload(),
        headers={"Authorization": "Bearer admin-token"},
    )

    assert response.status_code == 201
    assert response.json()["status"] == "draft"
