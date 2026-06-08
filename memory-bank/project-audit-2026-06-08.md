# Nairi Project Audit Report - 2026-06-08

## Verdict

- Overall: **healthy with minor documentation sync debt**.
- Main SHA: `576ff56f0cc840627ec4204e45ca6c20bc715e99`.
- Local branch state: `main...origin/main` at the same SHA.
- CI state: latest `main` Guards run passed.
- Worktree note: the only untracked path observed during audit is `.hermes/`, created for the local audit plan; no tracked project files were changed by the audit.

## Executive Summary

1. The project has not materially drifted from the accepted architecture: FastAPI remains the product API authority, public APIs are still separated under `/api/v1/public/...`, authenticated management routes remain under `/api/v1/posts...`, and admin work has stayed inside the incremental injected-client/TDD boundary.
2. Automated guards are in good shape. Local guard/test/build verification passed after using the same `PYTHONPATH=scripts/guards` environment that CI uses for structural checks.
3. No blocker or high-risk implementation drift was found.
4. Three documentation issues should be cleaned up before more feature work accumulates:
   - `memory-bank/project-state.md` and its local Chinese companion contain stale branch/current-state wording around Cloudflare dry-run dispatch and admin capabilities.
   - `memory-bank/roadmap.md` still has the older admin roadmap section saying the admin shell is only foundation-level and points to the already-completed `CMS Admin Post List API Client Boundary`; the later Admin Runtime section is current, but the coexistence creates ambiguity.
   - `docs/deployment-compose.md` and `docs/deployment-compose-cn.md` read more concrete than the repository supports: no Dockerfile/Compose files are tracked, while deployment readiness remains deferred.
5. The Chinese local companion roadmap (`memory-bank/roadmap-cn.md`) lags the English roadmap's latest admin completed-list details. This does not affect PR artifacts because it is ignored/local, but it affects local i18n confidence and should be synchronized in a docs remediation slice.

## Scope and Method

### Scope inspected

- Root docs: `README.md`, `README-cn.md`, `CONTRIBUTING.md`, `CONTRIBUTING-cn.md`, `SECURITY.md`, `SECURITY-cn.md`, `AGENTS.md`.
- External docs: `docs/*.md`.
- Project authority docs: tracked `memory-bank/*.md` and local ignored `memory-bank/*-cn.md` companions.
- Implementation surfaces: `services/api`, `apps/public-site`, `apps/admin`, `scripts`, `tests`.
- Guard/CI surfaces: `scripts/guards/*`, `scripts/checks/*`, `.github/workflows/guards.yml`.

### Method

1. Confirmed main baseline and latest CI state.
2. Inventoried docs and code surfaces.
3. Read canonical authority docs first, then compared implementation and guard anchors against those docs.
4. Searched for retired public positioning and overclaiming terms.
5. Checked API, admin, public frontend, migration/deployment, Cloudflare, and guard boundaries.
6. Ran full local verification and hygiene checks.

## Authority Map

- Product/API authority:
  - `services/api/src/nairi_api/main.py`
  - `memory-bank/api-contract.md`
  - `memory-bank/contract-index.md`
  - `docs/api-auth.md`
- Project planning authority:
  - `memory-bank/project-state.md`
  - `memory-bank/roadmap.md`
  - `memory-bank/progress-log.md`
  - `memory-bank/decisions.md`
- Admin authority:
  - `memory-bank/admin-console.md`
  - `docs/admin-guide.md`
  - `apps/admin/src/App.tsx`
  - `apps/admin/src/App.test.tsx`
  - `scripts/checks/frontend_admin_foundation_check.py`
- Public frontend authority:
  - `memory-bank/frontend-design.md`
  - `apps/public-site/**`
  - `scripts/checks/frontend_public_*_check.py`
- Deployment and side-effect authority:
  - `memory-bank/deployment.md`
  - `docs/deployment-compose.md`
  - `memory-bank/decisions.md`
  - `services/api/src/nairi_api/invalidation_dispatch.py`
  - `services/api/tests/test_public_invalidation_dispatcher.py`

## Findings

### Finding 1: Stale current-state wording in `project-state.md`

