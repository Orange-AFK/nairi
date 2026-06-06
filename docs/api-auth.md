# Nairi

## API Authentication Guide

### Purpose

This guide explains the planned API authentication and authorization model.

## Authentication Models

### Human Admin Access

1. Human administrators authenticate through an admin login flow.
2. Admin actions are checked against roles and scopes.

### API Token Access

1. Agents, MCP, webhooks, and automation use API tokens.
2. Tokens store hashes, not raw token values.
3. Tokens carry explicit scopes.
4. The current FastAPI scaffold accepts bearer tokens from the `Authorization` header and checks configured token-to-scope mappings.
5. Persistent hashed token storage is still future database work.

## Scope Model

### Core Scopes

1. `posts:read`
2. `posts:write`
3. `posts:publish`
4. `media:read`
5. `media:write`
6. `settings:read`
7. `settings:write`
8. `audit:read`
9. `agent:invoke`
10. `admin:all`

## Rule

No client may bypass API auth, scope checks, status transitions, or audit logging.

## Current Scaffold Behavior

### Protected Route Contract

1. `GET /api/v1/mdx-components` requires `settings:read`.
2. A token with `admin:all` satisfies the check.
3. Missing bearer token returns `401`.
4. Invalid bearer token returns `401`.
5. A valid token without `settings:read` or `admin:all` returns `403`.
6. Error responses use `code`, `message`, `details`, and `requestId`.
