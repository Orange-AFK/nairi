# Nairi

## Progress Log

### Foundational Documentation Creation

1. Status: completed.
2. Scope: root documents, memory-bank documents, docs documents, and project rules.
3. Verification performed: document completeness, bilingual pairing, `.gitignore` behavior, API prefix check, environment variable consistency, and Git status review.
4. Result: passed.
5. Next recommended named task: Documentation Guard and Contract Guard Completion.

### Documentation Guard and Contract Guard Completion

1. Status: completed.
2. Scope: implemented `docs_guard.py`, `i18n_doc_guard.py`, `contract_guard.py`, `api_schema_guard.py`, `secret_guard.py`, shared `guard_common.py`, and `.github/workflows/guards.yml`.
3. Changed files: guard scripts, CI workflow, `memory-bank/guard-ci.md`, local `memory-bank/guard-ci-cn.md`, roadmap, and progress log.
4. Verification performed: ran all guard scripts locally.
5. Result: passed after tightening the secret guard token heuristic to avoid false positives on long lowercase tool names.
6. Risks or blockers: current guards validate documented contracts only; future product code will require expanding contract extraction and source scanning.
7. Next recommended named task: Documentation Review and Acceptance.

### FastAPI Project Scaffold

1. Status: completed.
2. Scope: added Python project metadata, project-local virtual environment workflow, FastAPI app factory, settings module, public health endpoint, and route-level health test.
3. Changed files: `pyproject.toml`, `services/api/src/nairi_api/__init__.py`, `services/api/src/nairi_api/config.py`, `services/api/src/nairi_api/main.py`, `services/api/tests/test_health.py`, `memory-bank/project-state.md`, `memory-bank/architecture.md`, `memory-bank/api-contract.md`, `memory-bank/contract-index.md`, `memory-bank/tech-stack.md`, `memory-bank/roadmap.md`, and local Chinese memory-bank pairs.
4. Verification performed: verified project-local `.venv` isolation, watched the health test fail before implementation, implemented the smallest passing FastAPI scaffold, ran the focused test, ran the full API test suite, ran guard scripts, reviewed Git status, and ran secret guard.
5. Result: passed.
6. Risks or blockers: package install used `python3 -m venv` because `uv` is not available in PATH. FastAPI TestClient currently emits a Starlette deprecation warning unless filtered by pytest configuration.
7. Next recommended named task: Authentication and Scope System Development.

### Authentication and Scope System Development

1. Status: completed.
2. Scope: added a scaffold token-to-scope settings model, bearer-token parsing, scope dependency, standard API error handler, protected `GET /api/v1/mdx-components` route, and route-level tests for missing token, invalid token, missing scope, required scope, and `admin:all`.
3. Changed files: `services/api/src/nairi_api/auth.py`, `services/api/src/nairi_api/config.py`, `services/api/src/nairi_api/main.py`, `services/api/tests/test_scope_auth.py`, `memory-bank/api-contract.md`, `memory-bank/architecture.md`, `memory-bank/project-state.md`, `memory-bank/roadmap.md`, `docs/api-auth.md`, and local Chinese pairs.
4. Verification performed: wrote tests first, verified RED with missing `api_tokens` support, implemented minimal scaffold auth, verified focused GREEN with `5 passed`, then prepared documentation updates.
5. Result: passed for the current scaffold boundary.
6. Risks or blockers: tokens are configured in settings for the scaffold; persistent hashed token storage and token lifecycle audit events remain future database work.
7. Next recommended named task: Article Draft API Development.

### Initial GitHub Handoff

1. Status: in progress.
2. Scope: created GitHub repository `Orange-AFK/nairi`, committed initial project files, pushed `main`, verified remote commit and representative file readback, and started CI verification.
3. Changed files: `scripts/guards/docs_guard.py`, `scripts/guards/i18n_doc_guard.py`, `memory-bank/guard-ci.md`, local `memory-bank/guard-ci-cn.md`, and progress logs after CI revealed that local-only Chinese memory-bank files are intentionally not present on GitHub.
4. Verification performed so far: local tests and guards passed, staged whitespace/runtime/secret scans passed after refining secret-shaped scan, pushed `main`, verified local and remote SHA match, read back README, pyproject, auth module, and guards workflow from GitHub Contents API.
5. Result: remote push succeeded; CI follow-up fix is being prepared.
6. Risks or blockers: the first GitHub Actions run failed because guard scripts required ignored local Chinese memory-bank pairs in CI.
7. Next recommended named task: complete CI fix and verify final pushed HEAD.

### Article Draft Create API Scaffold

1. Status: completed.
2. Scope: added route-level tests and a minimal scaffold implementation for `POST /api/v1/posts` using `posts:write` or `admin:all`.
3. Changed files: `services/api/src/nairi_api/main.py`, `services/api/tests/test_post_drafts.py`, `memory-bank/project-state.md`, `memory-bank/architecture.md`, `memory-bank/roadmap.md`, and local Chinese memory-bank pairs.
4. Verification performed: wrote failing route tests first and observed `404` RED, implemented the smallest FastAPI route and Pydantic request/response models, then verified focused GREEN and full API test suite.
5. Result: passed for the scaffold boundary.
6. Risks or blockers: draft creation currently returns deterministic scaffold identifiers and does not persist `Post`, `PostRevision`, or `post.created` audit events.
7. Next recommended named task: Article Draft Persistence Boundary.

### Article Draft Persistence Boundary

1. Status: completed.
2. Scope: added SQLite-backed `PostStore`, `NAIRI_DATABASE_PATH`/`Settings.database_path`, route integration for `POST /api/v1/posts`, and tests proving persisted `posts`, `post_revisions`, and `post.created` audit rows.
3. Changed files: `services/api/src/nairi_api/config.py`, `services/api/src/nairi_api/main.py`, `services/api/src/nairi_api/posts.py`, `services/api/tests/test_post_persistence.py`, `memory-bank/project-state.md`, `memory-bank/architecture.md`, `memory-bank/data-model.md`, `memory-bank/decisions.md`, `memory-bank/progress-log.md`, and local Chinese pairs.
4. Verification performed: wrote the persistence route test first, observed RED on missing `database_path` and then missing `audit_events`, implemented the smallest SQLite store, then verified focused GREEN and full API test suite.
5. Result: passed for the minimal SQLite persistence boundary.
6. Risks or blockers: duplicate slug/id handling currently depends on raw SQLite constraint errors; SQLAlchemy/Alembic migrations remain deferred.
7. Next recommended named task: Article Draft Duplicate Slug Handling.

### Article Draft Duplicate Slug Handling

1. Status: completed.
2. Scope: added route-level conflict handling for duplicate draft slugs in `POST /api/v1/posts`, with a standard `409 conflict` error and no extra post revision or audit event side effects.
3. Changed files: `services/api/src/nairi_api/main.py`, `services/api/src/nairi_api/posts.py`, `services/api/tests/test_post_persistence.py`, `memory-bank/api-contract.md`, `memory-bank/project-state.md`, `memory-bank/progress-log.md`, and local Chinese pairs.
4. Verification performed: wrote the duplicate slug test first, observed RED on raw SQLite `UNIQUE constraint failed: posts.slug`, implemented the smallest store error and API mapping, then verified focused GREEN and full API test suite.
5. Result: passed for the duplicate slug conflict boundary.
6. Risks or blockers: broader input validation remains mostly Pydantic/default behavior; SQLAlchemy/Alembic migrations remain deferred.
7. Next recommended named task: Article Draft Input Validation Boundary.

### Article Draft Input Validation Boundary

1. Status: completed.
2. Scope: added route-level validation for blank `title`, invalid `slug`, and blank `content` in `POST /api/v1/posts`, with a standard `400 invalid_request` error and no persistence side effects.
3. Changed files: `services/api/src/nairi_api/main.py`, `services/api/tests/test_post_persistence.py`, `memory-bank/api-contract.md`, `memory-bank/project-state.md`, `memory-bank/progress-log.md`, and local Chinese pairs.
4. Verification performed: wrote the invalid draft input test first, observed RED because invalid input returned `201`, implemented the smallest route validation helper, then verified focused GREEN and full API test suite.
5. Result: passed for the draft input validation boundary.
6. Risks or blockers: validation remains intentionally limited to create-draft content fields; SQLAlchemy/Alembic migrations and production timestamp generation remain deferred.
7. Next recommended named task: Article Draft Store Timestamp Boundary.

### Article Draft Store Timestamp Boundary

1. Status: completed.
2. Scope: replaced the fixed scaffold draft timestamp with request-time UTC timestamps in `POST /api/v1/posts`, with injectable clock support for deterministic tests.
3. Changed files: `services/api/src/nairi_api/posts.py`, `services/api/tests/test_post_persistence.py`, `services/api/tests/test_post_drafts.py`, `memory-bank/api-contract.md`, `memory-bank/project-state.md`, `memory-bank/architecture.md`, `memory-bank/data-model.md`, `memory-bank/progress-log.md`, and local Chinese pairs.
4. Verification performed: wrote the injected UTC timestamp persistence test first, observed RED because `PostStore` lacked a `clock` parameter, implemented the smallest clock/timestamp helper, updated route scaffold timestamp expectations, then verified focused GREEN and full API test suite.
5. Result: passed for the draft timestamp boundary.
6. Risks or blockers: timestamp precision is intentionally seconds-only for the current API contract; SQLAlchemy/Alembic migrations and draft readback remain deferred.
7. Next recommended named task: Article Draft Response Readback Boundary.

### Article Draft Response Readback Boundary

1. Status: completed.
2. Scope: added authenticated `GET /api/v1/posts/{post_id}` readback for created drafts with `posts:read` scope, standard `403` scope enforcement, and standard `404 not_found` for unknown or non-draft IDs.
3. Changed files: `services/api/src/nairi_api/main.py`, `services/api/src/nairi_api/posts.py`, `services/api/tests/test_post_persistence.py`, `memory-bank/api-contract.md`, `memory-bank/project-state.md`, `memory-bank/architecture.md`, `memory-bank/data-model.md`, `memory-bank/progress-log.md`, and local Chinese pairs.
4. Verification performed: wrote readback route tests first, observed RED on the unwired route returning FastAPI `404`, implemented the smallest store read model and route mapping, then verified focused GREEN and full API test suite.
5. Result: passed for the draft readback boundary.
6. Risks or blockers: readback is intentionally limited to draft detail by ID; list, update, publish, and SQLAlchemy/Alembic migrations remain deferred.
7. Next recommended named task: Article Draft List Boundary.

### Article Draft List Boundary

1. Status: completed.
2. Scope: added authenticated `GET /api/v1/posts?status=draft` list readback for draft summaries with `posts:read` scope, empty-list behavior, and standard `403` scope enforcement.
3. Changed files: `services/api/src/nairi_api/main.py`, `services/api/src/nairi_api/posts.py`, `services/api/tests/test_post_persistence.py`, `memory-bank/api-contract.md`, `memory-bank/project-state.md`, `memory-bank/architecture.md`, `memory-bank/data-model.md`, `memory-bank/progress-log.md`, and local Chinese pairs.
4. Verification performed: wrote list route tests first, observed RED on the unwired route returning FastAPI `405`, implemented the smallest store list method and route mapping, then verified focused GREEN, persistence tests, full API suite, docs guards, schema guards, and secret guards.
5. Result: passed for the draft list boundary.
6. Risks or blockers: list is intentionally limited to draft summary items and omits content; filtering, pagination, update, publish, and SQLAlchemy/Alembic migrations remain deferred.
7. Next recommended named task: Article Draft Update Boundary.

### Article Draft Update Boundary

1. Status: completed.
2. Scope: added authenticated `PATCH /api/v1/posts/{post_id}` draft update with `posts:write` scope, new immutable revision creation, current revision pointer update, request-time `updatedAt`, `post.updated` audit event, standard `404 not_found`, and stale `expectedRevisionId` `409 conflict` without side effects.
3. Changed files: `services/api/src/nairi_api/main.py`, `services/api/src/nairi_api/posts.py`, `services/api/tests/test_post_persistence.py`, `memory-bank/api-contract.md`, `memory-bank/project-state.md`, `memory-bank/architecture.md`, `memory-bank/data-model.md`, `memory-bank/progress-log.md`, and local Chinese pairs.
4. Verification performed: wrote update route tests first, observed RED on the unwired route returning FastAPI `405`, implemented the smallest store update method and route mapping, then added revision-conflict coverage and verified focused GREEN, persistence tests, full API suite, docs guards, schema guards, and secret guards.
5. Result: passed for the draft update boundary.
6. Risks or blockers: update-time duplicate slug conflict handling, broader validation, publication, filtering/pagination, and SQLAlchemy/Alembic migrations remain deferred.
7. Next recommended named task: Article Draft Update Slug Conflict Boundary.

### Article Draft Update Slug Conflict Boundary

