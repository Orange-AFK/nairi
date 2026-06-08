# Nairi

## Deployment Goals

### Primary Deployment

Docker Compose is the planned primary deployment interface for self-hosted users.

### Current Runtime Status

1. Deployment readiness is deferred.
2. The repository does not currently ship Dockerfiles, a Compose file, container images, or deployment smoke tests.
3. `docs/deployment-compose.md` is a deferred deployment contract stub until those runtime artifacts exist.

## Service Boundaries

### Planned Services

1. `api`: FastAPI service.
2. `web`: Next.js public frontend.
3. `admin`: React/Vite admin console build served as a web service or static asset service.
4. `db`: optional PostgreSQL service under a compose profile.
5. `reverse-proxy`: optional reverse proxy service.

These services are planned boundaries only; no Compose runtime currently defines them.

## Database Modes

### SQLite Default

1. Uses a persistent volume under `data/`.
2. Suitable for lightweight single-node deployment.

### PostgreSQL Profile

1. Enabled through a compose profile.
2. Will use a future database connection setting after managed migrations and production database contracts exist.
3. Requires migration compatibility.

## Image Build

### GitHub Actions

1. The current Guards workflow validates the public site build but does not publish container images.
2. Automatic GHCR image publishing remains deferred until Dockerfile, Compose, runtime configuration, smoke-test, and deployment readiness contracts exist.
3. The first image publishing workflow should be manually triggered or release/tag-triggered before any automatic `main` image publishing is enabled.
4. Future production image publishing should build linux/amd64 and linux/arm64 images.
5. Local source builds from GitHub clone remain supported.

## Environment Variables

### Current Scaffold Variables

1. `NAIRI_SERVICE_NAME`
2. `NAIRI_VERSION`
3. `NAIRI_API_TOKENS`
4. `NAIRI_DATABASE_PATH`
5. `NAIRI_PUBLIC_INVALIDATION_DISPATCHER`
6. NAIRI_PUBLIC_INVALIDATION_CLOUDFLARE_ZONE_ID
7. NAIRI_PUBLIC_INVALIDATION_CLOUDFLARE_API_TOKEN

### Future Deployment Variables

Runtime URL, JWT, initial-admin, and database URL variables remain future deployment work until the corresponding settings and deployment contracts exist.

## Deployment Documentation Rule

Changes to services, ports, volumes, images, or environment variables must update this file, `.env.example`, and `docs/deployment-compose.md`.
