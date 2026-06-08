# Nairi

## Guard and CI Design

### Goal

Nairi uses automated guards to enforce documentation boundaries, bilingual synchronization, contract consistency, API schema naming, secret safety, and selected public-site structural rules. Guards are not optional utilities; they are part of the project contract.

## Source-of-Truth Roles

1. `project-state.md`: current status, current focus, latest completed functional boundaries, and blockers.
2. `roadmap.md`: current functional roadmap and sequencing.
3. `progress-log.md`: append-only historical evidence, not roadmap authority.
4. `decisions.md`: durable architecture decisions and long-lived constraints.
5. `architecture.md`: current module/system responsibility boundaries.
6. `api-contract.md`: API-visible contracts and behavior.
7. `data-model.md`: persistence and migration boundaries.
8. `frontend-design.md`: public frontend behavior, SEO, RSS/sitemap, rendering, and cache policy.
9. `integration-map.md`: allowed integration paths and duplicate capability prevention.
10. `project-review.md`: historical audit artifact only, not a normally updated source of truth.

## Documentation Update Triggers

1. Update `decisions.md` when a task changes durable architecture, module boundaries, public/auth behavior, security/secret handling, side-effect policy, cache/invalidation behavior, database/migration policy, integration authority, duplicate capability rules, or roadmap sequencing assumptions.
2. Update `roadmap.md` when a task completes, defers, splits, removes, or reorders a functional area.
3. Update `project-state.md` when current capabilities, current focus, blockers, or next named work change.
4. Update `progress-log.md` after every completed named task.
5. Update `README.md` only when GitHub-facing positioning, repository state, setup, or public project description changes.
6. Update local Chinese `memory-bank/*-cn.md` companions when local guards require them, but do not push them.

## Docs Guard

### Script

1. Path: `scripts/guards/docs_guard.py`
2. CI status: enabled in `.github/workflows/guards.yml`.

### Check Scope

1. `README.md` exists and links to `README-cn.md`.
2. `README-cn.md` exists.
3. `LICENSE` exists and uses MIT.
4. `docs/` and `memory-bank/` directories exist.
5. `docs/*.md` files have matching `docs/*-cn.md` files.
6. Local runs require `memory-bank/*.md` files to have matching local `memory-bank/*-cn.md` files.
7. CI skips local memory-bank Chinese pair existence checks because `memory-bank/*-cn.md` files are intentionally ignored and not pushed.
8. `memory-bank/*-cn.md` files are ignored by `.gitignore`.
9. Root development documents are forbidden.
10. `docs/` must not contain development planning or progress documents.
11. `memory-bank/` must not contain external deployment or user manuals.
12. Abstract `Step`, `Phase`, and `Slice` headings are forbidden.

### Known Limits

1. The docs guard enforces document placement and naming boundaries, not semantic freshness.
2. It does not prove `roadmap.md`, `project-state.md`, or `decisions.md` are up to date.

## I18n Doc Guard

### Script

1. Path: `scripts/guards/i18n_doc_guard.py`
2. CI status: enabled in `.github/workflows/guards.yml`.

### Check Scope

1. Every tracked English `docs/*.md` file has a tracked `docs/*-cn.md` pair.
2. Local runs require every English `memory-bank/*.md` file to have a local ignored `memory-bank/*-cn.md` pair; CI skips this because the Chinese memory-bank files are local-only by design.
3. English and Chinese pairs preserve matching contract-like backtick tokens.
4. The guard focuses on contract drift, not prose equality.

## Contract Guard

### Script

1. Path: `scripts/guards/contract_guard.py`
2. CI status: enabled in `.github/workflows/guards.yml`.

### Check Scope

1. API version prefixes must be declared in `contract-index.md`.
2. Permission scopes must be declared in `contract-index.md`.
3. API paths must be documented in `api-contract.md`.
4. MCP tools must be registered in `agent-mcp-design.md` and follow `contract-index.md` naming rules.
5. MCP tools must map to API capabilities.
6. Docker service names must be documented.
7. Environment variables must use `NAIRI_` prefix.
8. Audit event types must use canonical names.
9. Parallel APIs for the same product capability are forbidden.
10. API bypass paths are forbidden unless explicitly marked as internal infrastructure in `integration-map.md`.

## API Schema Guard

### Script

1. Path: `scripts/guards/api_schema_guard.py`
2. CI status: enabled in `.github/workflows/guards.yml`.

### Check Scope

1. Request fields, response fields, and query parameters in `api-contract.md` must use lowerCamelCase unless explicitly allowed.
2. Internal Python and database names may remain snake_case.

## Secret Guard

### Script

1. Path: `scripts/guards/secret_guard.py`
2. CI status: enabled in `.github/workflows/guards.yml`.

### Check Scope

1. Scans tracked files and non-ignored untracked files.
2. Blocks private keys, GitHub tokens, bearer tokens, likely Cloudflare-style tokens, AWS access keys, and suspicious secret assignments.
3. Allows documented placeholder values.

## Migration Repair Workflow Check

### Script

1. Path: `scripts/checks/migration_repair_workflow_check.py`
2. CI status: enabled in `.github/workflows/guards.yml`.

### Check Scope

1. Requires source-of-truth anchors for rehearsal JSON inspection.
2. Requires source/backup/rehearsal path comparison guidance.
3. Requires counts, `schema_migrations` rows, readback IDs, `migration_name_mismatch`, and manual intervention guidance.
4. Requires no-automatic-repair and no-live/production-database-mutation boundaries.
5. Requires project-state to advance beyond a completed Broader Migration Repair Workflow Boundary.

### Known Limits

1. The check verifies documentation anchors, not live database state.
2. It does not execute repair tooling, create migrations, or authorize production database mutation.

## Shared Guard Utilities

### Script

1. Path: `scripts/guards/guard_common.py`
2. Purpose: shared path, Git, markdown, and reporting helpers for guard scripts.

## CI Design

### GitHub Actions

1. Workflow path: `.github/workflows/guards.yml`.
2. Trigger: pull requests and pushes to `main`.
3. Uses read-only repository permissions.
4. Uses Python 3.11.
5. Runs docs guard.
6. Runs i18n doc guard.
7. Runs contract guard.
8. Runs API schema guard.
9. Runs secret guard.
10. Runs `scripts/checks/migration_repair_workflow_check.py`.
11. Runs `scripts/checks/frontend_public_detail_check.py`.
12. Runs `scripts/checks/frontend_public_list_check.py`.
13. Runs `scripts/checks/frontend_public_style_check.py`.
14. Runs `scripts/checks/frontend_public_metadata_check.py`.
15. Runs `scripts/checks/frontend_public_canonical_check.py`.
16. Runs `scripts/checks/frontend_public_render_check.py`.
17. Runs `scripts/checks/frontend_public_cache_check.py`.
18. Runs `scripts/checks/frontend_public_sitemap_check.py`.
19. Runs `scripts/checks/frontend_public_rss_check.py`.
20. Runs `npm ci`, `npm run typecheck`, and `npm run build` under `apps/public-site`.
21. Does not publish container images yet.
22. Uses concurrency cancellation so superseded Guards runs on the same ref are cancelled.
23. Forces JavaScript actions to run on Node.js 24.

## Completion Rule

Any development task that affects documents, contracts, public capability, API schema, environment variables, security, source-of-truth roles, or repository safety must pass the relevant guards. A task is not complete when relevant guards fail.
