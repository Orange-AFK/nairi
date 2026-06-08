#!/usr/bin/env python3
from __future__ import annotations

from guard_common import Guard, read


REQUIRED_PROJECT_STATE_ANCHORS = [
    "Migration Operator Handoff Docs Boundary",
    "typed migration policy failures",
    "manual intervention",
]

REQUIRED_DATA_MODEL_ANCHORS = [
    "migration repair workflow",
    "migration_name_mismatch",
    "source/backup/rehearsal paths",
    "counts",
    "schema_migrations",
    "readback IDs",
    "must stop before any automatic repair",
    "live database mutation",
]

REQUIRED_DECISION_ANCHORS = [
    "Use Explicit Migration Repair Policy Errors",
    "rehearsal JSON",
    "source/backup/rehearsal paths",
    "counts",
    "schema_migrations",
    "readback IDs",
    "migration_name_mismatch",
    "operator/developer intervention",
    "automatic metadata repair",
    "live database migration execution",
    "production database mutation",
]

REQUIRED_PROGRESS_ANCHORS = [
    "Broader Migration Repair Workflow Boundary",
    "source/backup/rehearsal paths",
    "counts",
    "schema_migrations",
    "readback IDs",
    "manual intervention",
]

FORBIDDEN_REPAIR_AUTOMATION_ANCHORS = [
    "auto-repair metadata mismatch",
    "automatically repair mismatched metadata",
    "live database migration execution is approved",
]


def main() -> None:
    guard = Guard("migration_repair_workflow_check", [])
    project_state = read("memory-bank/project-state.md")
    data_model = read("memory-bank/data-model.md")
    decisions = read("memory-bank/decisions.md")
    progress_log = read("memory-bank/progress-log.md")
    combined = "\n".join([project_state, data_model, decisions, progress_log]).lower()

    for anchor in REQUIRED_PROJECT_STATE_ANCHORS:
        guard.require(anchor in project_state, f"project-state missing migration repair workflow anchor: {anchor}")
    for anchor in REQUIRED_DATA_MODEL_ANCHORS:
        guard.require(anchor in data_model, f"data-model missing migration repair workflow anchor: {anchor}")
    for anchor in REQUIRED_DECISION_ANCHORS:
        guard.require(anchor in decisions, f"decisions missing migration repair workflow anchor: {anchor}")
    for anchor in REQUIRED_PROGRESS_ANCHORS:
        guard.require(anchor in progress_log, f"progress-log missing migration repair workflow anchor: {anchor}")
    guard.require(
        "### Broader Migration Repair Workflow Boundary\n\n1. Status: candidate next work." not in project_state,
        "project-state must not list completed Broader Migration Repair Workflow Boundary as candidate next work",
    )
    for anchor in FORBIDDEN_REPAIR_AUTOMATION_ANCHORS:
        guard.require(anchor.lower() not in combined, f"forbidden migration repair automation wording: {anchor}")

    guard.finish()


if __name__ == "__main__":
    main()
