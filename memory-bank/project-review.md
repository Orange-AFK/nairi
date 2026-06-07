# Nairi Project Review

## Review Status

1. Status: Historical review report for the Project Development Review and Documentation Governance Boundary.
2. Maintenance: Do not update this file during normal feature development.
3. Authority: This file is audit evidence and a remediation plan, not a current source of truth.
4. Required migration: Any finding that becomes an active project rule must be migrated into the appropriate authority document: `project-state.md`, `roadmap.md`, `decisions.md`, `architecture.md`, `api-contract.md`, `data-model.md`, `frontend-design.md`, `guard-ci.md`, or guard scripts.
5. Review branch: `docs/project-evolution-decision-documentation-boundary`.
6. Reviewed base: `0caef16 feat: add cloudflare invalidation request plan (#54)`.
7. Suspended implementation work: Cloudflare dry-run dispatch work is saved in git stash and is outside this review's code-change scope.

## Review Purpose

1. Re-establish control over project planning, progress, and documentation after many small verified development boundaries.
2. Check whether project implementation still matches the original product frame: API-first, agent-first CMS, public-safe publishing, and governed human review.
3. Check whether project documents are synchronized with actual progress.
4. Identify architecture decisions and constraints that emerged during development but were not promoted into durable decision records.
5. Identify document responsibility drift before adding more feature work.
6. Decide whether guard scripts or documentation rules need updates to keep the project from drifting again.

## Review Scope

1. In scope:
   - `memory-bank/*.md` English project-development documents.
   - local `memory-bank/*-cn.md` companion behavior and guard rules.
   - `docs/*.md` external/user/operator documentation boundary.
   - root `README.md` and `README-cn.md` entrypoint boundary.
   - guard/check scripts under `scripts/guards/` and `scripts/checks/`.
   - current implemented API routes and public-site route/check inventory.
   - consistency between `progress-log.md`, `project-state.md`, `roadmap.md`, `decisions.md`, `api-contract.md`, `architecture.md`, and implementation state.
2. Out of scope:
   - new product feature implementation.
   - changing Cloudflare dry-run dispatch code.
   - deleting historical progress entries.
   - rewriting every document in one pass.
   - changing public product requirements without owner review.

## Evidence Collected

1. Current branch is `docs/project-evolution-decision-documentation-boundary` with a clean worktree before this review file.
2. Current base commit is `0caef16 feat: add cloudflare invalidation request plan (#54)`.
3. Current tracked development documents include:
   - `memory-bank/admin-console.md`
   - `memory-bank/agent-mcp-design.md`
   - `memory-bank/api-contract.md`
   - `memory-bank/architecture.md`
   - `memory-bank/content-system.md`
   - `memory-bank/contract-index.md`
   - `memory-bank/data-model.md`
   - `memory-bank/decisions.md`
   - `memory-bank/deployment.md`
   - `memory-bank/frontend-design.md`
   - `memory-bank/guard-ci.md`
   - `memory-bank/integration-map.md`
   - `memory-bank/product-design.md`
   - `memory-bank/progress-log.md`
   - `memory-bank/project-state.md`
   - `memory-bank/requirements.md`
   - `memory-bank/roadmap.md`
   - `memory-bank/tech-stack.md`
4. Current tracked external docs include:
   - `docs/admin-guide.md`
   - `docs/agent-mcp-guide.md`
   - `docs/api-auth.md`
   - `docs/deployment-compose.md`
5. Current implemented API route inventory from source includes:
   - `GET /api/v1/health`
   - `GET /api/v1/mdx-components`
   - `GET /api/v1/posts`
   - `GET /api/v1/posts/{post_id}`
   - `PATCH /api/v1/posts/{post_id}`
   - `POST /api/v1/posts`
   - `POST /api/v1/posts/{post_id}/publish`
   - `GET /api/v1/public/posts`
   - `GET /api/v1/public/posts/{slug}`
6. Current relevant settings inventory from source includes:
   - `api_tokens`
   - `database_path`
   - `public_invalidation_dispatcher`
   - `public_invalidation_cloudflare_zone_id`
   - `public_invalidation_cloudflare_api_token`