1. Status: completed.
2. Scope: added update-time duplicate slug conflict handling for `PATCH /api/v1/posts/{post_id}`, returning the standard `409 conflict` response before creating a new revision, audit event, or mutating either post.
3. Changed files: `services/api/src/nairi_api/main.py`, `services/api/src/nairi_api/posts.py`, `services/api/tests/test_post_persistence.py`, `memory-bank/api-contract.md`, `memory-bank/project-state.md`, `memory-bank/progress-log.md`, and local Chinese pairs.
4. Verification performed: wrote the duplicate-slug update test first, observed RED as `500 Internal Server Error` from the raw SQLite unique constraint, implemented the smallest store slug ownership check and API mapping, then verified focused GREEN, persistence tests, full API suite, docs guards, schema guards, and secret guards.
5. Result: passed for the update slug conflict boundary.
6. Risks or blockers: broader update validation, publication, filtering/pagination, and SQLAlchemy/Alembic migrations remain deferred.
7. Next recommended named task: Article Draft Update Validation Boundary.

### Article Draft Update Validation Boundary

1. Status: completed.
2. Scope: added explicit update-time invalid content field coverage for `PATCH /api/v1/posts/{post_id}`, proving blank `title`, invalid `slug`, and blank `content` return the standard `400 invalid_request` before creating a revision, audit event, or mutating the post.
3. Changed files: `services/api/tests/test_post_persistence.py`, `memory-bank/api-contract.md`, `memory-bank/project-state.md`, `memory-bank/progress-log.md`, and local Chinese pairs.
4. Verification performed: wrote the invalid-update route test first and observed it pass because the update route already reused `validate_post_draft_request`; no production code change was needed. Verified focused GREEN, persistence tests, full API suite, docs guards, schema guards, and secret guards.
5. Result: passed for update validation coverage.
6. Risks or blockers: publication state changes, filtering/pagination, and SQLAlchemy/Alembic migrations remain deferred.
7. Next recommended named task: Article Draft Publish Contract Boundary.

### Article Draft Publish Contract Boundary

1. Status: completed.
2. Scope: added the first authenticated `POST /api/v1/posts/{post_id}/publish` route contract with `posts:publish` scope, queued job-shaped `202` response, standard `404 not_found`, and stale `revisionId` `409 conflict` without post, revision, or audit mutation.
3. Changed files: `services/api/src/nairi_api/main.py`, `services/api/src/nairi_api/posts.py`, `services/api/tests/test_post_persistence.py`, `memory-bank/api-contract.md`, `memory-bank/project-state.md`, `memory-bank/data-model.md`, `memory-bank/progress-log.md`, and local Chinese pairs.
4. Verification performed: wrote publish route tests first and observed RED on the unwired route returning FastAPI `404`; implemented the smallest request/response models, route mapping, and `PostStore.queue_publish` contract; then verified focused GREEN, persistence tests, full API suite, docs guards, schema guards, and secret guards.
5. Result: passed for the publish contract boundary.
6. Risks or blockers: actual publication state transition, `post.published` audit persistence, publish job storage, filtering/pagination, and SQLAlchemy/Alembic migrations remain deferred.
7. Next recommended named task: Article Draft Publish State Transition Boundary.

### Article Draft Publish State Transition Boundary

1. Status: completed.
2. Scope: changed `POST /api/v1/posts/{post_id}/publish` from a queued-only contract into the first persisted publish transition: draft posts become `published`, `publishedAt` and `updatedAt` use request-time UTC, the current revision is preserved, and `post.published` audit metadata is recorded.
3. Changed files: `services/api/src/nairi_api/main.py`, `services/api/src/nairi_api/posts.py`, `services/api/tests/test_post_persistence.py`, `memory-bank/api-contract.md`, `memory-bank/project-state.md`, `memory-bank/architecture.md`, `memory-bank/data-model.md`, `memory-bank/progress-log.md`, and local Chinese pairs.
4. Verification performed: rewrote the publish success test first and observed RED because the route still returned queued `202`; implemented the smallest store transition, response mapping, `published_at` scaffold column, and audit insert; then verified focused GREEN, persistence tests, full API suite, docs guards, schema guards, and secret guards.
5. Result: passed for the publish state transition boundary.
6. Risks or blockers: durable `publish_jobs` storage, scheduling semantics, job runner execution, public rendering, filtering/pagination, and SQLAlchemy/Alembic migrations remain deferred.
7. Next recommended named task: Article Draft Publish Job Storage Boundary.

### Article Draft Publish Job Storage Boundary

1. Status: completed.
2. Scope: added the first durable `publish_jobs` scaffold table behind `POST /api/v1/posts/{post_id}/publish`; successful immediate publish now records the deterministic job id, post/revision ids, `succeeded` status, null scheduling/error fields, and request-time start/completion timestamps.
3. Changed files: `services/api/src/nairi_api/posts.py`, `services/api/tests/test_post_persistence.py`, `memory-bank/api-contract.md`, `memory-bank/project-state.md`, `memory-bank/architecture.md`, `memory-bank/data-model.md`, `memory-bank/progress-log.md`, and local Chinese pairs.
4. Verification performed: extended the publish success test first and observed RED on missing `publish_jobs`; implemented the smallest scaffold table and insert before post/audit mutation; then verified focused GREEN, conflict no-side-effect coverage, persistence tests, full API suite, docs guards, schema guards, and secret guards.
5. Result: passed for the publish job storage boundary.
6. Risks or blockers: scheduling semantics, queued/running job lifecycle, retry/failure handling, job runner execution, public rendering/readback beyond draft-only routes, filtering/pagination, and SQLAlchemy/Alembic migrations remain deferred.
7. Next recommended named task: Article Draft Published Readback Boundary.

### Article Draft Published Readback Boundary

1. Status: completed.
2. Scope: added authenticated published post detail and list readback through the existing content endpoints: `GET /api/v1/posts/{post_id}` now returns published detail after publication, and `GET /api/v1/posts?status=published` returns published summaries with `publishedAt` while preserving draft list/detail response shapes.
3. Changed files: `services/api/src/nairi_api/main.py`, `services/api/src/nairi_api/posts.py`, `services/api/tests/test_post_persistence.py`, `memory-bank/api-contract.md`, `memory-bank/project-state.md`, `memory-bank/architecture.md`, `memory-bank/data-model.md`, `memory-bank/progress-log.md`, and local Chinese pairs.
4. Verification performed: wrote published detail/list route tests first and observed RED on draft-only read/list behavior; implemented the smallest shared status read helpers and published response models; then verified focused GREEN, persistence tests, full API suite, docs guards, schema guards, and secret guards.
5. Result: passed for the published readback boundary.
6. Risks or blockers: filtering, pagination, unauthenticated public-read policy, public rendering, scheduling semantics, job runner execution, and SQLAlchemy/Alembic migrations remain deferred.
7. Next recommended named task: Article Draft Published Filtering Boundary.

### Article Draft Published Filtering Boundary

1. Status: completed.
2. Scope: added the first authenticated published-list filters for `GET /api/v1/posts?status=published`: `tag`, `category`, and `series` filter published summaries while preserving the existing response shape and `posts:read` scope.
3. Changed files: `services/api/src/nairi_api/main.py`, `services/api/src/nairi_api/posts.py`, `services/api/tests/test_post_persistence.py`, `memory-bank/api-contract.md`, `memory-bank/project-state.md`, `memory-bank/architecture.md`, `memory-bank/data-model.md`, `memory-bank/progress-log.md`, and local Chinese pairs.
4. Verification performed: wrote the published filtering route test first and observed RED because the published list returned unrelated posts; implemented the smallest route query parameters and scaffold store filtering; then verified focused GREEN and persistence tests.
5. Result: passed for the published filtering boundary.
6. Risks or blockers: pagination, unauthenticated public-read policy, public rendering, scheduling semantics, job runner execution, and SQLAlchemy/Alembic migrations remain deferred.
7. Next recommended named task: Article Draft Published Pagination Boundary.

### Article Draft Published Pagination Boundary

1. Status: completed.
2. Scope: added the first authenticated published-list pagination behavior for `GET /api/v1/posts?status=published`: `limit` restricts page size and `cursor` resumes after the prior page item id while preserving filters, response item shape, and `posts:read` scope.
3. Changed files: `services/api/src/nairi_api/main.py`, `services/api/tests/test_post_persistence.py`, `memory-bank/api-contract.md`, `memory-bank/project-state.md`, `memory-bank/architecture.md`, `memory-bank/data-model.md`, `memory-bank/progress-log.md`, and local Chinese pairs.
4. Verification performed: wrote the published pagination route test first and observed RED because `limit` was ignored and all published posts were returned; implemented the smallest route-level pagination helper; then verified focused GREEN and persistence tests.
5. Result: passed for the published pagination boundary.
6. Risks or blockers: pagination is an in-memory scaffold over reconstructed posts; unauthenticated public-read policy, public rendering, scheduling semantics, job runner execution, and SQLAlchemy/Alembic migrations remain deferred.
7. Next recommended named task: Article Published Public List Boundary.

### API Permission Boundary Audit

1. Status: completed.
2. Scope: paused feature development to review completed API route behavior and project documents for public/authenticated permission mixing; accepted the policy that public content APIs and authenticated content-management APIs must use separate route contracts.
3. Changed files: `AGENTS.md`, `docs/api-auth.md`, `memory-bank/api-contract.md`, `memory-bank/architecture.md`, `memory-bank/contract-index.md`, `memory-bank/decisions.md`, `memory-bank/frontend-design.md`, `memory-bank/integration-map.md`, `memory-bank/project-state.md`, `memory-bank/progress-log.md`, and local Chinese pairs.
4. Verification performed: inspected FastAPI route dependencies, tests, and project documents; confirmed current implemented content routes still require explicit `posts:*` scopes and no `/api/v1/public/...` route exists yet; then documented that future public reads must use dedicated public endpoints and public-safe response schemas.
5. Result: passed for documentation and architecture boundary clarification.
6. Risks or blockers: existing code is not currently mixing anonymous public and authenticated management access, but prior documents were ambiguous because some frontend/client wording implied public frontend could use authenticated published-list routes. Public route implementation remains future work.
7. Next recommended named task: Article Published Public List Boundary.

### Article Published Public List Boundary

1. Status: completed.
2. Scope: added the first anonymous public published summary list at `GET /api/v1/public/posts` with a public-safe response schema while preserving authenticated `/api/v1/posts...` management routes and `posts:read` scope semantics.
3. Changed files: `services/api/src/nairi_api/main.py`, `services/api/tests/test_post_persistence.py`, `memory-bank/api-contract.md`, `memory-bank/project-state.md`, `memory-bank/architecture.md`, `memory-bank/data-model.md`, `memory-bank/progress-log.md`, and local Chinese pairs.
4. Verification performed: wrote the public list route test first and observed RED on missing route `404`; implemented the smallest public response model and route; then verified focused GREEN and related published list tests.
5. Result: passed for the public published list boundary.
6. Risks or blockers: public detail, public filtering/pagination inputs, public rendering, cache policy, scheduling semantics, job runner execution, and SQLAlchemy/Alembic migrations remain deferred.
7. Next recommended named task: Article Published Public Detail Boundary.

### Article Published Public Detail Boundary

1. Status: completed.
2. Scope: added the first anonymous public published detail readback at `GET /api/v1/public/posts/{slug}` with a public-safe response schema while preserving authenticated `/api/v1/posts/{post_id}` management detail and `posts:read` scope semantics.
3. Changed files: `services/api/src/nairi_api/main.py`, `services/api/src/nairi_api/posts.py`, `services/api/tests/test_post_persistence.py`, `memory-bank/api-contract.md`, `memory-bank/project-state.md`, `memory-bank/architecture.md`, `memory-bank/data-model.md`, `memory-bank/progress-log.md`, and local Chinese pairs.
4. Verification performed: wrote the public detail route test first and observed RED on missing slug route `404`; implemented the smallest public detail response model, route, and published-by-slug store lookup; then verified focused GREEN and related public/authenticated readback tests.
5. Result: passed for the public published detail boundary.
6. Risks or blockers: public rendering/sanitization, public filtering/pagination inputs, cache policy, scheduling semantics, job runner execution, and SQLAlchemy/Alembic migrations remain deferred.
7. Next recommended named task: Article Published Public Render Boundary.

### Article Published Public Render Boundary

1. Status: completed.
2. Scope: added `bodyHtml` to the public detail response while preserving raw authored `content` and keeping authenticated management detail unchanged.
3. Changed files: `services/api/src/nairi_api/main.py`, `services/api/tests/test_post_persistence.py`, `memory-bank/api-contract.md`, `memory-bank/project-state.md`, `memory-bank/architecture.md`, `memory-bank/data-model.md`, `memory-bank/progress-log.md`, and local Chinese pairs.
4. Verification performed: wrote the public detail render expectation first and observed RED because `bodyHtml` was absent; implemented minimal safe Markdown rendering for `#` headings, paragraphs, and `**strong**`; verified script blocks are excluded from `bodyHtml`.
5. Result: passed for the public published render boundary.
6. Risks or blockers: renderer coverage is intentionally tiny; full MDX/component rendering, sanitizer policy expansion, frontend page integration, cache policy, scheduling semantics, job runner execution, and SQLAlchemy/Alembic migrations remain deferred.
7. Next recommended named task: Article Published Public Render Coverage Boundary or Article Frontend Public Detail Integration Boundary.

### Article Frontend Public Detail Integration Boundary

