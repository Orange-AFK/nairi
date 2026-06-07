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


def test_list_post_drafts_returns_created_drafts_for_reader_scope(tmp_path: Path) -> None:
    database_path = tmp_path / "nairi.db"
    client = build_client(database_path)
    second_payload = draft_payload()
    second_payload.update(
        {
            "title": "Second persistent draft",
            "slug": "second-persistent-draft",
            "summary": "Second stored summary.",
            "tags": ["storage", "second"],
            "metadata": {"source": "second-persistence-test"},
        }
    )

    first_create_response = client.post(
        "/api/v1/posts",
        json=draft_payload(),
        headers={"Authorization": "Bearer post-writer-token"},
    )
    second_create_response = client.post(
        "/api/v1/posts",
        json=second_payload,
        headers={"Authorization": "Bearer post-writer-token"},
    )

    list_response = client.get(
        "/api/v1/posts?status=draft",
        headers={"Authorization": "Bearer post-reader-token"},
    )

    assert first_create_response.status_code == 201
    assert second_create_response.status_code == 201
    assert list_response.status_code == 200
    assert list_response.json() == {
        "items": [
            {
                "postId": first_create_response.json()["postId"],
                "title": "Persistent draft",
                "slug": "persistent-draft",
                "status": "draft",
                "contentFormat": "markdown",
                "summary": "Stored summary.",
                "tags": ["storage"],
                "categoryId": None,
                "seriesId": None,
                "metadata": {"source": "persistence-test"},
                "revisionId": first_create_response.json()["revisionId"],
                "createdAt": first_create_response.json()["createdAt"],
                "updatedAt": first_create_response.json()["createdAt"],
            },
            {
                "postId": second_create_response.json()["postId"],
                "title": "Second persistent draft",
                "slug": "second-persistent-draft",
                "status": "draft",
                "contentFormat": "markdown",
                "summary": "Second stored summary.",
                "tags": ["storage", "second"],
                "categoryId": None,
                "seriesId": None,
                "metadata": {"source": "second-persistence-test"},
                "revisionId": second_create_response.json()["revisionId"],
                "createdAt": second_create_response.json()["createdAt"],
                "updatedAt": second_create_response.json()["createdAt"],
            },
        ],
        "nextCursor": None,
    }


def test_list_post_drafts_requires_posts_read_scope(tmp_path: Path) -> None:
    database_path = tmp_path / "nairi.db"
    client = build_client(database_path)

    response = client.get(
        "/api/v1/posts?status=draft",
        headers={"Authorization": "Bearer post-writer-token"},
    )

    assert response.status_code == 403
    assert response.json() == {
        "code": "forbidden",
        "message": "Missing required scope",
        "details": {"requiredScope": "posts:read"},
        "requestId": "unavailable",
    }


def test_list_post_drafts_returns_empty_items_when_no_drafts(tmp_path: Path) -> None:
    database_path = tmp_path / "nairi.db"
    client = build_client(database_path)

    response = client.get(
        "/api/v1/posts?status=draft",
        headers={"Authorization": "Bearer post-reader-token"},
    )

    assert response.status_code == 200
    assert response.json() == {"items": [], "nextCursor": None}


