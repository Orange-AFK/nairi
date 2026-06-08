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

## Runtime API Client Boundary

1. `apps/admin/src/adminApiClient.ts` now provides `createAdminApiClient` for runtime management API reads.
2. It calls `GET /api/v1/posts?status=draft` with absolute `VITE_API_BASE_URL` from the Vite entrypoint and an injected token provider.
3. The top-level React `App` still receives an injected `AdminApiClient` and does not read env, call `fetch`, or touch direct database access.
4. The first runtime client boundary lists draft summaries only; edit, create, publish, settings, token persistence, routing, and live browser smoke remain deferred.

## Admin Token Provider Boundary

1. `apps/admin/src/adminTokenProvider.ts` defines the first admin token provider contract.
2. Current provider intentionally returns an empty token so the runtime client remains fail-closed until a later admin session/login boundary supplies credentials.
3. The provider does not read `VITE_*` token env names and does not persist bearer tokens in `localStorage` or `sessionStorage`.
4. The Vite entrypoint wires `getAuthToken` into `createAdminApiClient` while still only reading non-secret `VITE_API_BASE_URL`.
5. Login UI, token persistence, session restoration, refresh/logout, and live browser auth smoke remain deferred.

## Admin Module Shell Boundary

1. The admin app now exposes a minimal `Admin modules` navigation shell with `Content`, `Media`, and `Settings` entries.
2. `Content` remains the only API-backed working module and preserves the injected draft-list/preview boundary.
3. `Media` and `Settings` are placeholder panels only; media workflows, settings writes, routing libraries, create/edit/publish mutations, audit, and token management remain deferred.
4. Module switching is local React state and does not bypass documented API endpoints or direct database access rules.

## Admin Draft Detail Readback Boundary

1. The `Content` module now reads selected draft detail through injected `apiClient.getPost(postId)`.
2. The runtime admin API client calls authenticated `GET /api/v1/posts/{postId}` and maps `contentFormat`, `content`, and `revisionId` into the admin detail view.
3. The list still loads draft summaries only; detail loading is a separate readback step with a safe fallback message.
4. Boundary: no create/edit/publish mutation, no public route reuse, no direct database access, no token persistence, and no router expansion.

## Admin Draft Detail UX Refinement Boundary

1. The `Content` module now marks the selected draft summary with `aria-pressed` and a stable selected style.
2. Empty draft lists now show a stable message instead of a generic unselected-preview prompt.
3. The unselected detail panel prompt is explicit that selecting a draft loads API-backed detail.
4. Boundary: no create/edit/publish mutation, no router expansion, no direct fetch, no token persistence, and no media/settings business logic.
