# Nairi

## Admin Console Positioning

### Human Control Plane

The CMS admin console is the human-facing control plane for content, media, MDX governance, agent tasks, permissions, audit logs, and settings.

## Technology Stack

### Selected Stack

1. React
2. Vite
3. TypeScript
4. TanStack Router
5. TanStack Query
6. React Hook Form
7. Zod
8. Tailwind CSS
9. shadcn/ui

## Admin Modules

### Content Management

1. Post list
2. Post editor
3. Draft review
4. Revision history
5. Publication controls
6. Tags, categories, and series

### Media Library

1. Upload assets
2. Manage alt text
3. Track references
4. Select cover images

### MDX Governance

1. Component registry
2. Risk level configuration
3. Role and agent scope policy
4. Review requirement policy

### Agent Operations

1. Agent task list
2. Draft generation results
3. Risk explanations
4. Audit trail for agent actions

### System Settings

1. Site metadata
2. SEO defaults
3. API tokens
4. Webhooks
5. MCP configuration

## API Coupling Rule

### Admin API Access

The admin console must use documented API endpoints only. It must not perform direct database writes or bypass permission checks.

## Admin Foundation Implementation

### Current Shell

1. App path: `apps/admin`.
2. Stack: Vite, React, TypeScript, Vitest, React Testing Library.
3. Current behavior: a minimal API-injected shell renders `Nairi Admin`, loads draft summaries through an injected `AdminApiClient`, and shows an API-backed draft preview.
4. Boundary: no live fetch, no direct database access, no production mutation, no token storage, no router, no settings, no media, no publish action, and no scheduler.
5. CI: `scripts/checks/frontend_admin_foundation_check.py`, admin tests, admin typecheck, and admin build run in Guards.
