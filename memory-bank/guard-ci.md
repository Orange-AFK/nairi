# Nairi

## Guard and CI Design

### Goal

Nairi uses automated guards to enforce documentation boundaries, bilingual synchronization, contract consistency, API schema naming, secret safety, and API-first rules. Guards are not optional utilities; they are part of task completion.

## Docs Guard

### Script

1. Path: `scripts/guards/docs_guard.py`
2. CI status: enabled in `.github/workflows/guards.yml`.

### Check Scope

1. `README.md` exists and links to `README-cn.md`.
2. `LICENSE` exists and uses MIT.
3. `AGENTS.md` exists.
4. Root GitHub entry-point docs may include `SECURITY.md`, `SECURITY-cn.md`, `CONTRIBUTING.md`, and `CONTRIBUTING-cn.md`.
5. `docs/*.md` files have matching `docs/*-cn.md` files.
6. Local runs require `memory-bank/*.md` files to have matching local `memory-bank/*-cn.md` files.
7. CI skips local memory-bank Chinese pair existence checks because `memory-bank/*-cn.md` files are intentionally ignored and not pushed.
8. `memory-bank/*-cn.md` files are ignored by `.gitignore`.
9. Root directory must not contain scattered development-state documents.
10. `docs/` must not contain development planning or progress documents.
11. `memory-bank/` must not contain external deployment or user manuals.
12. Documents must not use Step, Phase, or Slice as development-stage headings.

## I18n Doc Guard

### Script

1. Path: `scripts/guards/i18n_doc_guard.py`
2. CI status: enabled in `.github/workflows/guards.yml`.

### Check Scope

1. Every tracked English `docs/*.md` file has a tracked `docs/*-cn.md` pair.
2. Local runs require every English `memory-bank/*.md` file to have a local ignored `memory-bank/*-cn.md` pair; CI skips this because the Chinese memory-bank files are local-only by design.
3. Contract-like tokens inside backticks must appear in both language versions.
4. The guard focuses on contract drift, not prose equality.

## Contract Guard

### Script

1. Path: `scripts/guards/contract_guard.py`
2. CI status: enabled in `.github/workflows/guards.yml`.

### Check Scope

1. API paths must use `/api/v1`.
2. API path, method, and scope must be registered in `api-contract.md`.
3. Scopes must be registered in `contract-index.md`.
4. MCP tools must be registered in `agent-mcp-design.md` and follow `contract-index.md` naming rules.
5. MCP tools must map to API capabilities.
6. Environment variables must match between `.env.example` and `deployment.md`.
7. Audit events referenced by API contracts must be registered in `contract-index.md`.
8. Canonical implemented entities must be registered in `data-model.md`.
9. Parallel APIs for the same product capability are forbidden.
10. API bypass paths are forbidden unless explicitly marked as internal infrastructure in `integration-map.md`.

## API Schema Guard

### Script

1. Path: `scripts/guards/api_schema_guard.py`
2. CI status: enabled in `.github/workflows/guards.yml`.

### Check Scope

1. API paths must use `/api/v1`.
2. Path parameters must use snake_case.
3. Request fields, response fields, and query parameters in `api-contract.md` must use lowerCamelCase unless explicitly allowed.

## Secret Guard

### Script

1. Path: `scripts/guards/secret_guard.py`
2. CI status: enabled in `.github/workflows/guards.yml`.

### Check Scope

1. Scans tracked and non-ignored untracked files.
2. Blocks private keys, GitHub tokens, bearer tokens, likely Cloudflare-style tokens, AWS access keys, and suspicious secret assignments.
3. Allows placeholder-only example values such as `change-me`, `placeholder`, `example`, and `replace-me`.
4. Skips deterministic dependency lockfiles such as `package-lock.json` because package integrity hashes can resemble provider tokens and are verified by the package manager instead.

## Shared Guard Utilities

### Script

1. Path: `scripts/guards/guard_common.py`
2. Purpose: shared path, Git, markdown, and reporting helpers for guard scripts.

## CI Design

### GitHub Actions

1. Workflow path: `.github/workflows/guards.yml`.
2. Runs on pull requests.
3. Runs on pushes to `main`.
4. Uses Python 3.11.
5. Runs docs guard.
6. Runs i18n doc guard.
7. Runs contract guard.
8. Runs API schema guard.
9. Runs secret guard.
10. Runs `scripts/checks/frontend_public_detail_check.py`.
11. Runs `scripts/checks/frontend_public_list_check.py`.
12. Runs `npm ci`, `npm run typecheck`, and `npm run build` under `apps/public-site`.

## Completion Rule

Any development task that affects documents, contracts, public capability, API schema, environment variables, or repository safety must pass the relevant guards. A task is not complete when guards fail.
