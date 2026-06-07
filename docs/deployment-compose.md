# Nairi

## Docker Compose Deployment Guide

### Purpose

This guide will document self-hosted Docker Compose deployment for Nairi.

## Deployment Modes

### SQLite Default Mode

1. Intended for lightweight single-node deployments.
2. Uses a persistent local data directory.
3. Uses the scaffold `NAIRI_DATABASE_PATH` setting until managed migrations and deployment database contracts exist.

### PostgreSQL Profile Mode

1. Intended for production deployments.
2. Uses a compose profile for the `db` service.
3. Requires migration compatibility with SQLite mode.

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

## Documentation Synchronization

Any deployment change must update `memory-bank/deployment.md`, this guide, the Chinese guide, and `.env.example` when environment variables change.
