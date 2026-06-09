# Nairi

## Roadmap Rule

1. Roadmap items use named functional areas and named tasks. Abstract labels such as Step, Phase, and Slice are forbidden.
2. `roadmap.md` is the current functional sequencing source of truth.
3. `progress-log.md` is historical evidence and does not define the current roadmap.
4. Update this file when a task completes, defers, splits, removes, or reorders a functional area.
5. Keep implementation history in `progress-log.md`; keep durable architecture decisions in `decisions.md`.

## Foundation and Governance

### Foundational Documentation

1. Status: completed.
2. Completed: root entry documents, `memory-bank/` documents, external `docs/`, documentation boundaries, bilingual policy, and project guard expectations.

### Guard and CI Contracts

1. Status: completed.
2. Completed: docs guard, i18n doc guard, contract guard, API schema guard, secret guard, shared guard utilities, Guards workflow, public-site structural checks, read-only workflow permissions, concurrency cancellation, and Node.js 24 opt-in.
3. Next candidates: decision-impact guard hardening after human-readable decision update rules stabilize.

### Documentation Source-of-Truth Remediation

1. Status: completed.
2. Goal: restore authority boundaries across root docs, `project-state.md`, `roadmap.md`, `progress-log.md`, `decisions.md`, `guard-ci.md`, and `tech-stack.md`.
3. Exit: source-of-truth docs agree with implemented state and guard verification passes.

## API Core and Authentication

### FastAPI Core Scaffold

1. Status: completed.
2. Completed: API package structure, app factory, health route, settings, test harness.

### Authentication and Scope System

1. Status: completed for scaffold boundary.
2. Completed: settings-backed token scopes, bearer parsing, scope dependency, protected route behavior, standard error handling.
3. Deferred: persistent hashed token storage, token lifecycle audit, admin token management UI.

## Content Draft and Publishing

### Article Draft Management

1. Status: completed for scaffold boundary.
2. Completed: draft create, persistence, duplicate slug handling, input validation, request-time timestamps, authenticated read/list, update, revision creation, expected revision conflicts, update validation, and audit events.

### Article Publishing

1. Status: completed for immediate publish scaffold.
2. Completed: publish contract, state transition, publish-job storage, published read/list, filters, and pagination through authenticated management routes.
3. Deferred: scheduled publish lifecycle, queued/running job lifecycle, retry/failure workflow, and real job runner execution.

## Taxonomy

### Category Management

1. Status: completed, not yet merged on `main`.
2. Completed: scaffold SQLite-backed `categories` table via `CategoryStore`, full CRUD routes with `taxonomy:read`/`taxonomy:write` scope enforcement, deterministic `cat-{slug}` IDs, slug validation, duplicate slug rejection, alphabetical name ordering, and 18 verified tests.
3. Deferred: tag entity, series entity, admin console category picker, hierarchical categories via `parentId`, audit events for taxonomy operations, and MCP tool wiring.

## Public Content API

### Anonymous Public Content Reads

1. Status: completed for list/detail scaffold.
2. Completed: public list, public detail, public-safe response schemas, minimal list pagination, page metadata, and minimal safe `bodyHtml` rendering.
3. Deferred: public filters, richer metadata, preview/private access modes, and full governed MDX rendering.

## Public Frontend

### Next.js Public Site

1. Status: completed for early alpha public surfaces.
2. Completed: home, post list, post detail, empty state, error state, styling boundary, metadata, canonical URLs, public API integration, and structural checks.
3. Deferred: full design system, Tailwind/shadcn expansion, richer typography, filter UI, previous-page navigation, infinite scroll, Open Graph image generation, and admin-facing previews.

### Public Cache Policy

1. Status: completed for route-level revalidation boundary.
2. Completed: explicit Next.js revalidation constants, dynamic public routes to avoid build-time API prerendering, RSS/sitemap route-level revalidation.
3. Deferred: CDN headers, deployment-specific cache policy, publish-triggered live invalidation, and tag/path invalidation.

## RSS, Sitemap, and SEO

### RSS and Sitemap

1. Status: completed for bounded full-history traversal and static/posts sitemap shards.
2. Completed: RSS 2.0 route, sitemap index, static sitemap shard, posts sitemap, bounded traversal over public list pages, route-level revalidation, and structural checks.
3. Deferred: Atom, richer feed contents, search-engine sitemap splitting beyond static/posts shards, richer SEO schema, and CDN cache policy.

## Publish Invalidation

### Invalidation Bookkeeping and Dispatcher

1. Status: completed through Cloudflare dry-run dispatch boundary.
2. Completed: public invalidation surfaces, durable recorded execution, dispatch result fields, dispatcher config, dispatcher interface, route integration, dispatch persistence, dispatcher error policy, contract adapter, Cloudflare config adapter, Cloudflare settings, inert Cloudflare request-plan construction, and configured Cloudflare dry-run dispatch bookkeeping.
3. Active next candidate: Cloudflare Live Execution Design Boundary if live provider behavior is prioritized; otherwise CMS Admin Console Foundation, Cloudflare Live Execution Design Boundary, or Migration Repair Executable Action Design Boundary.
4. Deferred: live HTTP client, authorization header sending, Cloudflare API response/error mapping, CDN purge, retry policy, external execution switch, and real job runner execution.

