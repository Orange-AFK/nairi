# Nairi

## Migration Operator Handoff Guide

### Purpose

This guide describes the current operator-facing runbook for local SQLite migration rehearsal and policy-conflict handoff. It is a safe evidence workflow, not live migration execution.

## Current Boundary

1. Use `nairi-post-store-migration-rehearsal` only with explicit local paths.
2. Provide a source database path, backup artifact path, and rehearsal artifact path for every run.
3. Review the rehearsal JSON before making any follow-up decision.
4. Do not run against production directly.
5. Do not automatically repair metadata.
6. Do not delete backup or rehearsal artifacts after a failure.
7. Do not continue when `migration_name_mismatch` appears; stop for manual intervention.

## Inputs

1. source database path: the SQLite file copied from the environment being evaluated.
2. backup artifact path: the immutable backup copy created by the rehearsal command.
3. rehearsal artifact path: the disposable copy that may be opened and migrated during rehearsal.

Example shape:

```bash
nairi-post-store-migration-rehearsal \
  --source /tmp/nairi/source.db \
  --backup /tmp/nairi/source.backup.db \
  --rehearsal /tmp/nairi/source.rehearsal.db
```

## Expected Output

The command prints rehearsal JSON. Operators should preserve the complete output with the database artifacts.

Required fields to inspect:

1. `backupPath`: confirms the backup artifact path.
2. `rehearsalPath`: confirms the rehearsal artifact path.
3. `preMigrationCounts`: captures source-copy counts before migration.
4. `postMigrationCounts`: captures rehearsal-copy counts after migration.
5. `postMigrationRows`: includes `schema_migrations` evidence.
6. `readbackPostIds`: proves post records can be read back through the store.

## Review Checklist

1. Confirm the source/backup/rehearsal paths are three different resolved files.
2. Confirm `preMigrationCounts` and `postMigrationCounts` preserve expected domain row counts.
3. Confirm `postMigrationRows` includes the expected `schema_migrations` record.
4. Confirm `readbackPostIds` contains the expected post IDs.
5. Confirm the original source database was not modified by the rehearsal.
6. Confirm the backup artifact exists and remains available for later analysis.

## Stop Conditions

Stop immediately and prepare an evidence bundle when any of these occur:

1. The command exits non-zero.
2. The rehearsal JSON is missing required fields.
3. source/backup/rehearsal paths alias each other or point to unexpected files.
4. Counts differ in a way that cannot be explained by the expected migration.
5. `schema_migrations` contains unexpected rows.
6. The policy code is `migration_name_mismatch`.
7. Any operator is tempted to manually edit or repair migration metadata.

## Evidence Bundle

For manual intervention, preserve this evidence bundle:

1. Command invocation with arguments, with no secrets.
2. Full stdout and stderr.
3. Full rehearsal JSON.
4. Source file checksum if available.
5. Backup artifact path and checksum if available.
6. Rehearsal artifact path and checksum if available.
7. `schema_migrations` rows from the rehearsal artifact.
8. A short escalation note explaining the observed stop condition.

## Escalation Note

The escalation note should include:

1. Which database copy was used.
2. Whether `migration_name_mismatch` appeared.
3. Which source/backup/rehearsal paths were compared.
4. Which `preMigrationCounts`, `postMigrationCounts`, `postMigrationRows`, and `readbackPostIds` values were observed.
5. What action was explicitly not taken, especially automatic metadata repair or live database mutation.

## Allowed Follow-Up

1. Share the evidence bundle with the project maintainer or database owner.
2. Re-run rehearsal with fresh artifact paths if the first run was blocked by local file placement.
3. Open an implementation task only after the stop condition is understood and scoped.

## Forbidden Follow-Up

1. Do not run against production directly.
2. Do not automatically repair metadata.
3. Do not edit `schema_migrations` in place.
4. Do not delete backup or rehearsal artifacts while investigation is active.
5. Do not treat local rehearsal as approval for live database migration execution.