def test_update_post_draft_creates_revision_and_updates_current_draft(tmp_path: Path) -> None:
    database_path = tmp_path / "nairi.db"
    settings = Settings(
        api_tokens={
            "post-writer-token": ["posts:write"],
            "post-reader-token": ["posts:read"],
        },
        database_path=str(database_path),
    )
    timestamps = iter(
        [
            datetime(2026, 6, 7, 8, 9, 10, tzinfo=UTC),
            datetime(2026, 6, 7, 8, 10, 11, tzinfo=UTC),
        ]
    )
    app = create_app(settings=settings)
    app.state.post_store = PostStore(str(database_path), clock=lambda: next(timestamps))
    client = TestClient(app)

    create_response = client.post(
        "/api/v1/posts",
        json=draft_payload(),
        headers={"Authorization": "Bearer post-writer-token"},
    )
    post_id = create_response.json()["postId"]
    original_revision_id = create_response.json()["revisionId"]

    update_response = client.patch(
        f"/api/v1/posts/{post_id}",
        json={
            "title": "Updated persistent draft",
            "slug": "updated-persistent-draft",
            "contentFormat": "mdx",
            "content": "# Updated persistent draft\n\nUpdated body.",
            "summary": "Updated stored summary.",
            "tags": ["storage", "updated"],
            "categoryId": "category-updated",
            "seriesId": "series-updated",
            "metadata": {"source": "update-test"},
            "expectedRevisionId": original_revision_id,
        },
        headers={"Authorization": "Bearer post-writer-token"},
    )

    assert create_response.status_code == 201
    assert update_response.status_code == 200
    update_body = update_response.json()
    assert update_body == {
        "postId": post_id,
        "status": "draft",
        "revisionId": "revision-persistent-draft-2",
        "updatedAt": "2026-06-07T08:10:11Z",
    }

    read_response = client.get(
        f"/api/v1/posts/{post_id}",
        headers={"Authorization": "Bearer post-reader-token"},
    )
    assert read_response.status_code == 200
    assert read_response.json() == {
        "postId": post_id,
        "title": "Updated persistent draft",
        "slug": "updated-persistent-draft",
        "status": "draft",
        "contentFormat": "mdx",
        "content": "# Updated persistent draft\n\nUpdated body.",
        "summary": "Updated stored summary.",
        "tags": ["storage", "updated"],
        "categoryId": "category-updated",
        "seriesId": "series-updated",
        "metadata": {"source": "update-test"},
        "revisionId": "revision-persistent-draft-2",
        "createdAt": "2026-06-07T08:09:10Z",
        "updatedAt": "2026-06-07T08:10:11Z",
    }

    with sqlite3.connect(database_path) as connection:
        post_row = connection.execute(
            """
            SELECT title, slug, content_format, current_revision_id, created_at, updated_at
            FROM posts
            WHERE id = ?
            """,
            (post_id,),
        ).fetchone()
        revision_rows = connection.execute(
            """
            SELECT id, post_id, content, metadata, created_by, created_at
            FROM post_revisions
            WHERE post_id = ?
            ORDER BY created_at ASC, id ASC
            """,
            (post_id,),
        ).fetchall()
        audit_rows = connection.execute(
            """
            SELECT event_type, actor_type, actor_id, target_type, target_id, metadata, created_at
            FROM audit_events
            WHERE target_id = ?
            ORDER BY id ASC
            """,
            (post_id,),
        ).fetchall()

    assert post_row == (
        "Updated persistent draft",
        "updated-persistent-draft",
        "mdx",
        "revision-persistent-draft-2",
        "2026-06-07T08:09:10Z",
        "2026-06-07T08:10:11Z",
    )
    assert revision_rows == [
        (
            original_revision_id,
            post_id,
            "# Persistent draft\n\nStored body.",
            '{"source":"persistence-test","summary":"Stored summary.","tags":["storage"],"categoryId":null,"seriesId":null}',
            "token:post-writer-token",
            "2026-06-07T08:09:10Z",
        ),
        (
            "revision-persistent-draft-2",
            post_id,
            "# Updated persistent draft\n\nUpdated body.",
            '{"source":"update-test","summary":"Updated stored summary.","tags":["storage","updated"],"categoryId":"category-updated","seriesId":"series-updated"}',
            "token:post-writer-token",
            "2026-06-07T08:10:11Z",
        ),
    ]
    assert audit_rows == [
        (
            "post.created",
            "api_token",
            "token:post-writer-token",
            "post",
            post_id,
            f'{{"revisionId":"{original_revision_id}"}}',
            "2026-06-07T08:09:10Z",
        ),
        (
            "post.updated",
            "api_token",
            "token:post-writer-token",
            "post",
            post_id,
            '{"revisionId":"revision-persistent-draft-2","previousRevisionId":"revision-persistent-draft-1"}',
            "2026-06-07T08:10:11Z",
        ),
    ]


