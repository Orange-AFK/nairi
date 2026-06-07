# Nairi

## Accepted Decisions

### Use API-First Architecture

1. Status: Accepted.
2. Decision: FastAPI is the single product capability authority.
3. Rationale: Nairi needs one governed capability layer shared by frontend, admin, MCP, agents, jobs, and automation.
4. Consequence: No module may bypass API auth, scopes, status transitions, or audit logging unless documented as internal infrastructure.

### Separate Public and Management APIs

1. Status: Accepted.
2. Decision: Public content APIs and authenticated content-management APIs must use separate route contracts.
3. Rationale: Public readers need anonymous, public-safe, cacheable published data, while admin, MCP, agents, and automation need authenticated management data that may include revision, workflow, and internal metadata.
4. Consequence: `/api/v1/posts...` remains authenticated management API even for `status=published`; future public reads must use dedicated public paths such as `/api/v1/public/posts...` and public-safe response schemas.

### Use FastAPI for Core API

1. Status: Accepted.
2. Decision: Use FastAPI instead of Hono for core API.
3. Rationale: FastAPI provides strong OpenAPI support, Python AI ecosystem access, Pydantic, SQLAlchemy, and Alembic.

### Use React Ecosystem for Frontend and Admin

1. Status: Accepted.
2. Decision: Use Next.js for public frontend and React/Vite for admin.
3. Rationale: Shared React, TypeScript, Tailwind, shadcn/ui, and API client patterns reduce maintenance cost.

### Use Governed MDX

1. Status: Accepted.
2. Decision: Support MDX through component registry, permissions, risk warning, audit, and rollback.
3. Rationale: High-risk content is not automatically unsafe, but it must be visible, controllable, and recoverable.

### Maintain Bilingual Documentation

1. Status: Accepted.
2. Decision: Maintain English and Chinese documentation with consistent meaning.
3. Rationale: GitHub PRs and open-source collaboration use English, while local Chinese memory-bank files serve the owner.

### Use Minimal SQLite Store Before ORM Migration

1. Status: Accepted.
2. Decision: Use a small `PostStore` with SQLite DDL for the first article draft persistence boundary before introducing SQLAlchemy and Alembic.
3. Rationale: The current task needs verified persistence for `Post`, `PostRevision`, and `post.created` without widening into a full migration/model layer.
4. Consequence: The next migration task must replace scaffold schema initialization with managed migrations while preserving the route contract and persistence tests.
