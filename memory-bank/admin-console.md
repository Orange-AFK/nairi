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

## Admin First Edit Form Boundary

1. The `Content` module now renders a first draft edit form after draft detail readback.
2. The form submits through injected `apiClient.updatePost(postId, input)` using `title`, `contentFormat`, `content`, and `expectedRevisionId` from the current detail revision.
3. Successful injected updates refresh the displayed draft detail and list summary; failed updates show the safe fallback `Draft changes could not be saved.`, and stale edit responses are ignored after a newer selection
4. Boundary: this is an injected UI contract only; runtime `createAdminApiClient` intentionally does not wire `PATCH /api/v1/posts/{post_id}` yet. No publish button, create flow, router expansion, direct fetch, token persistence, media/settings logic, or direct database access is added.

## Admin Runtime PATCH Client Boundary

1. Runtime `createAdminApiClient.updatePost(postId, input)` now calls authenticated `PATCH /api/v1/posts/{post_id}` with the encoded post id.
2. The request body sends `title`, `slug`, `contentFormat`, `content`, and `expectedRevisionId`; failed credentials, invalid base URLs, and non-2xx update responses remain fail-closed.
3. The admin UI still uses the injected API client boundary and preserves stale save-response protection; no publish/create/router/login/token-persistence flow is added.

## Admin Edit Slug Field Boundary

1. The draft edit form now renders an editable `Draft slug` field between title and content.
2. Save submits the form slug through the injected `apiClient.updatePost(postId, input)` payload instead of preserving only the loaded detail slug.
3. Boundary: no frontend slug validation, create/publish mutation, router expansion, login UI, token persistence, direct fetch, or direct database access is added.

## Admin Edit Summary Field Boundary

1. The draft edit form now renders an editable `Draft summary` field between slug and content.
2. Save submits the edited summary through the injected `apiClient.updatePost(postId, input)` payload and runtime PATCH body alongside title, slug, content format, content, and expected revision id.
3. Boundary: no frontend summary validation, taxonomy/tag/series editing, create/publish mutation, router expansion, login UI, token persistence, direct fetch, or direct database access is added.

## Admin Edit Tags Field Boundary

1. The draft edit form now renders an editable `Draft tags` comma-separated field between summary and content.
2. Save submits normalized tags through the injected `apiClient.updatePost(postId, input)` payload and runtime PATCH body alongside title, slug, summary, content format, content, and expected revision id.
3. Boundary: tags are comma-separated and deduplicated locally; no taxonomy/category/series selector, frontend tag validation, create/publish mutation, router expansion, login UI, token persistence, direct fetch, or direct database access is added.

## Admin Edit Category Field Boundary

1. The draft edit form now renders an editable `Draft category ID` field between summary and tags.
2. Save trims the field and submits `categoryId` through the injected `apiClient.updatePost(postId, input)` payload and runtime PATCH body alongside title, slug, summary, tags, content format, content, and expected revision id.
3. Boundary: blank category ID normalizes to `null`; no category selector, taxonomy management UI, create/publish mutation, router expansion, login UI, token persistence, direct fetch, or direct database access is added.

## Admin Edit Series Field Boundary

1. The draft edit form now renders an editable `Draft series ID` field between category ID and tags.
2. Save trims the field and submits `seriesId` through the injected `apiClient.updatePost(postId, input)` payload and runtime PATCH body alongside title, slug, summary, category ID, tags, content format, content, and expected revision id.
3. Boundary: blank series ID normalizes to `null`; no series selector, taxonomy/series management UI, create/publish mutation, router expansion, login UI, token persistence, direct fetch, or direct database access is added.

## Admin Edit Metadata JSON Field Boundary

1. The draft edit form now renders an editable `Draft metadata JSON` field between tags and content.
2. Save parses the field as a JSON object and submits `metadata` through the injected `apiClient.updatePost(postId, input)` payload and runtime PATCH body alongside title, slug, summary, category ID, series ID, tags, content format, content, and expected revision id.
3. Boundary: blank metadata normalizes to `{}` and non-object JSON fails safely through the existing edit error path; no richer metadata validation, taxonomy selectors, create/publish mutation, router expansion, login UI, token persistence, direct fetch, direct database access, public API change, or backend/API contract change is added.

## Admin Publish Request Review Boundary

1. The draft detail form now exposes a non-executing `Request publish review` button after `Save draft changes`.
2. Clicking it stages a local review status for the current `revisionId` without calling `updatePost`, without introducing a runtime publish API client method, and without changing the post status.
3. Boundary: this is a human-review UI affordance only; no `POST /api/v1/posts/{post_id}/publish` call, publish mutation, job creation, invalidation dispatch, router expansion, login UI, token persistence, direct fetch, or direct database access is added.

## Admin Publish Confirmation Contract Boundary

1. After a local `Request publish review`, the draft detail form now exposes a `Publish confirmation contract` panel for the current `revisionId`.
2. `Confirm publication intent` records a local confirmation status for that revision without calling `updatePost`, without introducing a runtime publish API client method, and without changing the post status.
3. Boundary: this is a confirmation-intent contract only; no `POST /api/v1/posts/{post_id}/publish` call, publish mutation, publish job creation, invalidation dispatch, router expansion, login UI, token persistence, direct fetch, or direct database access is added.

## Admin Publish Runtime Client Boundary

