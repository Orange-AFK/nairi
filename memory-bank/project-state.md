# Nairi

## Current State

### Project Status

1. Nairi has completed foundational documentation, guard scripts, the first API scaffold, the first protected scope-check route, scaffold-level article draft creation, and the first SQLite-backed draft persistence boundary.
2. The FastAPI service skeleton and auth dependency exist under `services/api/`.
3. The accepted product direction is API-first and agent-first CMS.
4. FastAPI is the product capability authority.
5. Documentation, contracts, guard rules, health endpoint tests, protected scope tests, article draft creation route tests, and draft persistence tests currently pass locally.

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
2. The next small task is Article Draft Duplicate Slug Handling: return a standard conflict/error response before expanding update or publication flow.
3. Keep SQLAlchemy and Alembic deferred until the explicit migration/model task.
4. Preserve scope checks and standard error behavior.

## Blockers

### Current Blockers

No active blocker. Continue one named task at a time and keep guard verification mandatory.
