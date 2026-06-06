# 参与 Nairi 贡献

Nairi 是一个早期 API-first CMS，用于 agent-assisted knowledge publishing。贡献应保持项目边界：API 是产品权威，public docs 描述当前行为，内部规划属于 `memory-bank/`。

## 开发流程

1. 从 `main` 创建分支。
2. 保持变更小而可 review。
3. 仓库变更通过 pull request 提交。
4. 等待必需 GitHub Actions checks 通过后再合并。
5. 优先 squash merge，并删除已合并分支。

Direct pushes to `main` 仅保留给明确授权的紧急维护。

## 本地验证

打开 PR 前，运行相关检查：

```bash
/home/openclaw/.hermes/projects/web/nairi/.venv/bin/python -m pytest -q
python3 scripts/guards/docs_guard.py
python3 scripts/guards/i18n_doc_guard.py
python3 scripts/guards/contract_guard.py
python3 scripts/guards/api_schema_guard.py
python3 scripts/guards/secret_guard.py
```

Fresh clone 时，先创建项目本地 virtual environment 并安装 development dependencies：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
```

## 文档规则

- Root documentation 限于 GitHub entry-point files，例如 `README.md`、`README-cn.md`、`AGENTS.md`、`LICENSE`、`SECURITY.md` 和 `CONTRIBUTING.md`。
- Operational 和 user-facing docs 属于 `docs/`。
- Planning、architecture、progress 和 contract notes 属于 `memory-bank/`。
- English public docs 需要按 guards 要求提供中文配对。
- Local Chinese memory-bank companion files 按设计被 ignored，不会 push。
- Project docs 不使用抽象的 Step、Phase 或 Slice headings。

## 安全与 secrets

- 不要提交 `.env`、virtual environments、caches、generated uploads、logs、databases、build outputs 或 private keys。
- 不要把 tokens 粘贴到 issues、PRs、commit messages、CI logs 或 docs。
- Push 前运行 secret guard。
- 漏洞通过 `SECURITY.md` 描述的私有流程报告。

## Pull request checklist

- [ ] 变更范围明确。
- [ ] 行为变化时同步更新 tests 或 guards。
- [ ] 本地验证已通过。
- [ ] Public docs 避免内部规划历史和已废弃定位。
- [ ] 没有包含 secrets 或 runtime artifacts。
