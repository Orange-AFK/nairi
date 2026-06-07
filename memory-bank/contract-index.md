# Nairi

## Global Contract Index

### API Version Prefix

1. Public and authenticated product APIs use `/api/v1`, but public content APIs must use a dedicated public path such as `/api/v1/public/...` instead of reusing authenticated management paths.
2. New endpoints must be registered in `api-contract.md` before implementation.

## Canonical Entity Names

### Content Entities

1. `Post`
2. `PostRevision`
3. `Page`
4. `MediaAsset`
5. `Tag`
6. `Category`
7. `Series`
8. `MdxComponent`

### Operational Entities

1. `User`
2. `Role`
3. `ApiToken`
4. `PublishJob`
5. `AgentTask`
6. `AuditEvent`
7. `SiteSetting`
8. `WebhookEndpoint`

## Permission Scopes

### Public Scopes

1. `public:read`

### Content Scopes

1. `posts:read`
2. `posts:write`
3. `posts:publish`
4. `pages:read`
5. `pages:write`
6. `media:read`
7. `media:write`

### System Scopes

1. `settings:read`
2. `settings:write`
3. `tokens:read`
4. `tokens:write`
5. `audit:read`
6. `agent:invoke`
7. `admin:all`

## Content Status Names

### Post Status

1. `draft`
2. `review`
3. `scheduled`
4. `published`
5. `archived`
6. `failed`

## Job Status Names

### Publish Job Status

1. `queued`
2. `running`
3. `succeeded`
4. `failed`
5. `cancelled`

## Audit Event Types

### Content Events

1. `post.created`
2. `post.updated`
3. `post.review_requested`
4. `post.published`
5. `post.archived`
6. `mdx.risk_detected`

### System Events

1. `token.created`
2. `token.revoked`
3. `agent.task_created`
4. `job.started`
5. `job.completed`

## Route Naming Rules

### API Routes

1. Use plural resource names.
2. Use resource identifiers in path variables.
3. Use verbs only for domain actions such as `publish`, `archive`, or `review`.
4. Do not create parallel admin or agent API paths for the same management capability.
5. Public read paths are separate capabilities when they use anonymous caller rules and public-safe responses.

## MCP Tool Naming Rules

### Tool Names

1. Use snake_case.
2. Name user intent, not internal endpoint mechanics.
3. Map every tool to documented API capability.
