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

## Progress Rule

Every completed named task must add a progress entry with:

1. Task name.
2. Completed scope.
3. Changed files.
4. Verification performed.
5. Result.
6. Risks or blockers.
7. Next recommended named task.