1. Status: completed.
2. Scope: added the first Next.js public site scaffold under `apps/public-site`, including `/posts/{slug}` article detail rendering from `GET /api/v1/public/posts/{slug}` and `bodyHtml`.
3. Changed files: `.github/workflows/guards.yml`, `.gitignore`, `apps/public-site/*`, `scripts/checks/frontend_public_detail_check.py`, `memory-bank/frontend-design.md`, `memory-bank/tech-stack.md`, `memory-bank/integration-map.md`, `memory-bank/guard-ci.md`, `memory-bank/project-state.md`, `memory-bank/progress-log.md`, and local Chinese pairs.
4. Verification performed: wrote `frontend_public_detail_check.py` first and observed RED because the public site files did not exist; implemented the smallest public site scaffold; verified the check, `npm run typecheck --prefix apps/public-site`, and `npm run build --prefix apps/public-site`.
5. Result: passed for the frontend public detail integration boundary.
6. Risks or blockers: public list navigation, frontend API base deployment configuration hardening, cache/CDN policy, styling system integration, full MDX/component rendering, and admin console remain deferred.
7. Next recommended named task: Article Frontend Public List Integration Boundary or Article Public Site Styling Boundary.

### Article Frontend Public List Integration Boundary

1. Status: completed.
2. Scope: added `/posts` to the Next.js public site, reading `GET /api/v1/public/posts`, rendering title/summary/publishedAt/tags, and linking each item to `/posts/{slug}`.
3. Changed files: `.github/workflows/guards.yml`, `apps/public-site/app/globals.css`, `apps/public-site/app/page.tsx`, `apps/public-site/app/posts/page.tsx`, `apps/public-site/lib/public-posts.ts`, `scripts/checks/frontend_public_list_check.py`, `memory-bank/frontend-design.md`, `memory-bank/integration-map.md`, `memory-bank/guard-ci.md`, `memory-bank/project-state.md`, `memory-bank/progress-log.md`, and local Chinese pairs.
4. Verification performed: wrote `frontend_public_list_check.py` first and observed RED because `apps/public-site/app/posts/page.tsx` did not exist; implemented the list client/page/root link; verified detail/list checks, public-site typecheck, and public-site build.
5. Result: passed for the frontend public list integration boundary.
6. Risks or blockers: pagination, filter UI, list error-state design, cache/CDN policy, RSS, sitemap, full styling system, and deployment configuration remain deferred.
7. Next recommended named task: Article Public Site Styling Boundary or Article Frontend Public List Empty/Error State Boundary.

### PostCSS Dependabot Advisory Maintenance

1. Status: completed.
2. Scope: resolved the `GHSA-qx2v-qp2m-jg93` PostCSS advisory for `apps/public-site/package-lock.json` by adding an npm override so the public site resolves `postcss` to patched version `8.5.10`.
3. Changed files: `apps/public-site/package.json`, `apps/public-site/package-lock.json`, `memory-bank/deployment.md`, `memory-bank/guard-ci.md`, `memory-bank/project-state.md`, `memory-bank/tech-stack.md`, and local Chinese pairs.
4. Verification performed: confirmed `npm update postcss` could not move the transitive dependency because `next@15.5.19` depended on `postcss@8.4.31`; added the override; verified `npm ls postcss --prefix apps/public-site` showed `postcss@8.5.10 overridden`; verified `npm audit --prefix apps/public-site --audit-level=moderate` reported no vulnerabilities; verified frontend checks, public-site typecheck/build, API tests, guards, runtime artifact scan, secret-shaped scan, PR CI, main CI, and Dependabot alert readback.
5. Result: passed; Dependabot alert #1 became fixed after the default branch was rescanned.
6. Risks or blockers: the override should be revisited when Next.js directly depends on a patched PostCSS version; current CI still has a Node.js 20 actions deprecation annotation until CI hygiene is completed.
7. Next recommended named task: CI Hygiene / Node 24 Actions Boundary, then Article Frontend Public List Empty/Error State Boundary.

### CI Hygiene / Node 24 Actions Boundary

1. Status: completed.
2. Scope: hardened the Guards workflow with read-only repository permissions, concurrency cancellation for superseded runs on the same ref, and `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: 'true'`.
3. Changed files: `.github/workflows/guards.yml`, `memory-bank/guard-ci.md`, `memory-bank/project-state.md`, `memory-bank/progress-log.md`, and local Chinese pairs.
4. Verification performed: verified workflow YAML parsing for `permissions`, `concurrency`, and `env`; verified frontend checks, docs/i18n/contract/API schema/secret guards, staged runtime artifact scan, secret-shaped scan, PR CI, main CI, and remote contents readback.
5. Result: passed for the CI hygiene boundary.
6. Risks or blockers: GitHub still emits an informational annotation that current action versions target Node.js 20 while being forced to run on Node.js 24; this can be revisited when newer action major versions are available.
7. Next recommended named task: Article Frontend Public List Empty/Error State Boundary.

### Article Frontend Public List Empty/Error State Boundary

1. Status: completed.
2. Scope: added a stable empty-list message for `/posts` and a controlled Next.js route error boundary for public list fetch failures.
3. Changed files: `apps/public-site/app/globals.css`, `apps/public-site/app/posts/error.tsx`, `scripts/checks/frontend_public_list_check.py`, `memory-bank/frontend-design.md`, `memory-bank/integration-map.md`, `memory-bank/project-state.md`, `memory-bank/progress-log.md`, and local Chinese pairs.
4. Verification performed: expanded `frontend_public_list_check.py` first and observed RED because `apps/public-site/app/posts/error.tsx` was missing; added the error boundary and focused styles; verified `frontend_public_list_check.py`, public-site typecheck, and public-site build.
5. Result: passed for the frontend public list empty/error state boundary.
6. Risks or blockers: pagination, filter UI, cache/CDN policy, RSS, sitemap, complete styling system, and deployment configuration remain deferred.
7. Next recommended named task: Article Public Site Styling Boundary.

### Article Public Site Styling Boundary

1. Status: completed.
2. Scope: unified the first public-site visual rhythm across `/`, `/posts`, `/posts/{slug}`, the list empty state, and the list error state using shared `article-header` and `surface-card` boundaries.
3. Changed files: `.github/workflows/guards.yml`, `apps/public-site/app/globals.css`, `apps/public-site/app/page.tsx`, `apps/public-site/app/posts/page.tsx`, `apps/public-site/app/posts/[slug]/page.tsx`, `apps/public-site/app/posts/error.tsx`, `scripts/checks/frontend_public_style_check.py`, `memory-bank/frontend-design.md`, `memory-bank/guard-ci.md`, `memory-bank/project-state.md`, `memory-bank/progress-log.md`, and local Chinese pairs.
4. Verification performed: added `frontend_public_style_check.py` first and observed RED on missing style tokens, shared header/card classes, and page usage; implemented the smallest shared style boundary; verified style/detail/list checks, public-site typecheck, and public-site build.
5. Result: passed for the public site styling boundary.
6. Risks or blockers: Tailwind, shadcn/ui, a complete design system, cache/CDN policy, SEO metadata, RSS, sitemap, pagination, and filter UI remain deferred.
7. Next recommended named task: Article Published Public Render Coverage Boundary or Article Public Site SEO Metadata Boundary.

### Article Public Site SEO Metadata Boundary

1. Status: completed.
2. Scope: added stable route metadata for `/` and `/posts`, kept `/posts/{slug}` metadata generated from public detail data, and added a structural metadata check to Guards.
3. Changed files: `.github/workflows/guards.yml`, `apps/public-site/app/page.tsx`, `apps/public-site/app/posts/page.tsx`, `scripts/checks/frontend_public_metadata_check.py`, `memory-bank/frontend-design.md`, `memory-bank/guard-ci.md`, `memory-bank/project-state.md`, `memory-bank/progress-log.md`, and local Chinese pairs.
4. Verification performed: added `frontend_public_metadata_check.py` first and observed RED on missing home/list metadata; added route metadata and wired the check into Guards; verified metadata/style/detail/list checks, public-site typecheck, and public-site build.
5. Result: passed for the public site SEO metadata boundary.
6. Risks or blockers: canonical URLs, Open Graph image generation, RSS, sitemap, cache/CDN policy, and richer SEO schema remain deferred.
7. Next recommended named task: Article Published Public Render Coverage Boundary.

### Article Published Public Render Coverage Boundary

1. Status: completed.
2. Scope: added structural coverage for published public list/detail rendering, including machine-readable published dates, summary fallback, tag rendering, public detail `bodyHtml`, not-found behavior, and public-route-only access.
3. Changed files: `.github/workflows/guards.yml`, `apps/public-site/app/posts/page.tsx`, `apps/public-site/app/posts/[slug]/page.tsx`, `scripts/checks/frontend_public_render_check.py`, `memory-bank/frontend-design.md`, `memory-bank/guard-ci.md`, `memory-bank/project-state.md`, `memory-bank/progress-log.md`, and local Chinese pairs.
4. Verification performed: added `frontend_public_render_check.py` first and observed RED on missing `time` date coverage, summary fallback, and detail tag rendering; implemented the smallest render coverage additions; verified render/metadata/style/detail/list checks, public-site typecheck, and public-site build.
5. Result: passed for the published public render coverage boundary.
6. Risks or blockers: pagination, filters, cache/CDN policy, canonical URLs, RSS, sitemap, Open Graph image generation, and richer SEO schema remain deferred.
7. Next recommended named task: Article Public API / Frontend Cache Policy Boundary or Article Public Sitemap/RSS Boundary.

### Article Public API / Frontend Cache Policy Boundary

1. Status: completed.
2. Scope: replaced public frontend `no-store` fetches with explicit Next.js revalidation constants for list/detail reads, kept routes dynamic to avoid build-time API prerendering, and added a structural cache-policy check to Guards.
3. Changed files: `.github/workflows/guards.yml`, `apps/public-site/lib/public-posts.ts`, `apps/public-site/app/posts/page.tsx`, `apps/public-site/app/posts/[slug]/page.tsx`, `scripts/checks/frontend_public_cache_check.py`, `memory-bank/frontend-design.md`, `memory-bank/guard-ci.md`, `memory-bank/project-state.md`, `memory-bank/progress-log.md`, and local Chinese pairs.
4. Verification performed: added `frontend_public_cache_check.py` first and observed RED on missing revalidation constants and `no-store` usage; implemented revalidation constants; observed build failure from build-time API prerendering; added `dynamic = "force-dynamic"` and extended the check; verified cache/render/metadata/style/detail/list checks, public-site typecheck, and public-site build.
5. Result: passed for the public API / frontend cache policy boundary.
6. Risks or blockers: CDN headers, publish-triggered invalidation, tag-based revalidation, pagination cache policy, RSS, and sitemap remain deferred.
7. Next recommended named task: Article Public Sitemap/RSS Boundary.

### Article Public Sitemap Boundary

1. Status: completed.
2. Scope: added the smallest `/sitemap.xml` public route with `/`, `/posts`, and published post detail URLs from public list data, including published timestamps as `lastmod`; added a structural sitemap check to Guards.
3. Changed files: `.github/workflows/guards.yml`, `apps/public-site/app/sitemap.xml/route.ts`, `scripts/checks/frontend_public_sitemap_check.py`, `memory-bank/frontend-design.md`, `memory-bank/guard-ci.md`, `memory-bank/project-state.md`, `memory-bank/progress-log.md`, and local Chinese pairs.
4. Verification performed: added `frontend_public_sitemap_check.py` first and observed RED on the missing route file; implemented the minimal dynamic route; verified sitemap check, public-site typecheck, and public-site build.
5. Result: passed for the public sitemap boundary.
6. Risks or blockers: RSS, canonical URLs, Open Graph image generation, richer SEO schema, pagination sitemap expansion, CDN headers, and publish-triggered invalidation remain deferred.
7. Next recommended named task: Article Public RSS Boundary.

### Article Public RSS Boundary

1. Status: completed.
2. Scope: added the smallest `/rss.xml` public route with RSS 2.0 items from public list data, including title, link, guid, `publishedAt` as `pubDate`, and summary fallback as description; added a structural RSS check to Guards.
3. Changed files: `.github/workflows/guards.yml`, `apps/public-site/app/rss.xml/route.ts`, `scripts/checks/frontend_public_rss_check.py`, `memory-bank/frontend-design.md`, `memory-bank/guard-ci.md`, `memory-bank/project-state.md`, `memory-bank/progress-log.md`, and local Chinese pairs.
4. Verification performed: added `frontend_public_rss_check.py` first and observed RED on the missing route file; implemented the minimal dynamic route; verified RSS check, public-site typecheck, and public-site build.
5. Result: passed for the public RSS boundary.
6. Risks or blockers: canonical URLs, Open Graph image generation, Atom, richer SEO schema, pagination sitemap/RSS expansion, CDN headers, and publish-triggered invalidation remain deferred.
7. Next recommended named task: Article Public Canonical URL Boundary or Article Public Pagination Boundary.

### Article Public Canonical URL Boundary

