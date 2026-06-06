# Nairi

## Integration Principle

### API-Centered Integration

Every product module integrates through documented API capabilities unless explicitly documented as internal infrastructure.

## Module Integration Map

### Public Frontend to API

1. Reads public content endpoints.
2. Uses published post data only.
3. Does not access admin-only endpoints.

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

1. Public frontend receives public data only.
2. Admin console needs human admin scopes.
3. MCP tools need agent-safe scopes.
4. Job runner needs documented internal authority.
5. Audit-sensitive operations must emit audit events.
