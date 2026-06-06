# Nairi

[中文说明](./README-cn.md)

## Project Positioning

Nairi is an API-first, agent-first CMS for turning valuable project work, engineering experience, and problem-solving processes into reviewable, editable, and publishable long-form content.

The project is not just another blog theme. Its core idea is that the API governs every product capability, while the public site, CMS admin console, MCP server, agents, jobs, and automation all operate through documented contracts.

## Core Principles

1. FastAPI owns and governs product capabilities.
2. No frontend, admin, MCP tool, agent, job, or automation path may bypass documented API auth, scope checks, status transitions, or audit logging.
3. Contracts are designed before implementation.
4. Documents are synchronized with development progress.
5. Markdown is the safe baseline; MDX is a governed enhancement with component registry, permission control, risk warning, audit, and rollback.

## Planned Stack

## Frontend

### Public Site

1. Next.js
2. React
3. TypeScript
4. Tailwind CSS
5. shadcn/ui
6. Markdown and governed MDX rendering

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
3. SQLAlchemy 2.x
4. Alembic
5. SQLite by default
6. PostgreSQL as the production option

## Agent Integration

### Interface Layers

1. OpenAPI as the canonical API description.
2. MCP server as the agent-friendly tool layer.
3. API token scopes for capability control.
4. Audit logs for every sensitive operation.

## Repository State

The project is currently in foundational documentation design. Product code should not be implemented until the initial contracts, architecture, roadmap, and guard rules are accepted.

## Documentation Layout

1. `memory-bank/`: development memory for maintainers and agents. English files are tracked. Local Chinese `*-cn.md` files are maintained but ignored by Git.
2. `docs/`: user, operator, and contributor documentation. English and Chinese files are both tracked.
3. root files: GitHub entry points, license, environment example, and project-wide agent rules.

## License

MIT
