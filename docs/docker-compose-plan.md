# Docker/Compose Deployment Plan

## Goal
Nairi 可通过 `docker compose up` 完整启动，包含 API + Admin + Public Site。

## Components

### API Service (`services/api`)
- **Dockerfile**: Python 3.11-slim, install deps from `pyproject.toml`, copy source, run via `uvicorn`
- **Port**: 8000 → 8000
- **Volume**: `nairi-data/` 目录 mount 到容器内 SQLite 文件目录
- **Env vars**: `NAIRI_DATABASE_PATH`, `NAIRI_API_TOKENS`

### Admin Frontend (`apps/admin`)
- **Dockerfile**: Node 20-slim, build with `npm run build`, serve static via nginx
- **Port**: 5173 → 80（nginx 代理 dev 模式也可以）
- **Dev mode**: mount source for hot-reload

### Public Site (`apps/public-site`)
- **Dockerfile**: Node 20-slim, build with `npm run build`, serve static via nginx
- **Port**: 3000 → 80

### Nginx Reverse Proxy
- 路由：`/` → admin (80), `/api/` → api (8000), `/public/` → public-site (3000)
- 开发模式可以用 nginx，生产用 Next.js standalone build

## File Structure
```
docker/
  Dockerfile.api
  Dockerfile.admin
  Dockerfile.public
  nginx.dev.conf
docker-compose.yml
.env.example
```

## Constraints
- 保持用户对 MIT 协议偏好
- 不污染源码目录，文件放 `docker/` 子目录
- 先跑 dev 模式（npm run dev），稳定后再切 production build
- SQLite 文件放 named volume `nairi-data`，不绑定 host 路径

## Implementation
1. ~~Write `docker-compose.yml` with all 3 services + nginx + volumes~~
2. ~~Write `Dockerfile.api`（Python 3.11-slim + uvicorn）~~
3. ~~Write `Dockerfile.admin` + `Dockerfile.public`（Node 20-slim + dev mode）~~
4. ~~Write `nginx.conf` 路由规则~~ (deferred — dev mode doesn't need nginx)
5. ~~Write `.env.example`~~
6. ~~Verify `docker compose config` 验证语法~~
7. ~~Verify `docker compose up -d` 能启动（不报 crash）~~ ✅

## Verification (2026-06-09)
```
docker compose build  ✅  (api + admin + public images built)
docker compose up -d  ✅  (all 3 services running)
curl localhost:8000/api/v1/health  ✅  → {"status":"ok","service":"nairi-api","version":"0.1.0"}
POST /api/v1/posts → 201 ✅
GET  /api/v1/public/posts → 200 ✅
Admin on :5173 → 200 ✅
Public on :3000 → 307 (Next.js dev redirect, normal) ✅
```

## Notes
- Dockerfiles placed in app/service directories (`apps/admin/Dockerfile`, `apps/public-site/Dockerfile`, `services/api/Dockerfile`) alongside source for portability
- `context: ..` in compose references project root; dockerfiles use paths like `apps/admin/`
- Volume mounts for admin and public enable hot-reload dev mode
- `nairi-data` named volume persists SQLite DB at `/data/nairi.db` inside container
- `NAIRI_API_TOKENS` env var defaults to admin-token with full scopes (override via `.env`)
- Production next steps: add nginx reverse proxy, Next.js standalone build mode, health checks for admin/public
