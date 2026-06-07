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

## Progress Rule

Every completed named task must add a progress entry with:

1. Task name.
2. Completed scope.
3. Changed files.
4. Verification performed.
5. Result.
6. Risks or blockers.
7. Next recommended named task.
