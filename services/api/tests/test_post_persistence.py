import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from nairi_api.config import Settings
from nairi_api.main import create_app


def build_client(database_path: Path) -> TestClient:
    settings = Settings(
        api_tokens={"post-writer-token": ["posts:write"]},
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
