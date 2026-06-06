# Nairi

## Docker Compose Deployment Guide

### Purpose

This guide will document self-hosted Docker Compose deployment for Nairi.

## Deployment Modes

### SQLite Default Mode

1. Intended for lightweight single-node deployments.
2. Uses a persistent local data directory.
3. Requires `NAIRI_DATABASE_URL` with SQLite connection string.

### PostgreSQL Profile Mode

1. Intended for production deployments.
2. Uses a compose profile for the `db` service.
3. Requires migration compatibility with SQLite mode.

## Environment Variables

### Required Variables

1. `NAIRI_ENV`
2. `NAIRI_API_BASE_URL`
3. `NAIRI_PUBLIC_SITE_URL`
4. `NAIRI_DATABASE_URL`
5. `NAIRI_JWT_SECRET`
6. `NAIRI_INITIAL_ADMIN_EMAIL`
7. `NAIRI_INITIAL_ADMIN_PASSWORD`

## Documentation Synchronization

Any deployment change must update `memory-bank/deployment.md`, this guide, the Chinese guide, and `.env.example` when environment variables change.
