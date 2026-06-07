# Nairi

## Docker Compose 部署手册

### 作用

本文档用于说明 Nairi 的自托管 Docker Compose 部署方式。

## 部署模式

### SQLite 默认模式

1. 面向轻量单机部署。
2. 使用本地持久化数据目录。
3. 在 managed migrations 和 deployment database contracts 存在前，使用 scaffold `NAIRI_DATABASE_PATH` setting。

### PostgreSQL Profile 模式

1. 面向生产部署。
2. 通过 compose profile 启用 `db` 服务。
3. 需要与 SQLite 模式共用兼容迁移路径。

## 环境变量

### 当前 Scaffold 变量

1. `NAIRI_SERVICE_NAME`
2. `NAIRI_VERSION`
3. `NAIRI_API_TOKENS`
4. `NAIRI_DATABASE_PATH`
5. `NAIRI_PUBLIC_INVALIDATION_DISPATCHER`
6. NAIRI_PUBLIC_INVALIDATION_CLOUDFLARE_ZONE_ID
7. NAIRI_PUBLIC_INVALIDATION_CLOUDFLARE_API_TOKEN

### 未来部署变量

Runtime URL、JWT、initial-admin 和 database URL 变量仍是未来部署工作，直到对应 settings 和 deployment contracts 存在。

## 文档同步

任何部署变更都必须同步更新 `memory-bank/deployment.md`、本手册、英文手册以及涉及环境变量时的 `.env.example`。
