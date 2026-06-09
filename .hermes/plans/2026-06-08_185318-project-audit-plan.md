# Nairi Project Audit Plan

> **For Hermes:** This is an audit-only plan. Do not implement product changes during the audit. Use read-only inspection first; produce findings, evidence, and a proposed remediation backlog. Any actual code/docs fixes should be a separate approved follow-up slice.

**Goal:** Audit the whole Nairi project for planning drift, documentation synchronization gaps, authority-boundary violations, and whether the implementation/docs/guards still match the agreed project constraints.

**Architecture:** Treat the repository as four authority layers: product/code contracts, memory-bank planning docs, external user/operator docs, and automated guards/checks. The audit compares these layers against each other and against recent Git history, then classifies gaps as blockers, drift risks, docs debt, or acceptable future-work items.

**Tech Stack:** FastAPI/Python backend, SQLite persistence, Next.js public site, React/Vite admin SPA, GitHub Actions Guards, project memory-bank docs, bilingual tracked docs plus ignored local Chinese memory-bank companions for i18n guard parity.

---

## Audit Scope

### In scope

1. Repository state and recent merged work on `main`.
2. All tracked project documents:
   - `README.md`, `README-cn.md`
   - `CONTRIBUTING.md`, `CONTRIBUTING-cn.md`
   - `SECURITY.md`, `SECURITY-cn.md`
   - `AGENTS.md`
   - `docs/*.md`
   - `memory-bank/*.md` tracked files
3. Local ignored Chinese companion docs under `memory-bank/*-cn.md` when they affect local i18n guard parity.
4. Automated guard/check scripts and GitHub workflow:
   - `scripts/guards/*`
   - `scripts/checks/*`
   - `.github/workflows/guards.yml`
5. Implementation surfaces that docs claim are current:
   - `apps/api`
   - `apps/public-site`
   - `apps/admin`
   - migration/repair tooling under `scripts/` and tests.
6. Planning and authority constraints:
   - FastAPI is product capability authority.
   - Public content APIs use `/api/v1/public/...` and management APIs remain authenticated.
   - Notion/Obsidian/publishing-bridge framing must not leak into current public positioning.
   - Admin work remains incremental and injected-client/TDD scoped.
   - No hidden expansion into router, live refetch, archive/history, filtering, backend contracts, Docker/GHCR, or live Cloudflare invalidation unless docs and implementation explicitly authorize it.
   - Secrets must not appear in docs, memory, tests, PR bodies, or reports.

### Out of scope

1. No code or docs remediation during this audit.
2. No deploy, Cloudflare, DNS, OCI, production database, or external service mutation.
3. No new PR unless the audit later produces an approved remediation slice.
4. No retention of short-lived PR/commit/run IDs into long-term memory.

---

## Deliverables

1. `memory-bank/project-audit-YYYY-MM-DD.md` or another owner-approved audit report path.
2. A chat summary with:
   - overall health verdict,
   - top drift risks,
   - documentation sync status,
   - guard coverage gaps,
   - recommended next remediation slices.
3. A machine-check appendix with exact commands run and their pass/fail summary.
4. A no-secrets statement based on repo guard plus targeted added/manual scans.

Do not stage, commit, or push the report unless explicitly approved.

---

## Audit Method

### Task 1: Establish clean baseline

**Objective:** Confirm we are auditing `main` with no local changes or unmerged branch residue.

**Files:**
- Read-only: repository root.

**Commands:**

```bash
cd /home/openclaw/.hermes/projects/web/nairi
git status --short --branch
git fetch origin main --prune
git rev-parse HEAD
git rev-parse origin/main
git log --oneline -20
```

**Expected:**
- Branch is `main...origin/main`.
- Local `HEAD` equals `origin/main`.
- Worktree is clean.

**Evidence to capture:**
- Current SHA.
- Last 20 commit subjects.
- Any dirty or ahead/behind state.

---

### Task 2: Inventory authority documents

**Objective:** Build an exact list of project documents and classify each by authority type.

