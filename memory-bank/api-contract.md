# Nairi

## API Contract Principles

### API Authority

1. FastAPI owns all product capability behavior.
2. API contracts are documented before implementation.
3. Every route must define method, path, scope, request, response, errors, audit behavior, and client mapping.

## Authentication

### Token Model

1. Admin users authenticate through session or token-backed flows.
2. Agents and automation use API tokens.
3. API tokens carry explicit scopes.
4. `admin:all` may imply all scopes only for trusted administrative use.

### Public and Authenticated API Boundary

1. Authenticated content-management APIs use `/api/v1/posts...` and require explicit content scopes such as `posts:read`, `posts:write`, or `posts:publish`.
2. Public content APIs must use a dedicated public contract such as `/api/v1/public/posts...` and must not share route handlers whose authorization depends on `status` query parameters.
3. Public responses must expose only public-safe published fields; they must not expose draft data, `revisionId`, internal `metadata`, audit state, job state, agent traces, or raw privileged workflow fields.
4. Public frontend, anonymous readers, and CDN-cacheable routes must use public contracts. Admin console, MCP, agents, and automation must use authenticated contracts.
5. A route may not be both anonymous-public and authenticated-management for the same path. If behavior differs by caller type, define separate route contracts.

## System API

### Read API Health

1. Method: `GET`
2. Path: `/api/v1/health`
3. Scope: `public:read`
4. Response fields: `status`, `service`, `version`
5. Clients: deployment smoke tests, uptime checks, and local development verification.

## Content API

### List Posts

1. Method: `GET`
2. Path: `/api/v1/posts`
3. Scope: `posts:read`
4. Query parameters: `status`, `tag`, `category`, `series`, `limit`, `cursor`
5. Current scaffold boundary: authenticated list for `status=draft` and `status=published`; published lists support minimal `tag`, `category`, and `series` filters plus `limit`/`cursor` pagination.
6. Response fields: `items`, `nextCursor`
7. Item fields for draft list: `postId`, `title`, `slug`, `status`, `contentFormat`, `summary`, `tags`, `categoryId`, `seriesId`, `metadata`, `revisionId`, `createdAt`, `updatedAt`.
8. Item fields for published list: `postId`, `title`, `slug`, `status`, `contentFormat`, `summary`, `tags`, `categoryId`, `seriesId`, `metadata`, `revisionId`, `publishedAt`, `createdAt`, `updatedAt`.
9. List items intentionally omit `content`; clients should use `GET /api/v1/posts/{post_id}` for detail.
10. Audit event: none for list readback.
11. Clients: admin console for authenticated lists, MCP for agent-safe listing, and authorized automation.

## Public Content API

### List Public Posts

1. Method: `GET`
2. Path: `/api/v1/public/posts`
3. Scope: `public:read`
4. Query parameters: `limit`, `cursor`
5. Current scaffold boundary: anonymous published summary list with minimal item-id cursor pagination and page metadata; no filters, Markdown/MDX rendering, or cache headers yet.
6. Response fields: `items`, `nextCursor`, `page`
7. `page` fields: `limit`, `cursor`, `hasNextPage`.
8. Item fields: `postId`, `title`, `slug`, `status`, `contentFormat`, `summary`, `tags`, `categoryId`, `seriesId`, `publishedAt`.
9. Public list items intentionally omit `content`, `revisionId`, `metadata`, `createdAt`, `updatedAt`, audit state, job state, and agent traces.
10. Audit event: none for public list readback.
11. Clients: public frontend, anonymous readers, and future CDN-cacheable public routes.

### Read Public Post

1. Method: `GET`
2. Path: `/api/v1/public/posts/{slug}`
3. Scope: `public:read`
4. Request body fields:
5. Response fields: `postId`, `title`, `slug`, `status`, `contentFormat`, `content`, `bodyHtml`, `summary`, `tags`, `categoryId`, `seriesId`, `publishedAt`
6. Current scaffold boundary: anonymous published detail by slug with a minimal safe Markdown-to-HTML rendering field. The renderer supports a deliberately small subset (`#` headings, paragraphs, and `**strong**`), escapes user text, and strips script blocks from `bodyHtml`; full MDX execution, component rendering, cache headers, and public revision history are deferred.
7. Public detail response intentionally omits `revisionId`, `metadata`, `createdAt`, `updatedAt`, audit state, job state, and agent traces. `content` remains the original authored source, while `bodyHtml` is the sanitized render output.
8. Errors: `404` with code `not_found` when `slug` is unknown or identifies a non-published post.
9. Audit event: none for public detail readback.
10. Clients: public frontend, anonymous readers, and future CDN-cacheable public routes.

## Management Content API

### Create Post Draft

1. Method: `POST`
2. Path: `/api/v1/posts`
3. Scope: `posts:write`
4. Request body fields: `title`, `slug`, `contentFormat`, `content`, `summary`, `tags`, `categoryId`, `seriesId`, `metadata`
5. Response fields: `postId`, `status`, `revisionId`, `createdAt`
6. Timestamp rule: `createdAt` is a request-time UTC timestamp serialized as `YYYY-MM-DDTHH:MM:SSZ`.
7. Audit event: `post.created`
8. Errors: `400` with code `invalid_request` when `title` is blank, `slug` is not lowercase letters/numbers/hyphens, or `content` is blank. The validation response must not create a post, revision, or audit event.
9. Errors: `409` with code `conflict` when the requested `slug` already exists. The conflict response must not create an additional post revision or audit event.

### Read Post

