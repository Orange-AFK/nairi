# Nairi

## Data Model Principles

### Naming

1. Entity, table, column, and field names use English.
2. API schema names and database model names should use the canonical entity names in `contract-index.md`.
3. Schema changes require Alembic migrations.

## Core Entities

### User

1. Represents a human administrator or system user.
2. Key fields: `id`, `email`, `displayName`, `roleId`, `createdAt`, `updatedAt`.

### Role

1. Groups permissions for human users.
2. Key fields: `id`, `name`, `scopes`, `createdAt`, `updatedAt`.

### ApiToken

1. Represents agent or automation credentials.
2. Stores token metadata, not raw token values.
3. Key fields: `id`, `name`, `tokenHash`, `scopes`, `expiresAt`, `revokedAt`, `createdAt`.

### Post

1. Represents a content article.
2. Key fields: `id`, `title`, `slug`, `status`, `contentFormat`, `currentRevisionId`, `publishedAt`, `createdAt`, `updatedAt`.

### PostRevision

1. Represents immutable content revisions.
2. Key fields: `id`, `postId`, `content`, `metadata`, `createdBy`, `createdAt`.

### MdxComponent

1. Represents registered MDX component governance.
2. Key fields: `name`, `enabled`, `riskLevel`, `propsSchema`, `allowedRoles`, `allowedAgentScopes`, `requiresReview`, `updatedAt`.

### PublishJob

1. Represents publication workflow execution.
2. Key fields: `id`, `postId`, `revisionId`, `status`, `scheduledAt`, `startedAt`, `completedAt`, `errorCode`, `errorMessage`.

### AgentTask

1. Represents agent-driven content work.
2. Key fields: `id`, `type`, `status`, `sourceRefs`, `targetPostId`, `createdByTokenId`, `createdAt`, `completedAt`.

### AuditEvent

1. Records sensitive and state-changing operations.
2. Key fields: `id`, `eventType`, `actorType`, `actorId`, `targetType`, `targetId`, `metadata`, `createdAt`.

## Database Support

### SQLite

1. Default deployment database.
2. Must enable foreign keys.
3. WAL mode should be considered for write reliability.

### PostgreSQL

1. Production option.
2. Must use the same migration path as SQLite where possible.
