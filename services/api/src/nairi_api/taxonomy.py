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
