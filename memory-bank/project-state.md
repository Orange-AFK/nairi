# Nairi

## Current State

### Project Status

1. Nairi has completed foundational documentation, guard scripts, the first API scaffold, the first protected scope-check route, scaffold-level article draft creation, the first SQLite-backed draft persistence boundary, duplicate draft slug conflict handling, the first draft input validation boundary, and request-time draft timestamps.
2. The FastAPI service skeleton and auth dependency exist under `services/api/`.
3. The accepted product direction is API-first and agent-first CMS.
4. FastAPI is the product capability authority.
5. Documentation, contracts, guard rules, health endpoint tests, protected scope tests, article draft creation route tests, draft persistence tests, duplicate slug tests, draft input validation tests, and draft timestamp tests currently pass locally.

## Confirmed Decisions

### Product Direction

1. Nairi helps convert valuable AI-agent-assisted project work into publishable articles.
2. Human administrators and AI agents are both first-class users.
3. The CMS admin console remains necessary because humans need review, editing, audit, media, settings, and recovery control.

### Technical Direction

1. Public site uses Next.js, React, Tailwind CSS, shadcn/ui, and Markdown/MDX.
2. Admin console uses React, Vite, TanStack Router, TanStack Query, React Hook Form, Zod, Tailwind CSS, and shadcn/ui.
3. Core API uses FastAPI, Pydantic, SQLAlchemy, and Alembic.
4. SQLite is default; PostgreSQL is optional for production.
5. MCP wraps documented API capabilities for agents.

## Next Named Work

### Article Draft API Development

1. SQLite-backed draft persistence now creates `Post`, `PostRevision`, and `post.created` audit rows for `POST /api/v1/posts`.
2. Duplicate draft slug requests now return a standard `409 conflict` response without creating additional persistence side effects.
3. Invalid draft input now returns a standard `400 invalid_request` response before persistence side effects.
4. Draft creation now uses request-time UTC timestamps, with injectable clock support for deterministic tests.
5. The next small task is Article Draft Response Readback Boundary: expose a minimal authenticated readback route for a created draft before widening into update or publication flow.
6. Keep SQLAlchemy and Alembic deferred until the explicit migration/model task.
7. Preserve scope checks and standard error behavior.

## Blockers

### Current Blockers

No active blocker. Continue one named task at a time and keep guard verification mandatory.
