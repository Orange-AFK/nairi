# Agent Instructions for Nairi

## Project Identity

Nairi is an API-first, agent-first CMS. FastAPI is the single product capability authority. The public site, CMS admin console, MCP server, agents, jobs, and automation must operate through documented API contracts.

## Required Reading Before Any Change

1. `memory-bank/project-state.md`
2. `memory-bank/roadmap.md`
3. `memory-bank/decisions.md`
4. `memory-bank/requirements.md`
5. `memory-bank/architecture.md`
6. `memory-bank/contract-index.md`
7. `memory-bank/api-contract.md`
8. `memory-bank/integration-map.md`
9. The specific design document for the module being changed.

If local Chinese `memory-bank/*-cn.md` files exist, update them together with the English files. Chinese memory-bank files are local-only and must not be pushed.

## Documentation Authority Map

1. `project-state.md`: current status, current focus, latest completed functional boundaries, and blockers.
2. `roadmap.md`: functional module plan and current sequencing.
3. `progress-log.md`: append-only historical evidence only; it is not the current roadmap or the only decision authority.
4. `decisions.md`: durable architecture decisions, owner decisions, and long-lived constraints created during development.
5. `architecture.md`: current system architecture and module responsibility boundaries.
6. `api-contract.md`: API-visible route, request, response, auth, error, and behavior contracts.
7. `data-model.md`: persistence entities, current scaffold persistence boundary, and migration/database support boundaries.
8. `frontend-design.md`: public frontend behavior, rendering, SEO, RSS/sitemap, and public cache policy.
9. `integration-map.md`: allowed integration paths and duplicate capability prevention.
10. `guard-ci.md`: guard and CI behavior, document synchronization rules, and executable check coverage.
11. `project-audit.md`: project-health audit cadence, triggers, finding taxonomy, report locations, and remediation rules.
12. Review files such as `project-review.md` and dated audit reports are historical audit artifacts, not normal active sources of truth.

## Documentation Boundaries

## Root Directory

### Allowed Root Documents

1. `README.md`
2. `README-cn.md`
3. `LICENSE`
4. `AGENTS.md`
5. `SECURITY.md`
6. `SECURITY-cn.md`
7. `CONTRIBUTING.md`
8. `CONTRIBUTING-cn.md`
9. `.env.example`
10. Engineering entry files such as package, compose, or build configuration.

### Forbidden Root Documents

1. `progress.md`
2. `roadmap.md`
3. `design.md`
4. `architecture.md`
5. Any development-state document that belongs in `memory-bank/`.

## memory-bank

### Purpose

Development memory for maintainers and agents.

### Contains

1. Requirements
2. Product design
3. Architecture
4. API contracts
5. Data model
6. Content system design
7. Agent and MCP design
8. Admin console design
9. Frontend design
10. Deployment design
11. Roadmap
12. Progress log
13. Decisions
14. Contract index
15. Integration map
16. Guard and CI design
17. Project-health audit cadence and finding taxonomy
18. Historical review artifacts created by explicit review tasks

### Git Rule

English `memory-bank/*.md` files are tracked. Chinese `memory-bank/*-cn.md` files are maintained locally and ignored by Git.

## docs

### Purpose

External documentation for users, operators, and contributors.

### Contains

1. Deployment guide
2. API authentication guide
3. Admin guide
4. Agent and MCP guide

English and Chinese `docs/*-cn.md` versions are both tracked.

## Document Structure Rule

All project documents must use heading hierarchy and named modules or named tasks.

Allowed style:

```markdown
# Nairi

## Backend

### Article Publishing API

1. Goal
2. Scope
3. Contract
4. Acceptance
5. Verification
```

Forbidden planning labels:

1. Step 1
2. Phase 2
3. Slice 3A
4. Ambiguous milestone labels without product meaning.

Every module and smallest development task must have a specific business name.

## Language Rules

1. `README.md` is English by default and links to `README-cn.md`.
2. Root and `docs/` documents are bilingual where applicable.
3. `memory-bank` English files are tracked; local Chinese `*-cn.md` files are maintained but ignored by Git.
4. Code identifiers, API fields, database fields, route names, comments, and environment variable names must be English.
5. Project document prose may be English or Chinese according to the file language.

## API-First Rule

FastAPI API contracts are the source of truth for product capabilities.

No client may bypass documented API authentication, permission scopes, status transitions, or audit logging.

