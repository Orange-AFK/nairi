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


SERIES_LIST = [
    {
        "name": "Getting Started",
        "slug": "getting-started",
        "description": "Introductory series",
    },
    {
        "name": "Advanced Topics",
        "slug": "advanced-topics",
        "description": "Advanced series",
    },
]


def _create_series(client: TestClient) -> None:
    for s in SERIES_LIST:
        response = client.post(
            "/api/v1/series",
            headers={"Authorization": "Bearer taxonomy-writer"},
            json=s,
        )
        assert response.status_code == 201, f"Failed to create series {s}: {response.json()}"


def test_series_list_rejects_missing_token(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    response = client.get("/api/v1/series")
    assert response.status_code == 401
    assert response.json()["code"] == "unauthorized"


def test_series_list_rejects_missing_scope(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    response = client.get(
        "/api/v1/series",
        headers={"Authorization": "Bearer posts-reader"},
    )
    assert response.status_code == 403
    assert response.json()["code"] == "forbidden"


def test_series_list_empty(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    response = client.get(
        "/api/v1/series",
        headers={"Authorization": "Bearer taxonomy-reader"},
    )
    assert response.status_code == 200
    assert response.json() == {"items": []}


def test_series_create_and_list(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    create_response = client.post(
        "/api/v1/series",
        headers={"Authorization": "Bearer taxonomy-writer"},
        json=SERIES_LIST[0],
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["seriesId"] == "series-getting-started"
    assert created["name"] == "Getting Started"
    assert created["slug"] == "getting-started"
    assert created["description"] == "Introductory series"
    assert created["createdAt"] == created["updatedAt"]

    list_response = client.get(
        "/api/v1/series",
        headers={"Authorization": "Bearer taxonomy-reader"},
    )
    assert list_response.status_code == 200
    items = list_response.json()["items"]
    assert len(items) == 1
    assert items[0]["seriesId"] == "series-getting-started"


def test_series_create_rejects_missing_scope(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    response = client.post(
        "/api/v1/series",
        headers={"Authorization": "Bearer taxonomy-reader"},
        json=SERIES_LIST[0],
    )
    assert response.status_code == 403


def test_series_create_rejects_duplicate_slug(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    client.post(
        "/api/v1/series",
        headers={"Authorization": "Bearer taxonomy-writer"},
        json=SERIES_LIST[0],
    )
    response = client.post(
        "/api/v1/series",
        headers={"Authorization": "Bearer taxonomy-writer"},
        json=SERIES_LIST[0],
    )
    assert response.status_code == 409
    assert response.json()["code"] == "conflict"


def test_series_create_rejects_blank_name(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    response = client.post(
        "/api/v1/series",
        headers={"Authorization": "Bearer taxonomy-writer"},
        json={"name": "  ", "slug": "blank-name", "description": None},
    )
    assert response.status_code == 400
    assert response.json()["code"] == "invalid_request"


def test_series_create_rejects_invalid_slug(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    response = client.post(
        "/api/v1/series",
        headers={"Authorization": "Bearer taxonomy-writer"},
        json={"name": "Bad Slug", "slug": "BAD SLUG", "description": None},
    )
    assert response.status_code == 400
    assert response.json()["code"] == "invalid_request"


def test_series_get_by_id(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    _create_series(client)
    response = client.get(
        "/api/v1/series/series-getting-started",
        headers={"Authorization": "Bearer taxonomy-reader"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Getting Started"


def test_series_get_404_for_unknown(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    response = client.get(
        "/api/v1/series/series-unknown",
        headers={"Authorization": "Bearer taxonomy-reader"},
    )
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


def test_series_update(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    _create_series(client)
    update_response = client.patch(
        "/api/v1/series/series-getting-started",
        headers={"Authorization": "Bearer taxonomy-writer"},
        json={"name": "Beginner", "slug": "beginner", "description": "Updated"},
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["name"] == "Beginner"
    assert updated["slug"] == "beginner"
    assert updated["description"] == "Updated"

    get_response = client.get(
        "/api/v1/series/series-getting-started",
        headers={"Authorization": "Bearer taxonomy-reader"},
    )
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Beginner"
    assert get_response.json()["slug"] == "beginner"


def test_series_update_rejects_duplicate_slug(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    _create_series(client)
    response = client.patch(
        "/api/v1/series/series-getting-started",
        headers={"Authorization": "Bearer taxonomy-writer"},
        json={"name": "Advanced Topics", "slug": "advanced-topics", "description": "Conflict"},
    )
    assert response.status_code == 409
    assert response.json()["code"] == "conflict"


def test_series_update_rejects_404(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    response = client.patch(
        "/api/v1/series/series-unknown",
        headers={"Authorization": "Bearer taxonomy-writer"},
        json={"name": "Unknown", "slug": "unknown", "description": None},
    )
    assert response.status_code == 404


def test_series_delete(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    _create_series(client)
    delete_response = client.delete(
        "/api/v1/series/series-getting-started",
        headers={"Authorization": "Bearer taxonomy-writer"},
    )
    assert delete_response.status_code == 204

    get_response = client.get(
        "/api/v1/series/series-getting-started",
        headers={"Authorization": "Bearer taxonomy-reader"},
    )
    assert get_response.status_code == 404


def test_series_delete_rejects_404(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    response = client.delete(
        "/api/v1/series/series-unknown",
        headers={"Authorization": "Bearer taxonomy-writer"},
    )
    assert response.status_code == 404


def test_series_order_by_name(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    for s in reversed(SERIES_LIST):
        client.post(
            "/api/v1/series",
            headers={"Authorization": "Bearer taxonomy-writer"},
            json=s,
        )
    response = client.get(
        "/api/v1/series",
        headers={"Authorization": "Bearer taxonomy-reader"},
    )
    items = response.json()["items"]
    assert len(items) == 2
    assert items[0]["name"] == "Advanced Topics"
    assert items[1]["name"] == "Getting Started"


def test_series_admin_all_scope(tmp_path: Path) -> None:
    client = build_client(db_path=str(tmp_path / "test.db"))
    response = client.get(
        "/api/v1/series",
        headers={"Authorization": "Bearer admin-token"},
    )
    assert response.status_code == 200


def test_series_preserves_data_across_restarts(tmp_path: Path) -> None:
    db_path = str(tmp_path / "test.db")
    client1 = build_client(db_path=db_path)
    client1.post(
        "/api/v1/series",
        headers={"Authorization": "Bearer taxonomy-writer"},
        json=SERIES_LIST[0],
    )
    client2 = build_client(db_path=db_path)
    response = client2.get(
        "/api/v1/series",
        headers={"Authorization": "Bearer taxonomy-reader"},
    )
    assert len(response.json()["items"]) == 1