1. Status: completed.
2. Scope: added the smallest canonical metadata boundary for `/`, `/posts`, and `/posts/{slug}` using `metadataBase` from `NEXT_PUBLIC_NAIRI_PUBLIC_SITE_URL` with a localhost fallback; added a structural canonical check to Guards.
3. Changed files: `.github/workflows/guards.yml`, `apps/public-site/app/page.tsx`, `apps/public-site/app/posts/page.tsx`, `apps/public-site/app/posts/[slug]/page.tsx`, `scripts/checks/frontend_public_canonical_check.py`, `memory-bank/frontend-design.md`, `memory-bank/guard-ci.md`, `memory-bank/project-state.md`, `memory-bank/progress-log.md`, and local Chinese pairs.
4. Verification performed: added `frontend_public_canonical_check.py` first and observed RED on missing canonical metadata; implemented the minimal metadata boundary; verified canonical/metadata checks, public-site typecheck, and public-site build.
5. Result: passed for the public canonical URL boundary.
6. Risks or blockers: Open Graph image generation, Atom, richer SEO schema, pagination sitemap/RSS expansion, CDN headers, and publish-triggered invalidation remain deferred.
7. Next recommended named task: Article Public Pagination Boundary.

### Article Public Pagination Boundary

1. Status: completed.
2. Scope: added minimal anonymous public published-list pagination for `GET /api/v1/public/posts` with `limit` and item-id `cursor`, reusing the existing route-level pagination helper while preserving public-safe response fields.
3. Changed files: `services/api/src/nairi_api/main.py`, `services/api/tests/test_post_persistence.py`, `memory-bank/api-contract.md`, `memory-bank/architecture.md`, `memory-bank/project-state.md`, `memory-bank/progress-log.md`, and local Chinese pairs.
4. Verification performed: added a public route-level pagination test first and observed RED because `limit` was ignored and all published posts were returned; wired public list to `paginate_posts`; verified the new public pagination test and existing public-safe summary test.
5. Result: passed for the public API pagination boundary.
6. Risks or blockers: frontend pagination controls, public filters, sitemap/RSS pagination expansion, CDN headers, and publish-triggered invalidation remain deferred.
7. Next recommended named task: Article Public Frontend Pagination Boundary.

### Article Public Frontend Pagination Boundary

1. Status: completed.
2. Scope: wired `/posts` to request `GET /api/v1/public/posts` with a small `limit`, accept an item-id `cursor` from query params, and render a `Load more articles` link when `nextCursor` is present while preserving public-route-only access.
3. Changed files: `scripts/checks/frontend_public_list_check.py`, `apps/public-site/lib/public-posts.ts`, `apps/public-site/app/posts/page.tsx`, `apps/public-site/app/rss.xml/route.ts`, `apps/public-site/app/sitemap.xml/route.ts`, `memory-bank/frontend-design.md`, `memory-bank/project-state.md`, and `memory-bank/progress-log.md`.
4. Verification performed: extended `frontend_public_list_check.py` first and observed RED on missing `searchParams`, `cursor`, page size, `nextCursor`, and pagination link markers; implemented the minimal frontend pagination link; fixed RSS/sitemap callers after `fetchPublicPosts` began returning the full list response; verified list check, typecheck, and public-site build.
5. Result: passed for the public frontend pagination boundary.
6. Risks or blockers: previous-page navigation, richer pagination metadata, public filters, infinite scroll, sitemap/RSS pagination expansion, CDN headers, and publish-triggered invalidation remain deferred.
7. Next recommended named task: Article Public Pagination Metadata Boundary.

### Article Public Pagination Metadata Boundary

1. Status: completed.
2. Scope: added minimal public list pagination metadata to `GET /api/v1/public/posts` with a `page` object containing `limit`, `cursor`, and `hasNextPage`, while preserving `items`, `nextCursor`, public-safe item fields, and anonymous public-route access.
3. Changed files: `services/api/src/nairi_api/main.py`, `services/api/tests/test_post_persistence.py`, `apps/public-site/lib/public-posts.ts`, `memory-bank/api-contract.md`, `memory-bank/project-state.md`, and `memory-bank/progress-log.md`.
4. Verification performed: extended the public pagination route test first and observed RED on missing `page`; implemented the smallest response model metadata; updated the public-safe list expectation and frontend list response type.
5. Result: passed for the public pagination metadata boundary.
6. Risks or blockers: frontend display of page metadata, previous-page navigation, total counts, public filters, infinite scroll, sitemap/RSS pagination expansion, CDN headers, and publish-triggered invalidation remain deferred.
7. Next recommended named task: Article Public Pagination Metadata Frontend Boundary.

### Article Public Pagination Metadata Frontend Boundary

1. Status: completed.
2. Scope: updated `/posts` to use the public list response `page.hasNextPage` metadata together with `nextCursor` when deciding whether to render the `Load more articles` link, without displaying page metadata or changing pagination UI.
3. Changed files: `scripts/checks/frontend_public_list_check.py`, `apps/public-site/app/posts/page.tsx`, `memory-bank/frontend-design.md`, `memory-bank/project-state.md`, and `memory-bank/progress-log.md`.
4. Verification performed: extended `frontend_public_list_check.py` first and observed RED on missing `page` and `hasNextPage` markers in the page; implemented the minimal render-condition change and updated project docs.
5. Result: passed for the public pagination metadata frontend boundary.
6. Risks or blockers: previous-page navigation, total counts, public filters, infinite scroll, displaying page metadata, sitemap/RSS pagination expansion, CDN headers, and publish-triggered invalidation remain deferred.
7. Next recommended named task: Article Public RSS/Sitemap Pagination Policy Boundary.

### Article Public RSS/Sitemap Pagination Policy Boundary

1. Status: completed.
2. Scope: fixed the RSS and sitemap pagination policy boundary without expanding functionality: `/rss.xml` and `/sitemap.xml` intentionally consume one single public list page only, do not request cursor follow-up pages, and do not perform implicit multi-page crawling.
3. Changed files: `scripts/checks/frontend_public_rss_check.py`, `scripts/checks/frontend_public_sitemap_check.py`, `apps/public-site/app/rss.xml/route.ts`, `apps/public-site/app/sitemap.xml/route.ts`, `memory-bank/frontend-design.md`, `memory-bank/project-state.md`, and `memory-bank/progress-log.md`.
4. Verification performed: extended RSS/sitemap structural checks first and observed RED on missing single-page policy markers; added minimal explicit route policy constants and docs while keeping the existing one-page fetch behavior unchanged.
5. Result: passed for the RSS/sitemap pagination policy boundary.
6. Risks or blockers: full-history RSS/sitemap pagination, Atom, richer SEO schema, CDN headers, and publish-triggered invalidation remain deferred.
7. Next recommended named task: Article Public RSS/Sitemap Full-History Pagination Boundary or Article Public CDN/Invalidation Boundary.

### Article Public CDN/Invalidation Boundary

1. Status: completed.
2. Scope: fixed the public CDN/invalidation boundary without wiring a real CDN: public frontend caching remains Next.js revalidation only, and the client explicitly declares no CDN headers, no publish-triggered invalidation, and no tag-based revalidation in this slice.
3. Changed files: `scripts/checks/frontend_public_cache_check.py`, `apps/public-site/lib/public-posts.ts`, `memory-bank/frontend-design.md`, `memory-bank/project-state.md`, and `memory-bank/progress-log.md`.
4. Verification performed: extended `frontend_public_cache_check.py` first and observed RED on missing CDN/invalidation policy markers; added the minimal public client policy constant and docs while keeping list/detail revalidation behavior unchanged.
5. Result: passed for the public CDN/invalidation boundary.
6. Risks or blockers: real CDN purge wiring, publish-triggered revalidation webhooks, tag/path invalidation, pagination cache policy, RSS/sitemap cache policy, and deployment/runtime purge configuration remain deferred.
7. Next recommended named task: Article Public Publish Invalidation Contract Boundary or Article Public RSS/Sitemap Full-History Pagination Boundary.

### Article Public Publish Invalidation Contract Boundary

1. Status: completed.
2. Scope: added a contract-only public invalidation plan to the publish response and `publish_jobs` storage, covering `/posts`, `/posts/{slug}`, `/rss.xml`, and `/sitemap.xml` for successful immediate publishes.
3. Changed files: `services/api/src/nairi_api/main.py`, `services/api/src/nairi_api/posts.py`, `services/api/tests/test_post_persistence.py`, `memory-bank/api-contract.md`, `memory-bank/architecture.md`, `memory-bank/project-state.md`, and `memory-bank/progress-log.md`.
4. Verification performed: extended the publish route/storage test first and observed RED on the missing `publicInvalidation` response contract; implemented the minimal storage/response contract and verified the focused publish success and stale-revision tests.
5. Result: passed for the public publish invalidation contract boundary.
6. Risks or blockers: real CDN purge, Next.js `revalidateTag`/`revalidatePath`, webhooks, cache headers, scheduling semantics, and a real job runner remain deferred.
7. Next recommended named task: Article Public RSS/Sitemap Full-History Pagination Boundary or Article Public Publish Invalidation Execution Boundary.

### Article Public RSS/Sitemap Full-History Pagination Boundary

1. Status: completed.
2. Scope: changed `/rss.xml` and `/sitemap.xml` from a single public list page to bounded full-history traversal over anonymous public list pages, using explicit page-size and max-page limits.
3. Changed files: `apps/public-site/app/rss.xml/route.ts`, `apps/public-site/app/sitemap.xml/route.ts`, `scripts/checks/frontend_public_rss_check.py`, `scripts/checks/frontend_public_sitemap_check.py`, `memory-bank/frontend-design.md`, `memory-bank/project-state.md`, and `memory-bank/progress-log.md`.
4. Verification performed: extended RSS/sitemap structural checks first and observed RED on missing `fetchAllPublicPosts`, pagination policy constants, cursor/nextCursor use, and bounded loop markers; implemented the minimal bounded traversal and verified RSS/sitemap checks plus public-site typecheck.
5. Result: passed for the RSS/sitemap full-history pagination boundary.
6. Risks or blockers: RSS/sitemap cache policy, CDN headers, publish-triggered invalidation execution, Atom, richer feed contents, and search-engine sitemap splitting remain deferred.
7. Next recommended named task: Article Public Publish Invalidation Execution Boundary or Article Public RSS/Sitemap Cache Policy Boundary.

### Article Public RSS/Sitemap Cache Policy Boundary

1. Status: completed.
2. Scope: added explicit route-level Next.js revalidation policy markers for `/rss.xml` and `/sitemap.xml`, using 300-second revalidation while keeping full-history pagination unchanged.
3. Changed files: `apps/public-site/app/rss.xml/route.ts`, `apps/public-site/app/sitemap.xml/route.ts`, `scripts/checks/frontend_public_rss_check.py`, `scripts/checks/frontend_public_sitemap_check.py`, `memory-bank/frontend-design.md`, `memory-bank/project-state.md`, and `memory-bank/progress-log.md`.
4. Verification performed: extended RSS/sitemap structural checks first and observed RED on missing revalidation constants, cache policy markers, and route-level revalidation exports; implemented the minimal route policy and verified RSS/sitemap checks plus public-site typecheck, then fixed the route `revalidate` export to use the statically analyzable literal required by Next.js builds.
5. Result: passed for the RSS/sitemap cache policy boundary.
6. Risks or blockers: real CDN purge, publish-triggered invalidation execution, `revalidateTag`/`revalidatePath`, cache headers, sitemap splitting, Atom, and richer feed contents remain deferred.
7. Next recommended named task: Article Public Publish Invalidation Execution Boundary or Article Public RSS/Sitemap Split Boundary.

### Article Public Publish Invalidation Execution Boundary

1. Status: completed.
2. Scope: promoted publish invalidation from contract-only surfaces to a durable recorded execution state on successful immediate publishes, while keeping invalidation side effects disabled.
3. Changed files: `services/api/src/nairi_api/main.py`, `services/api/src/nairi_api/posts.py`, `services/api/tests/test_post_persistence.py`, `memory-bank/api-contract.md`, `memory-bank/architecture.md`, `memory-bank/project-state.md`, and `memory-bank/progress-log.md`.
4. Verification performed: extended the publish route/storage test first and observed RED on missing `mode=recorded`, missing execution response fields, and missing durable publish-job execution columns; implemented the minimal recorded execution state and verified the focused publish test.
5. Result: passed for the publish invalidation execution boundary.
6. Risks or blockers: external invalidation dispatch, CDN purge, `revalidateTag`/`revalidatePath`, webhooks, cache headers, scheduling semantics, and the real job runner remain deferred.
7. Next recommended named task: Article Public Publish Invalidation Dispatch Boundary or Article Public RSS/Sitemap Split Boundary.

### Article Public Publish Invalidation Dispatch Boundary

1. Status: completed.
2. Scope: added future-safe dispatch bookkeeping to publish invalidation responses and `publish_jobs` rows, defaulting to `dispatch_skipped` with `no_dispatcher_configured` and `attempted=false` when no dispatcher exists.
3. Changed files: `services/api/src/nairi_api/main.py`, `services/api/src/nairi_api/posts.py`, `services/api/tests/test_post_persistence.py`, `memory-bank/api-contract.md`, `memory-bank/architecture.md`, `memory-bank/project-state.md`, and `memory-bank/progress-log.md`.
4. Verification performed: extended the publish route/storage test first and observed RED on missing dispatch response/storage fields; implemented minimal dispatch bookkeeping and verified focused publish tests.
5. Result: passed for the publish invalidation dispatch boundary.
6. Risks or blockers: dispatcher configuration, external dispatch execution, CDN purge, `revalidateTag`/`revalidatePath`, webhooks, cache headers, scheduling semantics, and the real job runner remain deferred.
7. Next recommended named task: Article Public Publish Invalidation Dispatcher Configuration Boundary or Article Public RSS/Sitemap Split Boundary.