7. Current public-site route/check inventory includes:
   - `apps/public-site/app/page.tsx`
   - `apps/public-site/app/posts/page.tsx`
   - `apps/public-site/app/posts/[slug]/page.tsx`
   - `apps/public-site/app/posts/error.tsx`
   - `apps/public-site/app/rss.xml/route.ts`
   - `apps/public-site/app/sitemap.xml/route.ts`
   - `apps/public-site/app/sitemap-posts.xml/route.ts`
   - `scripts/checks/frontend_public_*_check.py`
8. `docs_guard.py` enforces root document limits, `docs/` vs `memory-bank/` separation, local ignored Chinese memory-bank pairs, and forbidden abstract stage headings.
9. `i18n_doc_guard.py` compares contract-like backtick tokens between English and Chinese pairs; CI skips `memory-bank` Chinese pair checks because local Chinese memory-bank files are intentionally ignored.
10. `.gitignore` ignores `memory-bank/*-cn.md`; no `memory-bank/*-cn.md` files are tracked.

## Current Source-of-Truth Map

1. `project-state.md` should be the current status and current focus source of truth.
2. `roadmap.md` should be the functional module plan and near-future sequencing source of truth.
3. `progress-log.md` should be append-only historical evidence; it should not be the active roadmap or architecture decision authority.
4. `decisions.md` should be the durable architecture decision record and owner decision register.
5. `architecture.md` should describe current system architecture and module boundaries.
6. `api-contract.md` should describe canonical API contracts, auth/public route boundaries, response fields, and API-visible behavior.
7. `data-model.md` should describe current persistence entities and migration/database support boundaries.
8. `frontend-design.md` should describe current public frontend behavior, rendering, SEO, RSS/sitemap, and public cache policy.
9. `integration-map.md` should describe allowed module integration paths and duplicate capability prevention.
10. `guard-ci.md` should describe guard and CI behavior; guard scripts are the executable subset of those rules.
11. `docs/` should contain external user/operator guides and must not contain internal planning, progress, ADR, or contract-index content.
12. Root docs should be entrypoints only.

## Implementation State Review

1. The implementation still follows the original API-first direction.
   - Product capabilities are centered in FastAPI routes.
   - Public frontend reads public API routes rather than authenticated management routes.
   - MCP and admin remain planned API-backed clients rather than direct database writers.
2. The public/management API split appears intact.
   - Authenticated management routes use `/api/v1/posts...` and require scopes.
   - Anonymous public routes use `/api/v1/public/posts...` and public-safe response schemas.
3. The content/publishing flow is far beyond the early draft boundary.
   - Draft create/read/list/update exists.
   - Publish transition and publish-job storage exist.
   - Authenticated published read/list/filter/pagination exists.
   - Anonymous public list/detail/render exists.
4. The public frontend is no longer just a shell.
   - It has home, list, detail, error state, metadata, canonical URLs, RSS, sitemap index, posts sitemap, route-level revalidation, and bounded feed/sitemap traversal.
5. Public invalidation has evolved into a staged in-process model.
   - Contract surfaces are recorded.
   - Execution is durable bookkeeping with `executor=none`.
   - Dispatch bookkeeping is persisted.
   - Dispatcher exception policy is fail-closed relative to dispatch but preserves successful publish state.
   - Concrete Cloudflare adapter work has reached config, settings, and inert request-plan construction.
6. No reviewed document evidence indicates that the project has crossed into prohibited external invalidation execution on `main`.
   - The current mainline Cloudflare adapter request builder is inert.
   - Real HTTP client wiring, Cloudflare API execution, CDN purge, Next.js tag/path revalidation, webhooks, cache headers, scheduling semantics, and real job runner remain deferred in source-of-truth docs.

## Progress and Documentation Alignment

### Aligned Areas

1. `api-contract.md` is relatively current for public and management API behavior.
2. `architecture.md` reflects the main publish flow and invalidation dispatch architecture at a high level.
3. `frontend-design.md` is relatively current for public frontend routes, cache policy, RSS, sitemap, and SEO.
4. `guard-ci.md` matches the current guard scripts and CI workflow at a high level.
5. `progress-log.md` is detailed and provides strong historical evidence for completed slices.
6. `project-state.md` contains most completed work through Cloudflare request-plan boundary.

### Misaligned or Weak Areas

