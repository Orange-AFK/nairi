# Nairi

## Current State

### Project Status

1. Nairi has completed foundational documentation, guard scripts, the first API scaffold, the first protected scope-check route, scaffold-level article draft creation, the first SQLite-backed draft persistence boundary, duplicate draft slug conflict handling, the first draft input validation boundary, request-time draft timestamps, the first authenticated draft readback boundary, the first authenticated draft list boundary, the first authenticated draft update boundary, update-time duplicate slug conflict handling, update-time input validation coverage, the first authenticated publish route contract boundary, the first publish state transition boundary, and the first publish job storage boundary.
2. The FastAPI service skeleton and auth dependency exist under `services/api/`.
3. The accepted product direction is API-first and agent-first CMS.
4. FastAPI is the product capability authority.
5. Documentation, contracts, guard rules, health endpoint tests, protected scope tests, article draft creation route tests, draft persistence tests, duplicate slug tests, draft input validation tests, draft timestamp tests, draft readback tests, draft list tests, draft update tests, update duplicate slug tests, update input validation tests, publish contract tests, publish state transition tests, and publish job storage tests currently pass locally.

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
5. Authenticated draft readback now returns a created draft through `GET /api/v1/posts/{post_id}` with `posts:read` scope.
6. Authenticated draft list now returns summary-shaped draft items through `GET /api/v1/posts?status=draft` with `posts:read` scope.
7. Authenticated draft update now creates a new immutable revision through `PATCH /api/v1/posts/{post_id}` with `posts:write` scope and `expectedRevisionId` conflict protection.
8. Update-time duplicate slug requests now return a standard `409 conflict` response before creating a new revision, audit event, or post mutation.
9. Invalid update payloads now have explicit test coverage proving `400 invalid_request` before revision, audit, or post mutation side effects.
10. Authenticated publish requests now return a queued job-shaped response through `POST /api/v1/posts/{post_id}/publish` with `posts:publish` scope, standard `404`, and stale `revisionId` `409 conflict` without post/revision/audit mutation.
11. Publish requests now persist the first state transition from `draft` to `published`, set `publishedAt`/`updatedAt`, preserve the current revision, and record `post.published` audit metadata.
12. Publish requests now create a durable `publish_jobs` row for the immediate publish attempt while keeping runner and scheduling semantics deferred.
13. The next small task is Article Draft Published Readback Boundary: expose published article read/list behavior without changing public rendering yet.
14. Keep SQLAlchemy and Alembic deferred until the explicit migration/model task.
15. Preserve scope checks and standard error behavior.

## Blockers

### Current Blockers

No active blocker. Continue one named task at a time and keep guard verification mandatory.
