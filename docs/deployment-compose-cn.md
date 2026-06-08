# Nairi

## Docker Compose 部署手册

### 状态

1. 本文档是 deferred deployment contract stub。
2. 当前仓库不提供 Dockerfile、Compose file、container images 或 deployment smoke tests。
3. 下方内容只记录预期部署边界，不是 operator-ready deployment instructions。

### 作用

本文档记录 Nairi 未来自托管 Docker Compose 部署形态，直到 runtime files 和 smoke tests 存在。

## 部署模式

### SQLite 默认模式

1. 未来面向轻量单机部署。
2. Compose runtime 存在后会使用本地持久化数据目录。
3. 在 managed migrations 和 deployment database contracts 存在前，`NAIRI_DATABASE_PATH` 只是 scaffold contract note。

### PostgreSQL Profile 模式

1. 未来面向生产部署。
2. Compose runtime 存在后会通过 compose profile 启用 `db` 服务。
3. 在成为 deployable 之前，需要与 SQLite 模式共用兼容迁移路径。

## 环境变量

### 当前 Scaffold 变量

这些变量是当前 application settings，不证明 Compose runtime 已存在。

1. `NAIRI_SERVICE_NAME`
2. `NAIRI_VERSION`
3. `NAIRI_API_TOKENS`
4. `NAIRI_DATABASE_PATH`
5. `NAIRI_PUBLIC_INVALIDATION_DISPATCHER`
6. `NAIRI_PUBLIC_INVALIDATION_CLOUDFLARE_ZONE_ID`
7. `NAIRI_PUBLIC_INVALIDATION_CLOUDFLARE_API_TOKEN`

### 未来部署变量

Runtime URL、JWT、initial-admin 和 database URL 变量仍是未来部署工作，直到对应 settings 和 deployment contracts 存在。

## Deferred Runtime Artifacts

以下 artifacts 仍是未来工作：

1. API Dockerfile。
2. Public-site Dockerfile 或 static-serving image contract。
3. Admin Dockerfile 或 static-serving image contract。
4. Compose file 和 optional profiles。
5. Runtime `.env` template for Compose。
6. Container health checks 和 smoke tests。
7. GHCR image publishing。

## 文档同步

任何部署变更都必须同步更新 `memory-bank/deployment.md`、本手册、英文手册以及涉及环境变量时的 `.env.example`。
