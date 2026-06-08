# Nairi

## CMS Admin Guide

### Purpose

This guide documents how human administrators use the CMS console as it becomes available. The current implementation is a minimal foundation shell under `apps/admin`.

## Planned Areas

### Content Management

1. Posts
2. Pages
3. Drafts
4. Revisions
5. Publishing controls

### Governance

1. MDX component registry
2. Agent task review
3. API token management
4. Audit logs
5. Site settings

## API Rule

The admin console uses documented APIs only. It does not bypass API permissions or write directly to the database.

## Current Foundation

1. The current admin shell is a Vite React app under `apps/admin`.
2. It renders the `Nairi Admin` workspace and loads draft summaries through an injected API client boundary.
3. It does not perform live writes, direct database access, token management, publication, scheduling, repair actions, or production mutation.
4. Future admin modules must continue to use documented API contracts only.
