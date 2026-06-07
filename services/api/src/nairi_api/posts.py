import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable


DRAFT_STATUS = "draft"


def utc_timestamp(value: datetime) -> str:
    return value.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class PostDraftInput:
    title: str
    slug: str
    content_format: str
    content: str
    summary: str | None
    tags: list[str]
    category_id: str | None
    series_id: str | None
    metadata: dict[str, object]


@dataclass(frozen=True)
class CreatedPostDraft:
    post_id: str
    status: str
    revision_id: str
    created_at: str


class DuplicatePostSlugError(Exception):
    def __init__(self, slug: str) -> None:
        self.slug = slug


class PostStore:
    def __init__(self, database_path: str, clock: Callable[[], datetime] | None = None) -> None:
        self.database_path = database_path
        self.clock = clock or (lambda: datetime.now(UTC))

    def create_draft(self, draft: PostDraftInput, actor_token: str) -> CreatedPostDraft:
        post_id = f"draft-{draft.slug}"
        revision_id = f"revision-{draft.slug}-1"
        created_at = utc_timestamp(self.clock())
        metadata = dict(draft.metadata)
        metadata.update(
            {
                "summary": draft.summary,
                "tags": draft.tags,
                "categoryId": draft.category_id,
                "seriesId": draft.series_id,
            }
        )

        with self._connect() as connection:
            self._init_schema(connection)
            existing_post = connection.execute(
                "SELECT id FROM posts WHERE slug = ?",
                (draft.slug,),
            ).fetchone()
            if existing_post is not None:
                raise DuplicatePostSlugError(draft.slug)
            connection.execute(
                """
                INSERT INTO posts (id, title, slug, status, content_format, current_revision_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (post_id, draft.title, draft.slug, DRAFT_STATUS, draft.content_format, revision_id, created_at, created_at),
            )
            connection.execute(
                """
                INSERT INTO post_revisions (id, post_id, content, metadata, created_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    revision_id,
                    post_id,
                    draft.content,
                    json.dumps(metadata, separators=(",", ":")),
                    f"token:{actor_token}",
                    created_at,
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
                    f"token:{actor_token}",
                    "post",
                    post_id,
                    json.dumps({"revisionId": revision_id}, separators=(",", ":")),
                    created_at,
                ),
            )

        return CreatedPostDraft(
            post_id=post_id,
            status=DRAFT_STATUS,
            revision_id=revision_id,
            created_at=created_at,
        )

    def _connect(self) -> sqlite3.Connection:
        if self.database_path != ":memory:":
            Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.database_path, timeout=30.0, check_same_thread=False)
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 30000")
        if self.database_path != ":memory:":
            connection.execute("PRAGMA journal_mode = WAL")
        return connection

    def _init_schema(self, connection: sqlite3.Connection) -> None:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS posts (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                slug TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL,
                content_format TEXT NOT NULL,
                current_revision_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS post_revisions (
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
            CREATE TABLE IF NOT EXISTS audit_events (
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
