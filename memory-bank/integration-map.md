# Nairi

## Integration Principle

### API-Centered Integration

Every product module integrates through documented API capabilities unless explicitly documented as internal infrastructure.

## Module Integration Map

### Public Frontend to API

1. Reads public content endpoints.
2. Uses published post data only.
3. Does not access admin-only endpoints.
4. The first Next.js public site scaffold lives under `apps/public-site`.
5. `/posts` calls `GET /api/v1/public/posts` and links each item to `/posts/{slug}`.
6. `/posts/{slug}` calls `GET /api/v1/public/posts/{slug}` and renders `bodyHtml`.
7. Draft or unknown slugs map to not-found.

### CMS Admin Console to API

1. Uses authenticated admin endpoints.
2. Requires user session or token permissions.
3. Does not write directly to the database.

### MCP Server to API

1. Uses scoped API tokens.
2. Maps tools to documented endpoints.
3. Does not create behavior absent from API contract.

### AI Agent to MCP

1. Uses MCP tools for high-level operations.
2. Receives risk warnings and task status.
3. Does not call database or filesystem publication paths directly.

### Job Runner to API Core

1. Executes documented job transitions.
2. Records job and audit events.
3. May use internal service boundaries only when documented.

### FastAPI to Database

1. Owns database access through service and repository boundaries.
2. Enforces state and audit rules before persistence.

## Duplicate Capability Prevention

### Article Publishing

All clients use the same publishing capability: `POST /api/v1/posts/{post_id}/publish`.

Parallel publish endpoints are forbidden unless a future versioned contract explicitly replaces this capability.

## Permission Boundary

### Scope Enforcement

1. Public frontend receives public data only from dedicated public endpoints.
2. Public frontend must not call `/api/v1/posts...` content-management endpoints directly, even for `status=published`.
3. Admin console needs human admin scopes.
4. MCP tools need agent-safe scopes and must call authenticated content-management endpoints.
5. Job runner needs documented internal authority.
6. Audit-sensitive operations must emit audit events.

### Public vs Management Route Separation

1. Public routes are anonymous-read, CDN-cacheable candidates, and expose only public-safe published fields.
2. Management routes are authenticated, scope-checked, and may expose revision/workflow metadata required by admin, MCP, or agents.
3. Authorization must not depend on a query parameter such as `status=published` to switch a management route into a public route.
4. Adding a public capability is not a duplicate management capability when its response safety, cacheability, and caller model differ.
