# Nairi

## Frontend

### Public Site

1. Next.js provides React-based routing, rendering, and MDX integration.
2. React keeps the public site and admin console in one ecosystem.
3. Tailwind CSS and shadcn/ui provide customizable product UI.
4. Markdown and governed MDX support technical writing and embedded components.

### Admin Console

1. React and Vite provide a fast SPA admin experience.
2. TanStack Router handles typed admin routing.
3. TanStack Query handles API state and caching.
4. React Hook Form and Zod handle form state and validation.
5. shadcn/ui provides maintainable, customizable CMS UI components.

## Backend

### API Core

1. FastAPI is the selected API framework.
2. Pydantic defines request and response schemas.
3. SQLAlchemy 2.x defines persistence models.
4. Alembic manages database migrations.
5. SQLite is default for simple self-hosted deployments.
6. PostgreSQL is supported for production deployments.

## Agent Integration

### Local API Commands

1. Create the project virtual environment: `python3 -m venv .venv`.
2. Verify isolation: `.venv/bin/python -c "import sys; print(sys.prefix)"`.
3. Install API dependencies: `.venv/bin/python -m pip install -e '.[test]'`.
4. Run API tests: `.venv/bin/python -m pytest -q`.
5. Run the API app locally: `.venv/bin/python -m uvicorn nairi_api.main:app --app-dir services/api/src --reload`.

### API and MCP

1. OpenAPI is the canonical API description.
2. MCP server wraps API capabilities into agent-friendly tools.
3. API token scopes govern agent permissions.
4. Audit logs record sensitive operations.

## Deployment

### Self-Hosted Deployment

1. Docker Compose is the primary deployment interface.
2. GitHub Actions builds multi-architecture images.
3. GHCR is the planned container registry.
4. Local source builds from GitHub are supported.

## Rejected Alternatives

### Astro for Public Site

Astro remains strong for content sites, but React ecosystem unification is preferred for Nairi maintenance and shared components.

### Hono for Core API

Hono is strong for lightweight TypeScript and edge APIs, but FastAPI is preferred for OpenAPI, Python AI tooling, SQLAlchemy, Alembic, and complex CMS workflows.
