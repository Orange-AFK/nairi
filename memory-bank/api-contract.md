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
5. Current scaffold boundary: authenticated list for `status=draft` and `status=published`.
6. Response fields: `items`, `nextCursor`
7. Item fields for draft list: `postId`, `title`, `slug`, `status`, `contentFormat`, `summary`, `tags`, `categoryId`, `seriesId`, `metadata`, `revisionId`, `createdAt`, `updatedAt`.
8. Item fields for published list: `postId`, `title`, `slug`, `status`, `contentFormat`, `summary`, `tags`, `categoryId`, `seriesId`, `metadata`, `revisionId`, `publishedAt`, `createdAt`, `updatedAt`.
9. List items intentionally omit `content`; clients should use `GET /api/v1/posts/{post_id}` for detail.
10. Audit event: none for list readback.
11. Clients: public frontend for public posts, admin console for authenticated lists, MCP for agent-safe listing.

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
5. Response fields: `postId`, `status`, `publishedAt`, `jobId`
6. Current job storage boundary: validates the authenticated publish request, creates a durable `publish_jobs` row, changes the post status from `draft` to `published`, stores request-time `publishedAt`/`updatedAt`, and returns a published job-shaped response.
7. Errors: `404` with code `not_found` when `post_id` is unknown or does not identify a draft.
8. Errors: `409` with code `conflict` when `revisionId` does not match the current draft revision. The conflict response must not create a revision or audit event, and must not mutate the post.
9. Audit event: `post.published` with `revisionId` and `jobId` metadata.
10. Publish job storage: immediate publish currently stores a `publish_jobs` row with deterministic `id`, `postId`, `revisionId`, `status=succeeded`, `scheduledAt=null`, `startedAt=publishedAt`, `completedAt=publishedAt`, `errorCode=null`, and `errorMessage=null`.
11. Duplicate capability warning: admin, MCP, and agents must use this capability instead of creating parallel publish endpoints.

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