1. `project-state.md` is structurally stale.
   - The active section still says `Article Draft API Development`, but the content now spans public frontend, RSS, sitemap, invalidation, and Cloudflare adapter work.
   - It has become a long flat completion ledger instead of a concise current status document.
2. `roadmap.md` is significantly stale.
   - It does not reflect completed public API, public frontend, RSS/sitemap, invalidation, and Cloudflare adapter progress.
   - It still reads like an early project plan rather than a current functional roadmap.
3. `decisions.md` is under-maintained.
   - It contains early architecture decisions but misses many decisions that emerged during implementation.
4. `progress-log.md` is overburdened.
   - It is now the richest source of architecture decisions, deferred boundaries, and next-work hints, which makes it too authoritative for a historical log.
5. Document update rules are incomplete.
   - `progress-log.md` defines what a progress entry must contain, but not when a task must update `decisions.md`, `roadmap.md`, `project-state.md`, or guard scripts.
6. Some technology stack wording is ahead of implementation.
   - `tech-stack.md` says SQLAlchemy and Alembic manage migrations, but `architecture.md` and `data-model.md` correctly say they remain planned and not introduced in code.
   - This should be clarified as target stack versus currently implemented stack.
7. Some external docs remain high-level and may be acceptable, but their scope should stay external/operator-facing rather than mirroring internal progress.

## Architecture Decisions Found Outside `decisions.md`

The following durable decisions or constraints are currently documented mostly outside `decisions.md` and should be promoted or cross-referenced.

1. Public-safe schema for anonymous content APIs.
   - Found in `api-contract.md`, `architecture.md`, `integration-map.md`, and progress entries.
   - Decision essence: public routes use separate paths and expose only public-safe published fields.
2. Minimal public renderer boundary.
   - Found in `api-contract.md`, `frontend-design.md`, and progress entries.
   - Decision essence: public `bodyHtml` is generated by a deliberately small safe Markdown renderer; full MDX/component rendering is deferred.
3. Next.js route revalidation as the current public frontend cache policy.
   - Found in `frontend-design.md` and progress entries.
   - Decision essence: public frontend uses explicit Next.js revalidation and avoids `no-store`; CDN headers and publish-triggered invalidation are separate future work.
4. RSS/sitemap bounded traversal and split policy.
   - Found in `frontend-design.md`, progress entries, and public-site checks.
   - Decision essence: RSS and sitemap read anonymous public list pages with explicit bounds; `/sitemap.xml` is a sitemap index and `/sitemap-posts.xml` owns post URLs.
5. Public invalidation staged boundary model.
   - Found in `api-contract.md`, `architecture.md`, `project-state.md`, and progress entries.
   - Decision essence: invalidation advances through contract recording, durable bookkeeping, dispatch bookkeeping, adapter configuration, and provider request planning before any external side effect.
6. Dispatcher bookkeeping semantics.
   - Found in `api-contract.md` and tests.
   - Decision essence: dispatcher result status/reason/attempted/attemptedAt are persisted and returned; dispatcher exceptions do not roll back a successful publish transition.
7. Cloudflare adapter secret-safe staged model.
   - Found in `api-contract.md`, `architecture.md`, `project-state.md`, and tests.
   - Decision essence: Cloudflare zone/token settings exist; token is secret; dispatcher stores only token-configured boolean; request plan excludes token and Authorization data; plan is not executed on main.
8. Separation of invalidation concerns.
   - Found scattered across frontend/cache and invalidation progress entries.
   - Decision essence: Cloudflare purge, Next.js `revalidateTag`/`revalidatePath`, cache headers, scheduling semantics, and job runner are separate concerns and should not be smuggled into the same slice.
9. Guard scripts as executable project contract.
   - Found in `guard-ci.md` and workflow.
   - Decision essence: guards are mandatory completion gates, not optional utilities.
10. Local Chinese memory-bank companion policy.
   - Found in `guard-ci.md`, `.gitignore`, `docs_guard.py`, and `i18n_doc_guard.py`.
   - Decision essence: English memory-bank docs are tracked; Chinese memory-bank companions are required locally but intentionally ignored and skipped in CI.
11. PR/CI/readback completion discipline.
   - Found mostly in working practice and progress entries, not in a project contribution document.
   - Decision essence: significant repo changes should pass local guards/scans, push through PR, verify CI, and read back remote content. This may belong in a future contributing/workflow document if it is meant to be a repo rule rather than assistant operating practice.

