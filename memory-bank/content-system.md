# Nairi

## Content Philosophy

### Markdown Baseline

Markdown is the default content format because it is portable, readable, and safer than executable content.

### Governed MDX Enhancement

MDX is supported as an enhanced format, but the system must govern components, permissions, risk, audit, and rollback.

## MDX Governance

### Component Registry

Every MDX component must be registered before use.

Required component metadata:

1. `componentName`
2. `description`
3. `riskLevel`
4. `enabled`
5. `propsSchema`
6. `allowedRoles`
7. `allowedAgentScopes`
8. `requiresReview`

### Risk Levels

1. `low`
2. `medium`
3. `high`
4. `critical`

High risk does not mean forbidden. It means the capability requires explicit governance, warning, review, audit, and recovery controls.

## Publication Workflow

### Content Status

1. `draft`
2. `review`
3. `scheduled`
4. `published`
5. `archived`
6. `failed`

### Review Policy

1. Agent-created drafts should be reviewable before publication.
2. Risky MDX usage should require explicit approval according to configured policy.
3. Human administrators retain final control.

## Agent Risk Explanation

### Required Agent Checks

Before publishing or requesting publication, an agent should explain:

1. MDX components used.
2. Component risk levels.
3. External embeds or links.
4. Possible secret or internal information exposure.
5. Permission or review requirements.

## Revision and Rollback

### Revision Rule

Content updates create revisions. Publication should reference a specific revision to prevent accidental drift.
