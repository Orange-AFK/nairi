# Nairi

## Docker Compose Deployment Guide

### Status

1. This document is a deferred deployment contract stub.
2. The repository does not currently ship Dockerfiles, a Compose file, container images, or deployment smoke tests.
3. The notes below describe intended deployment boundaries only; they are not operator-ready deployment instructions.

### Purpose

This guide records the future self-hosted Docker Compose deployment shape for Nairi until the runtime files and smoke tests exist.

## Deployment Modes

### SQLite Default Mode

1. Intended future mode for lightweight single-node deployments.
2. Will use a persistent local data directory after the Compose runtime exists.
3. Uses the scaffold `NAIRI_DATABASE_PATH` setting as a contract note until managed migrations and deployment database contracts exist.

### PostgreSQL Profile Mode

1. Intended future mode for production deployments.
2. Will use a compose profile for the `db` service after the Compose runtime exists.
3. Requires migration compatibility with SQLite mode before it can become deployable.

## Environment Variables

### Current Scaffold Variables

These variables are current application settings, not proof that a Compose runtime exists.

1. `NAIRI_SERVICE_NAME`
2. `NAIRI_VERSION`
3. `NAIRI_API_TOKENS`
4. `NAIRI_DATABASE_PATH`
5. `NAIRI_PUBLIC_INVALIDATION_DISPATCHER`
6. `NAIRI_PUBLIC_INVALIDATION_CLOUDFLARE_ZONE_ID`
7. `NAIRI_PUBLIC_INVALIDATION_CLOUDFLARE_API_TOKEN`

### Future Deployment Variables

Runtime URL, JWT, initial-admin, and database URL variables remain future deployment work until the corresponding settings and deployment contracts exist.

## Deferred Runtime Artifacts

The following artifacts remain future work:

1. API Dockerfile.
2. Public-site Dockerfile or static-serving image contract.
3. Admin Dockerfile or static-serving image contract.
4. Compose file and optional profiles.
5. Runtime `.env` template for Compose.
6. Container health checks and smoke tests.
7. GHCR image publishing.

## Documentation Synchronization

Any deployment change must update `memory-bank/deployment.md`, this guide, the Chinese guide, and `.env.example` when environment variables change.
