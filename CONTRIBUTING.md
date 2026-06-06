# Contributing to Nairi

Nairi is an early-stage, API-first CMS for agent-assisted knowledge publishing. Contributions should preserve the project boundaries: the API is the product authority, public docs describe current behavior, and internal planning belongs in `memory-bank/`.

## Development workflow

1. Create a branch from `main`.
2. Keep changes small and reviewable.
3. Use pull requests for repository changes.
4. Wait for required GitHub Actions checks before merge.
5. Prefer squash merge and delete merged branches.

Direct pushes to `main` are reserved for explicitly approved emergency maintenance.

## Local verification

Before opening a PR, run the relevant checks:

```bash
/home/openclaw/.hermes/projects/web/nairi/.venv/bin/python -m pytest -q
python3 scripts/guards/docs_guard.py
python3 scripts/guards/i18n_doc_guard.py
python3 scripts/guards/contract_guard.py
python3 scripts/guards/api_schema_guard.py
python3 scripts/guards/secret_guard.py
```

For a fresh clone, create a project-local virtual environment first and install the package with development dependencies:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
```

## Documentation rules

- Root documentation is limited to GitHub entry-point files such as `README.md`, `README-cn.md`, `AGENTS.md`, `LICENSE`, `SECURITY.md`, and `CONTRIBUTING.md`.
- Operational and user-facing docs belong in `docs/`.
- Planning, architecture, progress, and contract notes belong in `memory-bank/`.
- English public docs should have Chinese pairs when required by the guards.
- Local Chinese memory-bank companion files are intentionally ignored and are not pushed.
- Do not use abstract Step, Phase, or Slice headings in project docs.

## Security and secrets

- Never commit `.env`, virtual environments, caches, generated uploads, logs, databases, build outputs, or private keys.
- Do not paste tokens into issues, PRs, commit messages, CI logs, or docs.
- Run the secret guard before pushing.
- Report vulnerabilities through the private process described in `SECURITY.md`.

## Pull request checklist

- [ ] The change is intentionally scoped.
- [ ] Tests or guards were updated when behavior changed.
- [ ] Local verification passed.
- [ ] Public docs avoid internal planning history and retired positioning.
- [ ] No secrets or runtime artifacts are included.
