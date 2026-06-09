import sqlite3
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

from fastapi.testclient import TestClient

from nairi_api.config import Settings
from nairi_api.invalidation_dispatch import PublicInvalidationDispatchResult
from nairi_api.main import create_app
from nairi_api.posts import (
    audit_token_actor_id,
    PostDraftInput,
    PostStore,
    PostStoreMigration,
    PostStoreMigrationError,
    rehearse_post_store_migration,
    run_schema_migrations,
)
from nairi_api.taxonomy import (
    CategoryNotFoundError,
    CategoryStore,
    SeriesNotFoundError,
    SeriesStore,
    TagNotFoundError,
    TagStore,
)


def seed_taxonomy(db: str) -> tuple[CategoryStore, TagStore, SeriesStore]:
    """Seed taxonomy entities for tests that need valid taxonomy references."""
    cat_store = CategoryStore(db)
    tag_store = TagStore(db)
    series_store = SeriesStore(db)
    cat_store.create_category("Guides", "guides", "Tutorial guides")
    cat_store.create_category("Updated", "updated", "Updated items")
    cat_store.create_category("Public", "public", "Public content")
    tag_store.create_tag("storage", "storage")
    tag_store.create_tag("second", "second")
    tag_store.create_tag("updated", "updated")
    tag_store.create_tag("featured", "featured")
    tag_store.create_tag("public", "public")
    series_store.create_series("Updated Series", "updated", "An updated series")
    return cat_store, tag_store, series_store


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
        "tags": [],
        "categoryId": None,
        "seriesId": None,
        "metadata": {"source": "persistence-test"},
    }


class RecordingPublicInvalidationDispatcher:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def dispatch(self, *, surfaces: Sequence[str], published_at: str | None) -> PublicInvalidationDispatchResult:
        self.calls.append({"surfaces": list(surfaces), "published_at": published_at})
        return PublicInvalidationDispatchResult(
            status="dispatch_skipped",
            reason="no_dispatcher_configured",
            attempted=True,
            attempted_at="2026-06-07T08:12:13Z",
        )


class FailingPublicInvalidationDispatcher:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def dispatch(self, *, surfaces: Sequence[str], published_at: str | None) -> PublicInvalidationDispatchResult:
        self.calls.append({"surfaces": list(surfaces), "published_at": published_at})
        raise RuntimeError("simulated dispatcher failure")


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
            "tags": [],
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
                "tags": [],
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
                "tags": [],
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
            '{"source":"persistence-test","summary":"Stored summary.","tags":[],"categoryId":null,"seriesId":null}',
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
    dispatcher = RecordingPublicInvalidationDispatcher()
    app.state.public_invalidation_dispatcher = dispatcher
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
        "publicInvalidation": {
            "mode": "recorded",
            "surfaces": [
                "/posts",
                "/posts/persistent-draft",
                "/rss.xml",
                "/sitemap.xml",
            ],
            "execution": {
                "status": "recorded",
                "executor": "none",
                "executedAt": "2026-06-07T08:11:12Z",
                "errorCode": None,
                "errorMessage": None,
            },
            "dispatch": {
                "status": "dispatch_skipped",
                "reason": "no_dispatcher_configured",
                "attempted": True,
                "attemptedAt": "2026-06-07T08:12:13Z",
            },
        },
    }
    assert dispatcher.calls == [
        {
            "surfaces": ["/posts", "/posts/persistent-draft", "/rss.xml", "/sitemap.xml"],
            "published_at": "2026-06-07T08:11:12Z",
        }
    ]
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
            SELECT
                id,
                post_id,
                revision_id,
                status,
                scheduled_at,
                started_at,
                completed_at,
                error_code,
                error_message,
                public_invalidation_surfaces,
                public_invalidation_status,
                public_invalidation_executor,
                public_invalidation_executed_at,
                public_invalidation_error_code,
                public_invalidation_error_message,
                public_invalidation_dispatch_status,
                public_invalidation_dispatch_reason,
                public_invalidation_dispatch_attempted,
                public_invalidation_dispatch_attempted_at
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
        '["/posts","/posts/persistent-draft","/rss.xml","/sitemap.xml"]',
        "recorded",
        "none",
        "2026-06-07T08:11:12Z",
        None,
        None,
        "dispatch_skipped",
        "no_dispatcher_configured",
        1,
        "2026-06-07T08:12:13Z",
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


def test_request_publish_review_persists_pending_request_without_publishing(tmp_path: Path) -> None:
    database_path = tmp_path / "nairi.db"
    settings = Settings(
        api_tokens={
            "post-writer-token": ["posts:write"],
            "post-reader-token": ["posts:read"],
            "post-publisher-token": ["posts:publish"],
        },
        database_path=str(database_path),
    )
    app = create_app(settings=settings)
    app.state.post_store = PostStore(
        str(database_path),
        clock=lambda: datetime(2026, 6, 7, 8, 11, 12, tzinfo=UTC),
    )
    client = TestClient(app)
    create_response = client.post(
        "/api/v1/posts",
        json=draft_payload(),
        headers={"Authorization": "Bearer post-writer-token"},
    )
    post_id = create_response.json()["postId"]
    revision_id = create_response.json()["revisionId"]

    response = client.post(
        f"/api/v1/posts/{post_id}/publish-requests",
        json={"revisionId": revision_id},
        headers={"Authorization": "Bearer post-publisher-token"},
    )

    assert response.status_code == 201
    assert response.json() == {
        "requestId": f"publish-request-{post_id}-{revision_id}",
        "postId": post_id,
        "revisionId": revision_id,
        "status": "pending",
        "requestedAt": "2026-06-07T08:11:12Z",
    }
    read_response = client.get(
        f"/api/v1/posts/{post_id}",
        headers={"Authorization": "Bearer post-reader-token"},
    )

    assert read_response.status_code == 200
    assert read_response.json()["status"] == "draft"
    with sqlite3.connect(database_path) as connection:
        post_row = connection.execute(
            "SELECT status, current_revision_id, published_at FROM posts WHERE id = ?",
            (post_id,),
        ).fetchone()
        publish_request_row = connection.execute(
            """
            SELECT id, post_id, revision_id, status, requested_at
            FROM publish_requests
            WHERE id = ?
            """,
            (f"publish-request-{post_id}-{revision_id}",),
        ).fetchone()
        publish_job_count = connection.execute("SELECT COUNT(*) FROM publish_jobs").fetchone()[0]
        audit_rows = connection.execute(
            """
            SELECT event_type, actor_type, actor_id, target_type, target_id, metadata, created_at
            FROM audit_events
            WHERE event_type = 'post.publish_requested'
            """
        ).fetchall()

    assert post_row == ("draft", revision_id, None)
    assert publish_request_row == (
        f"publish-request-{post_id}-{revision_id}",
        post_id,
        revision_id,
        "pending",
        "2026-06-07T08:11:12Z",
    )
    assert publish_job_count == 0
    assert audit_rows == [
        (
            "post.publish_requested",
            "api_token",
            audit_token_actor_id("post-publisher-token"),
            "post",
            post_id,
            f'{{"revisionId":"{revision_id}","requestId":"publish-request-{post_id}-{revision_id}"}}',
            "2026-06-07T08:11:12Z",
        )
    ]


