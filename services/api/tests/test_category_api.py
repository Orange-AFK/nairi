import json
from pathlib import Path

from fastapi.testclient import TestClient

from nairi_api.config import Settings
from nairi_api.main import create_app


def build_client(db_path: str = ":memory:") -> TestClient:
    settings = Settings(
        database_path=db_path,
        api_tokens={
            "taxonomy-reader": ["taxonomy:read"],
            "taxonomy-writer": ["taxonomy:read", "taxonomy:write"],
            "admin-token": ["admin:all"],
            "posts-reader": ["posts:read"],
        },
    )
    return TestClient(create_app(settings=settings))


CATEGORIES = [
    {
        "name": "Technology",
        "slug": "technology",
        "description": "Tech articles",
    },
    {
        "name": "Design",
        "slug": "design",
        "description": "Design articles",
    },
]


def _create_categories(client: TestClient) -> None:
    for cat in CATEGORIES:
        response = client.post(
            "/api/v1/categories",
            headers={"Authorization": "Bearer taxonomy-writer"},
            json=cat,
        )
        assert response.status_code == 201, f"Failed to create category {cat}: {response.json()}"


def test_category_list_rejects_missing_token(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    response = client.get("/api/v1/categories")
    assert response.status_code == 401
    assert response.json()["code"] == "unauthorized"


def test_category_list_rejects_missing_scope(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    response = client.get(
        "/api/v1/categories",
        headers={"Authorization": "Bearer posts-reader"},
    )
    assert response.status_code == 403
    assert response.json()["code"] == "forbidden"


def test_category_list_empty(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    response = client.get(
        "/api/v1/categories",
        headers={"Authorization": "Bearer taxonomy-reader"},
    )
    assert response.status_code == 200
    assert response.json() == {"items": []}


def test_category_create_and_list(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    create_response = client.post(
        "/api/v1/categories",
        headers={"Authorization": "Bearer taxonomy-writer"},
        json=CATEGORIES[0],
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["categoryId"] == "cat-technology"
    assert created["name"] == "Technology"
    assert created["slug"] == "technology"
    assert created["description"] == "Tech articles"
    assert created["createdAt"] == created["updatedAt"]

    list_response = client.get(
        "/api/v1/categories",
        headers={"Authorization": "Bearer taxonomy-reader"},
    )
    assert list_response.status_code == 200
    items = list_response.json()["items"]
    assert len(items) == 1
    assert items[0]["categoryId"] == "cat-technology"


def test_category_create_rejects_missing_scope(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    response = client.post(
        "/api/v1/categories",
        headers={"Authorization": "Bearer taxonomy-reader"},
        json=CATEGORIES[0],
    )
    assert response.status_code == 403


def test_category_create_rejects_duplicate_slug(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    client.post(
        "/api/v1/categories",
        headers={"Authorization": "Bearer taxonomy-writer"},
        json=CATEGORIES[0],
    )
    response = client.post(
        "/api/v1/categories",
        headers={"Authorization": "Bearer taxonomy-writer"},
        json=CATEGORIES[0],
    )
    assert response.status_code == 409
    assert response.json()["code"] == "conflict"


def test_category_create_rejects_blank_name(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    response = client.post(
        "/api/v1/categories",
        headers={"Authorization": "Bearer taxonomy-writer"},
        json={"name": "  ", "slug": "empty-name"},
    )
    assert response.status_code == 400
    assert response.json()["code"] == "invalid_request"


def test_category_create_rejects_invalid_slug(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    response = client.post(
        "/api/v1/categories",
        headers={"Authorization": "Bearer taxonomy-writer"},
        json={"name": "Bad Slug", "slug": "BAD SLUG"},
    )
    assert response.status_code == 400
    assert response.json()["code"] == "invalid_request"


def test_category_get_by_id(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    _create_categories(client)
    response = client.get(
        "/api/v1/categories/cat-technology",
        headers={"Authorization": "Bearer taxonomy-reader"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Technology"


def test_category_get_returns_404_for_unknown(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    response = client.get(
        "/api/v1/categories/cat-unknown",
        headers={"Authorization": "Bearer taxonomy-reader"},
    )
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


def test_category_update(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    _create_categories(client)
    update_response = client.patch(
        "/api/v1/categories/cat-technology",
        headers={"Authorization": "Bearer taxonomy-writer"},
        json={"name": "Tech", "slug": "tech", "description": "Updated"},
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["name"] == "Tech"
    assert updated["slug"] == "tech"
    assert updated["description"] == "Updated"

    get_response = client.get(
        "/api/v1/categories/cat-technology",
        headers={"Authorization": "Bearer taxonomy-reader"},
    )
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Tech"


def test_category_update_rejects_duplicate_slug(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    _create_categories(client)
    response = client.patch(
        "/api/v1/categories/cat-technology",
        headers={"Authorization": "Bearer taxonomy-writer"},
        json={"name": "Design", "slug": "design", "description": "Conflict"},
    )
    assert response.status_code == 409
    assert response.json()["code"] == "conflict"


def test_category_update_rejects_404(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    response = client.patch(
        "/api/v1/categories/cat-unknown",
        headers={"Authorization": "Bearer taxonomy-writer"},
        json={"name": "Unknown", "slug": "unknown"},
    )
    assert response.status_code == 404


def test_category_delete(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    _create_categories(client)
    delete_response = client.delete(
        "/api/v1/categories/cat-technology",
        headers={"Authorization": "Bearer taxonomy-writer"},
    )
    assert delete_response.status_code == 204

    get_response = client.get(
        "/api/v1/categories/cat-technology",
        headers={"Authorization": "Bearer taxonomy-reader"},
    )
    assert get_response.status_code == 404


def test_category_delete_rejects_404(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    response = client.delete(
        "/api/v1/categories/cat-unknown",
        headers={"Authorization": "Bearer taxonomy-writer"},
    )
    assert response.status_code == 404


def test_category_order_by_name(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    for cat in reversed(CATEGORIES):
        client.post(
            "/api/v1/categories",
            headers={"Authorization": "Bearer taxonomy-writer"},
            json=cat,
        )
    response = client.get(
        "/api/v1/categories",
        headers={"Authorization": "Bearer taxonomy-reader"},
    )
    items = response.json()["items"]
    assert len(items) == 2
    assert items[0]["name"] == "Design"  # alphabetically first
    assert items[1]["name"] == "Technology"


def test_category_admin_all_scope(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    response = client.get(
        "/api/v1/categories",
        headers={"Authorization": "Bearer admin-token"},
    )
    assert response.status_code == 200


def test_category_preserves_data_across_restarts(tmp_path: Path) -> None:
    """Verify that category data is persisted to the SQLite file,
    not ephemeral."""
    db_path = str(tmp_path / "test.db")
    client1 = build_client(db_path=db_path)
    client1.post(
        "/api/v1/categories",
        headers={"Authorization": "Bearer taxonomy-writer"},
        json=CATEGORIES[0],
    )
    client2 = build_client(db_path=db_path)
    response = client2.get(
        "/api/v1/categories",
        headers={"Authorization": "Bearer taxonomy-reader"},
    )
    assert len(response.json()["items"]) == 1