def test_update_post_draft_requires_posts_write_scope(tmp_path: Path) -> None:
    database_path = tmp_path / "nairi.db"
    client = build_client(database_path)

    response = client.patch(
        "/api/v1/posts/draft-persistent-draft",
        json={**draft_payload(), "expectedRevisionId": "revision-persistent-draft-1"},
        headers={"Authorization": "Bearer post-reader-token"},
    )

    assert response.status_code == 403
    assert response.json() == {
        "code": "forbidden",
        "message": "Missing required scope",
        "details": {"requiredScope": "posts:write"},
        "requestId": "unavailable",
    }


def test_update_post_draft_returns_not_found_for_unknown_post(tmp_path: Path) -> None:
    database_path = tmp_path / "nairi.db"
    client = build_client(database_path)

    response = client.patch(
        "/api/v1/posts/missing-post",
        json={**draft_payload(), "expectedRevisionId": "missing-revision"},
        headers={"Authorization": "Bearer post-writer-token"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "code": "not_found",
        "message": "Post not found",
        "details": {"postId": "missing-post"},
        "requestId": "unavailable",
    }


def test_update_post_draft_rejects_revision_conflict_without_side_effects(tmp_path: Path) -> None:
    database_path = tmp_path / "nairi.db"
    client = build_client(database_path)

    create_response = client.post(
        "/api/v1/posts",
        json=draft_payload(),
        headers={"Authorization": "Bearer post-writer-token"},
    )
    post_id = create_response.json()["postId"]
    response = client.patch(
        f"/api/v1/posts/{post_id}",
        json={**draft_payload(), "title": "Conflicting update", "expectedRevisionId": "stale-revision"},
        headers={"Authorization": "Bearer post-writer-token"},
    )

    assert create_response.status_code == 201
    assert response.status_code == 409
    assert response.json() == {
        "code": "conflict",
        "message": "Post revision conflict",
        "details": {"currentRevisionId": create_response.json()["revisionId"]},
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
        current_row = connection.execute(
            "SELECT title, current_revision_id FROM posts WHERE id = ?",
            (post_id,),
        ).fetchone()

    assert counts == (1, 1, 1)
    assert current_row == ("Persistent draft", create_response.json()["revisionId"])


def test_update_post_draft_rejects_duplicate_slug_without_side_effects(tmp_path: Path) -> None:
    database_path = tmp_path / "nairi.db"
    settings = Settings(
        api_tokens={"post-writer-token": ["posts:write"]},
        database_path=str(database_path),
    )
    client = TestClient(create_app(settings=settings), raise_server_exceptions=False)
    second_payload = draft_payload()
    second_payload.update({"title": "Second persistent draft", "slug": "second-persistent-draft"})

    first_create_response = client.post(
        "/api/v1/posts",
        json=draft_payload(),
        headers={"Authorization": "Bearer post-writer-token"},
    )
    second_create_response = client.post(
        "/api/v1/posts",
        json=second_payload,
        headers={"Authorization": "Bearer post-writer-token"},
    )
    first_post_id = first_create_response.json()["postId"]
    first_revision_id = first_create_response.json()["revisionId"]

    response = client.patch(
        f"/api/v1/posts/{first_post_id}",
        json={
            **draft_payload(),
            "title": "Conflicting slug update",
            "slug": "second-persistent-draft",
            "expectedRevisionId": first_revision_id,
        },
        headers={"Authorization": "Bearer post-writer-token"},
    )

    assert first_create_response.status_code == 201
    assert second_create_response.status_code == 201
    assert response.status_code == 409
    assert response.json() == {
        "code": "conflict",
        "message": "Post slug already exists",
        "details": {"slug": "second-persistent-draft"},
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
        first_row = connection.execute(
            "SELECT title, slug, current_revision_id FROM posts WHERE id = ?",
            (first_post_id,),
        ).fetchone()
        second_row = connection.execute(
            "SELECT title, slug, current_revision_id FROM posts WHERE id = ?",
            (second_create_response.json()["postId"],),
        ).fetchone()

    assert counts == (2, 2, 2)
    assert first_row == ("Persistent draft", "persistent-draft", first_revision_id)
    assert second_row == (
        "Second persistent draft",
        "second-persistent-draft",
        second_create_response.json()["revisionId"],
    )


def test_update_post_draft_rejects_invalid_content_fields_without_side_effects(tmp_path: Path) -> None:
    database_path = tmp_path / "nairi.db"
    client = build_client(database_path)

    create_response = client.post(
        "/api/v1/posts",
        json=draft_payload(),
        headers={"Authorization": "Bearer post-writer-token"},
    )
    post_id = create_response.json()["postId"]
    revision_id = create_response.json()["revisionId"]
    payload = draft_payload()
    payload.update(
        {
            "title": "   ",
            "slug": "Invalid Slug",
            "content": "",
            "expectedRevisionId": revision_id,
        }
    )

    response = client.patch(
        f"/api/v1/posts/{post_id}",
        json=payload,
        headers={"Authorization": "Bearer post-writer-token"},
    )

    assert create_response.status_code == 201
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
    with sqlite3.connect(database_path) as connection:
        counts = connection.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM posts),
                (SELECT COUNT(*) FROM post_revisions),
                (SELECT COUNT(*) FROM audit_events)
            """
        ).fetchone()
        post_row = connection.execute(
            "SELECT title, slug, current_revision_id FROM posts WHERE id = ?",
            (post_id,),
        ).fetchone()

    assert counts == (1, 1, 1)
    assert post_row == ("Persistent draft", "persistent-draft", revision_id)


def test_publish_post_draft_transitions_to_published_and_records_audit(tmp_path: Path) -> None:
    database_path = tmp_path / "nairi.db"
    settings = Settings(
        api_tokens={
            "post-writer-token": ["posts:write"],
            "post-reader-token": ["posts:read"],
            "post-publisher-token": ["posts:publish"],
        },
        database_path=str(database_path),
    )
    timestamps = iter(
        [
            datetime(2026, 6, 7, 8, 9, 10, tzinfo=UTC),
            datetime(2026, 6, 7, 8, 11, 12, tzinfo=UTC),
        ]
    )
    app = create_app(settings=settings)
    app.state.post_store = PostStore(str(database_path), clock=lambda: next(timestamps))
    client = TestClient(app)

    create_response = client.post(
        "/api/v1/posts",
        json=draft_payload(),
        headers={"Authorization": "Bearer post-writer-token"},
    )
    post_id = create_response.json()["postId"]
    revision_id = create_response.json()["revisionId"]

    response = client.post(
        f"/api/v1/posts/{post_id}/publish",
        json={"revisionId": revision_id, "publishMode": "immediate", "scheduledAt": None},
        headers={"Authorization": "Bearer post-publisher-token"},
    )

    assert create_response.status_code == 201
    assert response.status_code == 200
    assert response.json() == {
        "postId": post_id,
        "status": "published",
        "publishedAt": "2026-06-07T08:11:12Z",
        "jobId": f"publish-{post_id}-{revision_id}",
    }
    read_response = client.get(
        f"/api/v1/posts/{post_id}",
        headers={"Authorization": "Bearer post-reader-token"},
    )
    list_response = client.get(
        "/api/v1/posts?status=draft",
        headers={"Authorization": "Bearer post-reader-token"},
    )

    assert read_response.status_code == 200
    assert read_response.json()["status"] == "published"
    assert read_response.json()["publishedAt"] == "2026-06-07T08:11:12Z"
    assert list_response.status_code == 200
    assert list_response.json() == {"items": [], "nextCursor": None}
    with sqlite3.connect(database_path) as connection:
        post_row = connection.execute(
            """
            SELECT status, current_revision_id, published_at, updated_at
            FROM posts
            WHERE id = ?
            """,
            (post_id,),
        ).fetchone()
        revision_count = connection.execute(
            "SELECT COUNT(*) FROM post_revisions WHERE post_id = ?",
            (post_id,),
        ).fetchone()[0]
        audit_rows = connection.execute(
            """
            SELECT event_type, actor_type, actor_id, target_type, target_id, metadata, created_at
            FROM audit_events
            WHERE target_id = ?
            ORDER BY id ASC
            """,
            (post_id,),
        ).fetchall()
        publish_job_row = connection.execute(
            """
            SELECT id, post_id, revision_id, status, scheduled_at, started_at, completed_at, error_code, error_message
            FROM publish_jobs
            WHERE id = ?
            """,
            (f"publish-{post_id}-{revision_id}",),
        ).fetchone()

    assert post_row == ("published", revision_id, "2026-06-07T08:11:12Z", "2026-06-07T08:11:12Z")
    assert revision_count == 1
    assert publish_job_row == (
        f"publish-{post_id}-{revision_id}",
        post_id,
        revision_id,
        "succeeded",
        None,
        "2026-06-07T08:11:12Z",
        "2026-06-07T08:11:12Z",
        None,
        None,
    )
    assert audit_rows == [
        (
            "post.created",
            "api_token",
            "token:post-writer-token",
            "post",
            post_id,
            f'{{"revisionId":"{revision_id}"}}',
            "2026-06-07T08:09:10Z",
        ),
        (
            "post.published",
            "api_token",
            "token:post-publisher-token",
            "post",
            post_id,
            f'{{"revisionId":"{revision_id}","jobId":"publish-{post_id}-{revision_id}"}}',
            "2026-06-07T08:11:12Z",
        ),
    ]


def test_list_published_posts_returns_published_summaries_for_reader_scope(tmp_path: Path) -> None:
    database_path = tmp_path / "nairi.db"
    settings = Settings(
        api_tokens={
            "post-writer-token": ["posts:write"],
            "post-reader-token": ["posts:read"],
            "post-publisher-token": ["posts:publish"],
        },
        database_path=str(database_path),
    )
    timestamps = iter(
        [
            datetime(2026, 6, 7, 8, 9, 10, tzinfo=UTC),
            datetime(2026, 6, 7, 8, 11, 12, tzinfo=UTC),
        ]
    )
    app = create_app(settings=settings)
    app.state.post_store = PostStore(str(database_path), clock=lambda: next(timestamps))
    client = TestClient(app)

    create_response = client.post(
        "/api/v1/posts",
        json=draft_payload(),
        headers={"Authorization": "Bearer post-writer-token"},
    )
    post_id = create_response.json()["postId"]
    revision_id = create_response.json()["revisionId"]
    publish_response = client.post(
        f"/api/v1/posts/{post_id}/publish",
        json={"revisionId": revision_id, "publishMode": "immediate", "scheduledAt": None},
        headers={"Authorization": "Bearer post-publisher-token"},
    )

    list_response = client.get(
        "/api/v1/posts?status=published",
        headers={"Authorization": "Bearer post-reader-token"},
    )

    assert create_response.status_code == 201
    assert publish_response.status_code == 200
    assert list_response.status_code == 200
    assert list_response.json() == {
        "items": [
            {
                "postId": post_id,
                "title": "Persistent draft",
                "slug": "persistent-draft",
                "status": "published",
                "contentFormat": "markdown",
                "summary": "Stored summary.",
                "tags": ["storage"],
                "categoryId": None,
                "seriesId": None,
                "metadata": {"source": "persistence-test"},
                "revisionId": revision_id,
                "publishedAt": "2026-06-07T08:11:12Z",
                "createdAt": "2026-06-07T08:09:10Z",
                "updatedAt": "2026-06-07T08:11:12Z",
            }
        ],
        "nextCursor": None,
    }



def test_get_published_post_returns_published_detail_for_reader_scope(tmp_path: Path) -> None:
    database_path = tmp_path / "nairi.db"
    settings = Settings(
        api_tokens={
            "post-writer-token": ["posts:write"],
            "post-reader-token": ["posts:read"],
            "post-publisher-token": ["posts:publish"],
        },
        database_path=str(database_path),
    )
    timestamps = iter(
        [
            datetime(2026, 6, 7, 8, 9, 10, tzinfo=UTC),
            datetime(2026, 6, 7, 8, 11, 12, tzinfo=UTC),
        ]
    )
    app = create_app(settings=settings)
    app.state.post_store = PostStore(str(database_path), clock=lambda: next(timestamps))
    client = TestClient(app)

    create_response = client.post(
        "/api/v1/posts",
        json=draft_payload(),
        headers={"Authorization": "Bearer post-writer-token"},
    )
    post_id = create_response.json()["postId"]
    revision_id = create_response.json()["revisionId"]
    publish_response = client.post(
        f"/api/v1/posts/{post_id}/publish",
        json={"revisionId": revision_id, "publishMode": "immediate", "scheduledAt": None},
        headers={"Authorization": "Bearer post-publisher-token"},
    )

    read_response = client.get(
        f"/api/v1/posts/{post_id}",
        headers={"Authorization": "Bearer post-reader-token"},
    )

    assert create_response.status_code == 201
    assert publish_response.status_code == 200
    assert read_response.status_code == 200
    assert read_response.json() == {
        "postId": post_id,
        "title": "Persistent draft",
        "slug": "persistent-draft",
        "status": "published",
        "contentFormat": "markdown",
        "content": "# Persistent draft\n\nStored body.",
        "summary": "Stored summary.",
        "tags": ["storage"],
        "categoryId": None,
        "seriesId": None,
        "metadata": {"source": "persistence-test"},
        "revisionId": revision_id,
        "publishedAt": "2026-06-07T08:11:12Z",
        "createdAt": "2026-06-07T08:09:10Z",
        "updatedAt": "2026-06-07T08:11:12Z",
    }


def test_publish_post_draft_adds_published_at_column_for_existing_scaffold_database(tmp_path: Path) -> None:
    database_path = tmp_path / "nairi.db"
    with sqlite3.connect(database_path) as connection:
        connection.executescript(
            """
            CREATE TABLE posts (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                slug TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL,
                content_format TEXT NOT NULL,
                current_revision_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE post_revisions (
                id TEXT PRIMARY KEY,
                post_id TEXT NOT NULL REFERENCES posts(id),
                content TEXT NOT NULL,
                metadata TEXT NOT NULL,
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                actor_type TEXT NOT NULL,
                actor_id TEXT NOT NULL,
                target_type TEXT NOT NULL,
                target_id TEXT NOT NULL,
                metadata TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        connection.execute(
            """
            INSERT INTO posts (id, title, slug, status, content_format, current_revision_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "draft-persistent-draft",
                "Persistent draft",
                "persistent-draft",
                "draft",
                "markdown",
                "revision-persistent-draft-1",
                "2026-06-07T08:09:10Z",
                "2026-06-07T08:09:10Z",
            ),
        )
        connection.execute(
            """
            INSERT INTO post_revisions (id, post_id, content, metadata, created_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "revision-persistent-draft-1",
                "draft-persistent-draft",
                "# Persistent draft\n\nStored body.",
                '{"source":"persistence-test","summary":"Stored summary.","tags":["storage"],"categoryId":null,"seriesId":null}',
                "token:post-writer-token",
                "2026-06-07T08:09:10Z",
            ),
        )
        connection.execute(
            """
            INSERT INTO audit_events (event_type, actor_type, actor_id, target_type, target_id, metadata, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "post.created",
                "api_token",
                "token:post-writer-token",
                "post",
                "draft-persistent-draft",
                '{"revisionId":"revision-persistent-draft-1"}',
                "2026-06-07T08:09:10Z",
            ),
        )
    settings = Settings(
        api_tokens={"post-publisher-token": ["posts:publish"]},
        database_path=str(database_path),
    )
    app = create_app(settings=settings)
    app.state.post_store = PostStore(
        str(database_path),
        clock=lambda: datetime(2026, 6, 7, 8, 11, 12, tzinfo=UTC),
    )
    client = TestClient(app, raise_server_exceptions=False)

    response = client.post(
        "/api/v1/posts/draft-persistent-draft/publish",
        json={"revisionId": "revision-persistent-draft-1", "publishMode": "immediate", "scheduledAt": None},
        headers={"Authorization": "Bearer post-publisher-token"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "postId": "draft-persistent-draft",
        "status": "published",
        "publishedAt": "2026-06-07T08:11:12Z",
        "jobId": "publish-draft-persistent-draft-revision-persistent-draft-1",
    }
    with sqlite3.connect(database_path) as connection:
        post_row = connection.execute(
            "SELECT status, published_at, updated_at FROM posts WHERE id = ?",
            ("draft-persistent-draft",),
        ).fetchone()

    assert post_row == ("published", "2026-06-07T08:11:12Z", "2026-06-07T08:11:12Z")


def test_publish_post_draft_requires_posts_publish_scope(tmp_path: Path) -> None:
    database_path = tmp_path / "nairi.db"
    client = build_client(database_path)

    response = client.post(
        "/api/v1/posts/draft-persistent-draft/publish",
        json={"revisionId": "revision-persistent-draft-1", "publishMode": "immediate", "scheduledAt": None},
        headers={"Authorization": "Bearer post-writer-token"},
    )

    assert response.status_code == 403
    assert response.json() == {
        "code": "forbidden",
        "message": "Missing required scope",
        "details": {"requiredScope": "posts:publish"},
        "requestId": "unavailable",
    }


def test_publish_post_draft_returns_not_found_for_unknown_post(tmp_path: Path) -> None:
    database_path = tmp_path / "nairi.db"
    settings = Settings(
        api_tokens={"post-publisher-token": ["posts:publish"]},
        database_path=str(database_path),
    )
    client = TestClient(create_app(settings=settings))

    response = client.post(
        "/api/v1/posts/missing-post/publish",
        json={"revisionId": "missing-revision", "publishMode": "immediate", "scheduledAt": None},
        headers={"Authorization": "Bearer post-publisher-token"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "code": "not_found",
        "message": "Post not found",
        "details": {"postId": "missing-post"},
        "requestId": "unavailable",
    }
    assert persistence_counts(database_path) == (0, 0, 0)


def test_publish_post_draft_rejects_revision_conflict_without_side_effects(tmp_path: Path) -> None:
    database_path = tmp_path / "nairi.db"
    settings = Settings(
        api_tokens={
            "post-writer-token": ["posts:write"],
            "post-publisher-token": ["posts:publish"],
        },
        database_path=str(database_path),
    )
    client = TestClient(create_app(settings=settings))

    create_response = client.post(
        "/api/v1/posts",
        json=draft_payload(),
        headers={"Authorization": "Bearer post-writer-token"},
    )
    post_id = create_response.json()["postId"]
    current_revision_id = create_response.json()["revisionId"]

    response = client.post(
        f"/api/v1/posts/{post_id}/publish",
        json={"revisionId": "stale-revision", "publishMode": "immediate", "scheduledAt": None},
        headers={"Authorization": "Bearer post-publisher-token"},
    )

    assert create_response.status_code == 201
    assert response.status_code == 409
    assert response.json() == {
        "code": "conflict",
        "message": "Post revision conflict",
        "details": {"currentRevisionId": current_revision_id},
        "requestId": "unavailable",
    }
    with sqlite3.connect(database_path) as connection:
        counts = connection.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM posts WHERE status = 'draft'),
                (SELECT COUNT(*) FROM post_revisions),
                (SELECT COUNT(*) FROM audit_events),
                (SELECT COUNT(*) FROM publish_jobs)
            """
        ).fetchone()
        post_row = connection.execute(
            "SELECT current_revision_id FROM posts WHERE id = ?",
            (post_id,),
        ).fetchone()

    assert counts == (1, 1, 1, 0)
    assert post_row == (current_revision_id,)


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