## Cloudflare Provider Adapter

### Cloudflare Dry-Run Dispatch

1. Status: completed for dry-run bookkeeping.
2. Result: configured Cloudflare dispatch builds or depends on the inert request plan and records `cloudflare_adapter_dry_run`, `attempted=true`, and `attemptedAt=publishedAt`.
3. Boundary: dry-run dispatch remains side-effect-free and does not expose provider plan, zone, token, Authorization, or Bearer data.

### Cloudflare Live Execution

1. Status: candidate future work.
2. Prerequisites: dry-run dispatch boundary, explicit live execution decision, secret-safe request executor design, timeout/error mapping, tests, scans, and deployment configuration review.

## Data and Migrations

### SQLAlchemy and Alembic Migration Layer

1. Status: completed for SQLite baseline metadata, minimal ordered runner, local migration rehearsal helper, stable metadata-mismatch policy errors, standalone local rehearsal CLI, documented repair workflow guidance, and operator-facing runbook handoff, and executable repair tooling design contract.
2. Completed: `schema_migrations` metadata table, one-time `post_store_baseline` recording, reopen idempotency, pre-migration SQLite adoption without data loss, ordered pending migration application, idempotent skip of applied migrations, rollback on failed pending migrations, baseline schema reconciliation when metadata already exists, SQLite backup-API copy, path-alias rejection, exclusive destination creation, no-overwrite artifact safety, backup creation, rehearsal-copy migration, count verification, `PostStore` readback verification, typed `migration_name_mismatch` fail-fast errors, `nairi-post-store-migration-rehearsal` JSON summary entrypoint, operator/developer stop guidance for migration policy conflicts, and `docs/migration-operator-handoff.md` operator-facing runbook, the `memory-bank/executable-repair-tooling.md` design-only contract, and `nairi-post-store-repair-dry-run` local dry-run analysis plus operator evidence polish and refusal matrix test expansion.
3. Deferred: executable repair actions, Alembic integration, SQLAlchemy model layer, PostgreSQL support, deployment integration, and live database migration execution.

## Admin Console

### CMS Admin Console

1. Status: runtime API client boundary completed through Admin Draft Save Error Recovery Hint Boundary; merged and read back on `main`.
2. Completed: `apps/admin` Vite React shell, injected API-client component tests, runtime `createAdminApiClient`, draft list, separate published-history list, detail/update/publish API client wiring, draft edit and persisted publish-review request UI flow, post-publish list/read-only behavior, mixed-status copy, explicit hash routing for admin modules and selected content detail, frontend admin structural guard, and Guards CI admin test/typecheck/build coverage.
3. Goal: implement human-facing content review, editing, audit, media, settings, and recovery controls through authenticated API contracts.
4. Constraint: admin must not write directly to the database or bypass API scopes/state transitions.
5. Current detailed admin status is tracked in `Admin Runtime API Client Boundary`; next admin candidate is another narrow admin edit boundary.

## Agent and MCP

### MCP Server

1. Status: deferred.
2. Goal: wrap documented API capabilities into agent-friendly tools.
3. Constraint: MCP tools must not bypass API auth, scopes, state transitions, or audit logging.

## Deployment

### Deployment Readiness

1. Status: deferred.
2. Goal: Docker/Compose runtime hardening, smoke tests, runtime config documentation, database volume handling, and deployment readiness contracts.

### Image Publishing

1. Status: deferred.
2. Goal: GHCR image publishing after Dockerfile, Compose, smoke-test, and release contracts exist.

## Admin Runtime API Client Boundary

1. Status: completed and merged through Admin Draft Save Error Recovery Hint Boundary.
2. Completed: runtime `createAdminApiClient`, fail-closed `createAdminTokenProvider`, `Admin modules` navigation with `Content`, `Media`, and `Settings` shells, explicit hash routing for admin modules and selected content detail, `Content` module draft detail readback via `getPost(postId)`, selected draft affordance, empty draft-list copy, separate `listPublishedPosts()` runtime request to `GET /api/v1/posts?status=published`, separate Published history UI list, injected draft edit form contract via `updatePost(postId, input)`, runtime `PATCH /api/v1/posts/{post_id}` client wiring, editable draft slug payloads, editable draft summary payloads, editable draft tags payloads, editable draft category ID payloads, editable draft series ID payloads, editable draft metadata JSON payloads, targeted non-object metadata JSON error copy, editable draft content-format payloads, persisted `Request publish review` through `requestPublishReview(postId, { revisionId })`, publish confirmation intent, runtime `POST /api/v1/posts/{post_id}/publish` client wiring through `publishPost(postId, input)`, an App `Publish confirmed draft` action gated behind confirmation, post-publish removal from the draft review list while preserving detail readback, read-only detail behavior for published selections in the draft review workflow, status-aware `API-backed published detail` labelling for non-draft detail readback, mixed-status admin list labelling as `Content items`, mixed-status detail loading copy as `Loading item detail…`, explicit published read-only copy explaining hidden draft controls, draft workflow copy clarifying selected-draft scope, and publish-review status scoping regression coverage.
3. Next candidate: another narrow admin edit boundary.
