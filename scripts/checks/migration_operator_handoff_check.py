#!/usr/bin/env python3
from __future__ import annotations

from guard_common import Guard, exists, read


RUNBOOK = "docs/migration-operator-handoff.md"
CHINESE_RUNBOOK = "docs/migration-operator-handoff-cn.md"

REQUIRED_RUNBOOK_ANCHORS = [
    "nairi-post-store-migration-rehearsal",
    "source database path",
    "backup artifact path",
    "rehearsal artifact path",
    "rehearsal JSON",
    "source/backup/rehearsal paths",
    "preMigrationCounts",
    "postMigrationCounts",
    "postMigrationRows",
    "readbackPostIds",
    "schema_migrations",
    "migration_name_mismatch",
    "manual intervention",
    "evidence bundle",
    "escalation note",
    "do not run against production directly",
    "do not automatically repair metadata",
    "do not delete backup or rehearsal artifacts",
]

REQUIRED_MEMORY_ANCHORS = [
    "Migration Operator Handoff Docs Boundary",
    "migration-operator-handoff.md",
    "operator-facing runbook",
]

FORBIDDEN_HANDOFF_WORDING = [
    "run the rehearsal CLI against production",
    "repair schema_migrations automatically",
    "delete the backup artifact after failure",
    "continue after migration_name_mismatch",
]


def main() -> None:
    guard = Guard("migration_operator_handoff_check", [])

    guard.require(exists(RUNBOOK), f"missing operator handoff runbook: {RUNBOOK}")
    guard.require(exists(CHINESE_RUNBOOK), f"missing Chinese operator handoff runbook pair: {CHINESE_RUNBOOK}")

    runbook = read(RUNBOOK) if exists(RUNBOOK) else ""
    chinese_runbook = read(CHINESE_RUNBOOK) if exists(CHINESE_RUNBOOK) else ""
    memory_text = "\n".join(
        [
            read("memory-bank/project-state.md"),
            read("memory-bank/roadmap.md"),
            read("memory-bank/progress-log.md"),
        ]
    )
    combined = f"{runbook}\n{memory_text}".lower()

    runbook_lower = runbook.lower()
    chinese_runbook_lower = chinese_runbook.lower()
    memory_lower = memory_text.lower()
    for anchor in REQUIRED_RUNBOOK_ANCHORS:
        guard.require(anchor.lower() in runbook_lower, f"operator handoff runbook missing anchor: {anchor}")
        guard.require(anchor.lower() in chinese_runbook_lower, f"Chinese operator handoff runbook missing anchor: {anchor}")
    for anchor in REQUIRED_MEMORY_ANCHORS:
        guard.require(anchor.lower() in memory_lower, f"memory docs missing operator handoff anchor: {anchor}")
    for phrase in FORBIDDEN_HANDOFF_WORDING:
        guard.require(phrase.lower() not in combined, f"forbidden operator handoff wording: {phrase}")

    guard.finish()


if __name__ == "__main__":
    main()