**Files:**
- Root public docs: `README*.md`, `CONTRIBUTING*.md`, `SECURITY*.md`, `AGENTS.md`.
- Operator/user docs: `docs/*.md`.
- Planning/architecture docs: `memory-bank/*.md`.
- Ignored local companions: `memory-bank/*-cn.md` if present.

**Commands:**

```bash
git ls-files | grep -E '(^README|README|^docs/|^memory-bank/|CONTRIBUTING|SECURITY|AGENTS\.md)' | sort
python - <<'PY'
from pathlib import Path
root=Path('/home/openclaw/.hermes/projects/web/nairi')
for group in ['README*.md','CONTRIBUTING*.md','SECURITY*.md','docs/*.md','memory-bank/*.md']:
    print(f'## {group}')
    for p in sorted(root.glob(group)):
        print(p.relative_to(root))
PY
```

**Expected:**
- All core English docs have tracked Chinese counterpart where policy requires it.
- Local ignored companions are visible but not treated as PR artifacts unless explicitly requested.

**Evidence to capture:**
- Document inventory with category labels.
- Missing counterpart candidates.

---

### Task 3: Read canonical planning docs first

**Objective:** Reconstruct the intended project direction before checking code.

**Files to read:**
- `memory-bank/project-state.md`
- `memory-bank/roadmap.md`
- `memory-bank/requirements.md`
- `memory-bank/product-design.md`
- `memory-bank/architecture.md`
- `memory-bank/decisions.md`
- `memory-bank/contract-index.md`
- `memory-bank/api-contract.md`
- `memory-bank/admin-console.md`
- `memory-bank/progress-log.md`
- `memory-bank/project-review.md`

**Checks:**
1. Current focus in `project-state.md` matches most recent completed roadmap/progress entries.
2. `roadmap.md` has exactly one current/next pointer per active area, not conflicting next steps.
3. Completed admin boundaries match the recent commits and tests.
4. Historical `project-review.md` is clearly marked as historical and not accidentally treated as current progress.
5. Deferred items remain deferred unless code/docs moved them forward.

**Evidence to capture:**
- Current stated focus.
- Active/deferred roadmap sections.
- Any stale next-step pointers.

---

### Task 4: Check public positioning for drift

**Objective:** Ensure public docs describe the current product, not retired planning ideas.

**Files:**
- `README.md`, `README-cn.md`
- `CONTRIBUTING.md`, `CONTRIBUTING-cn.md`
- `SECURITY.md`, `SECURITY-cn.md`
- Public operator docs under `docs/`.

**Search commands:**

```bash
git grep -n -E 'Notion|Obsidian|publishing bridge|发布桥|GitHub-as-CMS|GitHub as CMS|bridge|MVP|prototype|temporary|later boundary|deferred|TODO|FIXME' -- '*.md'
```

**Review rule:**
- Mentions of future/deferred work are acceptable in memory-bank planning docs.
- Public docs should avoid retired-framing terms and should not imply unsupported capabilities are live.

**Evidence to capture:**
- Each suspicious hit with verdict: acceptable, stale, misleading, or needs remediation.

---

### Task 5: Verify docs/code contract alignment for API boundaries

**Objective:** Ensure the API docs and code still respect public-vs-management separation.

**Files:**
- `memory-bank/api-contract.md`
- `memory-bank/contract-index.md`
- `docs/api-auth.md`, `docs/api-auth-cn.md`
- `apps/api/**`
- API tests under `tests/**`.

**Commands:**

```bash
git grep -n -E '/api/v1/public|/api/v1/posts|Authorization|Bearer|status=published|public-safe|management' -- memory-bank docs apps tests
.venv/bin/python scripts/guards/contract_guard.py
.venv/bin/python scripts/guards/api_schema_guard.py
```

**Checks:**
1. Public published content uses `/api/v1/public/...` routes.
2. `/api/v1/posts...` remains authenticated management API.
3. Public responses use public-safe schemas and do not expose management-only fields.
4. Docs do not instruct public clients to call authenticated management routes for published content.