def test_request_publish_review_is_idempotent_for_existing_pending_request(tmp_path: Path) -> None:
    database_path = tmp_path / "nairi.db"
    settings = Settings(
        api_tokens={
            "post-writer-token": ["posts:write"],
            "post-publisher-token": ["posts:publish"],
        },
        database_path=str(database_path),
    )
    timestamps = iter(
        [
            datetime(2026, 6, 7, 8, 11, 12, tzinfo=UTC),
            datetime(2026, 6, 7, 8, 12, 13, tzinfo=UTC),
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
    request_body = {"revisionId": revision_id}

    first_response = client.post(
        f"/api/v1/posts/{post_id}/publish-requests",
        json=request_body,
        headers={"Authorization": "Bearer post-publisher-token"},
    )
    second_response = client.post(
        f"/api/v1/posts/{post_id}/publish-requests",
        json=request_body,
        headers={"Authorization": "Bearer post-publisher-token"},
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    assert second_response.json() == first_response.json()
    with sqlite3.connect(database_path) as connection:
        request_count = connection.execute("SELECT COUNT(*) FROM publish_requests").fetchone()[0]
        audit_count = connection.execute(
            "SELECT COUNT(*) FROM audit_events WHERE event_type = 'post.publish_requested'"
        ).fetchone()[0]
    assert request_count == 1
    assert audit_count == 1


def test_resolve_publish_review_approves_pending_request_without_publishing(tmp_path: Path) -> None:
    database_path = tmp_path / "nairi.db"
    settings = Settings(
        api_tokens={
            "post-writer-token": ["posts:write"],
            "post-publisher-token": ["posts:publish"],
            "admin-token": ["admin:all"],
        },
        database_path=str(database_path),
    )
    timestamps = iter(
        [
            datetime(2026, 6, 7, 8, 9, 10, tzinfo=UTC),
            datetime(2026, 6, 7, 8, 11, 12, tzinfo=UTC),
            datetime(2026, 6, 7, 8, 13, 14, tzinfo=UTC),
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
    request_id = f"publish-request-{post_id}-{revision_id}"
    client.post(
        f"/api/v1/posts/{post_id}/publish-requests",
        json={"revisionId": revision_id},
        headers={"Authorization": "Bearer post-publisher-token"},
    )

    response = client.post(
        f"/api/v1/publish-requests/{request_id}/resolve",
        json={"status": "approved"},
        headers={"Authorization": "Bearer admin-token"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "requestId": request_id,
        "postId": post_id,
        "revisionId": revision_id,
        "status": "approved",
        "requestedAt": "2026-06-07T08:11:12Z",
        "resolvedAt": "2026-06-07T08:13:14Z",
    }
    read_response = client.get(
        f"/api/v1/posts/{post_id}",
        headers={"Authorization": "Bearer admin-token"},
    )
    assert read_response.status_code == 200
    assert read_response.json()["status"] == "draft"
    with sqlite3.connect(database_path) as connection:
        publish_request_row = connection.execute(
            """
            SELECT status, resolved_at
            FROM publish_requests
            WHERE id = ?
            """,
            (request_id,),
        ).fetchone()
        publish_job_count = connection.execute("SELECT COUNT(*) FROM publish_jobs").fetchone()[0]
        audit_rows = connection.execute(
            """
            SELECT event_type, actor_type, actor_id, target_type, target_id, metadata, created_at
            FROM audit_events
            WHERE event_type = 'admin.publish_request.resolve'
            """
        ).fetchall()
    assert publish_request_row == ("approved", "2026-06-07T08:13:14Z")
    assert publish_job_count == 0
    assert audit_rows == [
        (
            "admin.publish_request.resolve",
            "api_token",
            audit_token_actor_id("admin-token"),
            "publish_request",
            request_id,
            f'{{"postId":"{post_id}","revisionId":"{revision_id}","status":"approved"}}',
            "2026-06-07T08:13:14Z",
        )
    ]


def test_resolve_publish_review_rejects_repeat_resolution_without_side_effects(tmp_path: Path) -> None:
    database_path = tmp_path / "nairi.db"
    settings = Settings(
        api_tokens={
            "post-writer-token": ["posts:write"],
            "post-publisher-token": ["posts:publish"],
            "admin-token": ["admin:all"],
        },
        database_path=str(database_path),
    )
    timestamps = iter(
        [
            datetime(2026, 6, 7, 8, 9, 10, tzinfo=UTC),
            datetime(2026, 6, 7, 8, 11, 12, tzinfo=UTC),
            datetime(2026, 6, 7, 8, 13, 14, tzinfo=UTC),
            datetime(2026, 6, 7, 8, 15, 16, tzinfo=UTC),
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
    request_id = f"publish-request-{post_id}-{revision_id}"
    client.post(
        f"/api/v1/posts/{post_id}/publish-requests",
        json={"revisionId": revision_id},
        headers={"Authorization": "Bearer post-publisher-token"},
    )
    first_response = client.post(
        f"/api/v1/publish-requests/{request_id}/resolve",
        json={"status": "rejected"},
        headers={"Authorization": "Bearer admin-token"},
    )

    second_response = client.post(
        f"/api/v1/publish-requests/{request_id}/resolve",
        json={"status": "approved"},
        headers={"Authorization": "Bearer admin-token"},
    )

    assert first_response.status_code == 200
    assert first_response.json()["status"] == "rejected"
    assert second_response.status_code == 409
    assert second_response.json()["code"] == "conflict"
    with sqlite3.connect(database_path) as connection:
        request_row = connection.execute(
            "SELECT status, resolved_at FROM publish_requests WHERE id = ?",
            (request_id,),
        ).fetchone()
        audit_count = connection.execute(
            "SELECT COUNT(*) FROM audit_events WHERE event_type = 'admin.publish_request.resolve'"
        ).fetchone()[0]
        publish_job_count = connection.execute("SELECT COUNT(*) FROM publish_jobs").fetchone()[0]
    assert request_row == ("rejected", "2026-06-07T08:13:14Z")
    assert audit_count == 1
    assert publish_job_count == 0


def test_resolve_publish_review_requires_admin_all_scope(tmp_path: Path) -> None:
    database_path = tmp_path / "nairi.db"
    settings = Settings(
        api_tokens={
            "post-writer-token": ["posts:write"],
            "post-publisher-token": ["posts:publish"],
        },
        database_path=str(database_path),
    )
    app = create_app(settings=settings)
    app.state.post_store = PostStore(str(database_path))
    client = TestClient(app)
    create_response = client.post(
        "/api/v1/posts",
        json=draft_payload(),
        headers={"Authorization": "Bearer post-writer-token"},
    )
    post_id = create_response.json()["postId"]
    revision_id = create_response.json()["revisionId"]
    request_id = f"publish-request-{post_id}-{revision_id}"
    client.post(
        f"/api/v1/posts/{post_id}/publish-requests",
        json={"revisionId": revision_id},
        headers={"Authorization": "Bearer post-publisher-token"},
    )

    response = client.post(
        f"/api/v1/publish-requests/{request_id}/resolve",
        json={"status": "approved"},
        headers={"Authorization": "Bearer post-publisher-token"},
    )

    assert response.status_code == 403
    assert response.json()["code"] == "forbidden"
    with sqlite3.connect(database_path) as connection:
        request_row = connection.execute(
            "SELECT status, resolved_at FROM publish_requests WHERE id = ?",
            (request_id,),
        ).fetchone()
        audit_count = connection.execute(
            "SELECT COUNT(*) FROM audit_events WHERE event_type = 'admin.publish_request.resolve'"
        ).fetchone()[0]
    assert request_row == ("pending", None)
    assert audit_count == 0


def test_resolve_publish_review_rejects_invalid_status_before_side_effects(tmp_path: Path) -> None:
    database_path = tmp_path / "nairi.db"
    settings = Settings(
        api_tokens={
            "post-writer-token": ["posts:write"],
            "post-publisher-token": ["posts:publish"],
            "admin-token": ["admin:all"],
        },
        database_path=str(database_path),
    )
    app = create_app(settings=settings)
    app.state.post_store = PostStore(str(database_path))
    client = TestClient(app)
    create_response = client.post(
        "/api/v1/posts",
        json=draft_payload(),
        headers={"Authorization": "Bearer post-writer-token"},
    )
    post_id = create_response.json()["postId"]
    revision_id = create_response.json()["revisionId"]
    request_id = f"publish-request-{post_id}-{revision_id}"
    client.post(
        f"/api/v1/posts/{post_id}/publish-requests",
        json={"revisionId": revision_id},
        headers={"Authorization": "Bearer post-publisher-token"},
    )

    response = client.post(
        f"/api/v1/publish-requests/{request_id}/resolve",
        json={"status": "published"},
        headers={"Authorization": "Bearer admin-token"},
    )

    assert response.status_code == 400
    assert response.json()["code"] == "invalid_request"
    with sqlite3.connect(database_path) as connection:
        request_row = connection.execute(
            "SELECT status, resolved_at FROM publish_requests WHERE id = ?",
            (request_id,),
        ).fetchone()
        audit_count = connection.execute(
            "SELECT COUNT(*) FROM audit_events WHERE event_type = 'admin.publish_request.resolve'"
        ).fetchone()[0]
        publish_job_count = connection.execute("SELECT COUNT(*) FROM publish_jobs").fetchone()[0]
    assert request_row == ("pending", None)
    assert audit_count == 0
    assert publish_job_count == 0


def test_request_publish_review_rejects_existing_resolved_request_without_side_effects(tmp_path: Path) -> None:
    database_path = tmp_path / "nairi.db"
    settings = Settings(
        api_tokens={
            "post-writer-token": ["posts:write"],
            "post-publisher-token": ["posts:publish"],
            "admin-token": ["admin:all"],
        },
        database_path=str(database_path),
    )
    timestamps = iter(
        [
            datetime(2026, 6, 7, 8, 9, 10, tzinfo=UTC),
            datetime(2026, 6, 7, 8, 11, 12, tzinfo=UTC),
            datetime(2026, 6, 7, 8, 13, 14, tzinfo=UTC),
            datetime(2026, 6, 7, 8, 15, 16, tzinfo=UTC),
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
    request_id = f"publish-request-{post_id}-{revision_id}"
    request_body = {"revisionId": revision_id}
    first_request_response = client.post(
        f"/api/v1/posts/{post_id}/publish-requests",
        json=request_body,
        headers={"Authorization": "Bearer post-publisher-token"},
    )
    resolve_response = client.post(
        f"/api/v1/publish-requests/{request_id}/resolve",
        json={"status": "approved"},
        headers={"Authorization": "Bearer admin-token"},
    )

    second_request_response = client.post(
        f"/api/v1/posts/{post_id}/publish-requests",
        json=request_body,
        headers={"Authorization": "Bearer post-publisher-token"},
    )

    assert first_request_response.status_code == 201
    assert resolve_response.status_code == 200
    assert second_request_response.status_code == 409
    assert second_request_response.json()["code"] == "conflict"
    with sqlite3.connect(database_path) as connection:
        request_row = connection.execute(
            "SELECT status, requested_at, resolved_at FROM publish_requests WHERE id = ?",
            (request_id,),
        ).fetchone()
        publish_request_audit_count = connection.execute(
            "SELECT COUNT(*) FROM audit_events WHERE event_type = 'post.publish_requested'"
        ).fetchone()[0]
        resolve_audit_count = connection.execute(
            "SELECT COUNT(*) FROM audit_events WHERE event_type = 'admin.publish_request.resolve'"
        ).fetchone()[0]
        publish_job_count = connection.execute("SELECT COUNT(*) FROM publish_jobs").fetchone()[0]
    assert request_row == ("approved", "2026-06-07T08:11:12Z", "2026-06-07T08:13:14Z")
    assert publish_request_audit_count == 1
    assert resolve_audit_count == 1
    assert publish_job_count == 0


def test_request_publish_review_rejects_stale_revision_without_side_effects(tmp_path: Path) -> None:
    database_path = tmp_path / "nairi.db"
    settings = Settings(
        api_tokens={"post-writer-token": ["posts:write"], "post-publisher-token": ["posts:publish"]},
        database_path=str(database_path),
    )
    app = create_app(settings=settings)
    app.state.post_store = PostStore(str(database_path))
    client = TestClient(app)
    post_id = client.post(
        "/api/v1/posts",
        json=draft_payload(),
        headers={"Authorization": "Bearer post-writer-token"},
    ).json()["postId"]

    response = client.post(
        f"/api/v1/posts/{post_id}/publish-requests",
        json={"revisionId": "stale-revision"},
        headers={"Authorization": "Bearer post-publisher-token"},
    )

    assert response.status_code == 409
    assert response.json()["code"] == "conflict"
    with sqlite3.connect(database_path) as connection:
        request_count = connection.execute("SELECT COUNT(*) FROM publish_requests").fetchone()[0]
        audit_count = connection.execute(
            "SELECT COUNT(*) FROM audit_events WHERE event_type = 'post.publish_requested'"
        ).fetchone()[0]
    assert request_count == 0
    assert audit_count == 0


def test_publish_post_records_dispatch_failure_without_rolling_back_publish(tmp_path: Path) -> None:
    database_path = tmp_path / "nairi.db"
    settings = Settings(
        api_tokens={
            "post-writer-token": ["posts:write"],
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
    dispatcher = FailingPublicInvalidationDispatcher()
    app.state.public_invalidation_dispatcher = dispatcher
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

    assert response.status_code == 200
    assert response.json()["status"] == "published"
    assert response.json()["publicInvalidation"]["dispatch"] == {
        "status": "dispatch_failed",
        "reason": "dispatcher_exception",
        "attempted": True,
        "attemptedAt": "2026-06-07T08:11:12Z",
    }
    assert dispatcher.calls == [
        {
            "surfaces": ["/posts", "/posts/persistent-draft", "/rss.xml", "/sitemap.xml"],
            "published_at": "2026-06-07T08:11:12Z",
        }
    ]

    with sqlite3.connect(database_path) as connection:
        post_row = connection.execute(
            "SELECT status, published_at FROM posts WHERE id = ?",
            (post_id,),
        ).fetchone()
        dispatch_row = connection.execute(
            """
            SELECT
                public_invalidation_dispatch_status,
                public_invalidation_dispatch_reason,
                public_invalidation_dispatch_attempted,
                public_invalidation_dispatch_attempted_at
            FROM publish_jobs
            WHERE id = ?
            """,
            (f"publish-{post_id}-{revision_id}",),
        ).fetchone()

    assert post_row == ("published", "2026-06-07T08:11:12Z")
    assert dispatch_row == (
        "dispatch_failed",
        "dispatcher_exception",
        1,
        "2026-06-07T08:11:12Z",
    )


def test_record_public_invalidation_dispatch_requires_existing_publish_job(tmp_path: Path) -> None:
    store = PostStore(str(tmp_path / "nairi.db"))

    try:
        store.record_public_invalidation_dispatch(
            "missing-job",
            status="dispatch_skipped",
            reason="no_dispatcher_configured",
            attempted=False,
            attempted_at=None,
        )
    except Exception as error:
        assert type(error).__name__ == "PublishJobNotFoundError"
        assert getattr(error, "job_id") == "missing-job"
    else:
        raise AssertionError("expected missing publish job to fail closed")


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
                "tags": [],
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


def test_list_published_posts_filters_by_tag_category_and_series(tmp_path: Path) -> None:
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
            datetime(2026, 6, 7, 8, 1, 0, tzinfo=UTC),
            datetime(2026, 6, 7, 8, 2, 0, tzinfo=UTC),
            datetime(2026, 6, 7, 8, 3, 0, tzinfo=UTC),
            datetime(2026, 6, 7, 8, 4, 0, tzinfo=UTC),
            datetime(2026, 6, 7, 8, 5, 0, tzinfo=UTC),
            datetime(2026, 6, 7, 8, 6, 0, tzinfo=UTC),
        ]
    )
    app = create_app(settings=settings)
    app.state.post_store = PostStore(str(database_path), clock=lambda: next(timestamps))
    client = TestClient(app)

    matching_payload = draft_payload()
    matching_payload.update(
        {
            "title": "Matching published post",
            "slug": "matching-published-post",
            "summary": "Matching summary.",
            "tags": ["storage", "featured"],
            "categoryId": "category-guides",
            "seriesId": "series-api-core",
            "metadata": {"source": "matching-filter-test"},
        }
    )
    tag_only_payload = draft_payload()
    tag_only_payload.update(
        {
            "title": "Tag only published post",
            "slug": "tag-only-published-post",
            "summary": "Tag only summary.",
            "tags": ["featured"],
            "categoryId": "category-not-guides",
            "seriesId": "series-other",
            "metadata": {"source": "tag-filter-test"},
        }
    )
    unrelated_payload = draft_payload()
    unrelated_payload.update(
        {
            "title": "Unrelated published post",
            "slug": "unrelated-published-post",
            "summary": "Unrelated summary.",
            "tags": ["other"],
            "categoryId": "category-other",
            "seriesId": "series-other",
            "metadata": {"source": "unrelated-filter-test"},
        }
    )

    created_posts = []
    for payload in (matching_payload, tag_only_payload, unrelated_payload):
        create_response = client.post(
            "/api/v1/posts",
            json=payload,
            headers={"Authorization": "Bearer post-writer-token"},
        )
        post_id = create_response.json()["postId"]
        revision_id = create_response.json()["revisionId"]
        publish_response = client.post(
            f"/api/v1/posts/{post_id}/publish",
            json={"revisionId": revision_id, "publishMode": "immediate", "scheduledAt": None},
            headers={"Authorization": "Bearer post-publisher-token"},
        )
        assert create_response.status_code == 201
        assert publish_response.status_code == 200
        created_posts.append((post_id, revision_id))

    tag_response = client.get(
        "/api/v1/posts?status=published&tag=featured",
        headers={"Authorization": "Bearer post-reader-token"},
    )
    category_response = client.get(
        "/api/v1/posts?status=published&category=category-guides",
        headers={"Authorization": "Bearer post-reader-token"},
    )
    series_response = client.get(
        "/api/v1/posts?status=published&series=series-api-core",
        headers={"Authorization": "Bearer post-reader-token"},
    )

    assert tag_response.status_code == 200
    assert [item["postId"] for item in tag_response.json()["items"]] == [created_posts[0][0], created_posts[1][0]]
    assert category_response.status_code == 200
    assert [item["postId"] for item in category_response.json()["items"]] == [created_posts[0][0]]
    assert series_response.status_code == 200
    assert [item["postId"] for item in series_response.json()["items"]] == [created_posts[0][0]]


def test_list_published_posts_paginates_with_limit_and_cursor(tmp_path: Path) -> None:
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
            datetime(2026, 6, 7, 8, 1, 0, tzinfo=UTC),
            datetime(2026, 6, 7, 8, 2, 0, tzinfo=UTC),
            datetime(2026, 6, 7, 8, 3, 0, tzinfo=UTC),
            datetime(2026, 6, 7, 8, 4, 0, tzinfo=UTC),
            datetime(2026, 6, 7, 8, 5, 0, tzinfo=UTC),
            datetime(2026, 6, 7, 8, 6, 0, tzinfo=UTC),
        ]
    )
    app = create_app(settings=settings)
    app.state.post_store = PostStore(str(database_path), clock=lambda: next(timestamps))
    client = TestClient(app)

    created_posts = []
    for index in range(3):
        payload = draft_payload()
        payload.update(
            {
                "title": f"Published page item {index + 1}",
                "slug": f"published-page-item-{index + 1}",
                "summary": f"Published page summary {index + 1}.",
                "metadata": {"source": f"pagination-test-{index + 1}"},
            }
        )
        create_response = client.post(
            "/api/v1/posts",
            json=payload,
            headers={"Authorization": "Bearer post-writer-token"},
        )
        post_id = create_response.json()["postId"]
        revision_id = create_response.json()["revisionId"]
        publish_response = client.post(
            f"/api/v1/posts/{post_id}/publish",
            json={"revisionId": revision_id, "publishMode": "immediate", "scheduledAt": None},
            headers={"Authorization": "Bearer post-publisher-token"},
        )
        assert create_response.status_code == 201
        assert publish_response.status_code == 200
        created_posts.append(post_id)

    first_page_response = client.get(
        "/api/v1/posts?status=published&limit=2",
        headers={"Authorization": "Bearer post-reader-token"},
    )
    second_page_response = client.get(
        f"/api/v1/posts?status=published&limit=2&cursor={created_posts[1]}",
        headers={"Authorization": "Bearer post-reader-token"},
    )

    assert first_page_response.status_code == 200
    assert [item["postId"] for item in first_page_response.json()["items"]] == created_posts[:2]
    assert first_page_response.json()["nextCursor"] == created_posts[1]
    assert second_page_response.status_code == 200
    assert [item["postId"] for item in second_page_response.json()["items"]] == [created_posts[2]]
    assert second_page_response.json()["nextCursor"] is None


def test_list_public_posts_paginates_with_limit_and_cursor_without_auth(tmp_path: Path) -> None:
    database_path = tmp_path / "nairi.db"
    settings = Settings(
        api_tokens={
            "post-writer-token": ["posts:write"],
            "post-publisher-token": ["posts:publish"],
        },
        database_path=str(database_path),
    )
    timestamps = iter(
        [
            datetime(2026, 6, 7, 8, 1, 0, tzinfo=UTC),
            datetime(2026, 6, 7, 8, 2, 0, tzinfo=UTC),
            datetime(2026, 6, 7, 8, 3, 0, tzinfo=UTC),
            datetime(2026, 6, 7, 8, 4, 0, tzinfo=UTC),
            datetime(2026, 6, 7, 8, 5, 0, tzinfo=UTC),
            datetime(2026, 6, 7, 8, 6, 0, tzinfo=UTC),
        ]
    )
    app = create_app(settings=settings)
    app.state.post_store = PostStore(str(database_path), clock=lambda: next(timestamps))
    client = TestClient(app)

    created_posts = []
    for index in range(3):
        payload = draft_payload()
        payload.update(
            {
                "title": f"Public page item {index + 1}",
                "slug": f"public-page-item-{index + 1}",
                "summary": f"Public page summary {index + 1}.",
                "metadata": {"source": f"public-pagination-test-{index + 1}"},
            }
        )
        create_response = client.post(
            "/api/v1/posts",
            json=payload,
            headers={"Authorization": "Bearer post-writer-token"},
        )
        post_id = create_response.json()["postId"]
        revision_id = create_response.json()["revisionId"]
        publish_response = client.post(
            f"/api/v1/posts/{post_id}/publish",
            json={"revisionId": revision_id, "publishMode": "immediate", "scheduledAt": None},
            headers={"Authorization": "Bearer post-publisher-token"},
        )
        assert create_response.status_code == 201
        assert publish_response.status_code == 200
        created_posts.append(post_id)

    first_page_response = client.get("/api/v1/public/posts?limit=2")
    second_page_response = client.get(f"/api/v1/public/posts?limit=2&cursor={created_posts[1]}")

    assert first_page_response.status_code == 200
    assert [item["postId"] for item in first_page_response.json()["items"]] == created_posts[:2]
    assert first_page_response.json()["nextCursor"] == created_posts[1]
    assert first_page_response.json()["page"] == {
        "limit": 2,
        "cursor": None,
        "hasNextPage": True,
    }
    assert second_page_response.status_code == 200
    assert [item["postId"] for item in second_page_response.json()["items"]] == [created_posts[2]]
    assert second_page_response.json()["nextCursor"] is None
    assert second_page_response.json()["page"] == {
        "limit": 2,
        "cursor": created_posts[1],
        "hasNextPage": False,
    }
    for item in first_page_response.json()["items"]:
        assert "content" not in item
        assert "revisionId" not in item
        assert "metadata" not in item


def test_list_public_posts_returns_public_safe_published_summaries_without_auth(tmp_path: Path) -> None:
    database_path = tmp_path / "nairi.db"
    settings = Settings(
        api_tokens={
            "post-writer-token": ["posts:write"],
            "post-publisher-token": ["posts:publish"],
        },
        database_path=str(database_path),
    )
    timestamps = iter(
        [
            datetime(2026, 6, 7, 8, 1, 0, tzinfo=UTC),
            datetime(2026, 6, 7, 8, 2, 0, tzinfo=UTC),
            datetime(2026, 6, 7, 8, 3, 0, tzinfo=UTC),
        ]
    )
    app = create_app(settings=settings)
    app.state.post_store = PostStore(str(database_path), clock=lambda: next(timestamps))
    client = TestClient(app)

    draft_only_payload = draft_payload()
    draft_only_payload.update(
        {
            "title": "Hidden draft",
            "slug": "hidden-draft",
            "content": "This draft body must not leak.",
            "summary": "Hidden draft summary.",
            "metadata": {"source": "draft-only"},
        }
    )
    draft_response = client.post(
        "/api/v1/posts",
        json=draft_only_payload,
        headers={"Authorization": "Bearer post-writer-token"},
    )
    published_payload = draft_payload()
    published_payload.update(
        {
            "title": "Public published post",
            "slug": "public-published-post",
            "content": "Published body is still omitted from public list.",
            "summary": "Public summary.",
            "tags": ["public", "storage"],
            "categoryId": "category-public",
            "seriesId": "series-public",
            "metadata": {"source": "public-list-test", "internalNote": "do-not-leak"},
        }
    )
    create_response = client.post(
        "/api/v1/posts",
        json=published_payload,
        headers={"Authorization": "Bearer post-writer-token"},
    )
    post_id = create_response.json()["postId"]
    revision_id = create_response.json()["revisionId"]
    publish_response = client.post(
        f"/api/v1/posts/{post_id}/publish",
        json={"revisionId": revision_id, "publishMode": "immediate", "scheduledAt": None},
        headers={"Authorization": "Bearer post-publisher-token"},
    )

    public_response = client.get("/api/v1/public/posts")

    assert draft_response.status_code == 201
    assert create_response.status_code == 201
    assert publish_response.status_code == 200
    assert public_response.status_code == 200
    assert public_response.json() == {
        "items": [
            {
                "postId": post_id,
                "title": "Public published post",
                "slug": "public-published-post",
                "status": "published",
                "contentFormat": "markdown",
                "summary": "Public summary.",
                "tags": ["public", "storage"],
                "categoryId": "category-public",
                "seriesId": "series-public",
                "publishedAt": "2026-06-07T08:03:00Z",
                "category": None,
                "series": None,
                "tagsEnriched": [],
            }
        ],
        "nextCursor": None,
        "page": {
            "limit": None,
            "cursor": None,
            "hasNextPage": False,
        },
    }
    serialized_response = str(public_response.json())
    assert "revisionId" not in serialized_response
    assert "metadata" not in serialized_response
    assert "internalNote" not in serialized_response
    assert "Hidden draft" not in serialized_response
    assert "This draft body must not leak" not in serialized_response
    assert "Published body is still omitted" not in serialized_response


def test_get_public_post_by_slug_returns_public_safe_published_detail_without_auth(tmp_path: Path) -> None:
    database_path = tmp_path / "nairi.db"
    settings = Settings(
        api_tokens={
            "post-writer-token": ["posts:write"],
            "post-publisher-token": ["posts:publish"],
        },
        database_path=str(database_path),
    )
    timestamps = iter(
        [
            datetime(2026, 6, 7, 8, 1, 0, tzinfo=UTC),
            datetime(2026, 6, 7, 8, 2, 0, tzinfo=UTC),
            datetime(2026, 6, 7, 8, 3, 0, tzinfo=UTC),
        ]
    )
    app = create_app(settings=settings)
    app.state.post_store = PostStore(str(database_path), clock=lambda: next(timestamps))
    client = TestClient(app)

    draft_only_payload = draft_payload()
    draft_only_payload.update(
        {
            "title": "Hidden draft detail",
            "slug": "hidden-draft-detail",
            "content": "Draft detail body must not leak.",
            "summary": "Hidden draft detail summary.",
            "metadata": {"source": "draft-detail-only"},
        }
    )
    draft_response = client.post(
        "/api/v1/posts",
        json=draft_only_payload,
        headers={"Authorization": "Bearer post-writer-token"},
    )
    published_payload = draft_payload()
    published_payload.update(
        {
            "title": "Public detail post",
            "slug": "public-detail-post",
            "content": "# Public Detail Post\n\nPublished **Markdown** detail body.\n\n<script>alert(1)</script>",
            "summary": "Public detail summary.",
            "tags": ["public", "detail"],
            "categoryId": "category-public-detail",
            "seriesId": "series-public-detail",
            "metadata": {"source": "public-detail-test", "internalNote": "do-not-leak"},
        }
    )
    create_response = client.post(
        "/api/v1/posts",
        json=published_payload,
        headers={"Authorization": "Bearer post-writer-token"},
    )
    post_id = create_response.json()["postId"]
    revision_id = create_response.json()["revisionId"]
    publish_response = client.post(
        f"/api/v1/posts/{post_id}/publish",
        json={"revisionId": revision_id, "publishMode": "immediate", "scheduledAt": None},
        headers={"Authorization": "Bearer post-publisher-token"},
    )

    detail_response = client.get("/api/v1/public/posts/public-detail-post")
    draft_detail_response = client.get("/api/v1/public/posts/hidden-draft-detail")
    unknown_response = client.get("/api/v1/public/posts/missing-public-detail")

    assert draft_response.status_code == 201
    assert create_response.status_code == 201
    assert publish_response.status_code == 200
    assert detail_response.status_code == 200
    assert detail_response.json() == {
        "postId": post_id,
        "title": "Public detail post",
        "slug": "public-detail-post",
        "status": "published",
        "contentFormat": "markdown",
        "content": "# Public Detail Post\n\nPublished **Markdown** detail body.\n\n<script>alert(1)</script>",
        "bodyHtml": "<h1>Public Detail Post</h1>\n<p>Published <strong>Markdown</strong> detail body.</p>",
        "summary": "Public detail summary.",
        "tags": ["public", "detail"],
        "categoryId": "category-public-detail",
        "seriesId": "series-public-detail",
        "publishedAt": "2026-06-07T08:03:00Z",
        "category": None,
        "series": None,
        "tagsEnriched": [],
    }
    serialized_response = str(detail_response.json())
    assert "revisionId" not in serialized_response
    assert "metadata" not in serialized_response
    assert "internalNote" not in serialized_response
    assert "createdAt" not in serialized_response
    assert "updatedAt" not in serialized_response
    assert "<script" not in detail_response.json()["bodyHtml"]
    assert "alert(1)" not in detail_response.json()["bodyHtml"]
    assert draft_detail_response.status_code == 404
    assert draft_detail_response.json()["code"] == "not_found"
    assert unknown_response.status_code == 404
    assert unknown_response.json()["code"] == "not_found"


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
        "tags": [],
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
                '{"source":"persistence-test","summary":"Stored summary.","tags":[],"categoryId":null,"seriesId":null}',
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
        "publicInvalidation": {
            "mode": "recorded",
            "surfaces": [
                "/posts",
                "/posts/persistent-draft",
                "/rss.xml",
                "/sitemap.xml",
            ],
            "execution": {
                "status": "recorded",
                "executor": "none",
                "executedAt": "2026-06-07T08:11:12Z",
                "errorCode": None,
                "errorMessage": None,
            },
            "dispatch": {
                "status": "dispatch_skipped",
                "reason": "no_dispatcher_configured",
                "attempted": False,
                "attemptedAt": None,
            },
        },
    }
    with sqlite3.connect(database_path) as connection:
        post_row = connection.execute(
            "SELECT status, published_at, updated_at FROM posts WHERE id = ?",
            ("draft-persistent-draft",),
        ).fetchone()
        publish_job_execution = connection.execute(
            """
            SELECT
                public_invalidation_surfaces,
                public_invalidation_status,
                public_invalidation_executor,
                public_invalidation_executed_at,
                public_invalidation_error_code,
                public_invalidation_error_message,
                public_invalidation_dispatch_status,
                public_invalidation_dispatch_reason,
                public_invalidation_dispatch_attempted,
                public_invalidation_dispatch_attempted_at
            FROM publish_jobs
            WHERE id = ?
            """,
            ("publish-draft-persistent-draft-revision-persistent-draft-1",),
        ).fetchone()

    assert post_row == ("published", "2026-06-07T08:11:12Z", "2026-06-07T08:11:12Z")
    assert publish_job_execution == (
        '["/posts","/posts/persistent-draft","/rss.xml","/sitemap.xml"]',
        "recorded",
        "none",
        "2026-06-07T08:11:12Z",
        None,
        None,
        "dispatch_skipped",
        "no_dispatcher_configured",
        0,
        None,
    )


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
        "tags": [],
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
        '{"source":"persistence-test","summary":"Stored summary.","tags":[],"categoryId":null,"seriesId":null}',
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


def test_post_store_records_schema_migration_baseline_once(tmp_path: Path) -> None:
    database_path = tmp_path / "nairi.db"

    PostStore(str(database_path)).create_draft(
        PostDraftInput(
            title="Persistent draft",
            slug="baseline-one",
            content_format="markdown",
            content="# Persistent draft\n\nStored body.",
            summary="Stored summary.",
            tags=["storage"],
            category_id=None,
            series_id=None,
            metadata={"source": "persistence-test"},
        ),
        actor_token="writer",
    )
    PostStore(str(database_path)).list_drafts()

    with sqlite3.connect(database_path) as connection:
        rows = connection.execute(
            "SELECT id, name FROM schema_migrations ORDER BY id"
        ).fetchall()

    assert rows == [(1, "post_store_baseline")]


def test_post_store_adopts_existing_pre_migration_database_without_data_loss(tmp_path: Path) -> None:
    database_path = tmp_path / "legacy.db"
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE posts (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                slug TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL,
                content_format TEXT NOT NULL,
                current_revision_id TEXT NOT NULL,
                published_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE post_revisions (
                id TEXT PRIMARY KEY,
                post_id TEXT NOT NULL REFERENCES posts(id),
                content TEXT NOT NULL,
                metadata TEXT NOT NULL,
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                actor_type TEXT NOT NULL,
                actor_id TEXT NOT NULL,
                target_type TEXT NOT NULL,
                target_id TEXT NOT NULL,
                metadata TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            INSERT INTO posts (id, title, slug, status, content_format, current_revision_id, published_at, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "draft-legacy",
                "Legacy",
                "legacy",
                "draft",
                "markdown",
                "revision-legacy-1",
                None,
                "2026-06-07T08:11:12Z",
                "2026-06-07T08:11:12Z",
            ),
        )
        connection.execute(
            """
            INSERT INTO post_revisions (id, post_id, content, metadata, created_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "revision-legacy-1",
                "draft-legacy",
                "Legacy content",
                '{"summary":"Legacy summary","tags":["old"],"categoryId":null,"seriesId":null}',
                "token:writer",
                "2026-06-07T08:11:12Z",
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
                "token:writer",
                "post",
                "draft-legacy",
                '{"revisionId":"revision-legacy-1"}',
                "2026-06-07T08:11:12Z",
            ),
        )

    drafts = PostStore(str(database_path)).list_drafts()

    assert [draft.post_id for draft in drafts] == ["draft-legacy"]
    with sqlite3.connect(database_path) as connection:
        migration_rows = connection.execute(
            "SELECT id, name FROM schema_migrations ORDER BY id"
        ).fetchall()
        data_counts = connection.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM posts),
                (SELECT COUNT(*) FROM post_revisions),
                (SELECT COUNT(*) FROM audit_events)
            """
        ).fetchone()

    assert migration_rows == [(1, "post_store_baseline")]
    assert data_counts == (1, 1, 1)


def test_post_store_reconciles_baseline_schema_when_metadata_already_exists(tmp_path: Path) -> None:
    database_path = tmp_path / "managed-but-incomplete.db"
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE schema_migrations (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE
            )
            """
        )
        connection.execute(
            "INSERT INTO schema_migrations (id, name) VALUES (?, ?)",
            (1, "post_store_baseline"),
        )

    PostStore(str(database_path)).list_drafts()

    with sqlite3.connect(database_path) as connection:
        table_rows = connection.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name IN ('posts', 'post_revisions', 'audit_events', 'publish_jobs')
            ORDER BY name
            """
        ).fetchall()
        migration_rows = connection.execute("SELECT id, name FROM schema_migrations ORDER BY id").fetchall()

    assert table_rows == [("audit_events",), ("post_revisions",), ("posts",), ("publish_jobs",)]
    assert migration_rows == [(1, "post_store_baseline")]


def test_schema_migration_runner_applies_pending_migrations_in_order() -> None:
    applied: list[str] = []

    def first(connection: sqlite3.Connection) -> None:
        applied.append("first")
        connection.execute("CREATE TABLE first_marker (id INTEGER PRIMARY KEY)")

    def second(connection: sqlite3.Connection) -> None:
        applied.append("second")
        connection.execute("CREATE TABLE second_marker (id INTEGER PRIMARY KEY)")

    with sqlite3.connect(":memory:") as connection:
        run_schema_migrations(
            connection,
            [
                PostStoreMigration(id=1, name="first", apply=first),
                PostStoreMigration(id=2, name="second", apply=second),
            ],
        )
        run_schema_migrations(
            connection,
            [
                PostStoreMigration(id=1, name="first", apply=first),
                PostStoreMigration(id=2, name="second", apply=second),
            ],
        )
        rows = connection.execute("SELECT id, name FROM schema_migrations ORDER BY id").fetchall()

    assert applied == ["first", "second"]
    assert rows == [(1, "first"), (2, "second")]


def test_schema_migration_runner_reports_stable_name_mismatch_policy() -> None:
    with sqlite3.connect(":memory:") as connection:
        connection.execute(
            """
            CREATE TABLE schema_migrations (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE
            )
            """
        )
        connection.execute("INSERT INTO schema_migrations (id, name) VALUES (?, ?)", (1, "legacy_baseline"))

        try:
            run_schema_migrations(
                connection,
                [PostStoreMigration(id=1, name="post_store_baseline", apply=lambda _: None)],
            )
        except PostStoreMigrationError as error:
            assert error.code == "migration_name_mismatch"
            assert error.migration_id == 1
            assert error.recorded_name == "legacy_baseline"
            assert error.expected_name == "post_store_baseline"
            assert str(error) == "schema migration 1 recorded as 'legacy_baseline', expected 'post_store_baseline'"
        else:
            raise AssertionError("migration name mismatch should fail fast with stable policy metadata")

        rows = connection.execute("SELECT id, name FROM schema_migrations ORDER BY id").fetchall()

    assert rows == [(1, "legacy_baseline")]


def test_schema_migration_runner_rolls_back_failed_pending_migration() -> None:
    def failing(connection: sqlite3.Connection) -> None:
        connection.execute("CREATE TABLE should_rollback (id INTEGER PRIMARY KEY)")
        raise RuntimeError("migration failed")

    with sqlite3.connect(":memory:") as connection:
        try:
            run_schema_migrations(
                connection,
                [PostStoreMigration(id=1, name="failing", apply=failing)],
            )
        except RuntimeError as error:
            assert str(error) == "migration failed"
        else:
            raise AssertionError("migration failure should be re-raised")

        migration_rows = connection.execute("SELECT id, name FROM schema_migrations ORDER BY id").fetchall()
        marker_row = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'should_rollback'"
        ).fetchone()

    assert migration_rows == []
    assert marker_row is None


def test_post_store_migration_rehearsal_backs_up_migrates_and_reads_back(tmp_path: Path) -> None:
    source_path = tmp_path / "pre-migration.db"
    rehearsal_path = tmp_path / "rehearsal" / "working.db"
    backup_path = tmp_path / "backups" / "pre-migration.db.bak"
    with sqlite3.connect(source_path) as connection:
        connection.execute(
            """
            CREATE TABLE posts (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                slug TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL,
                content_format TEXT NOT NULL,
                current_revision_id TEXT NOT NULL,
                published_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE post_revisions (
                id TEXT PRIMARY KEY,
                post_id TEXT NOT NULL REFERENCES posts(id),
                content TEXT NOT NULL,
                metadata TEXT NOT NULL,
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                actor_type TEXT NOT NULL,
                actor_id TEXT NOT NULL,
                target_type TEXT NOT NULL,
                target_id TEXT NOT NULL,
                metadata TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            INSERT INTO posts (id, title, slug, status, content_format, current_revision_id, published_at, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "draft-rehearsal",
                "Rehearsal",
                "rehearsal",
                "draft",
                "markdown",
                "revision-rehearsal-1",
                None,
                "2026-06-07T08:11:12Z",
                "2026-06-07T08:11:12Z",
            ),
        )
        connection.execute(
            """
            INSERT INTO post_revisions (id, post_id, content, metadata, created_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "revision-rehearsal-1",
                "draft-rehearsal",
                "Rehearsal content",
                '{"summary":"Rehearsal summary","tags":["migration"],"categoryId":null,"seriesId":null}',
                "token:writer",
                "2026-06-07T08:11:12Z",
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
                "token:writer",
                "post",
                "draft-rehearsal",
                '{"revisionId":"revision-rehearsal-1"}',
                "2026-06-07T08:11:12Z",
            ),
        )

    result = rehearse_post_store_migration(
        source_path=source_path,
        rehearsal_path=rehearsal_path,
        backup_path=backup_path,
    )

    assert source_path.exists()
    assert backup_path.exists()
    assert rehearsal_path.exists()
    assert result.backup_path == backup_path
    assert result.rehearsal_path == rehearsal_path
    assert result.pre_migration_tables == ["audit_events", "post_revisions", "posts"]
    assert result.pre_migration_has_schema_migrations is False
    assert result.post_migration_rows == [(1, "post_store_baseline")]
    assert result.pre_migration_counts == {"posts": 1, "post_revisions": 1, "audit_events": 1}
    assert result.post_migration_counts == {"posts": 1, "post_revisions": 1, "audit_events": 1}
    assert result.readback_post_ids == ["draft-rehearsal"]

    with sqlite3.connect(source_path) as connection:
        source_migration_table = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'schema_migrations'"
        ).fetchone()
        source_counts = connection.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM posts),
                (SELECT COUNT(*) FROM post_revisions),
                (SELECT COUNT(*) FROM audit_events)
            """
        ).fetchone()
    with sqlite3.connect(backup_path) as connection:
        backup_migration_table = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'schema_migrations'"
        ).fetchone()
        backup_counts = connection.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM posts),
                (SELECT COUNT(*) FROM post_revisions),
                (SELECT COUNT(*) FROM audit_events)
            """
        ).fetchone()

    assert source_migration_table is None
    assert backup_migration_table is None
    assert source_counts == (1, 1, 1)
    assert backup_counts == (1, 1, 1)


def test_post_store_migration_rehearsal_rejects_path_aliases_and_existing_artifacts(tmp_path: Path) -> None:
    source_path = tmp_path / "source.db"
    backup_path = tmp_path / "backup.db"
    rehearsal_path = tmp_path / "rehearsal.db"
    source_path.write_bytes(b"not used before alias validation")

    try:
        rehearse_post_store_migration(
            source_path=source_path,
            backup_path=backup_path,
            rehearsal_path=backup_path,
        )
    except ValueError as error:
        assert str(error) == "source_path, backup_path, and rehearsal_path must be distinct"
    else:
        raise AssertionError("path aliases should be rejected before copying")

    backup_path.write_bytes(b"existing backup")
    try:
        rehearse_post_store_migration(
            source_path=source_path,
            backup_path=backup_path,
            rehearsal_path=rehearsal_path,
        )
    except FileExistsError as error:
        assert error.args == (backup_path,)
    else:
        raise AssertionError("existing backup artifacts should not be overwritten")

    backup_path.unlink()
    rehearsal_path.write_bytes(b"existing rehearsal")
    try:
        rehearse_post_store_migration(
            source_path=source_path,
            backup_path=backup_path,
            rehearsal_path=rehearsal_path,
        )
    except FileExistsError as error:
        assert error.args == (rehearsal_path,)
    else:
        raise AssertionError("existing rehearsal artifacts should not be overwritten")


def test_create_draft_rejects_invalid_category_id(tmp_path: Path) -> None:
    db = str(tmp_path / "nairi.db")
    cat_store = CategoryStore(db)
    post_store = PostStore(db, category_store=cat_store)
    draft = PostDraftInput(
        title="Test",
        slug="test",
        content_format="markdown",
        content="# Test",
        summary=None,
        tags=[],
        category_id="cat-nonexistent",
        series_id=None,
        metadata={},
    )
    try:
        post_store.create_draft(draft, actor_token="t1")
    except CategoryNotFoundError as e:
        assert e.category_id == "cat-nonexistent"
    else:
        raise AssertionError("expected CategoryNotFoundError")


def test_create_draft_rejects_invalid_series_id(tmp_path: Path) -> None:
    db = str(tmp_path / "nairi.db")
    series_store = SeriesStore(db)
    post_store = PostStore(db, series_store=series_store)
    draft = PostDraftInput(
        title="Test",
        slug="test",
        content_format="markdown",
        content="# Test",
        summary=None,
        tags=[],
        category_id=None,
        series_id="series-nonexistent",
        metadata={},
    )
    try:
        post_store.create_draft(draft, actor_token="t1")
    except SeriesNotFoundError as e:
        assert e.series_id == "series-nonexistent"
    else:
        raise AssertionError("expected SeriesNotFoundError")


def test_create_draft_rejects_invalid_tag_ids(tmp_path: Path) -> None:
    db = str(tmp_path / "nairi.db")
    tag_store = TagStore(db)
    post_store = PostStore(db, tag_store=tag_store)
    draft = PostDraftInput(
        title="Test",
        slug="test",
        content_format="markdown",
        content="# Test",
        summary=None,
        tags=["tag-valid", "tag-invalid"],
        category_id=None,
        series_id=None,
        metadata={},
    )
    try:
        post_store.create_draft(draft, actor_token="t1")
    except TagNotFoundError as e:
        assert e.tag_id in ("tag-valid", "tag-invalid")
    else:
        raise AssertionError("expected TagNotFoundError")


def test_create_draft_accepts_valid_taxonomy_references(tmp_path: Path) -> None:
    db = str(tmp_path / "nairi.db")
    cat_store = CategoryStore(db)
    tag_store = TagStore(db)
    series_store = SeriesStore(db)
    cat_store.create_category("Field Notes", "field-notes", "FF series")
    tag_store.create_tag("ops", "ops")
    series_store.create_series("Field Journal", "field-journal", "JJ collection")
    post_store = PostStore(db, category_store=cat_store, tag_store=tag_store, series_store=series_store)
    draft = PostDraftInput(
        title="Valid taxonomy draft",
        slug="valid-taxonomy-draft",
        content_format="markdown",
        content="# Valid",
        summary="Valid.",
        tags=["tag-ops"],
        category_id="cat-field-notes",
        series_id="series-field-journal",
        metadata={"key": "val"},
    )
    result = post_store.create_draft(draft, actor_token="t1")
    assert result.post_id == "draft-valid-taxonomy-draft"


def test_update_draft_rejects_invalid_category_id(tmp_path: Path) -> None:
    db = str(tmp_path / "nairi.db")
    cat_store = CategoryStore(db)
    post_store = PostStore(db, category_store=cat_store)
    post_store.create_draft(
        PostDraftInput(
            title="Original",
            slug="orig",
            content_format="markdown",
            content="# Orig",
            summary=None,
            tags=[],
            category_id=None,
            series_id=None,
            metadata={},
        ),
        actor_token="t1",
    )
    draft = PostDraftInput(
        title="Updated",
        slug="orig",
        content_format="markdown",
        content="# Updated",
        summary=None,
        tags=[],
        category_id="cat-nonexistent",
        series_id=None,
        metadata={},
    )
    try:
        post_store.update_draft("draft-orig", draft, actor_token="t1", expected_revision_id="revision-orig-1")
    except CategoryNotFoundError as e:
        assert e.category_id == "cat-nonexistent"
    else:
        raise AssertionError("expected CategoryNotFoundError")


def test_public_list_resolves_taxonomy_names_when_entities_exist(tmp_path: Path) -> None:
    db = str(tmp_path / "nairi.db")
    settings = Settings(
        api_tokens={"post-writer-token": ["posts:write"], "post-publisher-token": ["posts:publish"]},
        database_path=db,
    )
    app = create_app(settings=settings)
    # Seed taxonomy using the same store instances the app uses
    app.state.category_store.create_category("Guides", "guides", "Tutorial guides")
    app.state.tag_store.create_tag("ops", "ops")
    app.state.tag_store.create_tag("second", "second")
    app.state.series_store.create_series("Updated Series", "updated", "An updated series")
    client = TestClient(app)

    # Create and publish a post with taxonomy references
    payload = {
        "title": "Taxonomy Enrichment Post",
        "slug": "taxonomy-enrichment-post",
        "contentFormat": "markdown",
        "content": "# Enriched post",
        "summary": "With taxonomy.",
        "tags": ["tag-ops", "tag-second"],
        "categoryId": "cat-guides",
        "seriesId": "series-updated",
        "metadata": {},
    }
    create_resp = client.post(
        "/api/v1/posts", json=payload, headers={"Authorization": "Bearer post-writer-token"}
    )
    assert create_resp.status_code == 201
    post_id = create_resp.json()["postId"]
    revision_id = create_resp.json()["revisionId"]
    pub_resp = client.post(
        f"/api/v1/posts/{post_id}/publish",
        json={"revisionId": revision_id, "publishMode": "immediate", "scheduledAt": None},
        headers={"Authorization": "Bearer post-publisher-token"},
    )
    assert pub_resp.status_code == 200

    # Verify public list enrichment
    list_resp = client.get("/api/v1/public/posts")
    assert list_resp.status_code == 200
    items = list_resp.json()["items"]
    assert len(items) >= 1
    post_item = next(i for i in items if i["slug"] == "taxonomy-enrichment-post")
    assert post_item["categoryId"] == "cat-guides"
    assert post_item["seriesId"] == "series-updated"
    assert post_item["tags"] == ["tag-ops", "tag-second"]
    # Resolved enrichment
    assert post_item["category"] == {"id": "cat-guides", "name": "Guides", "slug": "guides"}
    assert post_item["series"] == {"id": "series-updated", "name": "Updated Series", "slug": "updated"}
    assert post_item["tagsEnriched"] == [
        {"id": "tag-ops", "name": "ops", "slug": "ops"},
        {"id": "tag-second", "name": "second", "slug": "second"},
    ]


def test_public_detail_resolves_taxonomy_names_when_entities_exist(tmp_path: Path) -> None:
    db = str(tmp_path / "nairi.db")
    settings = Settings(
        api_tokens={"post-writer-token": ["posts:write"], "post-publisher-token": ["posts:publish"]},
        database_path=db,
    )
    app = create_app(settings=settings)
    app.state.category_store.create_category("Guides", "guides", "Tutorial guides")
    app.state.tag_store.create_tag("ops", "ops")
    app.state.series_store.create_series("Updated Series", "updated", "An updated series")
    client = TestClient(app)

    payload = {
        "title": "Taxonomy Detail Post",
        "slug": "taxonomy-detail-post",
        "contentFormat": "markdown",
        "content": "# Detail content",
        "summary": "Detail taxonomy.",
        "tags": ["tag-ops"],
        "categoryId": "cat-guides",
        "seriesId": "series-updated",
        "metadata": {},
    }
    create_resp = client.post(
        "/api/v1/posts", json=payload, headers={"Authorization": "Bearer post-writer-token"}
    )
    assert create_resp.status_code == 201
    post_id = create_resp.json()["postId"]
    revision_id = create_resp.json()["revisionId"]
    pub_resp = client.post(
        f"/api/v1/posts/{post_id}/publish",
        json={"revisionId": revision_id, "publishMode": "immediate", "scheduledAt": None},
        headers={"Authorization": "Bearer post-publisher-token"},
    )
    assert pub_resp.status_code == 200

    detail_resp = client.get("/api/v1/public/posts/taxonomy-detail-post")
    assert detail_resp.status_code == 200
    item = detail_resp.json()
    assert item["category"] == {"id": "cat-guides", "name": "Guides", "slug": "guides"}
    assert item["series"] == {"id": "series-updated", "name": "Updated Series", "slug": "updated"}
    assert item["tagsEnriched"] == [{"id": "tag-ops", "name": "ops", "slug": "ops"}]


def test_public_post_returns_null_for_deleted_taxonomy(tmp_path: Path) -> None:
    """When a taxonomy entity is deleted after a post references it, the API returns null for that field."""
    import sqlite3
    db = str(tmp_path / "nairi.db")
    settings = Settings(
        api_tokens={"post-writer-token": ["posts:write"], "post-publisher-token": ["posts:publish"]},
        database_path=db,
    )
    app = create_app(settings=settings)
    # Trigger lazy schema initialization before direct SQL insert
    app.state.category_store.list_categories()  # initializes category/tag/series tables
    app.state.post_store.get_draft("__init_schema__")  # initializes post tables
    client = TestClient(app)

    # Directly insert a published post with non-existent taxonomy IDs into the DB
    # (bypasses PostStore validation, simulating orphaned taxonomy after entity deletion)
    with sqlite3.connect(db) as conn:
        conn.execute("PRAGMA busy_timeout = 30000")
        conn.execute(
            "INSERT INTO posts (id, title, slug, status, content_format, current_revision_id, created_at, updated_at, published_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("orphan-post-1", "Orphan Taxonomy Post", "orphan-taxonomy-post", "published",
             "markdown", "orphan-rev-1", "2026-06-07T08:03:00Z", "2026-06-07T08:03:00Z", "2026-06-07T08:03:00Z"),
        )
        conn.execute(
            "INSERT INTO post_revisions (id, post_id, content, metadata, created_by, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            ("orphan-rev-1", "orphan-post-1", "# Orphan",
             '{"summary":"All taxonomy orphaned.","tags":["tag-orphan-a","tag-orphan-b"],"categoryId":"cat-orphan-cat","seriesId":"series-orphan-series"}',
             "token:t1", "2026-06-07T08:03:00Z"),
        )
        conn.commit()

    list_resp = client.get("/api/v1/public/posts")
    assert list_resp.status_code == 200
    items = list_resp.json()["items"]
    post_item = next(i for i in items if i["slug"] == "orphan-taxonomy-post")
    # IDs are still stored in DB
    assert post_item["categoryId"] == "cat-orphan-cat"
    assert post_item["seriesId"] == "series-orphan-series"
    assert post_item["tags"] == ["tag-orphan-a", "tag-orphan-b"]
    # But resolved values are null/empty since entities don't exist
    assert post_item["category"] is None
    assert post_item["series"] is None
    assert post_item["tagsEnriched"] == []
