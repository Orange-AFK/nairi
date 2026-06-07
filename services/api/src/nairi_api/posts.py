import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable, Literal, cast


DRAFT_STATUS = "draft"
PUBLISHED_STATUS = "published"
POST_STORE_BASELINE_MIGRATION_ID = 1
POST_STORE_BASELINE_MIGRATION_NAME = "post_store_baseline"


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


@dataclass(frozen=True)
class UpdatedPostDraft:
    post_id: str
    status: str
    revision_id: str
    updated_at: str


@dataclass(frozen=True)
class PublishedPost:
    post_id: str
    status: str
    published_at: str | None
    job_id: str
    public_invalidation_surfaces: list[str]
    public_invalidation_status: str
    public_invalidation_executor: str
    public_invalidation_executed_at: str | None
    public_invalidation_error_code: str | None
    public_invalidation_error_message: str | None
    public_invalidation_dispatch_status: str
    public_invalidation_dispatch_reason: str | None
    public_invalidation_dispatch_attempted: bool
    public_invalidation_dispatch_attempted_at: str | None


@dataclass(frozen=True)
class StoredPostDraft:
    post_id: str
    title: str
    slug: str
    status: str
    content_format: Literal["markdown", "mdx"]
    content: str
    summary: str | None
    tags: list[str]
    category_id: str | None
    series_id: str | None
    metadata: dict[str, object]
    revision_id: str
    created_at: str
    updated_at: str
    published_at: str | None = None


@dataclass(frozen=True)
class PostStoreMigration:
    id: int
    name: str
    apply: Callable[[sqlite3.Connection], None]