### Article Public Publish Invalidation Dispatcher Configuration Boundary

1. Status: completed.
2. Scope: added a safe settings-level dispatcher configuration contract for publish invalidation with `public_invalidation_dispatcher=none` as the only supported value and `NAIRI_PUBLIC_INVALIDATION_DISPATCHER=none` env wiring.
3. Changed files: `services/api/src/nairi_api/config.py`, `services/api/tests/test_config.py`, `memory-bank/api-contract.md`, `memory-bank/architecture.md`, `memory-bank/project-state.md`, and `memory-bank/progress-log.md`.
4. Verification performed: added config tests first and observed RED on the missing setting and forbidden extra input; implemented the minimal literal setting and verified config tests plus the focused publish route/storage test.
5. Result: passed for the publish invalidation dispatcher configuration boundary.
6. Risks or blockers: dispatcher interface, external dispatch execution, CDN purge, `revalidateTag`/`revalidatePath`, webhooks, cache headers, scheduling semantics, and the real job runner remain deferred.
7. Next recommended named task: Article Public Publish Invalidation Dispatcher Interface Boundary or Article Public RSS/Sitemap Split Boundary.

### Article Public Publish Invalidation Dispatcher Interface Boundary

1. Status: completed.
2. Scope: added an in-process `PublicInvalidationDispatcher` protocol, a no-op dispatcher implementation, a settings-based factory, and app-state wiring for the configured dispatcher.
3. Changed files: `services/api/src/nairi_api/invalidation_dispatch.py`, `services/api/src/nairi_api/main.py`, `services/api/tests/test_public_invalidation_dispatcher.py`, `memory-bank/api-contract.md`, `memory-bank/architecture.md`, `memory-bank/project-state.md`, and `memory-bank/progress-log.md`.
4. Verification performed: added dispatcher tests first and observed RED on the missing module and missing app-state wiring; implemented the minimal no-op interface and verified dispatcher tests plus the focused publish route/storage behavior.
5. Result: passed for the publish invalidation dispatcher interface boundary.
6. Risks or blockers: route integration, external dispatch execution, CDN purge, `revalidateTag`/`revalidatePath`, webhooks, cache headers, scheduling semantics, and the real job runner remain deferred.
7. Next recommended named task: Article Public Publish Invalidation Dispatcher Route Integration Boundary or Article Public RSS/Sitemap Split Boundary.

### Article Public Publish Invalidation Dispatcher Route Integration Boundary

1. Status: completed.
2. Scope: integrated the configured in-process public invalidation dispatcher into the publish route response path after successful publish storage.
3. Changed files: `services/api/src/nairi_api/main.py`, `services/api/tests/test_post_persistence.py`, `memory-bank/api-contract.md`, `memory-bank/architecture.md`, `memory-bank/project-state.md`, and `memory-bank/progress-log.md`.
4. Verification performed: extended the publish route test first with an injected recording dispatcher, observed RED because the response still returned stored no-dispatcher literals, then mapped the dispatcher result into `publicInvalidation.dispatch` and verified focused publish/dispatcher tests plus the full API test suite.
5. Result: passed for the publish invalidation dispatcher route integration boundary.
6. Risks or blockers: dispatcher result persistence, external dispatch execution, CDN purge, `revalidateTag`/`revalidatePath`, webhooks, cache headers, scheduling semantics, and the real job runner remain deferred.
7. Next recommended named task: Article Public RSS/Sitemap Split Boundary or Article Public Publish Invalidation Dispatcher Persistence Boundary.

### Article Public Publish Invalidation Dispatcher Persistence Boundary

1. Status: completed.
2. Scope: persisted the configured in-process public invalidation dispatcher result back onto the durable publish job dispatch fields after the publish route dispatcher call.
3. Changed files: `services/api/src/nairi_api/main.py`, `services/api/src/nairi_api/posts.py`, `services/api/tests/test_post_persistence.py`, `memory-bank/api-contract.md`, `memory-bank/architecture.md`, `memory-bank/project-state.md`, and `memory-bank/progress-log.md`.
4. Verification performed: extended the publish route/storage test first and observed RED because the response used the injected dispatcher result while the durable `publish_jobs` row still stored `attempted=0` and `attempted_at=null`; implemented minimal dispatch result persistence and verified focused publish/dispatcher tests plus the full API test suite.
5. Result: passed for the publish invalidation dispatcher persistence boundary.
6. Risks or blockers: dispatcher error policy, external dispatch execution, CDN purge, `revalidateTag`/`revalidatePath`, webhooks, cache headers, scheduling semantics, and the real job runner remain deferred.
7. Next recommended named task: Article Public Publish Invalidation Dispatcher Error Policy Boundary or Article Public RSS/Sitemap Split Boundary.

### Article Public Publish Invalidation Dispatcher Error Policy Boundary

1. Status: completed.
2. Scope: added deterministic in-process dispatcher exception bookkeeping and missing publish-job row fail-closed behavior for dispatch result persistence.
3. Changed files: `services/api/src/nairi_api/invalidation_dispatch.py`, `services/api/src/nairi_api/main.py`, `services/api/src/nairi_api/posts.py`, `services/api/tests/test_post_persistence.py`, `memory-bank/api-contract.md`, `memory-bank/architecture.md`, `memory-bank/project-state.md`, and `memory-bank/progress-log.md`.
4. Verification performed: added RED tests proving dispatcher exceptions no longer roll back successful publishes but instead record `dispatch_failed` / `dispatcher_exception` in both response and durable `publish_jobs`, and proving missing publish-job dispatch persistence fails closed; implemented the minimal exception fallback and rowcount check, then verified focused publish/dispatcher tests plus the full API test suite.
5. Result: passed for the publish invalidation dispatcher error policy boundary.
6. Risks or blockers: external invalidation execution, CDN purge, `revalidateTag`/`revalidatePath`, webhooks, cache headers, scheduling semantics, concrete adapters, and the real job runner remain deferred.
7. Next recommended named task: Article Public Publish Invalidation Adapter Contract Boundary or Article Public RSS/Sitemap Split Boundary.

### Article Public Publish Invalidation Adapter Contract Boundary

1. Status: completed.
2. Scope: added a contract-only public invalidation dispatcher adapter configuration that records deterministic attempted dispatch bookkeeping without external invalidation side effects.
3. Changed files: `services/api/src/nairi_api/config.py`, `services/api/src/nairi_api/invalidation_dispatch.py`, `services/api/src/nairi_api/main.py`, `services/api/tests/test_config.py`, `services/api/tests/test_public_invalidation_dispatcher.py`, `memory-bank/api-contract.md`, `memory-bank/architecture.md`, `memory-bank/project-state.md`, and `memory-bank/progress-log.md`.
4. Verification performed: added RED settings/factory/app-state tests for `public_invalidation_dispatcher=contract` and a contract dispatcher result, observed RED on the previous `none`-only literal and missing dispatcher class, then implemented the minimal settings literal, dispatcher class, factory branch, and response reason support before verifying focused config/dispatcher tests plus the full API test suite.
5. Result: passed for the publish invalidation adapter contract boundary.
6. Risks or blockers: concrete external adapters, CDN purge, `revalidateTag`/`revalidatePath`, webhooks, cache headers, scheduling semantics, external invalidation execution, and the real job runner remain deferred.
7. Next recommended named task: Article Public Publish Invalidation Concrete Adapter Boundary or Article Public RSS/Sitemap Split Boundary.

### Article Public RSS/Sitemap Split Boundary

1. Status: completed.
2. Scope: split the public sitemap surface so `/sitemap.xml` is a sitemap index and `/sitemap-posts.xml` owns the bounded full-history public posts sitemap.
3. Changed files: `apps/public-site/app/sitemap.xml/route.ts`, `apps/public-site/app/sitemap-posts.xml/route.ts`, `scripts/checks/frontend_public_sitemap_check.py`, `memory-bank/frontend-design.md`, `memory-bank/project-state.md`, and `memory-bank/progress-log.md`.
4. Verification performed: extended the sitemap structural check first and observed RED on the missing `sitemap-posts.xml` route; implemented the minimal sitemap index plus posts sitemap route while preserving anonymous public-list pagination, RSS separation, route-level revalidation only, and no CDN/purge/tag/path invalidation behavior; then verified sitemap/RSS checks, public-site typecheck, and the full API test suite.
5. Result: passed for the RSS/sitemap split boundary.
6. Risks or blockers: additional sitemap shards, concrete invalidation adapters, CDN purge, `revalidateTag`/`revalidatePath`, webhooks, cache headers, Atom, richer SEO schema, and the real job runner remain deferred.
7. Next recommended named task: Article Public Publish Invalidation Concrete Adapter Boundary or Article Public Sitemap Additional Shards Boundary.

### Article Public Publish Invalidation Cloudflare Adapter Config Boundary

1. Status: completed.
2. Scope: accepted `public_invalidation_dispatcher=cloudflare` as a config-only disabled concrete adapter boundary and exposed a `CloudflarePublicInvalidationDispatcher` that records deterministic skipped bookkeeping without Cloudflare API calls or purge side effects.
3. Changed files: `services/api/src/nairi_api/config.py`, `services/api/src/nairi_api/invalidation_dispatch.py`, `services/api/src/nairi_api/main.py`, `services/api/tests/test_config.py`, `services/api/tests/test_public_invalidation_dispatcher.py`, `memory-bank/api-contract.md`, `memory-bank/architecture.md`, `memory-bank/project-state.md`, and `memory-bank/progress-log.md`.
4. Verification performed: added RED config/env/factory/app-state/dispatcher tests for `cloudflare`, observed RED on the previous `none|contract` literal and missing dispatcher class, then implemented the minimal literal, disabled dispatcher, factory branch, and response reason support before verifying focused config/dispatcher tests and the full API test suite.
5. Result: passed for the Cloudflare adapter config boundary.
6. Risks or blockers: Cloudflare credentials/settings, zone/tag/path mapping, real Cloudflare API calls, CDN purge, `revalidateTag`/`revalidatePath`, webhooks, cache headers, scheduling semantics, external invalidation execution, and the real job runner remain deferred.
7. Next recommended named task: Article Public Publish Invalidation Cloudflare Adapter Settings Boundary or Article Public Sitemap Additional Shards Boundary.

### Article Public Publish Invalidation Cloudflare Adapter Settings Boundary

1. Status: completed.
2. Scope: added optional Cloudflare adapter settings for zone id and secret API token, made the config-only Cloudflare dispatcher distinguish missing settings from configured-but-disabled bookkeeping, and kept all external invalidation behavior disabled.
3. Changed files: `services/api/src/nairi_api/config.py`, `services/api/src/nairi_api/invalidation_dispatch.py`, `services/api/src/nairi_api/main.py`, `services/api/tests/test_config.py`, `services/api/tests/test_public_invalidation_dispatcher.py`, `memory-bank/api-contract.md`, `memory-bank/architecture.md`, `memory-bank/project-state.md`, and `memory-bank/progress-log.md`.
4. Verification performed: added RED tests for default-unconfigured settings, env-read zone/token settings with secret-safe repr, missing-settings dispatcher bookkeeping, and configured-disabled dispatcher bookkeeping; observed RED on missing settings fields and old disabled-only reason; then implemented the minimal settings fields, secret type, missing-settings reason literal, and settings-aware dispatcher factory.
5. Result: focused config/dispatcher tests and full API tests passed; production external-side-effect scan found zero Cloudflare/API/purge/revalidation/webhook/cache-header additions.
6. Risks or blockers: Cloudflare request construction, endpoint path/method, zone/tag/path mapping, real HTTP client, CDN purge, `revalidateTag`/`revalidatePath`, webhooks, cache headers, scheduling semantics, external invalidation execution, and job runner remain deferred.
7. Next recommended named task: Article Public Publish Invalidation Cloudflare Adapter Request Builder Boundary or Article Public Sitemap Additional Shards Boundary.

### Article Public Publish Invalidation Cloudflare Adapter Request Builder Boundary

1. Status: completed.
2. Scope: added an inert `CloudflarePurgeRequestPlan` and a Cloudflare dispatcher request-plan builder that derives method/path/body from the configured zone id and public invalidation surfaces while keeping dispatch disabled and side-effect-free.
3. Changed files: `services/api/src/nairi_api/invalidation_dispatch.py`, `services/api/tests/test_public_invalidation_dispatcher.py`, `memory-bank/api-contract.md`, `memory-bank/architecture.md`, `memory-bank/project-state.md`, and `memory-bank/progress-log.md`.
4. Verification performed: added RED tests for missing request plan type, plan method/path/body, deduplicated ordered surfaces, no token/Authorization in plan repr, missing-settings returning `None`, factory-exposed plan construction, and dispatch remaining `cloudflare_adapter_disabled`; observed RED on missing `CloudflarePurgeRequestPlan`, then implemented the minimal frozen dataclass and builder.
5. Result: focused dispatcher tests, focused config/dispatcher tests, and full API tests passed; production external-side-effect scan found zero HTTP clients, Cloudflare call execution, purge execution, revalidation, webhook, cache-header, or runner additions.
6. Risks or blockers: Cloudflare dry-run dispatch result shaping, actual HTTP client wiring, authorization headers, Cloudflare API responses/errors, CDN purge, `revalidateTag`/`revalidatePath`, webhooks, cache headers, scheduling semantics, external invalidation execution, and job runner remain deferred.
7. Next recommended named task: Article Public Publish Invalidation Cloudflare Adapter Dry-Run Dispatch Boundary or Article Public Sitemap Additional Shards Boundary.