Public frontend and anonymous-reader APIs must use dedicated public route contracts. Do not make authenticated management routes such as `/api/v1/posts...` conditionally public based on `status=published`, bearer-token absence, or caller type.

This applies to:

1. Public frontend
2. CMS admin console
3. MCP server
4. AI agents
5. Job runner
6. Webhooks
7. GitHub Actions
8. Local automation scripts

Any exception must be documented as internal infrastructure in `memory-bank/integration-map.md` and must explain auth, scope, state, and audit boundaries.

## Contract-First Rule

Before adding, removing, renaming, or changing any of the following, update the relevant contract documents first:

1. API endpoint
2. Request parameter
3. Response field
4. Permission scope
5. MCP tool
6. Frontend route
7. Admin route
8. Database entity
9. Database field
10. Job status
11. Audit event type
12. Docker service
13. Environment variable
14. MDX component
15. Webhook event

Do not invent parallel names or temporary paths during implementation.

## Duplicate Capability Rule

Before adding an API endpoint, MCP tool, admin action, job command, or automation path, check `memory-bank/contract-index.md` and `memory-bank/api-contract.md`.

If an existing capability covers the same product behavior, reuse it or make a documented versioned change. Do not create a second capability path for the same operation.

## Documentation Synchronization Rule

A task is not complete until affected source-of-truth documents agree with the code, tests, contracts, and project state.

Every create, update, delete, rename, or semantic change to a module, API, MCP tool, route, database entity, permission, job, audit event, deployment service, public feature, external side effect, or security boundary must update every affected authority document in the same task.

Update `decisions.md`, or explicitly cite an existing decision, whenever a task changes one of these durable concerns:

1. module boundaries
2. system responsibilities
3. public vs authenticated behavior
4. security or secret-handling policy
5. external side-effect policy
6. cache, CDN, or invalidation policy
7. database or migration policy
8. integration authority or duplicate capability rules
9. roadmap sequencing or future-work split

Update `roadmap.md` when a task completes, defers, splits, removes, or reorders a functional area. Update `project-state.md` when current capabilities, blockers, or next named work change. Update `progress-log.md` after every completed named task.

Update `README.md` and `README-cn.md` only when GitHub-facing positioning, repository state, setup, or public project description changes. Do not churn README for internal-only implementation boundaries.

If the roadmap mentions a feature, the progress log, decisions, and design documents must use the same feature name. If a feature is removed or renamed, stale references must be updated or explicitly marked historical.

## Development Execution Rule

1. Work on one named, verifiable task at a time.
2. Inspect relevant files before editing.
3. State scope, affected files, assumptions, acceptance, and verification before implementation.
4. Avoid speculative abstractions.
5. Do not refactor unrelated code.
6. Every changed line must map to the current named task.
7. Run verification that proves the task.
8. Update all affected documents.
9. Check `memory-bank/project-audit.md` before continuing feature work. If an audit trigger is active, perform the appropriate audit or complete the active audit-remediation queue before starting another feature task.
10. Stop after the named task is complete.

## Project Health Audit Rule

1. `memory-bank/project-audit.md` defines Nairi's lightweight, phase-transition, and high-risk mandatory audit triggers.
2. Audit findings must use the taxonomy in `project-audit.md`: blocker, drift risk, docs sync debt, guard gap, or accepted future work.
3. Blockers and drift risks stop feature work until remediated or explicitly approved by the owner.
4. Audit reports are evidence; active rules and corrected state must be migrated into the relevant source-of-truth document.
5. Do not hide audit remediation inside unrelated feature work. Prefer small docs-only or guard-only remediation tasks when behavior is already correct.

## Security Rule

1. Never commit secrets.
2. Never write real credentials into docs, memory, examples, logs, or chat output.
3. `.env.example` may contain placeholders only.
4. Before pushing, inspect ignored files, staged files, and secret-shaped values.
5. Nairi defaults to pull request workflow. Direct main pushes require explicit authorization or urgent hotfix context.

## Guard Requirement

Guard scripts and CI checks are mandatory project contracts, not optional utilities.

Current guards:

1. `scripts/guards/docs_guard.py`
2. `scripts/guards/contract_guard.py`
3. `scripts/guards/secret_guard.py`
4. `scripts/guards/i18n_doc_guard.py`
5. `scripts/guards/api_schema_guard.py`

A task is not complete when relevant guards fail.
