#!/usr/bin/env python3
from __future__ import annotations

from guard_common import Guard, exists, read


DESIGN_DOC = "memory-bank/executable-repair-tooling.md"

REQUIRED_DESIGN_ANCHORS = [
    "Executable Repair Tooling Design Boundary",
    "design-only contract",
    "evidence bundle",
    "docs/migration-operator-handoff.md",
    "nairi-post-store-migration-rehearsal",
    "input contract",
    "output contract",
    "Full stdout and stderr",
    "needs_manual_intervention",
    "preflight checks",
    "dry-run only",
    "manual intervention",
    "migration_name_mismatch",
    "schema_migrations",
    "PostStoreMigrationError",
    "no automatic metadata repair",
    "no production database mutation",
    "no live database migration execution",
    "no SQLAlchemy",
    "no Alembic",
    "no PostgreSQL",
    "no API route",
    "no scheduler",
    "no deployment integration",
    "refusal cases",
]

REQUIRED_PROJECT_ANCHORS = [
    "Executable Repair Tooling Design Boundary",
    "executable-repair-tooling.md",
    "candidate next work",
]

FORBIDDEN_WORDING = [
    "implement repair cli",
    "execute repair now",
    "repair schema_migrations automatically",
    "mutate production database",
    "run live database migration",
]


def main() -> None:
    guard = Guard("executable_repair_tooling_design_check", [])

    guard.require(exists(DESIGN_DOC), f"missing executable repair tooling design doc: {DESIGN_DOC}")

    design = read(DESIGN_DOC) if exists(DESIGN_DOC) else ""
    project_state = read("memory-bank/project-state.md")
    roadmap = read("memory-bank/roadmap.md")
    progress_log = read("memory-bank/progress-log.md")
    combined = "\n".join([design, project_state, roadmap, progress_log]).lower()

    design_lower = design.lower()
    project_text_lower = "\n".join([project_state, roadmap, progress_log]).lower()
    for anchor in REQUIRED_DESIGN_ANCHORS:
        guard.require(anchor.lower() in design_lower, f"design doc missing executable repair tooling anchor: {anchor}")
    for anchor in REQUIRED_PROJECT_ANCHORS:
        guard.require(anchor.lower() in project_text_lower, f"project docs missing executable repair tooling anchor: {anchor}")
    for phrase in FORBIDDEN_WORDING:
        guard.require(phrase.lower() not in combined, f"forbidden executable repair wording: {phrase}")

    guard.finish()


if __name__ == "__main__":
    main()