### Article Public Publish Invalidation Cloudflare Adapter Dry-Run Dispatch Boundary

1. Status: completed.
2. Scope: advanced the configured Cloudflare adapter from configured-disabled bookkeeping to side-effect-free dry-run dispatch bookkeeping. Complete Cloudflare settings now build or depend on the inert purge request plan and return `cloudflare_adapter_dry_run`, `attempted=true`, and `attemptedAt=publishedAt`; missing or partial settings still return `cloudflare_adapter_missing_settings`, `attempted=false`, and `attemptedAt=null`.
3. Changed files: `services/api/src/nairi_api/invalidation_dispatch.py`, `services/api/src/nairi_api/main.py`, `services/api/tests/test_public_invalidation_dispatcher.py`, `memory-bank/api-contract.md`, `memory-bank/architecture.md`, `memory-bank/decisions.md`, `memory-bank/project-state.md`, `memory-bank/roadmap.md`, `memory-bank/progress-log.md`, and local Chinese companion files.
4. Verification performed: applied the updated dispatcher tests to `main` in a temporary worktree and observed RED on the previous `cloudflare_adapter_disabled` result; implemented the minimal dry-run reason literal, API response reason literal, dispatch request-plan dependency, and secret-safe result shape; verified focused dispatcher tests and full API tests.
5. Result: configured Cloudflare dispatch records dry-run bookkeeping without exposing `CloudflarePurgeRequestPlan`, zone id, token fixture, `Authorization`, or `Bearer` data in the dispatch result. No external I/O, Cloudflare API call, CDN purge, Next.js revalidation, webhook, cache header, scheduling, or job runner behavior was added.
6. Risks or blockers: live HTTP client wiring, authorization header construction/sending, Cloudflare API responses/errors, CDN purge, retry policy, external execution switch, and real job runner remain deferred.
7. Decision impact: updated the existing Cloudflare staged/secret-safe decision to include dry-run request-plan build semantics.
8. Authority-doc impact: updated `api-contract.md`, `architecture.md`, `decisions.md`, `project-state.md`, `roadmap.md`, and this progress log.
9. Next recommended named task: Article Public Sitemap Additional Shards Boundary, or a separately planned Cloudflare Live Execution Design Boundary if live provider behavior becomes the priority.

### Article Public Sitemap Additional Shards Boundary

1. Status: completed.
2. Scope: added `/sitemap-static.xml` as a dedicated static public sitemap shard for `/` and `/posts`, kept `/sitemap-posts.xml` dedicated to post detail URLs from bounded full-history public-list traversal, and updated `/sitemap.xml` to index both shard documents.
3. Changed files: `apps/public-site/app/sitemap.xml/route.ts`, `apps/public-site/app/sitemap-posts.xml/route.ts`, `apps/public-site/app/sitemap-static.xml/route.ts`, `scripts/checks/frontend_public_sitemap_check.py`, `memory-bank/frontend-design.md`, `memory-bank/project-state.md`, `memory-bank/roadmap.md`, `memory-bank/progress-log.md`, and local Chinese companion files.
4. Verification performed: extended the sitemap structural check first and observed RED on missing `apps/public-site/app/sitemap-static.xml/route.ts`; implemented the static shard, updated the sitemap index, narrowed the posts sitemap to post detail URLs, and verified focused sitemap/RSS checks plus public-site typecheck/build.
5. Result: `/sitemap.xml` is a sitemap index for `/sitemap-static.xml` and `/sitemap-posts.xml`; static routes live in the static shard; post detail URLs remain in the posts shard with bounded traversal. No RSS mixing, management-route access, bearer tokens, CDN headers, purge calls, Cloudflare behavior, tag/path revalidation, or publish-triggered invalidation execution was added.
6. Risks or blockers: Atom, richer feed contents, richer SEO schema, search-engine sitemap splitting beyond current static/posts shards, CDN cache policy, and publish-triggered live invalidation remain deferred.
7. Decision impact: covered by existing bounded RSS/sitemap traversal and staged invalidation decisions; no new ADR needed.
8. Authority-doc impact: updated `frontend-design.md`, `project-state.md`, `roadmap.md`, and this progress log.
9. Next recommended named task: Data Migration Baseline Boundary, CMS Admin Console Foundation Boundary, or Cloudflare Live Execution Design Boundary if live provider behavior becomes the priority.

### SQLite Schema Migration Baseline Boundary

1. Status: completed.
2. Scope: added `schema_migrations` metadata for the current `PostStore` SQLite scaffold schema, recorded `post_store_baseline` once, kept reopen idempotency, and adopted existing pre-migration SQLite files without losing posts, revisions, or audit rows.
3. Changed files: `services/api/src/nairi_api/posts.py`, `services/api/tests/test_post_persistence.py`, `memory-bank/project-state.md`, `memory-bank/roadmap.md`, `memory-bank/tech-stack.md`, `memory-bank/progress-log.md`, and local Chinese companion files.
4. Verification performed: added migration tests first and observed RED on missing `schema_migrations`; implemented the minimal migrator called from store schema initialization; verified focused migration tests, full post persistence tests, and full API tests.
5. Result: fresh databases create `schema_migrations`, record `(1, "post_store_baseline")`, and do not duplicate the row on reopen. Existing pre-migration databases receive the baseline metadata while preserving existing `posts`, `post_revisions`, and `audit_events` data. No public API contract, route behavior, SQLAlchemy/Alembic layer, PostgreSQL support, or external migration runner was added.
6. Risks or blockers: standalone migration tooling, migration rollback/repair policy, Alembic integration, SQLAlchemy models, PostgreSQL support, and live database rehearsal remain deferred.
7. Decision impact: covered by existing data/migration roadmap and scaffold-to-managed-migrations direction; no new ADR needed.
8. Authority-doc impact: updated `project-state.md`, `roadmap.md`, `tech-stack.md`, and this progress log.
9. Next recommended named task: Managed Migration Runner Boundary, Data Migration Rehearsal Boundary, or CMS Admin Console Foundation Boundary.

### Managed Migration Runner Boundary

1. Status: completed.
2. Scope: extracted a minimal ordered `PostStoreMigration` runner, kept the current scaffold schema as migration 1, and preserved existing baseline/adoption behavior.
3. Changed files: `services/api/src/nairi_api/posts.py`, `services/api/tests/test_post_persistence.py`, `memory-bank/project-state.md`, `memory-bank/roadmap.md`, and `memory-bank/progress-log.md`.
4. Verification performed: added runner tests first and observed RED on missing `PostStoreMigration`; implemented ordered pending migration application, applied-migration skip, migration-name mismatch guard, and rollback on failed pending migration; verified focused runner/baseline/adoption tests, full post persistence tests, and full API tests.
5. Result: migrations are now represented as ordered objects, `schema_migrations` stays authoritative for applied IDs/names, applied migrations do not rerun, and failed pending migrations rollback without writing metadata, and baseline schema reconciliation still runs for already-managed databases. No public API contract, route behavior, SQLAlchemy/Alembic layer, PostgreSQL support, external migration CLI, route/UI change, or live database operation was added.
6. Risks or blockers: standalone migration CLI, migration repair policy, multi-package migration coordination, SQLAlchemy models, Alembic integration, PostgreSQL support, and live database rehearsal remain deferred.
7. Decision impact: covered by existing data/migration roadmap and scaffold-to-managed-migrations direction; no new ADR needed.
8. Authority-doc impact: updated `project-state.md`, `roadmap.md`, and this progress log.
9. Next recommended named task: Data Migration Rehearsal Boundary, Migration Repair Policy Boundary, or CMS Admin Console Foundation Boundary.

### Data Migration Rehearsal Boundary

1. Status: completed.
2. Scope: added a local `rehearse_post_store_migration` helper that copies a SQLite source file to both backup and rehearsal paths, triggers `PostStore` migration on the rehearsal copy, and verifies migration metadata, row counts, and `PostStore` readback.
3. Changed files: `services/api/src/nairi_api/posts.py`, `services/api/tests/test_post_persistence.py`, `memory-bank/project-state.md`, `memory-bank/roadmap.md`, and `memory-bank/progress-log.md`.
4. Verification performed: added rehearsal test first and observed RED on missing `rehearse_post_store_migration`; implemented SQLite backup-API copy, path-alias rejection, exclusive destination creation, no-overwrite artifact safety, pre-state inspection, migration trigger, post-state metadata/count checks, and readback IDs; verified focused rehearsal test, full post persistence tests, and full API tests.
5. Result: migration rehearsal can prove backup existence, source immutability, backup count immutability, migrated rehearsal metadata, preserved `posts`/`post_revisions`/`audit_events` counts, and `PostStore` readback without touching any live database. No public API contract, route behavior, SQLAlchemy/Alembic layer, PostgreSQL support, external migration CLI, deployment change, or live database operation was added.
6. Risks or blockers: standalone migration/rehearsal CLI, migration repair policy, backup retention policy, multi-package migration coordination, SQLAlchemy models, Alembic integration, PostgreSQL support, and live database execution remain deferred.
7. Decision impact: covered by existing data/migration roadmap and scaffold-to-managed-migrations direction; no new ADR needed.
8. Authority-doc impact: updated `project-state.md`, `roadmap.md`, and this progress log.
9. Next recommended named task: Migration Repair Policy Boundary, Standalone Migration Rehearsal CLI Boundary, or CMS Admin Console Foundation Boundary.

### Migration Repair Policy Boundary

1. Status: completed.
2. Scope: added stable typed migration-policy error metadata for `schema_migrations` id/name mismatches.
3. Changed files: `services/api/src/nairi_api/posts.py`, `services/api/tests/test_post_persistence.py`, `memory-bank/decisions.md`, `memory-bank/data-model.md`, `memory-bank/project-state.md`, `memory-bank/roadmap.md`, and `memory-bank/progress-log.md`.
4. Verification performed: added metadata-mismatch policy test first and observed RED on missing `PostStoreMigrationError`; implemented `PostStoreMigrationError` with `code`, `migration_id`, `recorded_name`, and `expected_name`; verified focused test and full post persistence tests.
5. Result: recorded migration id/name mismatches now fail fast with stable `migration_name_mismatch` policy metadata while preserving existing valid-metadata baseline reconciliation and pending-migration rollback behavior. No public API contract, route behavior, SQLAlchemy/Alembic layer, PostgreSQL support, external migration CLI, deployment change, automatic metadata repair, or live database operation was added.
6. Risks or blockers: standalone migration/rehearsal CLI, broader repair workflow, backup retention policy, SQLAlchemy models, Alembic integration, PostgreSQL support, and live database execution remain deferred.
7. Decision impact: added `Use Explicit Migration Repair Policy Errors` to `decisions.md`.
8. Authority-doc impact: updated `decisions.md`, `data-model.md`, `project-state.md`, `roadmap.md`, and this progress log.
9. Next recommended named task: Standalone Migration Rehearsal CLI Boundary, Broader Migration Repair Workflow Boundary, or CMS Admin Console Foundation Boundary.

### Standalone Migration Rehearsal CLI Boundary

1. Status: completed.
2. Scope: added a local-only `nairi-post-store-migration-rehearsal` console script that runs the existing SQLite rehearsal helper and prints a JSON summary.
3. Changed files: `pyproject.toml`, `services/api/src/nairi_api/migration_rehearsal.py`, `services/api/tests/test_migration_rehearsal_cli.py`, `memory-bank/data-model.md`, `memory-bank/project-state.md`, `memory-bank/roadmap.md`, and `memory-bank/progress-log.md`.
4. Verification performed: added CLI tests first and observed RED on missing `nairi_api.migration_rehearsal`; added entrypoint test and observed RED on missing project script; implemented argument parsing, missing-source fail-closed behavior, JSON summary output, and the project script entrypoint; verified focused CLI tests, full API tests, and a module smoke with caller-provided disposable paths.
5. Result: operators/developers have a local rehearsal entrypoint that requires explicit source/backup/rehearsal paths, refuses missing sources through a non-zero exit, prints machine-readable migration counts/rows/readback IDs, and does not mutate source or backup databases. No public API contract, route behavior, SQLAlchemy/Alembic layer, PostgreSQL support, deployment integration, scheduling, automatic repair, or live database migration execution was added.
6. Risks or blockers: broader repair workflow, operator handoff docs, backup retention policy, SQLAlchemy models, Alembic integration, PostgreSQL support, deployment integration, and live database execution remain deferred.
7. Decision impact: covered by existing migration repair/rehearsal decisions; no new ADR needed.
8. Authority-doc impact: updated `data-model.md`, `project-state.md`, `roadmap.md`, and this progress log.
9. Next recommended named task: Broader Migration Repair Workflow Boundary, Migration Operator Handoff Docs Boundary, or CMS Admin Console Foundation Boundary.