**Evidence to capture:**
- Route list and matching docs claims.
- Any drift or ambiguous language.

---

### Task 6: Verify admin roadmap and implementation alignment

**Objective:** Check whether the admin UI has stayed within the incremental plan.

**Files:**
- `memory-bank/admin-console.md`
- `docs/admin-guide.md`, `docs/admin-guide-cn.md`
- `apps/admin/src/App.tsx`
- `apps/admin/src/App.test.tsx`
- `apps/admin/src/adminApiClient.ts`
- `apps/admin/src/adminTokenProvider.ts`
- `scripts/checks/frontend_admin_foundation_check.py`

**Commands:**

```bash
git grep -n -E 'router|Route|live refetch|refetch|archive|history|filter|publish review|Publish confirmed draft|Draft controls|published read-only|Admin modules|createAdminApiClient|createAdminTokenProvider' -- memory-bank docs apps/admin scripts/checks/frontend_admin_foundation_check.py
npm test --prefix apps/admin -- --no-file-parallelism
npm run typecheck --prefix apps/admin
npm run build --prefix apps/admin
.venv/bin/python scripts/checks/frontend_admin_foundation_check.py
```

**Checks:**
1. Admin docs do not claim login/session UI or router behavior if not implemented.
2. Runtime client methods match backend contracts.
3. Recent admin slices are reflected in `memory-bank/admin-console.md`, `progress-log.md`, and `roadmap.md`.
4. Guard anchors cover critical admin boundary copies/tests.
5. Existing next-step recommendation does not contradict roadmap.

**Evidence to capture:**
- Implemented admin capabilities.
- Deferred admin capabilities.
- Any doc mismatch.

---

### Task 7: Verify public-site roadmap and implementation alignment

**Objective:** Confirm public frontend docs and implementation agree.

**Files:**
- `memory-bank/frontend-design.md`
- `docs/deployment-compose.md` if it references public frontend behavior.
- `apps/public-site/**`
- public structural checks under `scripts/checks/frontend_public_*`.

**Commands:**

```bash
git grep -n -E 'Next.js|public site|RSS|sitemap|canonical|revalidation|cache|metadata|bodyHtml|MDX' -- memory-bank docs apps/public-site scripts/checks/frontend_public_*
npm run typecheck --prefix apps/public-site
npm run build --prefix apps/public-site
for check in scripts/checks/frontend_public_*_check.py; do .venv/bin/python "$check"; done
```

**Checks:**
1. Public-site routes match sitemap/RSS/canonical docs.
2. Revalidation/cache claims match constants and structural checks.
3. Docs do not overclaim styling, MDX execution, comments, search, or analytics if absent.

---

### Task 8: Verify backend/data/migration/deployment alignment

**Objective:** Ensure backend, persistence, migration tooling, and deployment docs have not diverged.

**Files:**
- `memory-bank/data-model.md`
- `memory-bank/content-system.md`
- `memory-bank/deployment.md`
- `memory-bank/executable-repair-tooling.md`
- `docs/deployment-compose.md`, `docs/deployment-compose-cn.md`
- `docs/migration-operator-handoff.md`, `docs/migration-operator-handoff-cn.md`
- `apps/api/**`
- `scripts/**migration**`, `scripts/**repair**`.

**Commands:**

```bash
git grep -n -E 'SQLite|migration|schema_migrations|repair|backup|restore|Docker|Compose|GHCR|Cloudflare|dry-run|live execution|dispatch' -- memory-bank docs apps scripts tests
.venv/bin/python -m pytest -q
.venv/bin/python scripts/checks/migration_repair_workflow_check.py
.venv/bin/python scripts/checks/migration_operator_handoff_check.py
.venv/bin/python scripts/checks/executable_repair_tooling_design_check.py
.venv/bin/python scripts/checks/migration_repair_evidence_polish_check.py
```

