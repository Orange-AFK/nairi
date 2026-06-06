# Nairi

## Roadmap Rule

All roadmap items use named modules and named tasks. Abstract labels such as Step, Phase, and Slice are forbidden.

## Foundation

### Foundational Documentation Completion

1. Complete root project documents.
2. Complete memory-bank English documents.
3. Complete local memory-bank Chinese documents.
4. Complete external docs in English and Chinese.
5. Define guard and CI expectations.
6. Verify document boundaries and Git ignore rules.

### Documentation Guard Development

1. Implement `scripts/guards/docs_guard.py`.
2. Implement `scripts/guards/i18n_doc_guard.py`.
3. Validate root document requirements.
4. Validate bilingual document pairs.
5. Validate forbidden document locations.
6. Validate forbidden planning labels.
7. Status: completed.

### Contract Guard Development

1. Implement `scripts/guards/contract_guard.py`.
2. Implement `scripts/guards/api_schema_guard.py`.
3. Validate API path registration.
4. Validate scope registration.
5. Validate MCP tool mapping.
6. Validate route, environment, job, and audit contracts.
7. Status: completed.

### Secret Guard Development

1. Implement `scripts/guards/secret_guard.py`.
2. Scan tracked and non-ignored untracked files.
3. Block private keys, token patterns, and suspicious secret assignments.
4. Allow placeholder-only example values.
5. Status: completed.

### Guard CI Workflow Development

1. Implement `.github/workflows/guards.yml`.
2. Run docs guard, i18n doc guard, contract guard, API schema guard, and secret guard.
3. Trigger on pull requests and pushes to `main`.
4. Status: completed.

## API Core

### FastAPI Project Scaffold

1. Create FastAPI service structure.
2. Add health endpoint.
3. Add settings loader.
4. Add test harness.
5. Status: completed.

### Authentication and Scope System

1. Define token model.
2. Implement scope checks.
3. Add audit event creation for token actions.
4. Status: completed for the current scaffold boundary; persistent token storage and lifecycle audit remain future database work.

### Article Draft API Development

1. Implement post draft creation.
2. Implement post draft update.
3. Implement revision creation.

### Article Publishing API Development

1. Implement publication state transition.
2. Implement publish job creation.
3. Implement audit events.

## Content System

### MDX Component Registry Development

1. Implement component registry model.
2. Implement policy API.
3. Implement risk scanning foundation.

## Admin Console

### Admin Shell Development

1. Create React/Vite admin shell.
2. Configure routing.
3. Configure API client.

### Article Management Interface Development

1. Implement post list.
2. Implement post editor.
3. Implement revision and publication controls.

## Frontend Site

### Public Site Shell Development

1. Create Next.js public site shell.
2. Configure public routes.
3. Configure API-backed content loading.

## Agent and MCP

### MCP Server Contract Development

1. Define MCP tools.
2. Map tools to API endpoints.
3. Add permission and audit boundaries.

## Deployment

### Docker Compose Contract Development

1. Define compose services.
2. Define environment variables.
3. Validate SQLite and PostgreSQL modes.