### Broader Migration Repair Workflow Boundary

1. Status: completed.
2. Scope: documented the migration repair workflow for typed policy failures and added an executable guard that requires repair-workflow anchors in project-state, data-model, and decisions.
3. Changed files: `scripts/checks/migration_repair_workflow_check.py`, `.github/workflows/guards.yml`, `memory-bank/decisions.md`, `memory-bank/data-model.md`, `memory-bank/project-state.md`, `memory-bank/roadmap.md`, and `memory-bank/progress-log.md`.
4. Verification performed: added `migration_repair_workflow_check.py` first and observed RED on missing data-model/decision anchors; then documented rehearsal JSON inspection, `schema_migrations` comparison, `migration_name_mismatch` stop behavior, and the no-automatic-repair/no-live-mutation boundary.
5. Result: migration policy conflicts now have source-of-truth operator/developer guidance: inspect rehearsal JSON, compare source/backup/rehearsal paths, counts, `schema_migrations` rows, and readback IDs, then stop for manual intervention when `migration_name_mismatch` appears.
6. Boundary: no API contract, route behavior, SQLAlchemy/Alembic layer, PostgreSQL support, deployment integration, scheduling, automatic repair, production database access, or live database migration execution was added.
7. Risks or blockers: executable repair tooling, Alembic integration, SQLAlchemy models, PostgreSQL support, deployment integration, and live database execution remain deferred.
8. Decision impact: extended the accepted migration repair policy decision with workflow guidance; no new ADR was needed.
9. Next recommended named task: Migration Operator Handoff Docs Boundary, Executable Repair Tooling Design Boundary, or CMS Admin Console Foundation Boundary.

### Migration Operator Handoff Docs Boundary

1. Status: completed.
2. Scope: added the operator-facing runbook for SQLite migration rehearsal handoff and an executable guard that requires the runbook and memory-bank anchors.
3. Changed files: `docs/migration-operator-handoff.md`, `docs/migration-operator-handoff-cn.md`, `scripts/checks/migration_operator_handoff_check.py`, `.github/workflows/guards.yml`, `memory-bank/guard-ci.md`, `memory-bank/project-state.md`, `memory-bank/roadmap.md`, and `memory-bank/progress-log.md`.
4. Verification performed: added `migration_operator_handoff_check.py` first and observed RED on the missing runbook, Chinese pair, rehearsal CLI anchors, evidence bundle, escalation note, and memory-bank anchors; then added the runbook, CI step, and source-of-truth updates.
5. Result: operators now have `docs/migration-operator-handoff.md`, an operator-facing runbook that covers `nairi-post-store-migration-rehearsal`, source database path, backup artifact path, rehearsal artifact path, rehearsal JSON review, source/backup/rehearsal paths, `preMigrationCounts`, `postMigrationCounts`, `postMigrationRows`, `readbackPostIds`, `schema_migrations`, `migration_name_mismatch`, manual intervention, evidence bundle, and escalation note handling.
6. Boundary: no API contract, route behavior, SQLAlchemy/Alembic layer, PostgreSQL support, deployment integration, scheduling, automatic metadata repair, production database access, or live database migration execution was added.
7. Risks or blockers: executable repair tooling, backup retention policy, SQLAlchemy models, Alembic integration, PostgreSQL support, deployment integration, and live database execution remain deferred.
8. Decision impact: no new ADR; this operationalizes the accepted migration repair workflow and guard/CI decisions.
9. Next recommended named task: Executable Repair Tooling Design Boundary, CMS Admin Console Foundation Boundary, or Cloudflare Live Execution Design Boundary.

### Executable Repair Tooling Design Boundary

1. Status: completed.
2. Scope: added the design-only contract for future local executable repair tooling and an executable guard that requires the contract and source-of-truth anchors.
3. Changed files: `memory-bank/executable-repair-tooling.md`, `scripts/checks/executable_repair_tooling_design_check.py`, `.github/workflows/guards.yml`, `memory-bank/guard-ci.md`, `memory-bank/project-state.md`, `memory-bank/roadmap.md`, and `memory-bank/progress-log.md`.
4. Verification performed: added `executable_repair_tooling_design_check.py` first and observed RED on the missing design document plus missing input/output/preflight/refusal/no-live/no-auto-repair anchors; then added the design contract, CI step, and source-of-truth updates.
5. Result: future repair tooling now has a design-only contract requiring an evidence bundle from `docs/migration-operator-handoff.md`, input contract, output contract, preflight checks, dry-run only behavior, manual intervention, `migration_name_mismatch` refusal, `schema_migrations` evidence, and `PostStoreMigrationError` policy awareness.
6. Boundary: no repair tooling implementation, API contract, route behavior, SQLAlchemy/Alembic layer, PostgreSQL support, deployment integration, scheduling, automatic metadata repair, production database access, or live database migration execution was added.
7. Risks or blockers: local dry-run tooling implementation, backup retention policy, SQLAlchemy models, Alembic integration, PostgreSQL support, deployment integration, and live database execution remain deferred.
8. Decision impact: no new ADR; this refines the accepted migration repair workflow into a future implementation contract.
9. Next recommended named task: Local Repair Tooling Dry-Run Implementation Boundary, CMS Admin Console Foundation Boundary, or Cloudflare Live Execution Design Boundary.

### Local Repair Tooling Dry-Run Implementation Boundary

1. Status: completed.
2. Scope: implemented `nairi-post-store-repair-dry-run` as a local dry-run analysis entrypoint for the `memory-bank/executable-repair-tooling.md` input/output contract.
3. Changed files: `pyproject.toml`, `services/api/src/nairi_api/migration_repair_dry_run.py`, `services/api/tests/test_migration_repair_dry_run.py`, `memory-bank/executable-repair-tooling.md`, `memory-bank/project-state.md`, `memory-bank/roadmap.md`, and `memory-bank/progress-log.md`.
4. Verification performed: wrote RED tests for the missing module and missing project script entrypoint; implemented the analyzer and CLI; verified focused repair dry-run tests.
5. Result: the dry-run analyzer validates evidence bundle fields, artifact existence/path distinctness, structured rehearsal JSON, `schema_migrations` evidence, count consistency, escalation-note evidence, secret-like text refusal, output shape, `analysis_ready`, `refused`, and `needs_manual_intervention` for `migration_name_mismatch`.
6. Boundary: local analysis only; no metadata repair, no database mutation, no repair command generation, no API route, no scheduler, no production database access, no SQLAlchemy, no Alembic, no PostgreSQL, no deployment integration, and no live database migration execution was added.
7. Risks or blockers: operator-facing sample evidence polish, executable repair actions, Alembic integration, SQLAlchemy models, PostgreSQL support, deployment integration, and live migration execution remain deferred.
8. Decision impact: no new ADR; this implements the previously accepted dry-run contract while preserving manual intervention for policy conflicts.
9. Next recommended named task: Migration Repair Operator Evidence Polish Boundary, CMS Admin Console Foundation Boundary, or Cloudflare Live Execution Design Boundary.

### Migration Repair Operator Evidence Polish Boundary

1. Status: completed.
2. Scope: refined operator-facing evidence examples and checks around `nairi-post-store-repair-dry-run`, including sample evidence bundle shape and additional refusal-case documentation.
3. Changed files: `.github/workflows/guards.yml`, `docs/migration-operator-handoff.md`, `docs/migration-operator-handoff-cn.md`, `scripts/checks/migration_repair_evidence_polish_check.py`, `memory-bank/guard-ci.md`, `memory-bank/project-state.md`, `memory-bank/roadmap.md`, and `memory-bank/progress-log.md`.
4. Verification performed: added `migration_repair_evidence_polish_check.py` first and observed RED on missing dry-run CLI, sample evidence bundle, dry-run statuses, and refusal policy anchors; then updated the operator runbooks, CI wiring, and source-of-truth docs.
5. Result: operator handoff docs now describe `nairi-post-store-repair-dry-run`, a sample evidence bundle with `commandInvocation`, path fields, `stdout`, `stderr`, `rehearsalJson`, `observedStopCondition`, and `operatorEscalationNote`, plus `analysis_ready`, `refused`, `needs_manual_intervention`, and documented refusal policy codes.
6. Boundary: documentation/guard-only; no analyzer behavior change, repair tooling action, metadata repair, database mutation, API route, scheduler, production database access, SQLAlchemy, Alembic, PostgreSQL, deployment integration, or live database migration execution was added.
7. Risks or blockers: focused tests for every refusal policy code, executable repair actions, Alembic integration, SQLAlchemy models, PostgreSQL support, deployment integration, and live migration execution remain deferred.
8. Decision impact: no new ADR; this keeps operator docs aligned with the dry-run analyzer contract.
9. Next recommended named task: Migration Repair Refusal Matrix Test Expansion Boundary, CMS Admin Console Foundation Boundary, or Cloudflare Live Execution Design Boundary.

### Migration Repair Refusal Matrix Test Expansion Boundary

1. Status: completed.
2. Scope: added focused analyzer and CLI tests for `nairi-post-store-repair-dry-run` refusal policy codes and kept the operator evidence docs aligned with additional CLI fail-closed cases.
3. Changed files: `services/api/tests/test_migration_repair_dry_run.py`, `docs/migration-operator-handoff.md`, `docs/migration-operator-handoff-cn.md`, `memory-bank/guard-ci.md`, `memory-bank/project-state.md`, `memory-bank/roadmap.md`, and `memory-bank/progress-log.md`.
4. Verification performed: added focused tests for missing artifact, path aliasing, invalid rehearsal JSON, missing rehearsal JSON fields, count mismatch, missing escalation note, secret-like evidence, unreadable evidence file, and non-object evidence JSON; existing missing field, missing `schema_migrations`, `migration_name_mismatch`, success, mutation, and CLI status tests remained in place.
5. Result: the dry-run analyzer refusal matrix is now locked by tests for every documented operator-facing refusal code plus CLI fail-closed evidence parsing cases.
6. Boundary: tests/docs only; no analyzer behavior change, repair tooling action, metadata repair, database mutation, API route, scheduler, production database access, SQLAlchemy, Alembic, PostgreSQL, deployment integration, or live database migration execution was added.
7. Risks or blockers: executable repair actions, Alembic integration, SQLAlchemy models, PostgreSQL support, deployment integration, admin UI work, and live migration execution remain deferred.
8. Decision impact: no new ADR; this strengthens test coverage for the existing dry-run analyzer contract.
9. Next recommended named task: CMS Admin Console Foundation Boundary, Cloudflare Live Execution Design Boundary, or Migration Repair Executable Action Design Boundary.

### CMS Admin Console Foundation Boundary

1. Status: completed.
2. Scope: added the first minimal `apps/admin` Vite React shell with injected API-client component tests, package build/test/typecheck scripts, a frontend admin structural guard, CI wiring, and admin documentation updates.
3. Changed files: `.github/workflows/guards.yml`, `apps/admin/*`, `scripts/checks/frontend_admin_foundation_check.py`, `docs/admin-guide.md`, `docs/admin-guide-cn.md`, `memory-bank/admin-console.md`, `memory-bank/guard-ci.md`, `memory-bank/project-state.md`, `memory-bank/roadmap.md`, and `memory-bank/progress-log.md`.
4. Verification performed: wrote the admin shell tests first and observed RED on the missing `./App` module, then implemented the smallest shell and verified admin tests, typecheck, and build.
5. Result: the admin console now has a minimal tested foundation that renders `Nairi Admin`, loads draft summaries through an injected API client, and shows an API-backed draft preview, and renders a safe loading failure message.
6. Boundary: no direct database access, no live fetch in the shell component, no token persistence, no router, no settings, no media, no publish action, no scheduler, no repair action, no production mutation, and no live database migration execution was added.
7. Risks or blockers: runtime admin API client, auth/token UX, routing, content editing, publication controls, media, settings, deployment hardening, and live external side effects remain deferred.
8. Decision impact: no new ADR; this implements the existing React/Vite admin stack decision.
9. Next recommended named task: CMS Admin Post List API Client Boundary, Cloudflare Live Execution Design Boundary, or Migration Repair Executable Action Design Boundary.

## Progress Rule

`progress-log.md` is append-only historical evidence. It is not the current roadmap and it is not the only authority for durable architecture decisions.

Every completed named task must add a progress entry with:

1. Task name.
2. Completed scope.
3. Changed files.
4. Verification performed.
5. Result.
6. Risks or blockers.
7. Decision impact: added ADR, updated ADR, covered by existing ADR, or no durable decision.
8. Authority-doc impact: which source-of-truth documents changed, or why none changed.
9. Next recommended named task.

If a task creates or changes durable architecture decisions, update `decisions.md` in the same task. If a task completes, defers, splits, or reorders functional work, update `roadmap.md`. If a task changes current capabilities, blockers, or current focus, update `project-state.md`.

## Admin Runtime API Client Boundary

