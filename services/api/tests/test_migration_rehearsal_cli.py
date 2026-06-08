import json
import sqlite3
from pathlib import Path

from nairi_api.migration_rehearsal import main


def create_pre_migration_database(database_path: Path) -> None:
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
                "draft-cli",
                "CLI rehearsal",
                "cli-rehearsal",
                "draft",
                "markdown",
                "revision-cli-1",
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
                "revision-cli-1",
                "draft-cli",
                "CLI rehearsal content",
                '{"summary":"CLI rehearsal summary","tags":["migration"],"categoryId":null,"seriesId":null}',
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
                "draft-cli",
                "{}",
                "2026-06-07T08:11:12Z",
            ),
        )


def test_migration_rehearsal_cli_has_project_script_entrypoint() -> None:
    import tomllib

    project_config = tomllib.loads(Path("pyproject.toml").read_text())

    assert project_config["project"]["scripts"]["nairi-post-store-migration-rehearsal"] == (
        "nairi_api.migration_rehearsal:main"
    )


def test_migration_rehearsal_cli_outputs_json_summary(tmp_path: Path, capsys) -> None:
    source_path = tmp_path / "pre-migration.db"
    backup_path = tmp_path / "backup" / "pre-migration.db.bak"
    rehearsal_path = tmp_path / "rehearsal" / "working.db"
    create_pre_migration_database(source_path)

    exit_code = main(
        [
            "--source",
            str(source_path),
            "--backup",
            str(backup_path),
            "--rehearsal",
            str(rehearsal_path),
        ]
    )

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output == {
        "backupPath": str(backup_path),
        "rehearsalPath": str(rehearsal_path),
        "preMigrationHasSchemaMigrations": False,
        "preMigrationCounts": {"posts": 1, "post_revisions": 1, "audit_events": 1},
        "postMigrationCounts": {"posts": 1, "post_revisions": 1, "audit_events": 1},
        "postMigrationRows": [[1, "post_store_baseline"]],
        "readbackPostIds": ["draft-cli"],
    }

    with sqlite3.connect(source_path) as connection:
        source_migration_table = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'schema_migrations'"
        ).fetchone()
    with sqlite3.connect(backup_path) as connection:
        backup_migration_table = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'schema_migrations'"
        ).fetchone()

    assert source_migration_table is None
    assert backup_migration_table is None


def test_migration_rehearsal_cli_fails_closed_for_missing_source(tmp_path: Path, capsys) -> None:
    exit_code = main(
        [
            "--source",
            str(tmp_path / "missing.db"),
            "--backup",
            str(tmp_path / "backup.db"),
            "--rehearsal",
            str(tmp_path / "rehearsal.db"),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 2
    assert captured.out == ""
    assert "source database does not exist" in captured.err