1. Runtime `createAdminApiClient.publishPost(postId, input)` now calls authenticated `POST /api/v1/posts/{post_id}/publish` with the encoded post id.
2. The publish client sends `revisionId`, `publishMode`, and `scheduledAt`, maps the management response to a publish result with `jobId`, and fails closed before fetch when credentials are missing.
3. Boundary: this only adds the injected runtime API client contract; the admin App UI still does not call `publishPost`, does not expose a live `Publish` button, and does not add router/login/token persistence, direct App fetch, direct database access, job runner UI, or invalidation controls.

## Admin Publish Action UI Boundary

1. The admin detail form now exposes `Publish confirmed draft` only after the local publish confirmation intent is recorded.
2. The action calls the injected `apiClient.publishPost(postId, { revisionId, publishMode: "immediate", scheduledAt: null })`, validates the response post id, updates the selected/list status to the published response, and renders a safe success status with `publishedAt`.
3. Publish failures or mismatched publish response ids render `Draft could not be published.` without exposing backend details; stale in-flight publish responses are ignored after draft selection changes.
4. Boundary: this is the first explicit App publish action wiring; it still adds no router expansion, login UI, token persistence, direct component fetch, direct database access, scheduling UI, job runner UI, or invalidation controls.

## Admin Post-Publish List Behavior Boundary

1. After a confirmed admin publish succeeds, the published post remains visible in the detail pane for readback but is removed from the draft review list.
2. If that published item was the only draft in the injected list, the list renders `No draft posts are ready for review.` while keeping the success status visible in the detail pane; if other drafts remain, only the published draft is removed.
3. Boundary: this slice only clarifies list behavior after the existing injected publish action; it does not add published-list navigation, refetching, filters, router state, live fetch wiring, or archive/history UI.

## Admin Published Detail Read-Only Boundary

1. After a confirmed publish succeeds, the selected published detail remains visible for readback and publish action status stays visible outside the draft edit form.
2. Published details in the draft review workflow render the stable copy `Published detail is read-only in the draft review workflow.` and no longer show draft edit, save, publish review, confirmation, or publish action controls.
3. Boundary: this slice only gates draft controls by selected detail status; it does not add a published-list module, router state, live refetching, archive/history UI, or backend/API contract changes.

## Admin Published Detail Label Boundary

1. Non-draft selected details now render the eyebrow `API-backed published detail` instead of reusing `API-backed draft detail`.
2. Draft detail and draft preview labels remain unchanged, and published read-only behavior remains unchanged.
3. Boundary: this slice changes only local admin detail label semantics; it does not add routing, refetching, published-list navigation, archive/history UI, or backend/API contract changes.

## Admin List Status Label Boundary

1. The admin content list label remains `Drafts` when every loaded summary is a draft.
2. If a mixed-status list is injected, the label changes to `Content items` so published entries are not presented under a draft-only heading.
3. Boundary: this is copy/semantics only; no router, live refetch, published-list navigation, archive/history UI, filtering, or backend/API contract changes are added.

## Admin Mixed-Status Detail Loading Copy Boundary

1. Draft selections continue to show `Loading draft detail…` while detail readback is pending.
2. Non-draft selections now show `Loading item detail…` while detail readback is pending, avoiding draft-only copy for published content items.
3. Boundary: this is loading-copy semantics only; no empty-list behavior, router, live refetch, published-list navigation, archive/history UI, filtering, or backend/API contract changes are added.

## Admin Published Read-Only Copy Hardening Boundary

1. Published/non-draft detail remains read-only in the draft review workflow.
2. The read-only detail copy now explicitly says `Draft editing and publishing controls are hidden for this content item.` so hidden controls are explained without adding actions.
3. Boundary: copy and regression coverage only; no router, live refetch, published-list navigation, archive/history UI, filtering, draft-control exposure, or backend/API contract changes.

## Admin Draft Workflow Copy Boundary

1. Draft detail forms now show `Draft controls only affect the selected draft.` above the draft edit/publish controls.
2. Published/non-draft detail remains read-only and continues to hide draft workflow controls.
3. Boundary: copy and regression coverage only; no update/publish API behavior changes, router, live refetch, published-list navigation, archive/history UI, filtering, or backend/API contract changes.

## Admin Publish Review Status Scope Boundary

1. Staged publish-review status remains scoped to the currently selected draft and is cleared when another draft is selected.
2. The publish confirmation panel also clears with selection changes so an older staged revision is not shown for the newly selected draft.
3. Boundary: regression coverage and guard/docs only; no backend publish-review persistence, publish API changes, router, live refetch, published-list navigation, archive/history UI, or filtering changes.

## Admin Router Adoption Boundary

1. The admin module shell now adopts explicit hash routes for module selection: `#content`, `#media`, and `#settings`.
2. The content module supports selected-detail hash routes shaped as `#content/{postId}` and loads the matching injected summary through the existing `apiClient.getPost(postId)` detail boundary after list readback.
3. Clicking module navigation updates the hash route while preserving the existing `Admin modules` accessibility contract and placeholder-only `Media`/`Settings` modules.
4. Boundary: client-side hash routing only; no routing library, token storage, backend/API changes, direct component fetch, direct database writes, scheduler behavior, live migration execution, deployment changes, published-history/list module, or media/settings business logic is added.
