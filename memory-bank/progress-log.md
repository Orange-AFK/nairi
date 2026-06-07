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
7. Next recommended named task: Article Draft Published Public Read Policy Boundary.

## Progress Rule

Every completed named task must add a progress entry with:

1. Task name.
2. Completed scope.
3. Changed files.
4. Verification performed.
5. Result.
6. Risks or blockers.
7. Next recommended named task.
