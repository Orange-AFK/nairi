import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from nairi_api.posts import PostStoreMigrationError, rehearse_post_store_migration


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Rehearse a PostStore SQLite migration on a disposable copy.")
    parser.add_argument("--source", required=True, type=Path, help="Source SQLite database to rehearse from.")
    parser.add_argument("--backup", required=True, type=Path, help="Exclusive backup path to create.")
    parser.add_argument("--rehearsal", required=True, type=Path, help="Exclusive rehearsal database path to create.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    source_path: Path = args.source
    backup_path: Path = args.backup
    rehearsal_path: Path = args.rehearsal
    if not source_path.exists():
        print(f"source database does not exist: {source_path}", file=sys.stderr)
        return 2

    try:
        result = rehearse_post_store_migration(
            source_path=source_path,
            backup_path=backup_path,
            rehearsal_path=rehearsal_path,
        )
    except (FileExistsError, ValueError, PostStoreMigrationError, OSError) as error:
        print(f"migration rehearsal failed: {error}", file=sys.stderr)
        return 2

    print(
        json.dumps(
            {
                "backupPath": str(result.backup_path),
                "rehearsalPath": str(result.rehearsal_path),
                "preMigrationHasSchemaMigrations": result.pre_migration_has_schema_migrations,
                "preMigrationCounts": result.pre_migration_counts,
                "postMigrationCounts": result.post_migration_counts,
                "postMigrationRows": [[migration_id, name] for migration_id, name in result.post_migration_rows],
                "readbackPostIds": result.readback_post_ids,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
