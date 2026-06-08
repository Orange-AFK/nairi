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
