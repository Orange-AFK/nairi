# Nairi

## Executable Repair Tooling Design Boundary

### Purpose

This document defines a design-only contract for future local executable repair tooling. It consumes the evidence bundle described in `docs/migration-operator-handoff.md` and turns it into a bounded preflight/dry-run contract. It does not implement repair tooling.

## Current Boundary

1. This is a design-only contract.
2. The future tool is local and operator/developer initiated.
3. The current system remains based on `nairi-post-store-migration-rehearsal` for rehearsal evidence.
4. The future tool must preserve manual intervention for policy conflicts.
5. `migration_name_mismatch` remains a stop condition.
6. `schema_migrations` remains authoritative applied-history metadata.
7. `PostStoreMigrationError` remains the typed policy error surface for migration conflicts.

## Explicit Non-Goals

1. no automatic metadata repair.
2. no production database mutation.
3. no live database migration execution.
4. no SQLAlchemy.
5. no Alembic.
6. no PostgreSQL.
7. no API route.
8. no scheduler.
9. no deployment integration.
10. no Cloudflare or CDN behavior.

## Input Contract

The input contract for any future executable repair tooling must require an evidence bundle from `docs/migration-operator-handoff.md`.

Required input fields:

1. Command invocation for `nairi-post-store-migration-rehearsal`, with no secrets.
2. Source database path and optional checksum.
3. Backup artifact path and optional checksum.
4. Rehearsal artifact path and optional checksum.
5. Full stdout and stderr from the rehearsal command.
6. Full rehearsal JSON.
7. `preMigrationCounts`.
8. `postMigrationCounts`.
9. `postMigrationRows` including `schema_migrations` evidence.
10. `readbackPostIds`.
11. Observed stop condition.
12. Operator escalation note.

## Preflight Checks

Future tooling must perform preflight checks before any analysis result is produced:

1. Verify source, backup, and rehearsal paths are distinct resolved paths.
2. Verify backup and rehearsal artifacts exist.
3. Verify the rehearsal JSON parses as structured JSON.
4. Verify required JSON fields are present.
5. Verify `schema_migrations` rows are included in `postMigrationRows`.
6. Verify `preMigrationCounts`, `postMigrationCounts`, and `readbackPostIds` are internally consistent.
7. Verify no secret-like strings are present in the evidence bundle.
8. Verify the operator escalation note states which action was intentionally not taken.

## Output Contract

The output contract for future tooling must be dry-run only.

Required output fields:

1. `status`: one of `analysis_ready`, `refused`, or `needs_manual_intervention`.
2. `reason`: human-readable explanation.
3. `policyCode`: stable policy code when available, such as `migration_name_mismatch`.
4. `validatedArtifacts`: source, backup, and rehearsal paths that passed preflight.
5. `observedCounts`: summarized `preMigrationCounts` and `postMigrationCounts`.
6. `observedMigrationRows`: summarized `schema_migrations` rows.
7. `observedReadbackPostIds`: summarized `readbackPostIds`.
8. `recommendedNextAction`: documentation-only guidance, not an execution command.

## Refusal Cases

Future tooling must refuse when any refusal cases apply:

1. Evidence bundle is missing.
2. Required artifacts are missing.
3. Source, backup, or rehearsal paths alias each other.
4. Rehearsal JSON is missing required fields.
5. `schema_migrations` rows are missing from the evidence.
6. Counts are inconsistent with the expected migration boundary.
7. The requested action would treat `migration_name_mismatch` as repairable or continuable instead of returning `needs_manual_intervention`.
8. The requested action would edit migration metadata.
9. The requested action would mutate production data.
10. The requested action would perform live database migration execution.
11. The requested action would bypass manual intervention.

## Manual Intervention Rules

1. `migration_name_mismatch` always maps to manual intervention.
2. A renamed or corrupted migration history must be evaluated by a human maintainer or database owner.
3. The future tool may summarize evidence and refusal reasons.
4. The future tool must not recommend direct metadata edits.
5. The future tool must not generate an executable repair command.

## Future Implementation Gate

Before implementation starts, a new named boundary must define tests for:

1. Input contract validation.
2. Output contract shape.
3. Refusal cases.
4. Dry-run only behavior.
5. Secret-safe evidence handling.
6. No production database mutation.
7. No live database migration execution.