- Severity: docs sync debt.
- Evidence:
  - `memory-bank/project-state.md:81`: "The Cloudflare adapter distinguishes missing settings from configured dry-run bookkeeping on the feature branch."
  - `memory-bank/project-state.md:103`: "Current shell uses an injected API client in tests and has no live writes, token storage, router, publish action, scheduler, or production mutation."
- Expected authority:
  - Current `main` contains Cloudflare dry-run dispatch implementation and admin publish action wiring.
- Actual state:
  - Cloudflare dry-run dispatch is on `main`, not a feature branch.
  - Admin now has runtime API client methods, update wiring, publish wiring, and a confirmed publish action. It still has no router/token persistence/direct database writes, but the phrase "no ... publish action" is stale.
- Recommendation:
  - Small docs-only remediation slice: update `memory-bank/project-state.md` and local `memory-bank/project-state-cn.md` to reflect current mainline state.
- Suggested verification:
  - `PYTHONPATH=scripts/guards .venv/bin/python scripts/guards/i18n_doc_guard.py`
  - `.venv/bin/python scripts/guards/docs_guard.py`

### Finding 2: Roadmap has two admin sections with conflicting freshness

- Severity: docs sync debt / drift risk if left to accumulate.
- Evidence:
  - `memory-bank/roadmap.md:120-124`: older `CMS Admin Console` section says foundation shell completed and points to `CMS Admin Post List API Client Boundary`.
  - `memory-bank/roadmap.md:146-150`: newer `Admin Runtime API Client Boundary` section correctly says completed through admin publish review status scope boundary and lists recent completed admin work.
- Expected authority:
  - One clear current admin progress pointer should exist, or the older foundation section should explicitly delegate to the newer runtime section.
- Actual state:
  - The latest section is correct, but the earlier section still looks current when read in isolation.
- Recommendation:
  - Docs-only remediation: rewrite the older `CMS Admin Console` subsection as an umbrella/status summary that points to the later Admin Runtime section for current completed work and next candidates.
- Suggested verification:
  - `docs_guard`
  - `i18n_doc_guard`
  - targeted grep for `CMS Admin Post List API Client Boundary` to confirm it is not still presented as current next work.

### Finding 3: Local Chinese roadmap companion lags English admin completed list

- Severity: docs sync debt.
- Evidence:
  - `memory-bank/roadmap-cn.md:147` stops the completed admin list at status-aware `API-backed published detail` labelling.
  - `memory-bank/roadmap.md:149` continues through mixed-status list labelling, mixed-status loading copy, explicit published read-only copy, draft workflow copy, and publish-review status scoping regression coverage.
- Expected authority:
  - Local Chinese companion docs should preserve the same contract meaning as English, even when ignored and not staged.
- Actual state:
  - Local companion lags recent admin slices.
- Recommendation:
  - Sync `memory-bank/roadmap-cn.md` during the docs remediation slice but keep it unstaged unless explicitly requested.
- Suggested verification:
  - `PYTHONPATH=scripts/guards .venv/bin/python scripts/guards/i18n_doc_guard.py`
  - `git status --short --ignored memory-bank` to confirm ignored companion handling.

### Finding 4: Deployment Compose guide overstates deferred deployment surface

- Severity: docs sync debt.
- Evidence:
  - `docs/deployment-compose.md:7`: "This guide will document self-hosted Docker Compose deployment for Nairi."
  - `docs/deployment-compose.md:17-21`: describes PostgreSQL profile mode.
  - `docs/deployment-compose-cn.md:7`: Chinese counterpart describes a Docker Compose deployment guide.
  - No tracked Dockerfile or Compose files were found.
  - `memory-bank/roadmap.md:136-144` says deployment readiness and image publishing are deferred.
- Expected authority:
  - Deployment docs should clearly mark Compose deployment as a deferred contract stub until Docker/Compose runtime files and smoke tests exist.
- Actual state:
  - The guide is short and partially future-tense, but it can still read like a real deployment guide.
- Recommendation:
  - Docs-only remediation: add explicit "deferred/stub" status at the top, clarify no Compose file is currently shipped, and keep variables framed as scaffold/future contract notes.
