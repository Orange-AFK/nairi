# Nairi

## Decision Record Rule

1. `decisions.md` records durable architecture decisions, owner decisions, and long-lived constraints that affect future development.
2. Add or update a decision when a task changes module boundaries, system responsibilities, public/authenticated behavior, security or secret handling, external side effects, cache/CDN/invalidation behavior, database/migration policy, integration authority, duplicate capability rules, or roadmap sequencing.
3. Do not use `progress-log.md` as the only home for a durable decision. Progress entries may cite decisions, but decisions live here.
4. Decision entries should include status, origin, decision, rationale, consequences, and revisit triggers when useful.
5. Historical review reports such as `project-review.md` are audit artifacts. Findings become active rules only after they are migrated into the appropriate source-of-truth document.

## Accepted Decisions

### Use API-First Architecture

1. Status: Accepted.
2. Decision: FastAPI is the single product capability authority.
3. Rationale: Nairi needs one governed capability layer shared by frontend, admin, MCP, agents, jobs, and automation.
4. Consequence: No module may bypass API auth, scopes, status transitions, or audit logging unless documented as internal infrastructure.

### Separate Public and Management APIs

1. Status: Accepted.
2. Decision: Public content APIs and authenticated content-management APIs must use separate route contracts.
3. Rationale: Public readers need anonymous, public-safe, cacheable published data, while admin, MCP, agents, and automation need authenticated management data that may include revision, workflow, and internal metadata.
4. Consequence: `/api/v1/posts...` remains authenticated management API even for `status=published`; public reads use dedicated public paths such as `/api/v1/public/posts...` and public-safe response schemas.

### Use FastAPI for Core API

1. Status: Accepted.
2. Decision: Use FastAPI instead of Hono for core API.
3. Rationale: FastAPI provides strong OpenAPI support, Python AI ecosystem access, Pydantic, SQLAlchemy, and Alembic.

### Use React Ecosystem for Frontend and Admin

1. Status: Accepted.
2. Decision: Use Next.js for public frontend and React/Vite for admin.
3. Rationale: Shared React, TypeScript, Tailwind, shadcn/ui, and API client patterns reduce maintenance cost.

### Use Governed MDX

1. Status: Accepted.
2. Decision: Support MDX through component registry, permissions, risk warning, audit, and rollback.
3. Rationale: High-risk content is not automatically unsafe, but it must be visible, controllable, and recoverable.
4. Current boundary: public rendering currently uses a minimal safe renderer; full governed MDX execution remains future work.

### Maintain Bilingual Documentation

1. Status: Accepted.
2. Decision: Maintain English and Chinese documentation with consistent contract meaning.
3. Rationale: GitHub PRs and open-source collaboration use English, while local Chinese memory-bank files serve the owner.
4. Consequence: English `memory-bank/*.md` files are tracked; local Chinese `memory-bank/*-cn.md` files are maintained locally and ignored by Git. English and Chinese `docs/*.md` pairs are tracked.

### Use Minimal SQLite Store Before ORM Migration

1. Status: Accepted.
2. Decision: Use a small `PostStore` with SQLite DDL for scaffold persistence before introducing SQLAlchemy and Alembic migrations.
3. Rationale: Early article, publish, public API, and invalidation boundaries needed verified persistence without widening into a full migration/model layer.
4. Consequence: Future migration work must replace scaffold schema initialization with managed migrations while preserving logical entities and route contracts.
5. Revisit when: the explicit SQLAlchemy/Alembic migration task starts.

### Use Public-Safe Schemas for Anonymous Content

1. Status: Accepted.
2. Origin: Emerged during public list and public detail API implementation.
3. Decision: Anonymous public routes expose only public-safe published fields through dedicated `/api/v1/public/posts...` contracts.
4. Rationale: Public readers and CDN-cacheable routes need stable published data without revision, workflow, audit, agent trace, metadata, or internal job state leakage.
5. Consequence: Public frontend, anonymous readers, RSS, sitemap, and future CDN-cacheable routes must use public contracts. Admin, MCP, agents, and automation must use authenticated management contracts.
6. Revisit when: public filters, richer public metadata, or private/preview content modes are introduced.

### Use Minimal Safe Rendering Before Governed MDX Execution

1. Status: Accepted.
2. Origin: Emerged during public detail `bodyHtml` rendering.
3. Decision: Current public `bodyHtml` rendering uses a deliberately small safe Markdown subset and keeps full MDX/component execution deferred.
4. Rationale: Published public detail needed useful rendering before the full governed MDX registry, sanitizer expansion, component permission model, and rollback workflow are implemented.
5. Consequence: Public rendering must remain conservative and public-safe. Rich MDX rendering must be introduced through a separate governed MDX boundary.
6. Revisit when: MDX component registry enforcement, sanitizer policy expansion, or admin-controlled component publication is implemented.

### Use Next.js Route Revalidation as the Current Public Cache Policy

1. Status: Accepted.
2. Origin: Emerged during public frontend cache policy, RSS cache policy, and sitemap cache policy boundaries.
3. Decision: Current public frontend cache behavior uses explicit Next.js route/fetch revalidation and avoids `cache: "no-store"` for public content fetches unless a later cache-policy task changes the contract.
4. Rationale: The public frontend needs deterministic builds and predictable freshness without introducing CDN header policy or publish-triggered external invalidation too early.
5. Consequence: CDN headers, Cloudflare purge, publish-triggered revalidation, and Next.js tag/path invalidation are separate design concerns.
6. Revisit when: deployment topology, CDN policy, live invalidation execution, or public freshness requirements change.

### Use Bounded RSS and Sitemap Traversal with a Split Sitemap