## Missing or Under-Documented Decisions

1. Missing ADR: Public content safety model after public route implementation.
2. Missing ADR: Minimal renderer now, governed MDX later.
3. Missing ADR: Public frontend cache policy and separation from CDN/invalidation execution.
4. Missing ADR: RSS/sitemap bounded full-history traversal and sitemap split.
5. Missing ADR: Publish invalidation staged boundary model.
6. Missing ADR: Cloudflare adapter secret-safe staged boundary.
7. Missing ADR or guard-ci rule: when a completed task must update `decisions.md`.
8. Missing roadmap update: current roadmap does not represent the actual completed functional areas or near-future choices.
9. Missing project-state restructuring: current state should be grouped by functional area and current focus.
10. Missing tech-stack clarification: distinguish target stack from currently implemented stack where SQLAlchemy/Alembic are planned but not yet active.
11. Missing document-governance rule: `progress-log.md` is historical evidence only and should not become the only place a decision lives.
12. Missing document-governance rule: review reports are historical audit artifacts, not normal active source-of-truth docs.

## Drift Risk Assessment

1. Product direction drift: low.
   - The project still follows the API-first, agent-first CMS direction.
2. Public/auth boundary drift: low to medium.
   - Current code and core docs preserve the split, but future work could regress if `decisions.md` does not capture the evolved public-safe model.
3. Architecture decision loss risk: high.
   - Many decisions live only in progress entries and could be missed by future agents or contributors.
4. Roadmap drift: high.
   - `roadmap.md` is stale enough that it should not currently be trusted as the next-work authority.
5. Current-state drift: medium.
   - `project-state.md` is mostly current but structurally confusing and too ledger-like.
6. Documentation-role drift: medium to high.
   - Multiple documents describe overlapping future work, deferred work, and boundaries without a shared update rule.
7. Side-effect creep risk: medium.
   - The project has correctly avoided external invalidation side effects so far, but the Cloudflare staged work needs a durable decision record before live execution is attempted.
8. Guard coverage drift: medium.
   - Guards enforce paths, bilingual pairs, contract tokens, schema casing, secrets, and public-site structural checks, but they do not enforce decision-record updates or roadmap freshness.

## Document Governance Proposal

1. Keep `project-review.md` as a historical review artifact only.
   - It must not become a normally updated project source of truth.
   - Future reviews should create a dated review file or replace this file only as part of an explicit review task.
2. Reassert document authority boundaries:
   - `project-state.md`: current status, current focus, blockers, latest completed functional boundaries.
   - `roadmap.md`: current functional roadmap and sequencing.
   - `progress-log.md`: append-only historical evidence.
   - `decisions.md`: durable architecture and owner decisions.
   - `architecture.md`: current module/system boundaries.
   - `api-contract.md`: API-visible contracts and response semantics.
   - `guard-ci.md`: guard/CI behavior and document synchronization rules.
3. Add a decision-update trigger rule:
   - If a task changes module boundaries, system responsibilities, public/auth behavior, security/secret policy, external side-effect policy, cache/invalidation policy, database/migration policy, or future sequencing assumptions, update `decisions.md` or explicitly state that an existing decision already covers it.
4. Add a roadmap-update trigger rule:
   - If a task completes, defers, splits, or reorders a functional area, update `roadmap.md` or record why no roadmap change is needed.
5. Add a project-state-update trigger rule:
   - If a task changes current capabilities, blockers, or next named work, update `project-state.md`.
6. Add a progress-log decision impact field for future entries:
   - `Decision impact: added ADR / updated ADR / covered by existing ADR / no durable decision`.
7. Keep local Chinese memory-bank companion behavior as-is unless owner wants tracked bilingual internal docs.
   - Existing guards already support the current local-only Chinese policy.
8. Consider, but do not immediately add, a guard that detects `progress-log.md` entries with decision-bearing language and no `decisions.md` change.
   - This should be a later guard-hardening task because naive keyword checks may create noise.

## Root Entrypoint and Agent Rule Review

