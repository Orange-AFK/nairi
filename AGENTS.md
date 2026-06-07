# Agent Instructions for Nairi

## Project Identity

Nairi is an API-first, agent-first CMS. FastAPI is the single product capability authority. The public site, CMS admin console, MCP server, agents, jobs, and automation must operate through documented API contracts.

## Required Reading Before Any Change

1. `memory-bank/project-state.md`
2. `memory-bank/requirements.md`
3. `memory-bank/architecture.md`
4. `memory-bank/contract-index.md`
5. `memory-bank/api-contract.md`
6. `memory-bank/integration-map.md`
7. The specific design document for the module being changed.

If local Chinese `memory-bank/*-cn.md` files exist, update them together with the English files. Chinese memory-bank files are local-only and must not be pushed.

## Documentation Boundaries

## Root Directory

### Allowed Root Documents

1. `README.md`
2. `README-cn.md`
3. `LICENSE`
4. `AGENTS.md`
5. `.env.example`
6. Engineering entry files such as package, compose, or build configuration.

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

A task is not complete until code, contracts, bilingual documents, README, roadmap, project state, and progress log agree.

Every create, update, delete, rename, or semantic change to a module, API, MCP tool, route, database entity, permission, job, audit event, deployment service, or public feature must update every affected document in the same task.

If the roadmap mentions a feature, the progress log and design documents must use the same feature name. If a feature is removed or renamed, stale references must be updated or explicitly marked historical.

## Development Execution Rule

1. Work on one named, verifiable task at a time.
2. Inspect relevant files before editing.
3. State scope, affected files, assumptions, acceptance, and verification before implementation.
4. Avoid speculative abstractions.
5. Do not refactor unrelated code.
6. Every changed line must map to the current named task.
7. Run verification that proves the task.
8. Update all affected documents.
9. Stop after the named task is complete.

## Security Rule

1. Never commit secrets.
2. Never write real credentials into docs, memory, examples, logs, or chat output.
3. `.env.example` may contain placeholders only.
4. Before pushing, inspect ignored files, staged files, and secret-shaped values.
5. Nairi defaults to pull request workflow. Direct main pushes require explicit authorization or urgent hotfix context.

## Guard Requirement

The project must include guard scripts and CI checks for documentation and contract consistency before product code work begins.

Planned guards:

1. `scripts/guards/docs_guard.py`
2. `scripts/guards/contract_guard.py`
3. `scripts/guards/secret_guard.py`
4. `scripts/guards/i18n_doc_guard.py`
5. `scripts/guards/api_schema_guard.py`

A task is not complete when relevant guards fail.
