# Nairi

## Deployment Goals

### Primary Deployment

Docker Compose is the primary deployment interface for self-hosted users.

## Service Boundaries

### Planned Services

1. `api`: FastAPI service.
2. `web`: Next.js public frontend.
3. `admin`: React/Vite admin console build served as a web service or static asset service.
4. `db`: optional PostgreSQL service under a compose profile.
5. `reverse-proxy`: optional reverse proxy service.

## Database Modes

### SQLite Default

1. Uses a persistent volume under `data/`.
2. Suitable for lightweight single-node deployment.

### PostgreSQL Profile

1. Enabled through a compose profile.
2. Uses `NAIRI_DATABASE_URL`.
3. Requires migration compatibility.

## Image Build

### GitHub Actions

1. Build linux/amd64 images.
2. Build linux/arm64 images.
3. Publish to GHCR.
4. Support local source build from GitHub clone.

## Environment Variables

### Required Variables

1. `NAIRI_ENV`
2. `NAIRI_API_BASE_URL`
3. `NAIRI_PUBLIC_SITE_URL`
4. `NAIRI_DATABASE_URL`
5. `NAIRI_JWT_SECRET`
6. `NAIRI_INITIAL_ADMIN_EMAIL`
7. `NAIRI_INITIAL_ADMIN_PASSWORD`

## Deployment Documentation Rule

Changes to services, ports, volumes, images, or environment variables must update this file, `.env.example`, and `docs/deployment-compose.md`.
