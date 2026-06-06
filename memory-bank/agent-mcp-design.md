# Nairi

## Agent Integration Principle

### MCP Wraps API

MCP is the agent-friendly tool layer. It wraps documented FastAPI capabilities and must not become a second product backend.

## OpenAPI Role

### Canonical API Description

1. FastAPI generates OpenAPI.
2. API contracts are planned in `api-contract.md`.
3. MCP tools map to documented API capabilities.

## MCP Tool Design

### Planned Tools

#### Create Article Draft From Project Summary

1. Tool name: `create_article_draft_from_project_summary`
2. Backed by: `POST /api/v1/agent-tasks/article-draft`
3. Required scope: `agent:invoke`
4. Purpose: create a draft from project context.

#### Explain MDX Risks

1. Tool name: `explain_mdx_risks`
2. Backed by: MDX component policy and content analysis APIs.
3. Required scope: `agent:invoke`
4. Purpose: explain risky content before publication.

#### Publish Article After Review

1. Tool name: `publish_article_after_review`
2. Backed by: `POST /api/v1/posts/{post_id}/publish`
3. Required scope: `posts:publish`
4. Purpose: publish an approved revision.

## Agent Safety

### Boundaries

1. Agents use scoped API tokens.
2. Agents cannot bypass review policies.
3. Agents cannot directly mutate the database.
4. Agents must create audit events through API-backed operations.
