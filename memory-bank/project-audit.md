# Nairi

## Project Health Audit Cadence

### Purpose

1. Project audits are regular development control points, not exceptional cleanup.
2. Audits protect Nairi from roadmap drift, stale source-of-truth documents, missing guard coverage, public-doc overclaiming, and accidental scope expansion.
3. Audits classify findings before remediation so feature work does not hide project-health fixes.
4. Audits do not authorize product behavior changes by themselves.

## Audit Authority

### Source Documents

1. `project-audit.md` defines the audit cadence, triggers, finding taxonomy, report locations, and remediation rules.
2. Point-in-time reports such as `project-audit-YYYY-MM-DD.md` are audit evidence.
3. Audit reports become active project rules only after their findings are migrated into the relevant source-of-truth document.
4. `project-state.md`, `roadmap.md`, `decisions.md`, `guard-ci.md`, and module design documents remain the active planning and contract authorities.

### Report Locations

1. General project reports use `memory-bank/project-audit-YYYY-MM-DD.md`.
2. Focused reports may use `memory-bank/<module>-audit-YYYY-MM-DD.md` when the audit concerns one subsystem.
3. Reports must avoid secrets, credentials, raw noisy logs, and short-lived implementation trivia.
4. Reports should summarize evidence paths, commands, conclusions, and recommended remediation items.

## Audit Levels

### Lightweight Audit

Run a lightweight audit when any of these triggers occur:

1. Several small verified work items have landed without a project-health check.
2. Multiple tasks have changed the same subsystem or source-of-truth document.
3. `project-state.md`, `roadmap.md`, `guard-ci.md`, or `decisions.md` changes in a way that can affect future sequencing.
4. A guard, structural check, or CI workflow is added or materially changed.
5. The next feature direction is ambiguous or several candidates are listed.
6. A user or agent notices inconsistent current-state, roadmap, or progress wording.

A lightweight audit checks:

1. Current state, roadmap, progress, decisions, and relevant module docs agree.
2. Recent completed work is represented in the right authority documents.
3. Public/user docs do not claim unimplemented capability.
4. Guards and tests still cover the boundary that recent work depends on.
5. Deferred work remains clearly deferred.
6. Secret and runtime-artifact hygiene remains clean.

### Phase-Transition Audit

Run a phase-transition audit before moving into a new subsystem, deployment mode, integration surface, or user-facing capability group.

A phase-transition audit checks:

1. The previous subsystem has current source-of-truth docs and passing guards.
2. The next subsystem has explicit goals, non-goals, prerequisites, and verification boundaries.
3. Deferred concerns from the previous subsystem are not being smuggled into the next one.
4. New contracts, guards, or operator docs needed by the next subsystem are identified before feature implementation.
5. Next-step pointers in `project-state.md` and `roadmap.md` agree.

### High-Risk Mandatory Audit

Run a high-risk audit before any task involving:

1. External side effects, including provider API calls, CDN purge, webhooks, or publish-triggered live execution.
2. Production deployment, Docker/Compose runtime changes, image publishing, or infrastructure routing.
3. Authentication, session persistence, token storage, secret handling, or permission-scope changes.
4. Data migration execution, repair execution, destructive cleanup, restore, reset, or irreversible mutation.
5. Public API contract changes, public data exposure changes, or anonymous access changes.
6. Privileged automation, MCP mutation tools, job runners, schedulers, or agent-executed write paths.

A high-risk audit must document:

1. Owner-approved scope and non-goals.
2. Preconditions and stop conditions.
3. Secret-handling and log-safety expectations.
4. Rollback or recovery path where applicable.
5. Required tests, guards, smoke tests, readbacks, and operator documentation.
6. Side effects that remain explicitly forbidden in the current task.

## Finding Taxonomy

### Blocker

A blocker is a security, privacy, data-loss, destructive-action, public-contract, credential, or external-side-effect risk.

Required handling:

1. Stop feature work.
2. Remediate or get explicit owner approval for a bounded exception.
3. Re-run relevant verification before continuing.

### Drift Risk

A drift risk is a disagreement among implementation, roadmap, project-state, docs, guards, or next-step pointers that can steer future work wrong.

Required handling:

1. Prefer a small remediation task before new feature work.
2. Update the active source-of-truth documents rather than relying on the audit report alone.
3. Verify that stale wording no longer appears as an active instruction.

### Docs Sync Debt

Docs sync debt is stale, incomplete, or overclaiming documentation that does not currently make product behavior unsafe.

Required handling:

1. Track as a docs-only remediation item.
2. Avoid mixing with product behavior changes unless the owner explicitly requests a combined task.
3. Re-run docs, i18n, contract, and secret guards as applicable.

### Guard Gap

A guard gap means the current behavior or boundary is correct but not protected by tests, structural checks, CI, or review gates.

Required handling:

1. Add a guard or test when the boundary is durable and likely to regress.
2. If automation is not practical, document the manual review gate in `guard-ci.md` or the relevant module doc.

### Accepted Future Work

Accepted future work is explicitly deferred capability that remains correctly labelled and does not require remediation.

Required handling:

1. Keep it out of current implementation scope.
2. Preserve clear prerequisites and boundaries.
3. Do not treat it as a defect unless current docs imply it is already implemented.

## Remediation Rules

1. Do not hide audit remediation inside unrelated feature work.
2. Prefer one small remediation item at a time.
3. Use docs-only remediation when the implementation is already correct and only source-of-truth documents drifted.
4. Use guard-only remediation when the missing protection is the main issue.
5. Product behavior changes require a named implementation task with explicit acceptance and verification.
6. Local Chinese `memory-bank/*-cn.md` companions must be synchronized when local guards require them, but they are not pushed unless explicitly requested.
7. After remediation, update `project-state.md`, `roadmap.md`, `progress-log.md`, `decisions.md`, or `guard-ci.md` only when their authority role is affected.

## Current Audit State

### Last Audit

1. Date: 2026-06-08.
2. Report: `memory-bank/project-audit-2026-06-08.md`.
3. Result: no blocker or high-risk implementation drift was found.
4. Active remediation queue: project health audit cadence, project-state and roadmap freshness cleanup, deployment Compose stub clarification, and local check-runner ergonomics.

### Next Audit Trigger

Run the next lightweight audit after the active audit-remediation queue is completed or before the project resumes feature work that crosses into a new subsystem or high-risk boundary.