1. Status: merged into the current branch scope.
2. Scope: added a tested runtime `createAdminApiClient` for authenticated draft-list reads via `GET /api/v1/posts?status=draft`, wired from absolute `VITE_API_BASE_URL` in `main.tsx` with an injected token provider and no bundled token, while preserving the injected `AdminApiClient` boundary in `App`.
3. Verification: focused client tests, full admin tests, typecheck, build, and frontend admin foundation guard.
4. Deferred: token persistence, router, create/edit/publish UI, settings, media, scheduler, browser E2E, and production mutation.

## GitHub Actions Node Runtime Hygiene

1. Status: current CI maintenance slice.
2. Scope: updated Guards workflow JavaScript actions to Node-24-ready major refs: `actions/checkout@v6`, `actions/setup-python@v6`, and `actions/setup-node@v6`.
3. Boundary: no Docker/GHCR publishing, deployment behavior, product feature work, or guard semantic changes.
4. Reason: previous Guards runs passed but emitted a Node.js 20 deprecation annotation for older JavaScript action refs even with `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24`.

## Admin Token Provider Boundary

1. Status: completed for fail-closed provider contract.
2. Scope: added `createAdminTokenProvider`, wired it into `main.tsx`, and extended the admin guard/tests so the current provider supplies no credentials, reads no browser-bundled token env, and writes no browser storage.
3. Boundary: no login UI, token persistence, session restoration, refresh/logout, cookie/session auth, or live browser auth smoke.
4. Verification: focused admin token provider tests, full admin tests, admin typecheck/build, and `frontend_admin_foundation_check.py`.

## Admin Module Shell Boundary

1. Status: completed for minimal module navigation shell.
2. Scope: added `Admin modules` navigation with `Content`, `Media`, and `Settings`, default `Content` active state, accessible `aria-current`, and placeholder panels for reserved modules.
3. Boundary: no TanStack Router wiring, no media/settings business logic, no create/edit/publish mutation, no audit/token workflows, and no backend API expansion.
4. Verification: RED module-navigation RTL test, full admin tests, admin typecheck/build, and admin foundation guard.

## Admin Draft Detail Readback Boundary

1. Status: completed for selected-draft detail readback.
2. Scope: extended the injected admin UI client with `getPost(postId)`, added runtime `GET /api/v1/posts/{postId}` support, and rendered content format, revision id, and draft content in the `Content` module.
3. Boundary: summary list remains separate from detail readback; no edit/create/publish mutation, public API reuse, router expansion, token persistence, or direct database access.
4. Verification: RED UI/client tests, full admin tests, admin typecheck/build, and admin foundation guard.

## Admin Draft Detail UX Refinement Boundary

1. Status: completed for selected state and empty-state refinement.
2. Scope: added `aria-pressed` selected draft affordance, selected-item styling, and stable no-drafts/detail-prompt copy.
3. Boundary: preserved the injected API client and existing detail readback only; no edit/create/publish mutation, router expansion, token persistence, or media/settings logic.
4. Verification: RED RTL tests for selected state and empty draft list, full admin tests, admin typecheck/build, and admin foundation guard.

## Admin First Edit Form Boundary

1. Status: completed for first injected draft edit form contract.
2. Scope: added `AdminPostUpdateInput`, `apiClient.updatePost(postId, input)`, editable draft title/content fields, save success/error states, and list/detail refresh after an injected update.
3. Boundary: runtime API PATCH wiring remains deferred; no create/publish mutation, router expansion, token persistence, media/settings logic, direct fetch, or direct database access.
4. Verification: RED RTL tests for update payload and safe update failure, stale edit response regression, focused admin tests/typecheck, and admin foundation guard.

## Admin Runtime PATCH Client Boundary

1. Status: completed for runtime admin PATCH client wiring.
2. Scope: added runtime `PATCH /api/v1/posts/{post_id}` support to `createAdminApiClient.updatePost`, including encoded ids, JSON body, bearer auth, safe failure, optimistic detail mapping, and slug propagation through admin summary/detail/update types.
3. Boundary: no publish/create mutation, router expansion, login UI, token persistence, direct App fetch, or direct database access.
4. Verification: RED admin API client tests for PATCH path/body/auth/failure before implementation, focused admin tests/typecheck, and admin foundation guard.

## Admin Edit Slug Field Boundary

1. Status: completed for editable draft slug field.
2. Scope: added a `Draft slug` input to the admin edit form and verified save payloads use the edited slug through the injected update contract.
3. Boundary: no frontend slug validation, create/publish mutation, router expansion, login UI, token persistence, direct App fetch, or direct database access.
4. Verification: RED RTL test for missing slug field / stale payload, focused admin tests/typecheck, and admin foundation guard.

## Admin Edit Summary Field Boundary

1. Status: completed for editable draft summary field.
2. Scope: added a `Draft summary` input to the admin edit form, propagated summary through admin summary/detail/update types, and verified runtime PATCH bodies include the edited summary.
3. Boundary: no frontend summary validation, taxonomy/tag/series editing, create/publish mutation, router expansion, login UI, token persistence, direct App fetch, or direct database access.
4. Verification: RED RTL test for missing summary field, focused admin tests/typecheck, and admin foundation guard.

## Admin Edit Tags Field Boundary

1. Status: completed for editable draft tags field.
2. Scope: added a `Draft tags` input to the admin edit form, propagated tags through admin summary/detail/update types, and verified runtime PATCH bodies include normalized tags.
3. Boundary: no taxonomy/category/series selector, frontend tag validation, create/publish mutation, router expansion, login UI, token persistence, direct App fetch, or direct database access.
4. Verification: RED RTL test for missing tags field / stale payload, focused admin tests/typecheck, and admin foundation guard.

## Admin Edit Category Field Boundary

1. Status: completed for editable draft category ID field.
2. Scope: added a `Draft category ID` input to the admin edit form, propagated `categoryId` through admin summary/detail/update types, and verified runtime PATCH bodies include normalized category IDs.
3. Boundary: no category selector, taxonomy management UI, create/publish mutation, router expansion, login UI, token persistence, direct App fetch, or direct database access.
4. Verification: RED RTL test for missing category field / stale payload, focused admin tests/typecheck, and admin foundation guard.

## Admin Edit Series Field Boundary

1. Status: completed for editable draft series ID field.
2. Scope: added a `Draft series ID` input to the admin edit form, propagated `seriesId` through admin summary/detail/update types, and verified runtime PATCH bodies include normalized series IDs.
3. Boundary: no series selector, taxonomy/series management UI, create/publish mutation, router expansion, login UI, token persistence, direct App fetch, or direct database access.
4. Verification: RED RTL test for missing series field / stale payload, focused admin tests/typecheck, and admin foundation guard.

## Admin Publish Request Review Boundary

1. Status: completed for the first non-executing admin publish review request affordance.
2. Scope: added a `Request publish review` button to the loaded draft detail form and a local status message tied to the current `revisionId`.
3. Boundary: the button does not call `updatePost`, does not expose a live publish API client method, does not mutate post status, and does not call `POST /api/v1/posts/{post_id}/publish`.
4. Verification: RED RTL test for the missing review-request button, focused admin tests/typecheck, and admin foundation guard.

## Admin Publish Confirmation Contract Boundary

1. Status: completed for the first non-executing admin publish confirmation intent contract.
2. Scope: added a confirmation panel after local publish-review staging, with revision-specific copy and a local confirmation status.
3. Boundary: confirmation intent does not call `updatePost`, does not expose a live publish API client method, does not mutate post status, and does not call `POST /api/v1/posts/{post_id}/publish`.
4. Verification: RED RTL test first failed on the missing confirmation panel/action, then focused admin tests/typecheck passed.

## Admin Publish Runtime Client Boundary

1. Status: completed for the runtime admin publish API client contract.
2. Scope: added `AdminPostPublishInput`, `AdminPostPublishResult`, and `apiClient.publishPost(postId, input)` with authenticated POST wiring to `/api/v1/posts/{post_id}/publish`.
3. Boundary: the client contract is available for future explicit UI wiring only; the current App publish review/confirmation controls remain local and do not call the live publish endpoint.
4. Verification: RED API-client tests first failed on missing `publishPost`, then focused admin client tests/typecheck passed.

## Admin Publish Action UI Boundary

1. Status: completed for local implementation.
2. Scope: connected the existing confirmation flow to the injected `publishPost` contract through a `Publish confirmed draft` button that appears only after confirmation.
3. Tests: RED component tests first failed because the publish action button was absent; independent review then prompted stale-response and mismatched-id regression tests, which failed before request-id/id-match hardening and passed after the fix.
4. Boundary: publish action uses the injected client only; no direct fetch, auth/token persistence, router expansion, scheduling UI, job runner UI, or invalidation UI was added.

## Admin Post-Publish List Behavior Boundary

1. Status: completed for local implementation.
2. Scope: publish success now filters the published post out of the draft review list while keeping the detail pane readback and success status.
3. Tests: extended the publish success component test first, observed RED because the published post still remained in the draft list, then changed the post-list state update from status mapping to removal; a follow-up multi-draft regression test proves other draft buttons remain.
4. Boundary: no new router, live refetch, published list, filters, archive/history UI, or backend/API contract changes were added.

## Admin Published Detail Read-Only Boundary

1. Status: completed for local implementation.
2. Scope: publish success keeps detail readback and publish status while replacing draft edit/review controls with read-only published-detail copy.
3. Tests: extended the publish success component test first, observed RED because `Save draft changes` still rendered after publish, then gated the draft form behind `selectedPostDetail.status === "draft"` and moved publish status/error outside the draft-only form; a direct non-draft detail regression test proves read-only behavior is status-driven outside the publish-success path.
4. Boundary: no published-list navigation, router adoption, live refetch, archive/history UI, or backend/API contract changes were added.

## Admin Published Detail Label Boundary

1. Status: completed for local implementation.
2. Scope: non-draft admin detail readback now uses the stable eyebrow `API-backed published detail` while draft details keep `API-backed draft detail`.
3. Tests: extended the direct non-draft detail regression first, observed RED because the UI still rendered `API-backed draft detail`, then added the smallest status-aware label branch.
4. Boundary: no router, live refetch, published list/history UI, or backend/API contract changes were added.

## Admin List Status Label Boundary

1. Status: completed for local implementation.
2. Scope: mixed-status admin lists now show `Content items`; all-draft lists continue showing `Drafts`.
3. Tests: added a RED React test for a mixed draft/published injected list, then implemented the smallest derived label branch.
4. Boundary: no data-source, router, refetch, published navigation, archive/history UI, filtering, or backend/API contract changes.

## Admin Mixed-Status Detail Loading Copy Boundary

1. Status: completed for local implementation.
2. Scope: mixed-status detail selection loading copy now uses `Loading item detail…`; draft selection loading copy remains `Loading draft detail…`.
3. Tests: added a RED React test with a pending published-detail promise, then implemented the smallest derived loading-copy branch.
4. Boundary: no router, refetch, published navigation, filtering, empty-list behavior, or backend/API contract changes.

## Admin Published Read-Only Copy Hardening Boundary

1. Status: completed for local implementation.
2. Scope: strengthened published/non-draft read-only copy with `Draft editing and publishing controls are hidden for this content item.`
3. Tests: extended the non-draft detail read-only regression to require the explanatory copy while preserving absence of draft workflow controls.
4. Boundary: no router, refetch, published navigation, filtering, draft-control exposure, or backend/API contract changes.

## Admin Draft Workflow Copy Boundary

1. Status: completed for local implementation.
2. Scope: added draft-only form copy `Draft controls only affect the selected draft.` to clarify the selected-draft boundary.
3. Tests: extended the draft detail readback regression to require the copy and paired it with the existing non-draft read-only regression.
4. Boundary: no update/publish API behavior changes, router, refetch, published navigation, filtering, or backend/API contract changes.

## Admin Publish Review Status Scope Boundary

1. Status: completed for local implementation.
2. Scope: added regression coverage proving `Publish review request staged...` and the confirmation panel disappear after selecting another draft.
3. Result: current implementation already cleared review status on selection, so no App behavior change was required.
4. Boundary: test/guard/docs hardening only; no backend persistence, publish API changes, router, refetch, navigation, filtering, or backend/API contract changes.

## Project Health Audit Cadence Boundary

1. Status: completed for project governance documentation.
2. Scope: added `memory-bank/project-audit.md` as the project-health audit cadence and finding-taxonomy authority, linked it from `AGENTS.md` and `memory-bank/guard-ci.md`, and preserved the 2026-06-08 audit report as dated evidence.
3. Boundary: docs/governance only; no project behavior, API contract, admin UI, public frontend, deployment, live side effect, or guard semantic change.
4. Verification: docs guard, i18n doc guard, contract guard, secret guard, `git diff --check`, focused audit-anchor scan, and pending secret-shaped scan.

## Project State and Roadmap Freshness Cleanup

1. Status: completed for docs-only audit remediation.
2. Scope: updated `project-state.md`, `roadmap.md`, and `project-audit.md` so current focus, Cloudflare dry-run state, admin runtime/publish capabilities, admin roadmap status, and active remediation queue match implemented mainline behavior.
3. Boundary: docs-only; no product behavior, API contract, admin UI, public frontend, deployment, live side effect, or guard semantic change.
4. Verification: docs guard, i18n doc guard, contract guard, secret guard, `git diff --check`, targeted stale-wording scan, and pending secret-shaped scan.
