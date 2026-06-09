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


TAGS = [
    {
        "name": "Python",
        "slug": "python",
    },
    {
        "name": "FastAPI",
        "slug": "fastapi",
    },
]


def _create_tags(client: TestClient) -> None:
    for tag in TAGS:
        response = client.post(
            "/api/v1/tags",
            headers={"Authorization": "Bearer taxonomy-writer"},
            json=tag,
        )
        assert response.status_code == 201, f"Failed to create tag {tag}: {response.json()}"


def test_tag_list_rejects_missing_token(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    response = client.get("/api/v1/tags")
    assert response.status_code == 401
    assert response.json()["code"] == "unauthorized"


def test_tag_list_rejects_missing_scope(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    response = client.get(
        "/api/v1/tags",
        headers={"Authorization": "Bearer posts-reader"},
    )
    assert response.status_code == 403
    assert response.json()["code"] == "forbidden"


def test_tag_list_empty(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    response = client.get(
        "/api/v1/tags",
        headers={"Authorization": "Bearer taxonomy-reader"},
    )
    assert response.status_code == 200
    assert response.json() == {"items": []}


def test_tag_create_and_list(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    create_response = client.post(
        "/api/v1/tags",
        headers={"Authorization": "Bearer taxonomy-writer"},
        json=TAGS[0],
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["tagId"] == "tag-python"
    assert created["name"] == "Python"
    assert created["slug"] == "python"
    assert created["createdAt"] == created["updatedAt"]

    list_response = client.get(
        "/api/v1/tags",
        headers={"Authorization": "Bearer taxonomy-reader"},
    )
    assert list_response.status_code == 200
    items = list_response.json()["items"]
    assert len(items) == 1
    assert items[0]["tagId"] == "tag-python"


def test_tag_create_rejects_missing_scope(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    response = client.post(
        "/api/v1/tags",
        headers={"Authorization": "Bearer taxonomy-reader"},
        json=TAGS[0],
    )
    assert response.status_code == 403


def test_tag_create_rejects_duplicate_slug(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    client.post(
        "/api/v1/tags",
        headers={"Authorization": "Bearer taxonomy-writer"},
        json=TAGS[0],
    )
    response = client.post(
        "/api/v1/tags",
        headers={"Authorization": "Bearer taxonomy-writer"},
        json=TAGS[0],
    )
    assert response.status_code == 409
    assert response.json()["code"] == "conflict"


def test_tag_create_rejects_blank_name(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    response = client.post(
        "/api/v1/tags",
        headers={"Authorization": "Bearer taxonomy-writer"},
        json={"name": "  ", "slug": "empty-name"},
    )
    assert response.status_code == 400
    assert response.json()["code"] == "invalid_request"


def test_tag_create_rejects_invalid_slug(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    response = client.post(
        "/api/v1/tags",
        headers={"Authorization": "Bearer taxonomy-writer"},
        json={"name": "Bad Slug", "slug": "BAD SLUG"},
    )
    assert response.status_code == 400
    assert response.json()["code"] == "invalid_request"


def test_tag_get_by_id(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    _create_tags(client)
    response = client.get(
        "/api/v1/tags/tag-python",
        headers={"Authorization": "Bearer taxonomy-reader"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Python"


def test_tag_get_404_for_unknown(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    response = client.get(
        "/api/v1/tags/tag-unknown",
        headers={"Authorization": "Bearer taxonomy-reader"},
    )
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


def test_tag_update(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    _create_tags(client)
    update_response = client.patch(
        "/api/v1/tags/tag-python",
        headers={"Authorization": "Bearer taxonomy-writer"},
        json={"name": "Py", "slug": "py"},
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["name"] == "Py"
    assert updated["slug"] == "py"

    get_response = client.get(
        "/api/v1/tags/tag-python",
        headers={"Authorization": "Bearer taxonomy-reader"},
    )
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Py"


def test_tag_update_rejects_duplicate_slug(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    _create_tags(client)
    response = client.patch(
        "/api/v1/tags/tag-python",
        headers={"Authorization": "Bearer taxonomy-writer"},
        json={"name": "FastAPI", "slug": "fastapi"},
    )
    assert response.status_code == 409
    assert response.json()["code"] == "conflict"


def test_tag_update_rejects_404(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    response = client.patch(
        "/api/v1/tags/tag-unknown",
        headers={"Authorization": "Bearer taxonomy-writer"},
        json={"name": "Unknown", "slug": "unknown"},
    )
    assert response.status_code == 404


def test_tag_delete(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    _create_tags(client)
    delete_response = client.delete(
        "/api/v1/tags/tag-python",
        headers={"Authorization": "Bearer taxonomy-writer"},
    )
    assert delete_response.status_code == 204

    get_response = client.get(
        "/api/v1/tags/tag-python",
        headers={"Authorization": "Bearer taxonomy-reader"},
    )
    assert get_response.status_code == 404


def test_tag_delete_rejects_404(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    response = client.delete(
        "/api/v1/tags/tag-unknown",
        headers={"Authorization": "Bearer taxonomy-writer"},
    )
    assert response.status_code == 404


def test_tag_order_by_name(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    for tag in reversed(TAGS):
        client.post(
            "/api/v1/tags",
            headers={"Authorization": "Bearer taxonomy-writer"},
            json=tag,
        )
    response = client.get(
        "/api/v1/tags",
        headers={"Authorization": "Bearer taxonomy-reader"},
    )
    items = response.json()["items"]
    assert len(items) == 2
    assert items[0]["name"] == "FastAPI"
    assert items[1]["name"] == "Python"


def test_tag_admin_all_scope(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    response = client.get(
        "/api/v1/tags",
        headers={"Authorization": "Bearer admin-token"},
    )
    assert response.status_code == 200


def test_tag_preserves_data_across_restarts(tmp_path: Path) -> None:
    db_path = str(tmp_path / "test.db")
    client1 = build_client(db_path=db_path)
    client1.post(
        "/api/v1/tags",
        headers={"Authorization": "Bearer taxonomy-writer"},
        json=TAGS[0],
    )
    client2 = build_client(db_path=db_path)
    response = client2.get(
        "/api/v1/tags",
        headers={"Authorization": "Bearer taxonomy-reader"},
    )
    assert len(response.json()["items"]) == 1
