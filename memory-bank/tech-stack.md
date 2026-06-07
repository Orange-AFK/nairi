# Nairi

## Stack Status Rule

1. This document distinguishes current implementation from target stack.
2. Do not describe a target technology as active until code, tests, and documentation verify it.
3. `data-model.md` is the authority for current persistence boundaries.

## Frontend

### Public Site

1. Current implementation: Next.js, React, TypeScript, route-level revalidation, RSS/sitemap routes, and structural checks.
2. Target expansion: Tailwind CSS, shadcn/ui, richer typography, richer SEO, and governed MDX/component rendering.
3. React keeps the public site and admin console in one ecosystem.

### CMS Admin Console

1. Current implementation: not yet implemented.
2. Target stack: React, Vite, TypeScript, TanStack Router, TanStack Query, React Hook Form, Zod, Tailwind CSS, and shadcn/ui.
3. Admin must use authenticated API contracts and must not write directly to the database.

## Backend

### API Core

1. Current implementation: FastAPI, Pydantic, scaffold settings, route tests, and SQLite-backed `PostStore` persistence.
2. Current persistence: `PostStore` initializes scaffold SQLite tables for posts, revisions, audit events, and publish jobs.
3. Target migration stack: SQLAlchemy 2.x and Alembic.
4. SQLite is the default scaffold persistence mode.
5. PostgreSQL is a future production option after the migration layer exists.

## Agent Integration

### Local API Commands

1. Use project-local virtual environments.
2. Create venv: `python3 -m venv .venv`.
3. Install API dependencies: `.venv/bin/python -m pip install -e '.[test]'`.
4. Do not reuse global or Hermes virtual environments.

### API and MCP

1. Current implementation: documented API contracts and scaffold auth routes.
2. Target implementation: MCP server wraps API capabilities into agent-friendly tools.
3. MCP tools must not bypass API auth, scopes, status transitions, or audit logging.

## Deployment

### Self-Hosted Deployment

1. Current implementation: Guards CI validates API tests and public-site build.
2. Target deployment: Docker Compose for self-hosted operation.
3. Target default database mode: SQLite.
4. Target production option: PostgreSQL after managed migrations exist.
5. Image publishing remains deferred until Dockerfile, Compose, smoke-test, runtime config, and release contracts exist.

## Rejected Alternatives

### Astro for Public Site

Astro was considered for static-first publishing, but Next.js better supports React ecosystem sharing with the planned CMS admin console.

### Hono for Core API

Hono is strong for lightweight TypeScript and edge APIs, but FastAPI is preferred for OpenAPI, Python AI tooling, SQLAlchemy, Alembic, and complex CMS workflows.
