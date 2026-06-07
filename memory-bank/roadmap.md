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

1. Status: active.
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

1. Status: completed for bounded full-history traversal and split sitemap.
2. Completed: RSS 2.0 route, sitemap index, posts sitemap, bounded traversal over public list pages, route-level revalidation, and structural checks.
3. Deferred: Atom, richer feed contents, additional sitemap shards, search-engine sitemap splitting, richer SEO schema, and CDN cache policy.

## Publish Invalidation

### Invalidation Bookkeeping and Dispatcher

1. Status: completed through adapter request-plan boundary.
2. Completed: public invalidation surfaces, durable recorded execution, dispatch result fields, dispatcher config, dispatcher interface, route integration, dispatch persistence, dispatcher error policy, contract adapter, Cloudflare config adapter, Cloudflare settings, and inert Cloudflare request-plan construction.
3. Active next after documentation remediation: Article Public Publish Invalidation Cloudflare Adapter Dry-Run Dispatch Boundary.
4. Deferred: live HTTP client, authorization header sending, Cloudflare API response/error mapping, CDN purge, retry policy, external execution switch, and real job runner execution.

## Cloudflare Provider Adapter

### Cloudflare Dry-Run Dispatch

1. Status: paused.
2. Reason: Documentation source-of-truth remediation is intentionally blocking live/provider progression until staged invalidation decisions are documented.
3. Next action: resume saved WIP after remediation merges.

### Cloudflare Live Execution

1. Status: candidate future work.
2. Prerequisites: dry-run dispatch boundary, explicit live execution decision, secret-safe request executor design, timeout/error mapping, tests, scans, and deployment configuration review.

## Data and Migrations

### SQLAlchemy and Alembic Migration Layer

1. Status: deferred.
2. Goal: replace scaffold SQLite schema initialization with managed migrations while preserving current route contracts and logical entities.
3. PostgreSQL remains a future production option after migration support exists.

## Admin Console

### CMS Admin Console

1. Status: deferred.
2. Goal: implement human-facing content review, editing, audit, media, settings, and recovery controls through authenticated API contracts.
3. Constraint: admin must not write directly to the database or bypass API scopes/state transitions.

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