**Checks:**
1. Docker/GHCR remains deferred unless deploy contracts are actually implemented.
2. Cloudflare invalidation remains dry-run/side-effect-free if docs say so.
3. Migration repair docs match executable tooling and guards.
4. Deployment docs do not claim production readiness beyond current contracts.

---

### Task 9: Bilingual and local companion sync audit

**Objective:** Check English/Chinese docs maintain equivalent contract meaning without accidentally staging ignored companions.

**Files:**
- Tracked `*-cn.md` docs.
- Local ignored `memory-bank/*-cn.md` companions.

**Commands:**

```bash
PYTHONPATH=scripts/guards .venv/bin/python scripts/guards/i18n_doc_guard.py
git status --ignored --short memory-bank | sed -n '1,160p'
python - <<'PY'
from pathlib import Path
root=Path('/home/openclaw/.hermes/projects/web/nairi')
english=[p for p in root.glob('memory-bank/*.md') if not p.name.endswith('-cn.md')]
for p in sorted(english):
    cn=p.with_name(p.stem+'-cn.md')
    print(f'{p.relative_to(root)} -> {cn.relative_to(root)} exists={cn.exists()} tracked={cn.as_posix() in []}')
PY
```

**Checks:**
1. Guard passes locally.
2. Recent English contract tokens are present in corresponding Chinese docs/companions.
3. Ignored companions are not accidentally staged.
4. Differences are acceptable translation differences, not semantic contradictions.

---

### Task 10: Guard and CI coverage audit

**Objective:** Verify automated checks still cover project authority boundaries and current slices.

**Files:**
- `.github/workflows/guards.yml`
- `scripts/guards/*.py`
- `scripts/checks/*.py`
- `memory-bank/guard-ci.md`

**Commands:**

```bash
.venv/bin/python scripts/guards/docs_guard.py
PYTHONPATH=scripts/guards .venv/bin/python scripts/guards/i18n_doc_guard.py
.venv/bin/python scripts/guards/contract_guard.py
.venv/bin/python scripts/guards/api_schema_guard.py
.venv/bin/python scripts/guards/secret_guard.py
for check in scripts/checks/*_check.py; do .venv/bin/python "$check"; done
gh run list --branch main --limit 10 --json databaseId,workflowName,status,conclusion,headSha,url,createdAt
```

**Checks:**
1. Local guard suite matches CI workflow commands.
2. CI workflow uses read-only permissions and expected concurrency.
3. Guard docs explain the current guard set and Node/action maintenance state.
4. No guard is obsolete or checking stale retired text.

---

### Task 11: Secret/privacy and artifact hygiene audit

**Objective:** Ensure no sensitive content or runtime artifacts are in source/docs.

**Commands:**

```bash
.venv/bin/python scripts/guards/secret_guard.py
git ls-files | grep -E '(^|/)(\.env|node_modules|dist|\.next|__pycache__|\.venv|uploads|logs)(/|$)' || true
git grep -n -E 'gh[pousr]_|github_pat_|Bearer [A-Za-z0-9._-]{16,}|TOKEN=|API_KEY=|SECRET=|PASSWORD=' -- . ':!package-lock.json' || true
```

**Checks:**
1. No secrets or token-shaped values in tracked files.
2. Runtime/build artifacts are excluded.
3. Docs do not leak operational private details.

---

### Task 12: Drift classification and remediation backlog

**Objective:** Convert findings into a bounded action list without doing the fixes yet.

**Classification:**

- **Blocker:** implementation violates accepted decision, public/auth boundary, secret safety, or docs materially mislead operators/users.
- **High drift risk:** current direction ambiguous; next-step pointers conflict; guard coverage missing for important boundary.
- **Docs sync debt:** docs lag implementation but not dangerous.
- **Guard gap:** correct docs/code but no automated anchor protects it.
- **Acceptable future work:** planned/deferred item is clearly labelled and not implemented.

**Report format:**

