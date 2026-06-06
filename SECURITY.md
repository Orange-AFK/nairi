# Security Policy

## Supported scope

Nairi is in early alpha. Security fixes target the `main` branch unless a stable release branch is introduced later.

## Reporting a vulnerability

Please report suspected vulnerabilities privately. Do not open a public GitHub issue for secrets, authentication bypasses, data exposure, or deployment-sensitive findings.

Use one of these paths:

1. Open a private security advisory on GitHub if available for this repository.
2. Contact the maintainer through the public GitHub profile and include only non-sensitive reproduction context until a private channel is established.

## Sensitive areas

Please treat the following as high-risk surfaces:

- API token parsing, scope checks, and admin boundaries.
- Draft, private, and public content separation.
- MCP and agent-facing endpoints.
- Audit logs and revision history.
- Deployment secrets, environment files, database files, uploads, logs, and generated artifacts.
- GitHub Actions permissions and release automation.

## Maintainer handling rules

- Keep secrets out of issues, pull requests, commit messages, and logs.
- Reproduce security reports in an isolated local environment.
- Add regression tests or guard coverage when practical.
- Prefer small, reviewable pull requests for fixes.
- Rotate any exposed credentials before publishing details.

## Disclosure

Public disclosure should wait until a fix is available or the maintainer explicitly agrees on a disclosure timeline.