- Suggested verification:
  - `docs_guard`
  - grep for `Docker Compose Deployment Guide` and `Status: deferred`.

### Finding 5: Guard script invocation nuance should be documented or standardized

- Severity: low guard ergonomics issue.
- Evidence:
  - Running `for check in scripts/checks/*_check.py; do .venv/bin/python "$check"; done` failed on `ModuleNotFoundError: No module named 'guard_common'` for `executable_repair_tooling_design_check.py`.
  - Retrying with `PYTHONPATH=scripts/guards` passed all structural checks.
- Expected authority:
  - CI uses an environment where guard_common imports work; local audit/full-check instructions should match that.
- Actual state:
  - Some prior local commands ran individual checks without `PYTHONPATH`, but the full wildcard loop needs it.
- Recommendation:
  - Update docs/check instructions or add a small wrapper script for running all checks with the correct `PYTHONPATH`.
- Suggested verification:
  - `PYTHONPATH=scripts/guards .venv/bin/python scripts/checks/executable_repair_tooling_design_check.py`

## Non-findings / Healthy Checks

### Public vs management API boundary

- Public routes are present under:
  - `services/api/src/nairi_api/main.py:295` `/api/v1/public/posts`
  - `services/api/src/nairi_api/main.py:308` `/api/v1/public/posts/{slug}`
- Public frontend uses `/api/v1/public/posts` and structural checks reject accidental management-route calls.
- Management routes under `/api/v1/posts...` remain authenticated and are used by the admin runtime client.
- No evidence found that public docs instruct anonymous clients to use authenticated management routes.

### Admin scope

- Admin remains a Vite/React SPA using an injected API boundary in `App.tsx` tests.
- Runtime client methods now match the completed admin roadmap: list/get/update/publish.
- Token provider still fails closed and tests assert it does not read Vite token names or browser storage.
- No router library, published-history module, archive/history UI, filtering UI, or direct database access was found in admin code.

### Cloudflare/live side effects

- Cloudflare adapter builds inert request plans and records `cloudflare_adapter_dry_run` only.
- Tests assert request plans do not expose token/Authorization/Bearer data.
- No `httpx`, `requests`, fetch-based Cloudflare API execution, CDN purge, Next.js `revalidateTag`, or `revalidatePath` side effect was found in the implementation surfaces checked.

### Public frontend

- Public site uses public API routes.
- Public checks cover list/detail/render/metadata/style/cache/canonical/RSS/sitemap boundaries.
- Builds pass.

### Migration/repair tooling

- Migration rehearsal/dry-run and operator handoff checks pass.
- Repair tooling remains dry-run/analysis oriented and policy-bounded.

## Documentation Sync Matrix

- Root public docs: no retired Notion/Obsidian/publishing-bridge framing found in public positioning; root docs currently align with product shape.
- External docs: generally aligned, except Compose deployment guide should be explicitly marked as deferred/stub.
- Memory-bank docs: mostly aligned; `project-state.md` and older admin roadmap subsection need freshness cleanup.
- Chinese tracked docs: root/docs counterparts present.
- Chinese local memory-bank companions: present but ignored/local; at least `roadmap-cn.md` and `project-state-cn.md` need sync with English current state.

## Planning Drift Check

- Current implementation has advanced admin incrementally through the publish-review status scoping regression boundary.
- No major feature drift detected.
- The biggest planning-control issue is document freshness: older roadmap/project-state sections can mislead the next agent into repeating already-completed admin work or thinking publish action is still absent.
- Deferred items still appear deferred in implementation:
  - Docker/Compose runtime.
  - GHCR image publishing.
  - live Cloudflare execution.
  - external invalidation side effects.
  - MCP server.
  - admin router/history/filter modules.

## Guard Coverage Check

Passed local verification:

- `pytest`: 93 passed.
- `docs_guard`: ok.
- `i18n_doc_guard`: ok.
- `contract_guard`: ok.
- `api_schema_guard`: ok.
- `secret_guard`: ok.
- all `scripts/checks/*_check.py`: ok when run with `PYTHONPATH=scripts/guards`.
- public-site typecheck/build: ok.
- admin tests: 42 passed.
- admin typecheck/build: ok.
- `git diff --check`: ok.