1. Method: `GET`
2. Path: `/api/v1/posts/{post_id}`
3. Scope: `posts:read`
4. Request body fields: none
5. Response fields for draft posts: `postId`, `title`, `slug`, `status`, `contentFormat`, `content`, `summary`, `tags`, `categoryId`, `seriesId`, `metadata`, `revisionId`, `createdAt`, `updatedAt`
6. Response fields for published posts: `postId`, `title`, `slug`, `status`, `contentFormat`, `content`, `summary`, `tags`, `categoryId`, `seriesId`, `metadata`, `revisionId`, `publishedAt`, `createdAt`, `updatedAt`
7. Errors: `404` with code `not_found` when `post_id` is unknown or does not identify a draft or published post.
8. Audit event: none for readback.

### Update Post Draft

1. Method: `PATCH`
2. Path: `/api/v1/posts/{post_id}`
3. Scope: `posts:write`
4. Request body fields: `title`, `slug`, `contentFormat`, `content`, `summary`, `tags`, `categoryId`, `seriesId`, `metadata`, `expectedRevisionId`
5. Response fields: `postId`, `status`, `revisionId`, `updatedAt`
6. Timestamp rule: `updatedAt` is a request-time UTC timestamp serialized as `YYYY-MM-DDTHH:MM:SSZ`.
7. Audit event: `post.updated`
8. Errors: `400` with code `invalid_request` when `title` is blank, `slug` is not lowercase letters/numbers/hyphens, or `content` is blank. The validation response must not create a post revision or audit event, and must not mutate the post.
9. Errors: `404` with code `not_found` when `post_id` is unknown or does not identify a draft.
10. Errors: `409` with code `conflict` when `expectedRevisionId` does not match the current draft revision. The conflict response must not create a post revision or audit event.
11. Errors: `409` with code `conflict` when the requested `slug` belongs to another post. The conflict response must not create a post revision or audit event, and must not mutate either post.

### Publish Post

1. Method: `POST`
2. Path: `/api/v1/posts/{post_id}/publish`
3. Scope: `posts:publish`
4. Request body fields: `revisionId`, `publishMode`, `scheduledAt`
5. Response fields: `postId`, `status`, `publishedAt`, `jobId`, `publicInvalidation`
6. Current job storage boundary: validates the authenticated publish request, creates a durable `publish_jobs` row, changes the post status from `draft` to `published`, stores request-time `publishedAt`/`updatedAt`, and returns a published job-shaped response with a recorded public invalidation execution record and dispatch bookkeeping.
7. Errors: `404` with code `not_found` when `post_id` is unknown or does not identify a draft.
8. Errors: `409` with code `conflict` when `revisionId` does not match the current draft revision. The conflict response must not create a revision or audit event, and must not mutate the post.
9. Audit event: `post.published` with `revisionId` and `jobId` metadata.
10. Publish job storage: immediate publish currently stores a `publish_jobs` row with deterministic `id`, `postId`, `revisionId`, `status=succeeded`, `scheduledAt=null`, `startedAt=publishedAt`, `completedAt=publishedAt`, `errorCode=null`, `errorMessage=null`, `publicInvalidationSurfaces` for `/posts`, `/posts/{slug}`, `/rss.xml`, and `/sitemap.xml`, plus public invalidation execution and dispatch fields.
11. Public invalidation mode: `recorded`; the API records and returns intended public surfaces plus `execution.status=recorded`, `execution.executor=none`, `execution.executedAt=publishedAt`, `execution.errorCode=null`, and `execution.errorMessage=null`.
12. Public invalidation dispatch boundary: the API records `dispatch.status=dispatch_skipped`, `dispatch.reason=no_dispatcher_configured`, `dispatch.attempted=false`, and `dispatch.attemptedAt=null` as future-safe dispatch semantics when no dispatcher is configured.
13. Public invalidation execution boundary: recorded execution and dispatch bookkeeping are durable bookkeeping only; they do not trigger CDN purge, `revalidateTag`, `revalidatePath`, webhooks, cache headers, or any external invalidation side effect.
14. Duplicate capability warning: admin, MCP, and agents must use this capability instead of creating parallel publish endpoints.

## MDX Component API

### List MDX Components

1. Method: `GET`
2. Path: `/api/v1/mdx-components`
3. Scope: `settings:read`
4. Response fields: `items`
5. Errors: `401` when the bearer token is missing or invalid; `403` when the token lacks `settings:read` or `admin:all`.
6. Clients: CMS admin console and Agent/MCP risk-policy readers.

### Update MDX Component Policy

1. Method: `PATCH`
2. Path: `/api/v1/mdx-components/{component_name}`
3. Scope: `settings:write`
4. Request body fields: `enabled`, `riskLevel`, `allowedRoles`, `allowedAgentScopes`, `requiresReview`, `propsSchema`
5. Response fields: `componentName`, `enabled`, `riskLevel`, `updatedAt`
6. Audit event: `mdx.risk_detected` when risk policy changes affect pending content.

## Agent Task API

### Create Agent Draft Task

1. Method: `POST`
2. Path: `/api/v1/agent-tasks/article-draft`
3. Scope: `agent:invoke`
4. Request body fields: `sourceType`, `sourceRefs`, `prompt`, `targetPostId`, `riskPolicy`
5. Response fields: `agentTaskId`, `status`, `createdAt`
6. Audit event: `agent.task_created`

## Error Model

### Standard Error Fields

1. `code`
2. `message`
3. `details`
4. `requestId`

## Versioning

### API Versioning Rule

Breaking changes require a new version prefix or a documented migration plan. Non-breaking extensions may add optional fields.
