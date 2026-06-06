# Nairi

## Accepted Decisions

### Use API-First Architecture

1. Status: Accepted.
2. Decision: FastAPI is the single product capability authority.
3. Rationale: Nairi needs one governed capability layer shared by frontend, admin, MCP, agents, jobs, and automation.
4. Consequence: No module may bypass API auth, scopes, status transitions, or audit logging unless documented as internal infrastructure.

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
