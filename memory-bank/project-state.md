# Nairi

## Current State

### Project Status

1. Nairi is in early alpha implementation.
2. The implementation still follows the accepted API-first, agent-first CMS direction.
3. Core public and management content flows exist as scaffold implementations with verified route tests and guards.
4. The current development focus is Article Public Sitemap Additional Shards Boundary.
5. Cloudflare dry-run dispatch has merged; the sitemap work is now splitting stable public landing routes into a dedicated static sitemap shard.

### Current Authority Snapshot

1. `project-state.md` is the current status source of truth.
2. `roadmap.md` is the functional roadmap source of truth.
3. `decisions.md` is the durable architecture decision source of truth.
4. `progress-log.md` is append-only historical evidence.
5. `project-review.md` is a historical review artifact for this remediation and is not maintained during normal feature work.

## Implemented Functional Areas

### Foundation and Guards

1. Foundational documentation, documentation boundaries, bilingual rules, guard scripts, and Guards CI exist.
2. Current guards cover docs boundaries, bilingual contract-token drift, contract consistency, API schema casing, secret safety, and selected public-site structural checks.
3. CI uses read-only permissions, concurrency cancellation, and Node.js 24 opt-in for JavaScript actions.

### API Core and Authentication

1. FastAPI service skeleton and app factory exist under `services/api/`.
2. Health endpoint and tests exist.
3. Scaffold token-to-scope authentication, bearer parsing, protected scope checks, and standard API error handling exist.
4. Current route inventory includes `GET /api/v1/health`, `GET /api/v1/mdx-components`, content management routes, and public content routes.

### Content Draft and Publishing

1. SQLite-backed scaffold persistence uses `PostStore` for posts, revisions, audit events, and publish jobs.
2. Authenticated draft create, read, list, update, duplicate slug handling, update conflict handling, validation, request-time timestamps, and immutable revisions exist.
3. Authenticated publish requests perform the first immediate publish transition, preserve current revision, record `post.published`, and create durable publish-job bookkeeping.
4. Authenticated published read/list/filter/pagination exists through management routes with `posts:read` scope.

### Public Content API

1. Anonymous `GET /api/v1/public/posts` exposes public-safe published summaries.
2. Anonymous `GET /api/v1/public/posts/{slug}` exposes public-safe published detail by slug.
3. Public list supports minimal `limit` and item-id `cursor` pagination plus `page` metadata.
4. Public detail includes minimal safe `bodyHtml` rendering.
5. Authenticated management routes remain separate from public routes.

### Public Frontend

1. `apps/public-site` provides a Next.js public site scaffold.
2. Implemented routes include home, `/posts`, `/posts/{slug}`, `/rss.xml`, `/sitemap.xml`, `/sitemap-static.xml`, and `/sitemap-posts.xml`.
3. Public pages use public APIs and avoid management routes.
4. Public list/detail render core fields, summary fallback, tags, machine-readable dates, not-found behavior, empty state, and controlled error state.
5. Public route metadata and canonical URLs exist.
6. Current public cache policy uses explicit Next.js route/fetch revalidation and avoids `cache: "no-store"` for public content fetches.

### RSS, Sitemap, and SEO

1. `/rss.xml` emits RSS 2.0 items from bounded full-history public-list traversal.
2. `/sitemap.xml` is a sitemap index.
3. `/sitemap-static.xml` emits stable public landing URLs for `/` and `/posts`.
4. `/sitemap-posts.xml` emits post URLs from bounded full-history public-list traversal.
5. RSS and sitemap routes use public APIs, route-level revalidation, and explicit page-size/max-page bounds.
6. Atom, richer feed contents, richer SEO schema, Open Graph image generation, search-engine sitemap splitting, and CDN cache policy remain future work.

### Publish Invalidation

1. Publish responses and `publish_jobs` record public invalidation surfaces for `/posts`, `/posts/{slug}`, `/rss.xml`, and `/sitemap.xml`.
2. Public invalidation execution is durable bookkeeping with `mode=recorded`, `status=recorded`, and `executor=none`.
3. Dispatch bookkeeping is recorded in response and durable publish-job fields.
4. Dispatcher exceptions produce `dispatch_failed` / `dispatcher_exception` bookkeeping without rolling back successful publish state.
5. Current dispatchers include `none`, `contract`, and `cloudflare`.

### Cloudflare Adapter

1. Settings accept `public_invalidation_dispatcher=cloudflare`.
2. Settings accept optional `public_invalidation_cloudflare_zone_id` and secret `public_invalidation_cloudflare_api_token` values.
3. The Cloudflare adapter distinguishes missing settings from configured dry-run bookkeeping on the feature branch.
4. The Cloudflare adapter can build an inert `CloudflarePurgeRequestPlan` with method, path, and deduplicated ordered files body.
5. Request plans exclude token, `Authorization`, and `Bearer` data and are not executed on `main`.
6. Cloudflare dry-run dispatch is active: complete settings build an inert request plan and record `cloudflare_adapter_dry_run` without external I/O.

## Deferred Functional Areas

### Data and Migrations

1. SQLAlchemy and Alembic are target stack components but are not yet introduced in code.
2. Migration work must preserve current logical entities and route contracts while replacing scaffold schema initialization.
3. PostgreSQL remains a future production option after managed migrations exist.

### Admin Console

1. CMS admin console implementation remains future work.
2. Admin must use authenticated API contracts and must not write directly to the database.

### Agent and MCP

1. MCP server implementation remains future work.
2. MCP tools must wrap documented API capabilities and must not bypass API auth, scopes, state transitions, or audit logging.

### Deployment

1. Deployment readiness, Docker/Compose runtime hardening, smoke tests, and image publishing remain future work.
2. Current CI validates guards and the public-site build but does not publish GHCR images.

### Live External Side Effects

1. Real Cloudflare API calls, CDN purge, authorization header sending, provider response/error mapping, retries, webhooks, Next.js tag/path revalidation, cache headers, scheduling semantics, and real job runner execution remain future work.
2. These concerns must be introduced through explicit named tasks and decisions.

## Next Named Work

### Article Public Sitemap Additional Shards Boundary

1. Status: in progress.
2. Scope: add `/sitemap-static.xml` as a dedicated static public sitemap shard, keep `/sitemap-posts.xml` for post detail URLs, and make `/sitemap.xml` index both shard documents.
3. Boundary: preserve route-level Next.js revalidation only; do not add RSS logic, management-route access, bearer tokens, CDN headers, purge calls, `revalidateTag`, `revalidatePath`, Cloudflare behavior, or publish-triggered invalidation execution.
4. Verification: RED sitemap structural check, focused sitemap/RSS checks, public-site typecheck/build, full frontend structural checks, guards, scans, PR CI, and main CI.
5. After completion: consider Cloudflare Live Execution Design Boundary only if live provider behavior becomes the priority; otherwise continue toward data migrations or admin console foundation.

## Blockers

### Current Blockers

No current product blocker. Live Cloudflare execution remains blocked until an explicit future design task defines secret-safe HTTP execution and response/error handling.
