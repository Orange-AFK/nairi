# Docker/Compose 部署计划

## 目标
Nairi 可通过 `docker compose up` 完整启动，包含 API + Admin + Public Site。

## 组件

### API 服务（`services/api`）
- **Dockerfile**：Python 3.11-slim，安装依赖（`pyproject.toml`），运行 `uvicorn`
- **端口**：8000 → 8000
- **Volume**：`nairi-data/` 目录挂载到容器内 SQLite 文件目录
- **环境变量**：`NAIRI_DATABASE_PATH`、`NAIRI_API_TOKENS`、`CORS_ORIGINS`

### Admin 前端（`apps/admin`）
- **Dockerfile**：Node 20-slim，build 后通过 nginx 提供静态文件
- **端口**：5173 → 80（dev 模式也可）
- **Dev 模式**：挂载源码实现热重载

### Public Site（`apps/public-site`）
- **Dockerfile**：Node 20-slim，build 后通过 nginx 提供静态文件
- **端口**：3000 → 80

### Nginx 反向代理
- 路由：`/` → admin（80），`/api/` → api（8000），`/public/` → public-site（3000）
- 开发模式可用 nginx，生产用 Next.js standalone build

## 文件结构
```
docker/
  Dockerfile.api
  Dockerfile.admin
  Dockerfile.public
  nginx.dev.conf
docker-compose.yml
.env.example
```

## 约束
- 保持用户对 MIT 协议偏好
- 不污染源码目录，文件放 `docker/` 子目录
- 先跑 dev 模式（npm run dev），稳定后再切 production build
- SQLite 文件放 named volume `nairi-data`，不绑定 host 路径

## 操作步骤
1. 编写 `docker-compose.yml`，包含全部 3 个服务 + nginx + volumes
2. 编写 `Dockerfile.api`（Python 3.11-slim + uvicorn）
3. 编写 `Dockerfile.admin` + `Dockerfile.public`（Node 20-slim + dev 模式）
4. 编写 `nginx.conf` 路由规则
5. 编写 `.env.example`
6. 验证 `docker compose config` 语法
7. 验证 `docker compose up -d` 能启动（不报 crash）

## 验证结果（2026-06-09）
```
docker compose build  ✅  （api + admin + public 镜像构建成功）
docker compose up -d  ✅  （3 个服务全部运行）
curl localhost:8000/api/v1/health  ✅  → {"status":"ok","service":"nairi-api","version":"0.1.0"}
POST /api/v1/posts → 201 ✅
GET  /api/v1/public/posts → 200 ✅
Admin on :5173 → 200 ✅
Public on :3000 → 307 (Next.js dev redirect, 正常) ✅
```

## 备注
- Dockerfiles 放在 app/service 目录（`apps/admin/Dockerfile`、`apps/public-site/Dockerfile`、`services/api/Dockerfile`），便于移植
- compose 中 `context: ..` 引用项目根目录；dockerfile 使用 `apps/admin/` 等路径
- Admin 和 public 的 volume mount 实现热重载开发模式
- `nairi-data` named volume 在容器内持久化 SQLite DB（`/data/nairi.db`）
- `NAIRI_API_TOKENS` 环境变量默认为 full scopes admin-token（通过 `.env` 覆盖）
- 生产环境下一步：nginx 反向代理 + HTTPS、Next.js standalone build、admin/public healthchecks