1. Status: Accepted.
2. Origin: Emerged during RSS/sitemap pagination, full-history traversal, cache policy, and sitemap split boundaries.
3. Decision: RSS and sitemap generation read anonymous public list pages with explicit bounds. `/sitemap.xml` is a sitemap index, and `/sitemap-posts.xml` owns post URL entries.
4. Rationale: Feeds and sitemaps should include published history beyond the first page without unbounded crawling or management-route access.
5. Consequence: RSS and sitemap routes must use public APIs, bounded traversal constants, route-level revalidation, and no publish-triggered purge side effects in the current boundary.
6. Revisit when: additional sitemap shards, Atom, richer feed contents, search-engine sitemap splitting, or CDN cache policy is introduced.

### Use Staged Public Invalidation Boundaries

1. Status: Accepted.
2. Origin: Emerged during publish invalidation contract, execution, dispatch, persistence, error policy, adapter contract, and Cloudflare adapter boundaries.
3. Decision: Public invalidation advances through explicit boundaries before any external side effect: contract surfaces, durable recorded execution, dispatch bookkeeping, dispatcher configuration, dispatcher route integration, dispatch persistence, error policy, concrete adapter configuration, provider settings, inert provider request plan, dry-run dispatch, and only later live execution if explicitly planned.
4. Rationale: Publish side effects are high risk. Separating state recording, dispatcher semantics, provider configuration, request construction, and external I/O keeps each step testable and reversible.
5. Consequence: Future invalidation tasks must state exactly which boundary they cross. They must not smuggle HTTP clients, Cloudflare API execution, CDN purge, `revalidateTag`, `revalidatePath`, webhooks, cache headers, scheduling semantics, or job runner execution into unrelated slices.
6. Revisit when: live invalidation execution is planned or deployment cache topology changes.

### Persist Dispatcher Bookkeeping Without Rolling Back Successful Publishes

1. Status: Accepted.
2. Origin: Emerged during dispatcher route integration, persistence, and error policy boundaries.
3. Decision: Successful publish state changes remain successful even if the configured invalidation dispatcher fails. Dispatcher outcome is recorded in response and durable `publish_jobs` dispatch fields.
4. Rationale: Publishing content and invalidating public surfaces are related but distinct operations. A dispatcher failure should be observable and durable without silently undoing a successful state transition.
5. Consequence: Dispatcher exceptions map to `dispatch_failed` with `dispatcher_exception`; dispatch persistence fails closed when expected publish-job rows are missing.
6. Revisit when: retry policy, queued dispatcher execution, or live provider calls are implemented.

### Keep Cloudflare Adapter Secret-Safe and Staged

1. Status: Accepted.
2. Origin: Emerged during Cloudflare adapter config, settings, and request-plan boundaries.
3. Decision: The Cloudflare adapter is introduced in stages. Settings may include zone id and secret token, but dispatcher construction receives only the zone id and token-configured state needed for inert request planning. Request plans must not include token, `Authorization`, or `Bearer` data. Configured dispatch may perform only an in-process dry-run request-plan build and record `cloudflare_adapter_dry_run`; it must not execute or expose the plan.
4. Rationale: Cloudflare purge is an external side effect involving secrets. Secret handling, request construction, dry-run semantics, and live execution must remain separate.
5. Consequence: Real HTTP client wiring, authorization header construction/sending, Cloudflare API response/error mapping, and CDN purge require explicit future tasks and tests.
6. Revisit when: the dry-run dispatch boundary or live Cloudflare execution boundary changes provider behavior.

### Keep Cloudflare Purge, Next.js Revalidation, Cache Headers, and Job Runner Separate

1. Status: Accepted.
2. Origin: Emerged during public cache, RSS/sitemap cache, and public invalidation development.
3. Decision: Cloudflare CDN purge, Next.js `revalidateTag`/`revalidatePath`, HTTP cache headers, scheduling semantics, and job runner execution are separate system concerns.
4. Rationale: Combining these concerns hides side effects and makes public freshness behavior hard to test or reason about.
5. Consequence: A Cloudflare adapter task does not imply Next.js tag/path revalidation. A cache-header task does not imply provider purge execution. A job-runner task does not imply provider-specific request construction.
6. Revisit when: deployment runtime design or cache topology requires cross-layer coordination.

### Treat Guards as Executable Project Contracts

1. Status: Accepted.
2. Origin: Emerged during documentation guard, contract guard, secret guard, CI hygiene, and public-site structural checks.
3. Decision: Guard scripts and CI checks are mandatory executable contracts for documentation boundaries, bilingual synchronization, contract consistency, API schema shape, secret safety, and selected public-site structural behavior.
4. Rationale: The project uses docs as source-of-truth inputs; executable guards prevent silent drift.
5. Consequence: A task is not complete when relevant guards fail. Human-readable rules in `guard-ci.md` should describe what guard scripts enforce and where guards intentionally do not enforce policy.
6. Revisit when: new source-of-truth rules become stable enough for executable enforcement.

### Use Explicit Migration Repair Policy Errors

1. Status: Accepted.
2. Origin: Emerged during the Migration Repair Policy Boundary.
3. Decision: `schema_migrations` metadata mismatches fail fast with stable, typed migration-policy errors instead of ad hoc generic exceptions.
4. Rationale: Migration metadata is the authority for applied schema history. A recorded id/name mismatch may indicate renamed or corrupted migration history and must not be auto-repaired silently.
5. Consequence: Idempotent baseline DDL reconciliation may still repair missing scaffold tables when metadata is valid, but metadata mismatches require explicit operator/developer intervention.
6. Revisit when: standalone migration CLI, Alembic integration, or live database repair workflow is introduced.
