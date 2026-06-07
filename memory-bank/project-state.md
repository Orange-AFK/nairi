# Nairi

## Current State

### Project Status

1. Nairi has completed foundational documentation, guard scripts, the first API scaffold, the first protected scope-check route, scaffold-level article draft creation, the first SQLite-backed draft persistence boundary, duplicate draft slug conflict handling, the first draft input validation boundary, request-time draft timestamps, the first authenticated draft readback boundary, the first authenticated draft list boundary, the first authenticated draft update boundary, update-time duplicate slug conflict handling, update-time input validation coverage, the first authenticated publish route contract boundary, the first publish state transition boundary, the first publish job storage boundary, and the first published readback boundary, the first published filtering boundary, and the first published pagination boundary.
2. The FastAPI service skeleton and auth dependency exist under `services/api/`.
3. The accepted product direction is API-first and agent-first CMS.
4. FastAPI is the product capability authority.
5. Documentation, contracts, guard rules, health endpoint tests, protected scope tests, article draft creation route tests, draft persistence tests, duplicate slug tests, draft input validation tests, draft timestamp tests, draft readback tests, draft list tests, draft update tests, update duplicate slug tests, update input validation tests, publish contract tests, publish state transition tests, publish job storage tests, published read/list tests, published filtering tests, and published pagination tests currently pass locally.

## Confirmed Decisions

### Product Direction

1. Nairi helps convert valuable AI-agent-assisted project work into publishable articles.
2. Human administrators and AI agents are both first-class users.
3. The CMS admin console remains necessary because humans need review, editing, audit, media, settings, and recovery control.

### Technical Direction

1. Public site uses Next.js, React, Tailwind CSS, shadcn/ui, and Markdown/MDX.
2. Admin console uses React, Vite, TanStack Router, TanStack Query, React Hook Form, Zod, Tailwind CSS, and shadcn/ui.
3. Core API uses FastAPI, Pydantic, SQLAlchemy, and Alembic.
4. SQLite is default; PostgreSQL is optional for production.
5. MCP wraps documented API capabilities for agents.

## Next Named Work

### Article Draft API Development