Latest main CI:

- Guards passed for `576ff56f0cc840627ec4204e45ca6c20bc715e99`.

## Secret and Artifact Hygiene

- `secret_guard`: ok.
- Tracked runtime artifact scan: `0` matches for `.env`, `node_modules`, `dist`, `.next`, `__pycache__`, `.venv`, uploads, logs.
- Additional token-shaped grep returned 65 lines, all observed as guard patterns or short test bearer fixtures such as `post-reader-token` / `post-writer-token`; no real secret-shaped credential was identified.

## Recommended Remediation Items

### Remediation Item 1: Project State and Roadmap Freshness Cleanup

- Type: docs-only.
- Files:
  - `memory-bank/project-state.md`
  - `memory-bank/roadmap.md`
  - local ignored companions: `memory-bank/project-state-cn.md`, `memory-bank/roadmap-cn.md`
- Goal:
  - Remove stale feature-branch wording.
  - Correct admin current-state wording around publish action/runtime client.
  - Make the older admin roadmap section delegate to the newer completed Admin Runtime section or merge them.
  - Sync Chinese local companions.
- Verification:
  - `docs_guard`
  - `i18n_doc_guard`
  - `contract_guard`
  - staged secret/artifact scan before PR.

### Remediation Item 2: Deployment Compose Stub Clarification

- Type: docs-only.
- Files:
  - `docs/deployment-compose.md`
  - `docs/deployment-compose-cn.md`
  - maybe `memory-bank/deployment.md` if it needs an explicit cross-reference.
- Goal:
  - Mark Compose deployment guide as deferred/stub.
  - State no Dockerfile/Compose runtime is currently shipped.
  - Preserve future contract notes without implying production readiness.
- Verification:
  - `docs_guard`
  - `i18n_doc_guard`
  - grep for Docker/Compose overclaiming.

### Remediation Item 3: Local Check Runner Ergonomics

- Type: docs or tooling.
- Files:
  - Option A: `AGENTS.md` / `memory-bank/guard-ci.md` local command wording.
  - Option B: create `scripts/checks/run_all_checks.py` or similar wrapper.
- Goal:
  - Avoid local `guard_common` import failures when running wildcard structural checks.
- Verification:
  - Run wrapper or documented command from clean shell.

## Commands Run

Evidence files captured under `/tmp/nairi-audit/`:

- `/tmp/nairi-audit/01-baseline.txt`
- `/tmp/nairi-audit/02-doc-inventory.txt`
- `/tmp/nairi-audit/03-doc-readthrough.txt`
- `/tmp/nairi-audit/04-targeted-grep.txt`
- `/tmp/nairi-audit/05-code-inventory.txt`

Key commands included:

```bash
git status --short --branch
git fetch origin main --prune
git rev-parse HEAD
git rev-parse origin/main
git log --oneline -25
gh run list --branch main --limit 10 --json databaseId,workflowName,status,conclusion,headSha,url,createdAt
.venv/bin/python -m pytest -q
.venv/bin/python scripts/guards/docs_guard.py
PYTHONPATH=scripts/guards .venv/bin/python scripts/guards/i18n_doc_guard.py
.venv/bin/python scripts/guards/contract_guard.py
.venv/bin/python scripts/guards/api_schema_guard.py
.venv/bin/python scripts/guards/secret_guard.py
PYTHONPATH=scripts/guards .venv/bin/python scripts/checks/<each_check>.py
npm run typecheck --prefix apps/public-site
npm run build --prefix apps/public-site
npm test --prefix apps/admin -- --no-file-parallelism
npm run typecheck --prefix apps/admin
npm run build --prefix apps/admin
git diff --check
```

## Final Audit State

- No remediation was applied during the audit.
- The audit report itself is an uncommitted tracked-path addition if kept under `memory-bank/`; do not stage/commit it until explicitly approved.
- Recommended next step: run Remediation Item 1 as a very small docs-only PR before continuing admin feature work, because stale project-state/roadmap wording affects future steering accuracy.