def run_schema_migrations(connection: sqlite3.Connection, migrations: list[PostStoreMigration]) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        )
        """
    )
    applied_rows = connection.execute("SELECT id, name FROM schema_migrations").fetchall()
    applied = {cast(int, row[0]): cast(str, row[1]) for row in applied_rows}
    for migration in sorted(migrations, key=lambda item: item.id):
        applied_name = applied.get(migration.id)
        if applied_name is not None:
            if applied_name != migration.name:
                raise ValueError(
                    f"schema migration {migration.id} recorded as {applied_name!r}, expected {migration.name!r}"
                )
            continue
        try:
            connection.execute("BEGIN")
            migration.apply(connection)
            connection.execute(
                "INSERT INTO schema_migrations (id, name) VALUES (?, ?)",
                (migration.id, migration.name),
            )
            connection.execute("COMMIT")
        except Exception:
            connection.execute("ROLLBACK")
            raise
        applied[migration.id] = migration.name


def public_invalidation_surfaces_for_post(slug: str) -> list[str]:
    return ["/posts", f"/posts/{slug}", "/rss.xml", "/sitemap.xml"]


class DuplicatePostSlugError(Exception):

    def __init__(self, slug: str) -> None:
        self.slug = slug


class PostDraftNotFoundError(Exception):

    def __init__(self, post_id: str) -> None:
        self.post_id = post_id


class PostRevisionConflictError(Exception):

    def __init__(self, current_revision_id: str) -> None:
        self.current_revision_id = current_revision_id


class PublishJobNotFoundError(Exception):

    def __init__(self, job_id: str) -> None:
        self.job_id = job_id


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

    def update_draft(
        self,
        post_id: str,
        draft: PostDraftInput,
        actor_token: str,
        expected_revision_id: str,
    ) -> UpdatedPostDraft:
        updated_at = utc_timestamp(self.clock())
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
            row = connection.execute(
                """
                SELECT current_revision_id
                FROM posts
                WHERE id = ? AND status = ?
                """,
                (post_id, DRAFT_STATUS),
            ).fetchone()
            if row is None:
                raise PostDraftNotFoundError(post_id)
            previous_revision_id = cast(str, row[0])
            if previous_revision_id != expected_revision_id:
                raise PostRevisionConflictError(previous_revision_id)
            existing_slug = connection.execute(
                "SELECT id FROM posts WHERE slug = ? AND id != ?",
                (draft.slug, post_id),
            ).fetchone()
            if existing_slug is not None:
                raise DuplicatePostSlugError(draft.slug)
            revision_count = connection.execute(
                "SELECT COUNT(*) FROM post_revisions WHERE post_id = ?",
                (post_id,),
            ).fetchone()[0]
            revision_id = f"revision-{post_id.removeprefix('draft-')}-{revision_count + 1}"
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
                    updated_at,
                ),
            )
            connection.execute(
                """
                UPDATE posts
                SET title = ?, slug = ?, content_format = ?, current_revision_id = ?, updated_at = ?
                WHERE id = ?
                """,
                (draft.title, draft.slug, draft.content_format, revision_id, updated_at, post_id),
            )
            connection.execute(
                """
                INSERT INTO audit_events (event_type, actor_type, actor_id, target_type, target_id, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "post.updated",
                    "api_token",
                    f"token:{actor_token}",
                    "post",
                    post_id,
                    json.dumps(
                        {"revisionId": revision_id, "previousRevisionId": previous_revision_id},
                        separators=(",", ":"),
                    ),
                    updated_at,
                ),
            )
        return UpdatedPostDraft(
            post_id=post_id,
            status=DRAFT_STATUS,
            revision_id=revision_id,
            updated_at=updated_at,
        )

    def publish_draft(self, post_id: str, revision_id: str, actor_token: str) -> PublishedPost:
        published_at = utc_timestamp(self.clock())
        job_id = f"publish-{post_id}-{revision_id}"
        with self._connect() as connection:
            self._init_schema(connection)
            row = connection.execute(
                """
                SELECT current_revision_id, slug
                FROM posts
                WHERE id = ? AND status = ?
                """,
                (post_id, DRAFT_STATUS),
            ).fetchone()
            if row is None:
                raise PostDraftNotFoundError(post_id)
            current_revision_id = cast(str, row[0])
            slug = cast(str, row[1])
            if current_revision_id != revision_id:
                raise PostRevisionConflictError(current_revision_id)
            public_invalidation_surfaces = public_invalidation_surfaces_for_post(slug)
            public_invalidation_status = "recorded"
            public_invalidation_executor = "none"
            public_invalidation_executed_at = published_at
            public_invalidation_dispatch_status = "dispatch_skipped"
            public_invalidation_dispatch_reason = "no_dispatcher_configured"
            public_invalidation_dispatch_attempted = False
            public_invalidation_dispatch_attempted_at = None
            connection.execute(
                """
                INSERT INTO publish_jobs (
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
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job_id,
                    post_id,
                    revision_id,
                    "succeeded",
                    None,
                    published_at,
                    published_at,
                    None,
                    None,
                    json.dumps(public_invalidation_surfaces, separators=(",", ":")),
                    public_invalidation_status,
                    public_invalidation_executor,
                    public_invalidation_executed_at,
                    None,
                    None,
                    public_invalidation_dispatch_status,
                    public_invalidation_dispatch_reason,
                    int(public_invalidation_dispatch_attempted),
                    public_invalidation_dispatch_attempted_at,
                ),
            )
            connection.execute(
                """
                UPDATE posts
                SET status = ?, published_at = ?, updated_at = ?
                WHERE id = ?
                """,
                (PUBLISHED_STATUS, published_at, published_at, post_id),
            )
            connection.execute(
                """
                INSERT INTO audit_events (event_type, actor_type, actor_id, target_type, target_id, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "post.published",
                    "api_token",
                    f"token:{actor_token}",
                    "post",
                    post_id,
                    json.dumps({"revisionId": revision_id, "jobId": job_id}, separators=(",", ":")),
                    published_at,
                ),
            )

        return PublishedPost(
            post_id=post_id,
            status=PUBLISHED_STATUS,
            published_at=published_at,
            job_id=job_id,
            public_invalidation_surfaces=public_invalidation_surfaces,
            public_invalidation_status=public_invalidation_status,
            public_invalidation_executor=public_invalidation_executor,
            public_invalidation_executed_at=public_invalidation_executed_at,
            public_invalidation_error_code=None,
            public_invalidation_error_message=None,
            public_invalidation_dispatch_status=public_invalidation_dispatch_status,
            public_invalidation_dispatch_reason=public_invalidation_dispatch_reason,
            public_invalidation_dispatch_attempted=public_invalidation_dispatch_attempted,
            public_invalidation_dispatch_attempted_at=public_invalidation_dispatch_attempted_at,
        )

    def record_public_invalidation_dispatch(
        self,
        job_id: str,
        *,
        status: str,
        reason: str | None,
        attempted: bool,
        attempted_at: str | None,
    ) -> None:
        with self._connect() as connection:
            self._init_schema(connection)
            cursor = connection.execute(
                """
                UPDATE publish_jobs
                SET
                    public_invalidation_dispatch_status = ?,
                    public_invalidation_dispatch_reason = ?,
                    public_invalidation_dispatch_attempted = ?,
                    public_invalidation_dispatch_attempted_at = ?
                WHERE id = ?
                """,
                (status, reason, int(attempted), attempted_at, job_id),
            )
            if cursor.rowcount != 1:
                raise PublishJobNotFoundError(job_id)

    def list_drafts(self) -> list[StoredPostDraft]:
        return self._list_posts_by_status(DRAFT_STATUS)

    def list_published(
        self,
        tag: str | None = None,
        category_id: str | None = None,
        series_id: str | None = None,
    ) -> list[StoredPostDraft]:
        posts = self._list_posts_by_status(PUBLISHED_STATUS)
        if tag is not None:
            posts = [post for post in posts if tag in post.tags]
        if category_id is not None:
            posts = [post for post in posts if post.category_id == category_id]
        if series_id is not None:
            posts = [post for post in posts if post.series_id == series_id]
        return posts

    def _list_posts_by_status(self, status: str) -> list[StoredPostDraft]:
        with self._connect() as connection:
            self._init_schema(connection)
            rows = connection.execute(
                """
                SELECT
                    posts.id,
                    posts.title,
                    posts.slug,
                    posts.status,
                    posts.content_format,
                    post_revisions.content,
                    post_revisions.metadata,
                    posts.current_revision_id,
                    posts.published_at,
                    posts.created_at,
                    posts.updated_at
                FROM posts
                JOIN post_revisions ON post_revisions.id = posts.current_revision_id
                WHERE posts.status = ?
                ORDER BY posts.created_at ASC, posts.id ASC
                """,
                (status,),
            ).fetchall()
        return [self._stored_draft_from_row(row) for row in rows]

    def get_draft(self, post_id: str) -> StoredPostDraft | None:
        return self._get_post_by_status(post_id, DRAFT_STATUS)

    def get_published(self, post_id: str) -> StoredPostDraft | None:
        return self._get_post_by_status(post_id, PUBLISHED_STATUS)

    def get_published_by_slug(self, slug: str) -> StoredPostDraft | None:
        return self._get_post_by_slug_and_status(slug, PUBLISHED_STATUS)

    def _get_post_by_status(self, post_id: str, status: str) -> StoredPostDraft | None:
        return self._get_post_by_column_and_status("posts.id", post_id, status)

    def _get_post_by_slug_and_status(self, slug: str, status: str) -> StoredPostDraft | None:
        return self._get_post_by_column_and_status("posts.slug", slug, status)

    def _get_post_by_column_and_status(self, column: Literal["posts.id", "posts.slug"], value: str, status: str) -> StoredPostDraft | None:
        with self._connect() as connection:
            self._init_schema(connection)
            row = connection.execute(
                f"""
                SELECT
                    posts.id,
                    posts.title,
                    posts.slug,
                    posts.status,
                    posts.content_format,
                    post_revisions.content,
                    post_revisions.metadata,
                    posts.current_revision_id,
                    posts.published_at,
                    posts.created_at,
                    posts.updated_at
                FROM posts
                JOIN post_revisions ON post_revisions.id = posts.current_revision_id
                WHERE {column} = ? AND posts.status = ?
                """,
                (value, status),
            ).fetchone()
        if row is None:
            return None
        return self._stored_draft_from_row(row)

    def _stored_draft_from_row(self, row: sqlite3.Row | tuple[object, ...]) -> StoredPostDraft:
        metadata = json.loads(cast(str, row[6]))
        summary = metadata.pop("summary", None)
        tags = metadata.pop("tags", [])
        category_id = metadata.pop("categoryId", None)
        series_id = metadata.pop("seriesId", None)
        return StoredPostDraft(
            post_id=cast(str, row[0]),
            title=cast(str, row[1]),
            slug=cast(str, row[2]),
            status=cast(str, row[3]),
            content_format="mdx" if row[4] == "mdx" else "markdown",
            content=cast(str, row[5]),
            summary=summary,
            tags=tags,
            category_id=category_id,
            series_id=series_id,
            metadata=metadata,
            revision_id=cast(str, row[7]),
            published_at=cast(str | None, row[8]),
            created_at=cast(str, row[9]),
            updated_at=cast(str, row[10]),
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
        run_schema_migrations(
            connection,
            [
                PostStoreMigration(
                    id=POST_STORE_BASELINE_MIGRATION_ID,
                    name=POST_STORE_BASELINE_MIGRATION_NAME,
                    apply=self._apply_baseline_schema,
                ),
            ],
        )
        self._apply_baseline_schema(connection)

    def _apply_baseline_schema(self, connection: sqlite3.Connection) -> None:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS posts (
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
        post_columns = {cast(str, row[1]) for row in connection.execute("PRAGMA table_info(posts)").fetchall()}
        if "published_at" not in post_columns:
            connection.execute("ALTER TABLE posts ADD COLUMN published_at TEXT")
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
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS publish_jobs (
                id TEXT PRIMARY KEY,
                post_id TEXT NOT NULL REFERENCES posts(id),
                revision_id TEXT NOT NULL REFERENCES post_revisions(id),
                status TEXT NOT NULL,
                scheduled_at TEXT,
                started_at TEXT,
                completed_at TEXT,
                error_code TEXT,
                error_message TEXT,
                public_invalidation_surfaces TEXT NOT NULL DEFAULT '[]',
                public_invalidation_status TEXT NOT NULL DEFAULT 'contract_only',
                public_invalidation_executor TEXT NOT NULL DEFAULT 'none',
                public_invalidation_executed_at TEXT,
                public_invalidation_error_code TEXT,
                public_invalidation_error_message TEXT,
                public_invalidation_dispatch_status TEXT NOT NULL DEFAULT 'dispatch_skipped',
                public_invalidation_dispatch_reason TEXT,
                public_invalidation_dispatch_attempted INTEGER NOT NULL DEFAULT 0,
                public_invalidation_dispatch_attempted_at TEXT
            )
            """
        )
        publish_job_columns = {cast(str, row[1]) for row in connection.execute("PRAGMA table_info(publish_jobs)").fetchall()}
        if "public_invalidation_surfaces" not in publish_job_columns:
            connection.execute("ALTER TABLE publish_jobs ADD COLUMN public_invalidation_surfaces TEXT NOT NULL DEFAULT '[]'")
        if "public_invalidation_status" not in publish_job_columns:
            connection.execute("ALTER TABLE publish_jobs ADD COLUMN public_invalidation_status TEXT NOT NULL DEFAULT 'contract_only'")
        if "public_invalidation_executor" not in publish_job_columns:
            connection.execute("ALTER TABLE publish_jobs ADD COLUMN public_invalidation_executor TEXT NOT NULL DEFAULT 'none'")
        if "public_invalidation_executed_at" not in publish_job_columns:
            connection.execute("ALTER TABLE publish_jobs ADD COLUMN public_invalidation_executed_at TEXT")
        if "public_invalidation_error_code" not in publish_job_columns:
            connection.execute("ALTER TABLE publish_jobs ADD COLUMN public_invalidation_error_code TEXT")
        if "public_invalidation_error_message" not in publish_job_columns:
            connection.execute("ALTER TABLE publish_jobs ADD COLUMN public_invalidation_error_message TEXT")
        if "public_invalidation_dispatch_status" not in publish_job_columns:
            connection.execute("ALTER TABLE publish_jobs ADD COLUMN public_invalidation_dispatch_status TEXT NOT NULL DEFAULT 'dispatch_skipped'")
        if "public_invalidation_dispatch_reason" not in publish_job_columns:
            connection.execute("ALTER TABLE publish_jobs ADD COLUMN public_invalidation_dispatch_reason TEXT")
        if "public_invalidation_dispatch_attempted" not in publish_job_columns:
            connection.execute("ALTER TABLE publish_jobs ADD COLUMN public_invalidation_dispatch_attempted INTEGER NOT NULL DEFAULT 0")
        if "public_invalidation_dispatch_attempted_at" not in publish_job_columns:
            connection.execute("ALTER TABLE publish_jobs ADD COLUMN public_invalidation_dispatch_attempted_at TEXT")
