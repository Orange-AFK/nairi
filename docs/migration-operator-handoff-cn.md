# Nairi

## Migration Operator Handoff Guide

### Purpose

本文档描述当前 operator-facing runbook，用于 local SQLite migration rehearsal 和 policy-conflict handoff。它是 safe evidence workflow，不是 live migration execution。

## Current Boundary

1. 只在 explicit local paths 上使用 `nairi-post-store-migration-rehearsal`。
2. 每次运行都提供 source database path、backup artifact path 和 rehearsal artifact path。
3. 在任何 follow-up decision 前先 review rehearsal JSON。
4. Do not run against production directly。
5. Do not automatically repair metadata。
6. Do not delete backup or rehearsal artifacts after a failure。
7. 当出现 `migration_name_mismatch` 时不要继续；停止并进入 manual intervention。

## Inputs

1. source database path: 从被评估环境复制出的 SQLite file。
2. backup artifact path: rehearsal command 创建的 immutable backup copy。
3. rehearsal artifact path: rehearsal 期间可以被打开和 migrated 的 disposable copy。

Example shape:

```bash
nairi-post-store-migration-rehearsal \
  --source /tmp/nairi/source.db \
  --backup /tmp/nairi/source.backup.db \
  --rehearsal /tmp/nairi/source.rehearsal.db
```

## Expected Output

命令会打印 rehearsal JSON。Operators 应把完整输出和 database artifacts 一起保留。

Required fields to inspect:

1. `backupPath`: 确认 backup artifact path。
2. `rehearsalPath`: 确认 rehearsal artifact path。
3. `preMigrationCounts`: 记录 migration 前 source-copy counts。
4. `postMigrationCounts`: 记录 migration 后 rehearsal-copy counts。
5. `postMigrationRows`: 包含 `schema_migrations` evidence。
6. `readbackPostIds`: 证明 post records 可以通过 store read back。

## Review Checklist

1. 确认 source/backup/rehearsal paths 是三个不同 resolved files。
2. 确认 `preMigrationCounts` 和 `postMigrationCounts` 保留 expected domain row counts。
3. 确认 `postMigrationRows` 包含 expected `schema_migrations` record。
4. 确认 `readbackPostIds` 包含 expected post IDs。
5. 确认 original source database 未被 rehearsal 修改。
6. 确认 backup artifact 存在并可用于后续分析。

## Stop Conditions

出现以下任一情况时立即停止并准备 evidence bundle：

1. 命令返回 non-zero。
2. rehearsal JSON 缺少 required fields。
3. source/backup/rehearsal paths alias each other 或指向 unexpected files。
4. Counts differ in a way that cannot be explained by the expected migration。
5. `schema_migrations` 包含 unexpected rows。
6. Policy code 是 `migration_name_mismatch`。
7. 任何 operator 想要 manually edit 或 repair migration metadata。

## Evidence Bundle

manual intervention 时保留这个 evidence bundle：

1. Command invocation with arguments, with no secrets。
2. Full stdout and stderr。
3. Full rehearsal JSON。
4. Source file checksum if available。
5. Backup artifact path and checksum if available。
6. Rehearsal artifact path and checksum if available。
7. `schema_migrations` rows from the rehearsal artifact。
8. A short escalation note explaining the observed stop condition。

## Dry-Run Evidence Analysis

保存 rehearsal evidence bundle 后，operator 可以运行 local dry-run analysis。This is analysis only，并不批准 repair actions。

Example shape:

```bash
nairi-post-store-repair-dry-run --evidence /tmp/nairi/evidence.json
```

Dry-run analyzer 读取 evidence bundle，并输出三个 status 之一：

1. `analysis_ready`: evidence bundle passed local preflight checks and can be reviewed。
2. `refused`: evidence bundle is incomplete or unsafe to summarize。
3. `needs_manual_intervention`: evidence is safe to summarize, but policy conflict such as `migration_name_mismatch` requires escalation before any repair action。

Analyzer performs no automatic metadata repair, no production database mutation, and no live database migration execution。

## Sample Evidence Bundle

A sample evidence bundle uses this JSON shape。Paths are examples；do not include secrets。

```json
{
  "commandInvocation": "nairi-post-store-migration-rehearsal --source /tmp/nairi/source.db --backup /tmp/nairi/source.backup.db --rehearsal /tmp/nairi/source.rehearsal.db",
  "sourceDatabasePath": "/tmp/nairi/source.db",
  "backupArtifactPath": "/tmp/nairi/source.backup.db",
  "rehearsalArtifactPath": "/tmp/nairi/source.rehearsal.db",
  "stdout": "{...full rehearsal JSON...}",
  "stderr": "",
  "rehearsalJson": {
    "backupPath": "/tmp/nairi/source.backup.db",
    "rehearsalPath": "/tmp/nairi/source.rehearsal.db",
    "preMigrationCounts": {"posts": 1, "post_revisions": 1, "audit_events": 1},
    "postMigrationCounts": {"posts": 1, "post_revisions": 1, "audit_events": 1},
    "postMigrationRows": [[1, "post_store_baseline"]],
    "readbackPostIds": ["draft-example"]
  },
  "observedStopCondition": null,
  "operatorEscalationNote": "No automatic metadata repair, no production database mutation, and no live database migration execution were performed."
}
```

## Dry-Run Refusal Cases

`nairi-post-store-repair-dry-run` returns `refused` for these policy codes：

1. `missing_evidence_field`: a required top-level field is missing。
2. `missing_artifact`: the source, backup, or rehearsal artifact cannot be found。
3. `path_aliasing`: source, backup, and rehearsal paths do not resolve to three different files。
4. `invalid_rehearsal_json`: `rehearsalJson` is not structured JSON。
5. `missing_rehearsal_json_field`: required rehearsal JSON fields are missing。
6. `missing_schema_migrations`: `postMigrationRows` does not include usable `schema_migrations` evidence。
7. `count_mismatch`: `preMigrationCounts` and `postMigrationCounts` are inconsistent for this boundary。
8. `missing_escalation_note`: escalation note does not state which actions were intentionally not taken。
9. `secret_like_evidence`: evidence appears to contain secret-like text and must be redacted before analysis。
10. `unreadable_evidence_bundle`: evidence file cannot be read or parsed by the CLI。
11. `invalid_evidence_bundle`: evidence file is valid JSON but is not a JSON object。

A `migration_name_mismatch` with usable `schema_migrations` evidence returns `needs_manual_intervention`, not repair approval。

## Escalation Note

escalation note 应包含：

1. Which database copy was used。
2. Whether `migration_name_mismatch` appeared。
3. Which source/backup/rehearsal paths were compared。
4. Which `preMigrationCounts`, `postMigrationCounts`, `postMigrationRows`, and `readbackPostIds` values were observed。
5. What action was explicitly not taken, especially automatic metadata repair or live database mutation。

## Allowed Follow-Up

1. Share the evidence bundle with the project maintainer or database owner。
2. 如果第一次运行被 local file placement 阻塞，可以用 fresh artifact paths re-run rehearsal。
3. 只有在 stop condition 被理解并 scoped 后，才 open implementation task。

## Forbidden Follow-Up

1. Do not run against production directly。
2. Do not automatically repair metadata。
3. Do not edit `schema_migrations` in place。
4. Do not delete backup or rehearsal artifacts while investigation is active。
5. Do not treat local rehearsal as approval for live database migration execution。