```markdown
## Finding N: <title>

- Severity: blocker | high drift risk | docs sync debt | guard gap | acceptable future work
- Evidence:
  - `path:line` quote or command output summary
- Expected authority:
  - source doc/decision/guard
- Actual state:
  - current code/docs behavior
- Recommendation:
  - smallest safe remediation slice
- Suggested verification:
  - exact commands/tests/guards
```

---

## Full Verification Bundle for Audit

Run after read-only analysis to establish project health:

```bash
cd /home/openclaw/.hermes/projects/web/nairi
.venv/bin/python -m pytest -q
.venv/bin/python scripts/guards/docs_guard.py
PYTHONPATH=scripts/guards .venv/bin/python scripts/guards/i18n_doc_guard.py
.venv/bin/python scripts/guards/contract_guard.py
.venv/bin/python scripts/guards/api_schema_guard.py
.venv/bin/python scripts/guards/secret_guard.py
for check in scripts/checks/*_check.py; do .venv/bin/python "$check"; done
npm run typecheck --prefix apps/public-site
npm run build --prefix apps/public-site
npm test --prefix apps/admin -- --no-file-parallelism
npm run typecheck --prefix apps/admin
npm run build --prefix apps/admin
git diff --check
git status --short --branch
```

Expected: all pass, no worktree mutation except generated ignored artifacts if any; inspect and clean only after confirming they are generated artifacts.

---

## Audit Report Outline

```markdown
# Nairi Project Audit Report - YYYY-MM-DD

## Verdict

- Overall: healthy | minor docs debt | drift risk | blocker
- Main SHA:
- Worktree state:
- CI state:

## Executive Summary

## Scope and Method

## Authority Map

- Product/source-of-truth docs:
- Operator docs:
- Automated guards:
- Implementation surfaces:

## Findings

### Finding 1: ...

## Documentation Sync Matrix

- Root public docs:
- External docs:
- Memory-bank docs:
- Chinese counterparts/local companions:

## Planning Drift Check

- Current roadmap focus:
- Recent completed slices:
- Deferred items still deferred:
- Next-step recommendation consistency:

## Guard Coverage Check

## Secret and Artifact Hygiene

## Recommended Remediation Slices

1. <smallest slice>
2. <next slice>

## Commands Run
```

---

## Initial Observations Already Established

From the pre-plan discovery on `2026-06-08_185318`:

1. Repository was clean on `main...origin/main`.
2. Recent admin commits form a consistent sequence through:
   - `test(admin): scope publish review status to selection`
   - `feat(admin): clarify draft workflow scope`
   - `feat(admin): explain published read-only controls`
   - `feat(admin): clarify mixed detail loading copy`
   - `feat(admin): label mixed content lists`
3. Tracked docs include root public docs, `docs/*.md`, and many `memory-bank/*.md` authority files.
4. `memory-bank/project-review.md` is explicitly historical and says not to update during normal feature development.
5. `memory-bank/roadmap.md` currently says admin foundation is completed through the publish-review status scope boundary, with next candidates including router adoption, richer edit metadata, publish-request persistence, or published-history/list module if product wants it.
6. `memory-bank/guard-ci.md` still contains a current CI maintenance slice note about Node-ready action refs; the audit should verify whether that is still current, stale, or simply historical progress wording.

---

## Stop Conditions

Stop and report immediately if any of these appear:

1. Secret/token-shaped content in tracked files or docs.
2. Public docs instruct use of authenticated management APIs for public published content.
3. A doc claims live deployment/GHCR/Cloudflare behavior that implementation intentionally keeps dry-run/deferred.
4. Worktree becomes dirty during read-only audit in a way that is not an expected generated ignored artifact.
5. Local main diverges from origin/main.

---

## Suggested Next Action After Approval

If approved, execute the audit in this order:

1. Baseline and inventory.
2. Authority-doc readthrough.
3. Targeted drift searches.
4. Code/docs contract alignment checks.
5. Full verification bundle.
6. Draft audit report locally.
7. Report findings and wait for approval before any remediation PR.
