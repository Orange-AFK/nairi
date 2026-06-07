# Nairi

[中文说明](./README-cn.md)

## Project Positioning

Nairi is an API-first, agent-first CMS for turning valuable project work, engineering experience, and problem-solving processes into reviewable, editable, and publishable long-form content.

The project is not just another blog theme. Its core idea is that the API governs every product capability, while the public site, CMS admin console, MCP server, agents, jobs, and automation all operate through documented contracts.

## Core Principles

1. FastAPI owns and governs product capabilities.
2. No frontend, admin, MCP tool, agent, job, or automation path may bypass documented API auth, scope checks, status transitions, or audit logging.
3. Public reader capabilities use dedicated public API contracts and public-safe response schemas.
4. Contracts and architecture decisions are documented before or with implementation.
5. Documents are synchronized through source-of-truth roles instead of duplicated ad hoc status notes.
6. Markdown is the safe baseline; MDX is a governed enhancement with component registry, permission control, risk warning, audit, and rollback.

## Current Repository State

Nairi is in early alpha implementation.

Implemented scaffold capabilities include:

1. FastAPI service skeleton, settings, health route, and API tests.
2. Scaffold token-to-scope authentication and protected route checks.
3. SQLite-backed article draft create, read, list, update, and publish transition.
4. Durable publish job bookkeeping.
5. Authenticated published content read/list/filter/pagination.
6. Anonymous public post list and detail APIs with public-safe responses.
7. Minimal safe public `bodyHtml` rendering.
8. Next.js public site routes for home, post list, post detail, RSS, sitemap index, and posts sitemap.
9. Public frontend route metadata, canonical URLs, route-level revalidation, and bounded RSS/sitemap traversal.
10. Staged public invalidation bookkeeping with dispatcher configuration and an inert Cloudflare request-plan boundary.
11. Documentation, contract, schema, secret, and public-site structural guards in CI.

Still under active development:

1. CMS admin console implementation.
2. MCP server implementation.
3. SQLAlchemy/Alembic migration layer.
4. Deployment readiness, Docker/Compose runtime hardening, and image publishing.
5. Live external invalidation execution, including real Cloudflare purge wiring.
6. Full governed MDX/component rendering.

## Stack

## Frontend

### Public Site

1. Next.js
2. React
3. TypeScript
4. Route-level revalidation for current public cache policy
5. Planned Tailwind CSS and shadcn/ui expansion
6. Markdown baseline and future governed MDX rendering

### CMS Admin Console

1. React
2. Vite
3. TypeScript
4. TanStack Router
5. TanStack Query
6. React Hook Form
7. Zod
8. Tailwind CSS
9. shadcn/ui

## Backend

### API Core

1. FastAPI
2. Pydantic
3. Current scaffold persistence through SQLite-backed `PostStore`
4. Target migration stack: SQLAlchemy 2.x and Alembic
5. SQLite by default
6. PostgreSQL as the production option after migration support exists

## Agent Integration

### Interface Layers

1. OpenAPI as the canonical API description.
2. MCP server as the planned agent-friendly tool layer.
3. API token scopes for capability control.
4. Audit logs for sensitive operations.

## Documentation Layout

1. `memory-bank/`: development memory for maintainers and agents. English files are tracked. Local Chinese `*-cn.md` files are maintained but ignored by Git.
2. `docs/`: user, operator, and contributor documentation. English and Chinese files are both tracked.
3. root files: GitHub entry points, license, environment example, contribution/security policy, and project-wide agent rules.

## License

MIT
