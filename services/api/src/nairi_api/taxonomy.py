import re
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable, cast

SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class DuplicateCategorySlugError(Exception):
    def __init__(self, slug: str) -> None:
        self.slug = slug


class CategoryNotFoundError(Exception):
    def __init__(self, category_id: str) -> None:
        self.category_id = category_id


@dataclass(frozen=True)
class Category:
    category_id: str
    name: str
    slug: str
    description: str | None
    created_at: str
    updated_at: str


class CategoryStore:
    def __init__(self, database_path: str, clock: Callable[[], datetime] | None = None) -> None:
        self.database_path = database_path
        self.clock = clock or (lambda: datetime.now(UTC))

    def _utc_now(self) -> str:
        value = self.clock()
        return value.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def list_categories(self) -> list[Category]:
        with self._connect() as connection:
            self._init_schema(connection)
            rows = connection.execute(
                "SELECT id, name, slug, description, created_at, updated_at FROM categories ORDER BY name ASC"
            ).fetchall()
        return [
            Category(
                category_id=cast(str, row[0]),
                name=cast(str, row[1]),
                slug=cast(str, row[2]),
                description=cast(str | None, row[3]),
                created_at=cast(str, row[4]),
                updated_at=cast(str, row[5]),
            )
            for row in rows
        ]

    def create_category(self, name: str, slug: str, description: str | None) -> Category:
        category_id = f"cat-{slug}"
        now = self._utc_now()
        with self._connect() as connection:
            self._init_schema(connection)
            existing = connection.execute(
                "SELECT id FROM categories WHERE slug = ?", (slug,)
            ).fetchone()
            if existing is not None:
                raise DuplicateCategorySlugError(slug)
            connection.execute(
                "INSERT INTO categories (id, name, slug, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (category_id, name, slug, description, now, now),
            )
        return Category(
            category_id=category_id,
            name=name,
            slug=slug,
            description=description,
            created_at=now,
            updated_at=now,
        )

    def get_category(self, category_id: str) -> Category | None:
        with self._connect() as connection:
            self._init_schema(connection)
            row = connection.execute(
                "SELECT id, name, slug, description, created_at, updated_at FROM categories WHERE id = ?",
                (category_id,),
            ).fetchone()
        if row is None:
            return None
        return Category(
            category_id=cast(str, row[0]),
            name=cast(str, row[1]),
            slug=cast(str, row[2]),
            description=cast(str | None, row[3]),
            created_at=cast(str, row[4]),
            updated_at=cast(str, row[5]),
        )

    def update_category(self, category_id: str, name: str, slug: str, description: str | None) -> Category:
        now = self._utc_now()
        with self._connect() as connection:
            self._init_schema(connection)
            existing_row = connection.execute(
                "SELECT id FROM categories WHERE id = ?", (category_id,)
            ).fetchone()
            if existing_row is None:
                raise CategoryNotFoundError(category_id)
            slug_row = connection.execute(
                "SELECT id FROM categories WHERE slug = ? AND id != ?",
                (slug, category_id),
            ).fetchone()
            if slug_row is not None:
                raise DuplicateCategorySlugError(slug)
            connection.execute(
                "UPDATE categories SET name = ?, slug = ?, description = ?, updated_at = ? WHERE id = ?",
                (name, slug, description, now, category_id),
            )
        return self.get_category(category_id)  # type: ignore[return-value]

    def delete_category(self, category_id: str) -> None:
        with self._connect() as connection:
            self._init_schema(connection)
            existing_row = connection.execute(
                "SELECT id FROM categories WHERE id = ?", (category_id,)
            ).fetchone()
            if existing_row is None:
                raise CategoryNotFoundError(category_id)
            connection.execute("DELETE FROM categories WHERE id = ?", (category_id,))

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
            CREATE TABLE IF NOT EXISTS categories (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                slug TEXT NOT NULL UNIQUE,
                description TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tags (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                slug TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )


class DuplicateTagSlugError(Exception):
    def __init__(self, slug: str) -> None:
        self.slug = slug


class TagNotFoundError(Exception):
    def __init__(self, tag_id: str) -> None:
        self.tag_id = tag_id


@dataclass(frozen=True)
class Tag:
    tag_id: str
    name: str
    slug: str
    created_at: str
    updated_at: str


class TagStore:
    def __init__(self, database_path: str, clock: Callable[[], datetime] | None = None) -> None:
        self.database_path = database_path
        self.clock = clock or (lambda: datetime.now(UTC))

    def _utc_now(self) -> str:
        value = self.clock()
        return value.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def list_tags(self) -> list[Tag]:
        with self._connect() as connection:
            self._init_schema(connection)
            rows = connection.execute(
                "SELECT id, name, slug, created_at, updated_at FROM tags ORDER BY name ASC"
            ).fetchall()
        return [
            Tag(
                tag_id=cast(str, row[0]),
                name=cast(str, row[1]),
                slug=cast(str, row[2]),
                created_at=cast(str, row[3]),
                updated_at=cast(str, row[4]),
            )
            for row in rows
        ]

    def create_tag(self, name: str, slug: str) -> Tag:
        tag_id = f"tag-{slug}"
        now = self._utc_now()
        with self._connect() as connection:
            self._init_schema(connection)
            existing = connection.execute(
                "SELECT id FROM tags WHERE slug = ?", (slug,)
            ).fetchone()
            if existing is not None:
                raise DuplicateTagSlugError(slug)
            connection.execute(
                "INSERT INTO tags (id, name, slug, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (tag_id, name, slug, now, now),
            )
        return Tag(
            tag_id=tag_id,
            name=name,
            slug=slug,
            created_at=now,
            updated_at=now,
        )

    def get_tag(self, tag_id: str) -> Tag | None:
        with self._connect() as connection:
            self._init_schema(connection)
            row = connection.execute(
                "SELECT id, name, slug, created_at, updated_at FROM tags WHERE id = ?",
                (tag_id,),
            ).fetchone()
        if row is None:
            return None
        return Tag(
            tag_id=cast(str, row[0]),
            name=cast(str, row[1]),
            slug=cast(str, row[2]),
            created_at=cast(str, row[3]),
            updated_at=cast(str, row[4]),
        )

    def update_tag(self, tag_id: str, name: str, slug: str) -> Tag:
        now = self._utc_now()
        with self._connect() as connection:
            self._init_schema(connection)
            existing_row = connection.execute(
                "SELECT id FROM tags WHERE id = ?", (tag_id,)
            ).fetchone()
            if existing_row is None:
                raise TagNotFoundError(tag_id)
            slug_row = connection.execute(
                "SELECT id FROM tags WHERE slug = ? AND id != ?",
                (slug, tag_id),
            ).fetchone()
            if slug_row is not None:
                raise DuplicateTagSlugError(slug)
            connection.execute(
                "UPDATE tags SET name = ?, slug = ?, updated_at = ? WHERE id = ?",
                (name, slug, now, tag_id),
            )
        return self.get_tag(tag_id)  # type: ignore[return-value]

    def delete_tag(self, tag_id: str) -> None:
        with self._connect() as connection:
            self._init_schema(connection)
            existing_row = connection.execute(
                "SELECT id FROM tags WHERE id = ?", (tag_id,)
            ).fetchone()
            if existing_row is None:
                raise TagNotFoundError(tag_id)
            connection.execute("DELETE FROM tags WHERE id = ?", (tag_id,))

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
            CREATE TABLE IF NOT EXISTS tags (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                slug TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS series (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                slug TEXT NOT NULL UNIQUE,
                description TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )


class DuplicateSeriesSlugError(Exception):
    def __init__(self, slug: str) -> None:
        self.slug = slug


class SeriesNotFoundError(Exception):
    def __init__(self, series_id: str) -> None:
        self.series_id = series_id


@dataclass(frozen=True)
class Series:
    series_id: str
    name: str
    slug: str
    description: str | None
    created_at: str
    updated_at: str


class SeriesStore:
    def __init__(self, database_path: str, clock: Callable[[], datetime] | None = None) -> None:
        self.database_path = database_path
        self.clock = clock or (lambda: datetime.now(UTC))

    def _utc_now(self) -> str:
        value = self.clock()
        return value.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def list_series(self) -> list[Series]:
        with self._connect() as connection:
            self._init_schema(connection)
            rows = connection.execute(
                "SELECT id, name, slug, description, created_at, updated_at FROM series ORDER BY name ASC"
            ).fetchall()
        return [
            Series(
                series_id=cast(str, row[0]),
                name=cast(str, row[1]),
                slug=cast(str, row[2]),
                description=cast(str | None, row[3]),
                created_at=cast(str, row[4]),
                updated_at=cast(str, row[5]),
            )
            for row in rows
        ]

    def create_series(self, name: str, slug: str, description: str | None) -> Series:
        series_id = f"series-{slug}"
        now = self._utc_now()
        with self._connect() as connection:
            self._init_schema(connection)
            existing = connection.execute(
                "SELECT id FROM series WHERE slug = ?", (slug,)
            ).fetchone()
            if existing is not None:
                raise DuplicateSeriesSlugError(slug)
            connection.execute(
                "INSERT INTO series (id, name, slug, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (series_id, name, slug, description, now, now),
            )
        return Series(
            series_id=series_id,
            name=name,
            slug=slug,
            description=description,
            created_at=now,
            updated_at=now,
        )

    def get_series(self, series_id: str) -> Series | None:
        with self._connect() as connection:
            self._init_schema(connection)
            row = connection.execute(
                "SELECT id, name, slug, description, created_at, updated_at FROM series WHERE id = ?",
                (series_id,),
            ).fetchone()
        if row is None:
            return None
        return Series(
            series_id=cast(str, row[0]),
            name=cast(str, row[1]),
            slug=cast(str, row[2]),
            description=cast(str | None, row[3]),
            created_at=cast(str, row[4]),
            updated_at=cast(str, row[5]),
        )

    def update_series(self, series_id: str, name: str, slug: str, description: str | None) -> Series:
        now = self._utc_now()
        with self._connect() as connection:
            self._init_schema(connection)
            existing_row = connection.execute(
                "SELECT id FROM series WHERE id = ?", (series_id,)
            ).fetchone()
            if existing_row is None:
                raise SeriesNotFoundError(series_id)
            slug_row = connection.execute(
                "SELECT id FROM series WHERE slug = ? AND id != ?",
                (slug, series_id),
            ).fetchone()
            if slug_row is not None:
                raise DuplicateSeriesSlugError(slug)
            connection.execute(
                "UPDATE series SET name = ?, slug = ?, description = ?, updated_at = ? WHERE id = ?",
                (name, slug, description, now, series_id),
            )
        return self.get_series(series_id)  # type: ignore[return-value]

    def delete_series(self, series_id: str) -> None:
        with self._connect() as connection:
            self._init_schema(connection)
            existing_row = connection.execute(
                "SELECT id FROM series WHERE id = ?", (series_id,)
            ).fetchone()
            if existing_row is None:
                raise SeriesNotFoundError(series_id)
            connection.execute("DELETE FROM series WHERE id = ?", (series_id,))

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
            CREATE TABLE IF NOT EXISTS series (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                slug TEXT NOT NULL UNIQUE,
                description TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
