import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from fastapi.testclient import TestClient

from nairi_api.config import Settings
from nairi_api.main import create_app
from nairi_api.posts import PostStore


def build_client(database_path: Path) -> TestClient:
    settings = Settings(
        api_tokens={
            "post-writer-token": ["posts:write"],
            "post-reader-token": ["posts:read"],
        },
        database_path=str(database_path),
    )
    return TestClient(create_app(settings=settings))


def draft_payload() -> dict[str, object]:
    return {
        "title": "Persistent draft",
        "slug": "persistent-draft",
        "contentFormat": "markdown",
        "content": "# Persistent draft\n\nStored body.",
        "summary": "Stored summary.",
        "tags": ["storage"],
        "categoryId": None,
        "seriesId": None,
        "metadata": {"source": "persistence-test"},
    }


def test_create_post_draft_uses_injected_utc_timestamp(tmp_path: Path) -> None:
    database_path = tmp_path / "nairi.db"
    settings = Settings(
        api_tokens={"post-writer-token": ["posts:write"]},
        database_path=str(database_path),
    )
    app = create_app(settings=settings)
    app.state.post_store = PostStore(
        str(database_path),
        clock=lambda: datetime(2026, 6, 7, 8, 9, 10, tzinfo=UTC),
    )
    client = TestClient(app)

    response = client.post(
        "/api/v1/posts",
        json=draft_payload(),
        headers={"Authorization": "Bearer post-writer-token"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["createdAt"] == "2026-06-07T08:09:10Z"

    with sqlite3.connect(database_path) as connection:
        timestamps = connection.execute(
            """
            SELECT
                posts.created_at,
                posts.updated_at,
                post_revisions.created_at,
                audit_events.created_at
            FROM posts
            JOIN post_revisions ON post_revisions.post_id = posts.id
            JOIN audit_events ON audit_events.target_id = posts.id
            WHERE posts.id = ?
            """,
            (body["postId"],),
        ).fetchone()

    assert timestamps == (
        "2026-06-07T08:09:10Z",
        "2026-06-07T08:09:10Z",
        "2026-06-07T08:09:10Z",
        "2026-06-07T08:09:10Z",
    )


def test_get_post_draft_returns_created_draft_for_reader_scope(tmp_path: Path) -> None:
    database_path = tmp_path / "nairi.db"
    client = build_client(database_path)

    create_response = client.post(
        "/api/v1/posts",
        json=draft_payload(),
        headers={"Authorization": "Bearer post-writer-token"},
    )
    post_id = create_response.json()["postId"]

    read_response = client.get(
        f"/api/v1/posts/{post_id}",
        headers={"Authorization": "Bearer post-reader-token"},
    )

    assert create_response.status_code == 201
    assert read_response.status_code == 200
    assert read_response.json() == {
        "postId": post_id,
        "title": "Persistent draft",
        "slug": "persistent-draft",
        "status": "draft",
        "contentFormat": "markdown",
        "content": "# Persistent draft\n\nStored body.",
        "summary": "Stored summary.",
        "tags": ["storage"],
        "categoryId": None,
        "seriesId": None,
        "metadata": {"source": "persistence-test"},
        "revisionId": create_response.json()["revisionId"],
        "createdAt": create_response.json()["createdAt"],
        "updatedAt": create_response.json()["createdAt"],
    }


def test_get_post_draft_requires_posts_read_scope(tmp_path: Path) -> None:
    database_path = tmp_path / "nairi.db"
    client = build_client(database_path)

    response = client.get(
        "/api/v1/posts/draft-persistent-draft",
        headers={"Authorization": "Bearer post-writer-token"},
    )

    assert response.status_code == 403
    assert response.json() == {
        "code": "forbidden",
        "message": "Missing required scope",
        "details": {"requiredScope": "posts:read"},
        "requestId": "unavailable",
    }


def test_get_post_draft_returns_not_found_for_unknown_post(tmp_path: Path) -> None:
    database_path = tmp_path / "nairi.db"
    client = build_client(database_path)

    response = client.get(
        "/api/v1/posts/missing-post",
        headers={"Authorization": "Bearer post-reader-token"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "code": "not_found",
        "message": "Post not found",
        "details": {"postId": "missing-post"},
        "requestId": "unavailable",
    }


def test_create_post_draft_persists_post_and_revision(tmp_path: Path) -> None:
    database_path = tmp_path / "nairi.db"
    client = build_client(database_path)

    response = client.post(
        "/api/v1/posts",
        json=draft_payload(),
        headers={"Authorization": "Bearer post-writer-token"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "draft"
    assert body["postId"]
    assert body["revisionId"]
    assert body["createdAt"]

    with sqlite3.connect(database_path) as connection:
        post_row = connection.execute(
            """
            SELECT id, title, slug, status, content_format, current_revision_id, created_at, updated_at
            FROM posts
            WHERE id = ?
            """,
            (body["postId"],),
        ).fetchone()
        revision_row = connection.execute(
            """
            SELECT id, post_id, content, metadata, created_by, created_at
            FROM post_revisions
            WHERE id = ?
            """,
            (body["revisionId"],),
        ).fetchone()
        audit_row = connection.execute(
            """
            SELECT event_type, actor_type, actor_id, target_type, target_id, metadata, created_at
            FROM audit_events
            WHERE target_id = ?
            """,
            (body["postId"],),
        ).fetchone()

    assert post_row == (
        body["postId"],
        "Persistent draft",
        "persistent-draft",
        "draft",
        "markdown",
        body["revisionId"],
        body["createdAt"],
        body["createdAt"],
    )
    assert revision_row == (
        body["revisionId"],
        body["postId"],
        "# Persistent draft\n\nStored body.",
        '{"source":"persistence-test","summary":"Stored summary.","tags":["storage"],"categoryId":null,"seriesId":null}',
        "token:post-writer-token",
        body["createdAt"],
    )
    assert audit_row == (
        "post.created",
        "api_token",
        "token:post-writer-token",
        "post",
        body["postId"],
        f'{{"revisionId":"{body["revisionId"]}"}}',
        body["createdAt"],
    )


def test_create_post_draft_duplicate_slug_returns_conflict_without_side_effects(tmp_path: Path) -> None:
    database_path = tmp_path / "nairi.db"
    client = build_client(database_path)

    first_response = client.post(
        "/api/v1/posts",
        json=draft_payload(),
        headers={"Authorization": "Bearer post-writer-token"},
    )
    second_response = client.post(
        "/api/v1/posts",
        json=draft_payload(),
        headers={"Authorization": "Bearer post-writer-token"},
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json() == {
        "code": "conflict",
        "message": "Post slug already exists",
        "details": {"slug": "persistent-draft"},
        "requestId": "unavailable",
    }

    with sqlite3.connect(database_path) as connection:
        counts = connection.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM posts),
                (SELECT COUNT(*) FROM post_revisions),
                (SELECT COUNT(*) FROM audit_events)
            """
        ).fetchone()

    assert counts == (1, 1, 1)


def persistence_counts(database_path: Path) -> tuple[int, int, int]:
    if not database_path.exists():
        return (0, 0, 0)
    with sqlite3.connect(database_path) as connection:
        table_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM sqlite_master
            WHERE type = 'table' AND name IN ('posts', 'post_revisions', 'audit_events')
            """
        ).fetchone()[0]
        if table_count == 0:
            return (0, 0, 0)
        return connection.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM posts),
                (SELECT COUNT(*) FROM post_revisions),
                (SELECT COUNT(*) FROM audit_events)
            """
        ).fetchone()


def test_create_post_draft_rejects_invalid_content_fields_without_side_effects(tmp_path: Path) -> None:
    database_path = tmp_path / "nairi.db"
    client = build_client(database_path)
    payload = draft_payload()
    payload.update({"title": "   ", "slug": "Invalid Slug", "content": ""})

    response = client.post(
        "/api/v1/posts",
        json=payload,
        headers={"Authorization": "Bearer post-writer-token"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "code": "invalid_request",
        "message": "Invalid post draft request",
        "details": {
            "title": "Title is required",
            "slug": "Slug must contain only lowercase letters, numbers, and hyphens",
            "content": "Content is required",
        },
        "requestId": "unavailable",
    }
    assert persistence_counts(database_path) == (0, 0, 0)
