#!/usr/bin/env python3
from __future__ import annotations

from guard_common import Guard, exists, read


EN_RUNBOOK = "docs/migration-operator-handoff.md"
CN_RUNBOOK = "docs/migration-operator-handoff-cn.md"

REQUIRED_RUNBOOK_ANCHORS = [
    "nairi-post-store-repair-dry-run",
    "sample evidence bundle",
    "commandInvocation",
    "sourceDatabasePath",
    "backupArtifactPath",
    "rehearsalArtifactPath",
    "stdout",
    "stderr",
    "rehearsalJson",
    "observedStopCondition",
    "operatorEscalationNote",
    "analysis_ready",
    "refused",
    "needs_manual_intervention",
    "missing_evidence_field",
    "missing_artifact",
    "path_aliasing",
    "invalid_rehearsal_json",
    "missing_rehearsal_json_field",
    "missing_schema_migrations",
    "count_mismatch",
    "missing_escalation_note",
    "secret_like_evidence",
    "migration_name_mismatch",
    "no automatic metadata repair",
    "no production database mutation",
    "no live database migration execution",
]

REQUIRED_MEMORY_ANCHORS = [
    "Migration Repair Operator Evidence Polish Boundary",
    "nairi-post-store-repair-dry-run",
    "sample evidence bundle",
    "additional refusal-case documentation",
]


def require_anchors(guard: Guard, path: str) -> None:
    guard.require(exists(path), f"missing migration repair evidence polish doc: {path}")
    text = read(path).lower() if exists(path) else ""
    for anchor in REQUIRED_RUNBOOK_ANCHORS:
        guard.require(anchor.lower() in text, f"{path} missing migration repair evidence polish anchor: {anchor}")


def main() -> None:
    guard = Guard("migration_repair_evidence_polish_check", [])
    require_anchors(guard, EN_RUNBOOK)
    require_anchors(guard, CN_RUNBOOK)
    memory_text = "\n".join(
        read(path)
        for path in ["memory-bank/project-state.md", "memory-bank/roadmap.md", "memory-bank/progress-log.md"]
    ).lower()
    for anchor in REQUIRED_MEMORY_ANCHORS:
        guard.require(anchor.lower() in memory_text, f"memory docs missing migration repair evidence polish anchor: {anchor}")
    guard.finish()


if __name__ == "__main__":
    main()
