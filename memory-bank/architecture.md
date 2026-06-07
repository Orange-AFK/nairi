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
6. Post persistence module: `nairi_api.posts`.
7. Current public health endpoint: `GET /api/v1/health`.
8. Current protected contract smoke endpoint: `GET /api/v1/mdx-components`.
9. Current article draft creation endpoint: `POST /api/v1/posts`.
10. Current article list endpoint: `GET /api/v1/posts?status=draft|published`.
11. Current article readback endpoint: `GET /api/v1/posts/{post_id}` for draft or published posts.
12. Current article draft update endpoint: `PATCH /api/v1/posts/{post_id}`.
13. Current article draft publish endpoint: `POST /api/v1/posts/{post_id}/publish`.
14. Test path: `services/api/tests/`.

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
4. Current scaffold-level SQLite tables are initialized by `PostStore` for `posts`, `post_revisions`, `audit_events`, and `publish_jobs`.
5. SQLAlchemy and Alembic remain planned but are not yet introduced in code.

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
3. `PostStore` creates a `posts` row with status `draft`.
4. `PostStore` assigns a request-time UTC timestamp and stores it on the post, revision, and audit event rows.
5. `PostStore` creates a matching immutable `post_revisions` row.
6. `PostStore` records a `post.created` audit row.
7. Admin, MCP, or authorized clients list drafts through `GET /api/v1/posts?status=draft` with `posts:read` scope.
8. Admin, MCP, or authorized clients read a draft detail through `GET /api/v1/posts/{post_id}` with `posts:read` scope.
9. Admin, MCP, or authorized clients update a draft through `PATCH /api/v1/posts/{post_id}` with `posts:write` scope and `expectedRevisionId` concurrency control.
10. Admin reviews the draft through the CMS console.
11. Publish request goes through `/api/v1/posts/{post_id}/publish` with `posts:publish` scope and the current draft `revisionId`.
12. `PostStore` creates a durable `publish_jobs` row for the immediate publish attempt.
13. `PostStore` changes the post status to `published`, writes request-time `published_at` and `updated_at`, preserves the current revision, and records `post.published` audit metadata.
14. `PostStore` stores a recorded public invalidation execution and dispatch row on the publish job, including surfaces `/posts`, `/posts/{slug}`, `/rss.xml`, and `/sitemap.xml`, `status=recorded`, `executor=none`, `executed_at=published_at`, no error fields, `dispatch_status=dispatch_skipped`, `dispatch_reason=no_dispatcher_configured`, `dispatch_attempted=false`, and `dispatch_attempted_at=null`.
15. The publish API returns that invalidation record with `mode=recorded` plus dispatch bookkeeping. API settings currently expose `public_invalidation_dispatcher=none|contract|cloudflare`, with env wiring for `NAIRI_PUBLIC_INVALIDATION_DISPATCHER=none|contract|cloudflare`; Cloudflare settings can also be supplied as `NAIRI_PUBLIC_INVALIDATION_CLOUDFLARE_ZONE_ID` plus secret `NAIRI_PUBLIC_INVALIDATION_CLOUDFLARE_API_TOKEN`; unsupported dispatcher values are still rejected before external dispatch behavior exists.
16. App creation builds `app.state.public_invalidation_dispatcher` from settings. Current implementations are `NoopPublicInvalidationDispatcher` for `none`, `ContractPublicInvalidationDispatcher` for `contract`, and `CloudflarePublicInvalidationDispatcher` for `cloudflare`; all return deterministic bookkeeping and do not call external systems. The Cloudflare adapter returns `cloudflare_adapter_missing_settings` until both Cloudflare settings are configured. Once settings are present, dispatch builds or depends on an inert `CloudflarePurgeRequestPlan` for `/client/v4/zones/{zone_id}/purge_cache` from deduplicated ordered surfaces and returns `cloudflare_adapter_dry_run` with `attempted=true` and `attempted_at=published_at`; dispatch does not expose the plan, execute the plan, or call Cloudflare.
17. After successful publish storage, the publish route calls the configured dispatcher with the recorded surfaces and `published_at`, maps the dispatcher result into the response `publicInvalidation.dispatch` object, and records the same dispatcher result back onto the durable `publish_jobs` dispatch fields.
18. If the dispatcher raises, the publish route records failed dispatch bookkeeping (`dispatch_failed` / `dispatcher_exception`) in the response and publish job instead of rolling back the successful publish transition; direct dispatch-row updates fail closed if the publish job row is missing.
19. The publish flow does not trigger CDN purge, Next.js tag/path revalidation, webhooks, cache headers, or any external invalidation side effect.
20. Admin, MCP, and authorized clients can read published summaries through `GET /api/v1/posts?status=published` and published detail through `GET /api/v1/posts/{post_id}` with `posts:read` scope in the current scaffold.
21. Public clients read published summaries through `GET /api/v1/public/posts`, which is anonymous and returns only public-safe fields.
22. Public clients read published detail through `GET /api/v1/public/posts/{slug}`, which is anonymous, slug-based, published-only, and returns a public-safe detail response.
23. Public detail includes both authored `content` and a minimal sanitized `bodyHtml` render output. The renderer is intentionally not full MDX execution; it only handles a small Markdown subset and strips script blocks from rendered HTML.
24. Public clients must not reuse authenticated content-management routes.
25. Authenticated published summary lists can currently be filtered by tag membership, category id, or series id.
26. Authenticated and public published summary lists can currently be paginated with `limit` and an item-id `cursor`.
27. Public filtering inputs, full MDX/component rendering, scheduling semantics, external invalidation execution, and the job runner remain future work under documented state rules.

## Security Boundary

### Forbidden Bypass

1. Admin console direct database write.
2. MCP direct database write.
3. Agent direct filesystem publication.
4. Job runner state mutation without documented status transition.
5. Any content publication without permission and audit trail.
