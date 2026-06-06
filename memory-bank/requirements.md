# Nairi

## Product Goal

### Core Goal

Nairi provides an API-first CMS that allows human administrators and AI agents to create, review, publish, and maintain technical articles derived from project development experience.

## Users

### Human Administrator

1. Manages posts, pages, media, settings, tokens, components, and publishing workflows.
2. Reviews and edits agent-generated drafts.
3. Controls risky MDX capabilities and publication permissions.

### AI Agent

1. Creates article drafts from project context.
2. Revises drafts based on human instructions.
3. Explains content and MDX risks before publication.
4. Uses MCP tools backed by documented APIs.

### Public Reader

1. Reads articles, project retrospectives, series, tags, and pages.
2. Does not interact with admin or agent capabilities.

## Functional Requirements

### API Core

1. Provide documented versioned APIs under `/api/v1`.
2. Enforce auth scopes, status transitions, and audit logs.
3. Serve all product capabilities to frontend, admin, MCP, agents, and jobs.

### Content Management

1. Manage posts, pages, tags, categories, series, and revisions.
2. Support Markdown as default content format.
3. Support governed MDX through registered components.
4. Support draft, review, scheduled, published, archived, and failed states where applicable.

### Admin Console

1. Provide a complete CMS interface for humans.
2. Use APIs only; do not write directly to the database.
3. Manage content, media, MDX components, agent tasks, API tokens, audit logs, and settings.

### Agent and MCP

1. Provide MCP tools mapped to documented API capabilities.
2. Support agent draft generation, revision, risk explanation, and publishing workflows.
3. Prevent agents from bypassing permissions or audit rules.

## Non-Goals

### Excluded From Initial Scope

1. A WordPress-compatible plugin ecosystem.
2. Direct database access by frontend, admin, MCP, or agents.
3. Unrestricted arbitrary MDX execution.
4. Theme-only static blog implementation.

## Acceptance Criteria

### Foundational Acceptance

1. Root, memory-bank, and docs structure is complete.
2. API-first and contract-first rules are documented.
3. Bilingual documentation rules are documented.
4. Guard and CI expectations are documented.
5. No product code is required before documentation acceptance.
