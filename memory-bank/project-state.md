# Nairi

## Current State

### Project Status

1. Nairi is in early alpha implementation.
2. The implementation still follows the accepted API-first, agent-first CMS direction.
3. Core public and management content flows exist as scaffold implementations with verified route tests and guards.
4. The current development focus is post-merge source-of-truth closeout after Admin Draft Content Format Edit Boundary merged and passed main readback.
5. CMS admin console work has advanced beyond the foundation shell into the runtime API client boundary through draft list/detail, draft update, content-format edit payloads, targeted metadata JSON error copy, publish-review staging, publish confirmation, injected `publishPost` wiring, post-publish list/read-only behavior, separate published-history list readback, mixed-status copy, publish-review status scoping coverage, and explicit hash routing; it follows the Migration Operator Handoff Docs Boundary for typed migration policy failures, remains bounded to authenticated API contracts, and preserves manual intervention for migration repair workflows.

### Current Authority Snapshot

1. `project-state.md` is the current status source of truth.
2. `roadmap.md` is the functional roadmap source of truth.
3. `decisions.md` is the durable architecture decision source of truth.
4. `progress-log.md` is append-only historical evidence.
5. `project-audit.md` defines the active project-health audit cadence and remediation rules.
6. `project-review.md` and dated audit reports are historical review artifacts and are not maintained during normal feature work.

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

1. SQLite-backed scaffold persistence uses `PostStore` for posts, revisions, audit events, publish jobs, and publish review requests.
2. Authenticated draft create, read, list, update, duplicate slug handling, update conflict handling, validation, request-time timestamps, and immutable revisions exist.
3. Authenticated publish-review requests persist pending human review intent with `post.publish_requested` audit rows while leaving draft status unchanged.
4. Authenticated publish requests perform the first immediate publish transition, preserve current revision, record `post.published`, and create durable publish-job bookkeeping.
5. Authenticated published read/list/filter/pagination exists through management routes with `posts:read` scope.

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
3. The Cloudflare adapter distinguishes missing settings from configured dry-run bookkeeping on `main`.
4. The Cloudflare adapter can build an inert `CloudflarePurgeRequestPlan` with method, path, and deduplicated ordered files body.
5. Request plans exclude token, `Authorization`, and `Bearer` data and are not executed on `main`.
6. Cloudflare dry-run dispatch is active: complete settings build an inert request plan and record `cloudflare_adapter_dry_run` without external I/O.

## Deferred Functional Areas

### Data and Migrations

1. SQLite `PostStore` now uses an ordered `PostStoreMigration` runner to record and apply the current scaffold baseline / `post_store_baseline`.
2. `schema_migrations` records the current `(1, "post_store_baseline")` row and the runner skips already-applied migrations.
3. Existing pre-migration SQLite files can be adopted by creating migration metadata without losing posts, revisions, or audit rows.
4. A local rehearsal helper can copy a source SQLite file to backup and rehearsal paths, trigger migration on the rehearsal copy, and verify metadata/count/readback safety.
5. Migration metadata name mismatches fail fast with a stable `PostStoreMigrationError` carrying `migration_name_mismatch` policy metadata; they are not auto-repaired.
6. `nairi-post-store-migration-rehearsal` is a local-only console script that rehearses migration against caller-provided source/backup/rehearsal paths and emits a JSON summary.
7. SQLAlchemy and Alembic are target stack components but are not yet introduced in code.
8. PostgreSQL remains a future production option after managed migrations exist.

### Admin Console

1. CMS admin console foundation exists under `apps/admin` as a minimal Vite React shell with runtime API client wiring for draft list, separate published-history list, detail, update, publish-review request, and publish actions.
2. Admin must use authenticated API contracts and must not write directly to the database.
3. Current shell uses an injected API client in tests, has a persisted publish-review request through `requestPublishReview`, has a confirmed publish action through the injected `publishPost` contract, and has explicit client-side hash routing for admin modules and selected content detail; it still has no token storage, routing library, scheduler, direct database writes, production mutation outside documented APIs, or live database migration execution.

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

### Publish Request Resolve Workflow Boundary

1. Status: completed, merged, and read back on `main`.
2. Starting point: `POST /api/v1/posts/{post_id}/publish-requests`, `publish_requests` persistence, `post.publish_requested` audit event, and admin injected/runtime `requestPublishReview` wiring exist and are verified.
3. Completed scope: `POST /api/v1/publish-requests/{request_id}/resolve` resolves pending publish requests to `approved` or `rejected`, stores request-time `resolvedAt`, records `admin.publish_request.resolve`, and preserves the no-publish side-effect boundary.
4. Boundary: approval or rejection updates only the publish request review state; it does not mutate post status, call live publish, create `publish_jobs`, trigger invalidation dispatch, add deployment behavior, or bypass API scopes/audit.

### Admin Published History List Boundary

1. Status: completed, merged, and read back on `main`.
2. Completed scope: admin runtime client now exposes a separate injected `listPublishedPosts()` request backed by authenticated `GET /api/v1/posts?status=published`, and the Content workspace renders a dedicated read-only Published history list beside the draft review list.
3. Boundary: no backend route change, no public API change, no publish workflow state-machine change, no filters/pagination UI, no router expansion, no token storage, no direct database access, and no live external side effects.

### Admin Draft Content Format Edit Boundary

1. Status: completed, merged, and read back on `main`.
2. Completed scope: admin draft edit form now exposes a `Draft content format` select and submits the selected `contentFormat` through the existing injected `updatePost` payload.
3. Boundary: admin edit payload only; no backend route change, no public API change, no renderer behavior, no MDX execution, no router expansion, no token storage, no direct database access, and no live external side effects.
4. Candidate next work: another narrow admin edit boundary, Executable Repair Tooling Design Boundary, or Cloudflare Live Execution Design Boundary after a high-risk audit.

## Blockers

### Current Blockers

No current product blocker. Live Cloudflare execution remains blocked until an explicit future design task defines secret-safe HTTP execution and response/error handling.
