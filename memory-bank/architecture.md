# Nairi

## Architecture Principle

### API Governs Everything

FastAPI is the single authority for product capabilities. Other modules are clients or infrastructure around documented API contracts.

## System Modules

### Public Frontend

1. Renders public content.
2. Reads public API endpoints.
3. Does not access the database directly.
4. Does not perform admin operations.

### CMS Admin Console

1. Provides human-facing CMS management.
2. Calls authenticated API endpoints.
3. Does not bypass API permissions or audit logging.

### FastAPI Core

1. Owns business rules.
2. Owns authentication and permission checks.
3. Owns content status transitions.
4. Owns audit event creation.
5. Owns database writes through service boundaries.

### FastAPI Scaffold

1. Package path: `services/api/src/nairi_api/`.
2. Application factory: `nairi_api.main.create_app`.
3. Runtime app object: `nairi_api.main.app`.
4. Settings module: `nairi_api.config`.
5. Auth module: `nairi_api.auth`.
6. Current public health endpoint: `GET /api/v1/health`.
7. Current protected contract smoke endpoint: `GET /api/v1/mdx-components`.
8. Test path: `services/api/tests/`.

### Authentication and Scope Boundary

1. API tokens are supplied through the `Authorization` bearer-token header.
2. Token-to-scope mappings are loaded from settings for the current scaffold.
3. Missing or invalid bearer tokens return `401` with the standard error model.
4. Tokens without the required scope return `403` with `requiredScope` in error details.
5. `admin:all` satisfies protected scope checks.
6. Current scaffold does not yet persist tokens or audit token lifecycle events.

### MCP Server

1. Exposes agent-friendly tools.
2. Maps tools to documented API capabilities.
3. Does not invent product behavior absent from API contracts.
4. Does not write directly to the database.

### Job Runner

1. Executes asynchronous publication, generation, and maintenance work.
2. Uses documented internal boundaries.
3. Preserves status transitions and audit logs.

### Database

1. Persists data for API-owned capabilities.
2. Is not an external product interface.
3. Schema changes require data model and migration updates.

## Data Flow

### Health Check Flow

1. Client calls `GET /api/v1/health`.
2. FastAPI returns `status`, `service`, and `version` from configured settings.
3. The endpoint is public-read and does not mutate state.

### Protected Scope Check Flow

1. Client calls a protected API route with a bearer token.
2. FastAPI parses the bearer token and looks up configured scopes.
3. FastAPI accepts the request when the token has the route scope or `admin:all`.
4. FastAPI rejects missing or invalid tokens before route behavior runs.
5. FastAPI rejects insufficient scopes before route behavior runs.

### Article Publishing Flow

1. Admin or agent requests draft creation through API or MCP-backed API call.
2. FastAPI validates scope and input.
3. FastAPI creates or updates content records.
4. Risk checks and audit events are recorded.
5. Admin reviews the draft through the CMS console.
6. Publish request goes through `/api/v1/posts/{post_id}/publish`.
7. The job runner performs publication work under documented state rules.

## Security Boundary

### Forbidden Bypass

1. Admin console direct database write.
2. MCP direct database write.
3. Agent direct filesystem publication.
4. Job runner state mutation without documented status transition.
5. Any content publication without permission and audit trail.