1. SQLite-backed draft persistence now creates `Post`, `PostRevision`, and `post.created` audit rows for `POST /api/v1/posts`.
2. Duplicate draft slug requests now return a standard `409 conflict` response without creating additional persistence side effects.
3. Invalid draft input now returns a standard `400 invalid_request` response before persistence side effects.
4. Draft creation now uses request-time UTC timestamps, with injectable clock support for deterministic tests.
5. Authenticated draft readback now returns a created draft through `GET /api/v1/posts/{post_id}` with `posts:read` scope.
6. Authenticated draft list now returns summary-shaped draft items through `GET /api/v1/posts?status=draft` with `posts:read` scope.
7. Authenticated draft update now creates a new immutable revision through `PATCH /api/v1/posts/{post_id}` with `posts:write` scope and `expectedRevisionId` conflict protection.
8. Update-time duplicate slug requests now return a standard `409 conflict` response before creating a new revision, audit event, or post mutation.
9. Invalid update payloads now have explicit test coverage proving `400 invalid_request` before revision, audit, or post mutation side effects.
10. Authenticated publish requests now return a queued job-shaped response through `POST /api/v1/posts/{post_id}/publish` with `posts:publish` scope, standard `404`, and stale `revisionId` `409 conflict` without post/revision/audit mutation.
11. Publish requests now persist the first state transition from `draft` to `published`, set `publishedAt`/`updatedAt`, preserve the current revision, and record `post.published` audit metadata.
12. Publish requests now create a durable `publish_jobs` row for the immediate publish attempt while keeping runner and scheduling semantics deferred.
13. Authenticated management read/list now exposes published posts through `GET /api/v1/posts/{post_id}` and `GET /api/v1/posts?status=published`; public read remains a separate dedicated endpoint task.
14. Published lists now support the first minimal `tag`, `category`, and `series` filters.
15. Published lists now support the first minimal `limit`/`cursor` pagination boundary.
16. `GET /api/v1/public/posts` now provides the first anonymous public published summary list with public-safe fields while keeping authenticated `/api/v1/posts...` management routes separate.
17. `GET /api/v1/public/posts/{slug}` now provides the first anonymous public published detail readback with public-safe fields while keeping authenticated `/api/v1/posts...` management detail separate.
18. `GET /api/v1/public/posts/{slug}` now includes `bodyHtml`, a minimal sanitized render output for public detail content. It preserves the original authored `content` and keeps management detail unchanged.
19. `apps/public-site` now provides the first Next.js public frontend scaffold with `/posts/{slug}` reading `GET /api/v1/public/posts/{slug}` and rendering `bodyHtml` while preserving the public/management API boundary.
20. `/posts` now provides the first public article list page, reads `GET /api/v1/public/posts`, displays title/summary/publishedAt/tags, and links each item to `/posts/{slug}` without using management routes.
21. Current CI validates the public-site build but intentionally does not publish Docker or GHCR images until deployment readiness contracts exist.
22. The Dependabot PostCSS advisory for `apps/public-site/package-lock.json` is fixed by resolving `postcss` to patched version `8.5.10`.
23. CI Hygiene / Node 24 Actions Boundary is complete: Guards use read-only permissions, concurrency cancellation, and Node.js 24 opt-in for JavaScript actions.
24. `/posts` now has a stable empty-list state and controlled fetch-failure error boundary without calling management routes.
25. Article Public Site Styling Boundary is complete: `/`, `/posts`, `/posts/{slug}`, list empty state, and list error state share a narrow header/card surface rhythm without introducing a full design system.
26. Article Public Site SEO Metadata Boundary is complete: `/` and `/posts` define stable route metadata while `/posts/{slug}` keeps generating metadata from public detail data.
27. Article Published Public Render Coverage Boundary is complete: public list/detail rendering now guard machine-readable publish dates, summary fallback, tags, public detail `bodyHtml`, and not-found behavior without calling management routes.
28. Article Public API / Frontend Cache Policy Boundary is complete: public list/detail fetches use explicit Next.js revalidation constants and the dynamic routes avoid build-time API prerendering.
29. Article Public Sitemap Boundary is complete: `/sitemap.xml` exposes `/`, `/posts`, and published post detail URLs from public list data without RSS or management-route access.
30. Article Public RSS Boundary is complete: `/rss.xml` exposes RSS 2.0 items from public list data without full body content, Atom, or management-route access.
31. Article Public Canonical URL Boundary is complete: `/`, `/posts`, and `/posts/{slug}` define canonical metadata using the public site URL setting without management-route access.
32. Article Public Pagination Boundary is complete: anonymous `GET /api/v1/public/posts` supports minimal `limit` and item-id `cursor` pagination while preserving public-safe fields.
33. Article Public Frontend Pagination Boundary is complete: `/posts` requests a limited public list page, accepts `cursor` from query params, and renders a `Load more articles` link when `nextCursor` exists.
34. Article Public Pagination Metadata Boundary is complete: anonymous `GET /api/v1/public/posts` now returns minimal `page` metadata (`limit`, `cursor`, `hasNextPage`) alongside `items` and `nextCursor`.
35. Article Public Pagination Metadata Frontend Boundary is complete: `/posts` now uses `page.hasNextPage` plus `nextCursor` to decide whether to render the next-page link.
36. Article Public RSS/Sitemap Pagination Policy Boundary is complete: `/rss.xml` and `/sitemap.xml` explicitly consume one single public list page only, with cursor/full-history expansion deferred.
37. Article Public CDN/Invalidation Boundary is complete: public frontend caching remains Next.js revalidation only, with no CDN headers, publish-triggered invalidation, tag-based revalidation, or CDN purge wiring yet.
38. Article Public Publish Invalidation Contract Boundary is complete: publish responses and `publish_jobs` now record contract-only public invalidation surfaces for `/posts`, `/posts/{slug}`, `/rss.xml`, and `/sitemap.xml` without executing real CDN or Next.js invalidation.
39. Article Public RSS/Sitemap Full-History Pagination Boundary is complete: `/rss.xml` and `/sitemap.xml` now traverse anonymous public list pages with explicit page-size and max-page bounds so feeds include published history beyond the first list page.
40. Article Public RSS/Sitemap Cache Policy Boundary is complete: `/rss.xml` and `/sitemap.xml` now declare route-level Next.js revalidation with explicit RSS/sitemap cache policy markers and no CDN headers, purge, or publish-triggered invalidation execution.
41. Article Public Publish Invalidation Execution Boundary is complete: publish responses and `publish_jobs` now record public invalidation execution status as durable bookkeeping with `mode=recorded`, `status=recorded`, and `executor=none`, without CDN purge, webhooks, cache headers, or Next.js tag/path invalidation.
42. Article Public Publish Invalidation Dispatch Boundary is complete: publish responses and `publish_jobs` now record dispatch semantics with `dispatch_skipped`, `no_dispatcher_configured`, `attempted=false`, and no external invalidation side effects.
43. Article Public Publish Invalidation Dispatcher Configuration Boundary is complete: API settings now expose `public_invalidation_dispatcher` with the only supported value `none`, including `NAIRI_PUBLIC_INVALIDATION_DISPATCHER=none` env wiring and validation that rejects unsupported dispatcher values.
44. Article Public Publish Invalidation Dispatcher Interface Boundary is complete: app creation now builds a configured `PublicInvalidationDispatcher`, with a `none` no-op implementation that returns skipped dispatch bookkeeping without external side effects.
45. Article Public Publish Invalidation Dispatcher Route Integration Boundary is complete: the publish route now invokes the configured in-process dispatcher after successful publish storage and maps the dispatcher result into the response dispatch object.
46. Article Public Publish Invalidation Dispatcher Persistence Boundary is complete: the publish route now records the dispatcher result back onto the durable `publish_jobs` dispatch fields after the dispatcher returns, keeping response dispatch and durable dispatch bookkeeping aligned without running external invalidation.
47. The next product-development task is Article Public RSS/Sitemap Split Boundary or Article Public Publish Invalidation Dispatcher Error Policy Boundary.
17. Keep SQLAlchemy and Alembic deferred until the explicit migration/model task.
18. Preserve scope checks and standard error behavior.

## Blockers

### Current Blockers

No active blocker. Continue one named task at a time and keep guard verification mandatory.