1. `AGENTS.md` is an active project rule file and must be part of the remediation scope.
   - It currently contains the strongest documentation synchronization rule.
   - The old rule is too broad because it implies README, roadmap, project state, and progress log always update together.
   - It does not explicitly require `decisions.md` updates when durable architecture decisions emerge.
2. `README.md` and `README-cn.md` are stale.
   - They still describe the repository as foundational documentation design before product code.
   - They must be refreshed to early alpha implementation status.
3. `CONTRIBUTING.md` and `CONTRIBUTING-cn.md` are mostly valid but should add source-of-truth and decision-register checklist items.
4. `SECURITY.md` and `SECURITY-cn.md` remain acceptable for the current review scope.
5. `.env.example` is stale relative to current `Settings`.
   - Current source settings are `NAIRI_SERVICE_NAME`, `NAIRI_VERSION`, `NAIRI_API_TOKENS`, `NAIRI_DATABASE_PATH`, `NAIRI_PUBLIC_INVALIDATION_DISPATCHER`, `NAIRI_PUBLIC_INVALIDATION_CLOUDFLARE_ZONE_ID`, and `NAIRI_PUBLIC_INVALIDATION_CLOUDFLARE_API_TOKEN`.
   - The old `NAIRI_DATABASE_URL`, JWT, and initial-admin examples are not current settings.

## Recommended Remediation Tasks

### Project Documentation Source-of-Truth Reset

1. Restructure `project-state.md` by functional area.
2. Make it concise and current rather than a long chronological ledger.
3. Preserve detailed chronology in `progress-log.md`.
4. Add current focus and next named work clearly.

### Roadmap Refresh

1. Rewrite `roadmap.md` around current functional areas:
   - Foundation and guards.
   - API core and auth.
   - Content draft/publishing.
   - Public content API.
   - Public frontend.
   - RSS/sitemap/SEO/cache.
   - Publish invalidation.
   - Cloudflare provider adapter.
   - Data/migrations.
   - Admin console.
   - Agent/MCP.
   - Deployment.
2. Mark completed, active, deferred, and candidate work with named tasks, not abstract stage labels.

### Decision Register Catch-Up

1. Add ADRs for missing decisions listed above.
2. Add a decision record rule at the top of `decisions.md`.
3. Cross-reference relevant authority docs instead of duplicating full contracts.

### Progress Rule Update

1. Keep `progress-log.md` append-only.
2. Extend the progress entry template with decision impact and authority-doc impact.
3. Clarify that progress log is not next-step authority.

### Guard and Script Review

1. Update `guard-ci.md` to document source-of-truth roles and update triggers.
2. Keep `docs_guard.py` unchanged initially unless the source-of-truth reset reveals enforceable rules.
3. Keep `i18n_doc_guard.py` behavior unchanged for local ignored memory-bank Chinese pairs.
4. Consider later guard hardening for decision-record impact after the human-readable rule has stabilized.

### Tech Stack Clarification

1. Update `tech-stack.md` so SQLAlchemy/Alembic are clearly target stack, not current implemented stack.
2. Keep `data-model.md` as the current persistence boundary authority.

## Recommended Immediate Order

1. Finish this review report and local Chinese companion.
2. Run docs/i18n/contract/schema/secret guards to verify the review artifact obeys current rules.
3. Do not PR this review alone unless the owner wants the audit artifact committed before remediation.
4. Apply source-of-truth remediation in one focused documentation PR:
   - `decisions.md`
   - `project-state.md`
   - `roadmap.md`
   - `progress-log.md`
   - `guard-ci.md`
   - `tech-stack.md`
   - local Chinese companions
5. After merge, return to the suspended Cloudflare dry-run dispatch branch and rebase/apply the stash.

## Review Conclusion

1. The project does not appear to have been built in the wrong direction.
2. The implementation trajectory still matches the original project frame: API-first, public-safe publishing, agent/admin integration through documented APIs, and guarded incremental development.
3. The main problem is documentation control, not feature direction.
4. The most urgent fix is to stop relying on `progress-log.md` as the implicit decision database and to restore clear authority boundaries among `project-state.md`, `roadmap.md`, `decisions.md`, `architecture.md`, and `api-contract.md`.
5. Future Cloudflare/live invalidation work should not continue until the staged invalidation decisions and side-effect boundaries are promoted into `decisions.md` and reflected in the current roadmap.
