# Nairi

[English README](./README.md)

## 项目定位

Nairi 是一个 API-first、Agent-first 的 CMS，用于把项目开发经验、工程实践、问题解决思路低摩擦地转化为可审核、可编辑、可发布、可维护的长文内容。

它不是普通博客主题。Nairi 的核心是 API 管控一切：前台、CMS 后台、MCP、Agent、Job 和自动化都必须围绕已文档化的契约运行。

## 核心原则

1. FastAPI 是产品能力唯一权威入口。
2. 前台、后台、MCP、Agent、Job、自动化不能绕过 API 权限、scope、状态机和审计。
3. 公开读者能力使用专用 public API 契约和 public-safe response schema。
4. 契约和架构决策必须先于实现或随实现同步文档化。
5. 文档通过明确事实源职责保持同步，而不是到处复制临时状态。
6. Markdown 是安全基础格式；MDX 是受治理的增强能力，依赖组件注册、权限控制、风险预警、审计和回滚。

## 当前仓库状态

Nairi 处于 early alpha implementation。

已实现的 scaffold 能力包括：

1. FastAPI 服务骨架、settings、health route 和 API tests。
2. Scaffold token-to-scope authentication 与 protected route checks。
3. SQLite-backed article draft create、read、list、update 和 publish transition。
4. Durable publish job bookkeeping。
5. Authenticated published content read/list/filter/pagination。
6. Anonymous public post list/detail APIs，使用 public-safe responses。
7. Minimal safe public `bodyHtml` rendering。
8. Next.js public site routes：home、post list、post detail、RSS、sitemap index 和 posts sitemap。
9. Public frontend route metadata、canonical URLs、route-level revalidation 和 bounded RSS/sitemap traversal。
10. Staged public invalidation bookkeeping，包含 dispatcher configuration 和 inert Cloudflare request-plan boundary。
11. Documentation、contract、schema、secret 和 public-site structural guards in CI。

仍在开发中的能力：

1. CMS admin console implementation。
2. MCP server implementation。
3. SQLAlchemy/Alembic migration layer。
4. Deployment readiness、Docker/Compose runtime hardening 和 image publishing。
5. Live external invalidation execution，包括 real Cloudflare purge wiring。
6. Full governed MDX/component rendering。

## 技术栈

## 前端

### 前台展示站

1. Next.js
2. React
3. TypeScript
4. 当前 public cache policy 使用 route-level revalidation
5. Tailwind CSS 与 shadcn/ui 后续扩展
6. Markdown baseline 与未来 governed MDX rendering

### CMS 管理后台

1. React
2. Vite
3. TypeScript
4. TanStack Router
5. TanStack Query
6. React Hook Form
7. Zod
8. Tailwind CSS
9. shadcn/ui

## 后端

### API 核心

1. FastAPI
2. Pydantic
3. 当前 scaffold persistence 使用 SQLite-backed `PostStore`
4. 目标 migration stack：SQLAlchemy 2.x 和 Alembic
5. SQLite 默认
6. PostgreSQL 在 migration support 存在后作为生产选项

## Agent 接入

### 接口层

1. OpenAPI 作为标准 API 描述。
2. MCP Server 是计划中的 Agent 友好工具层。
3. API Token Scope 控制能力。
4. 敏感操作记录审计日志。

## 文档结构

1. `memory-bank/`：维护者和 Agent 使用的开发记忆。英文文件提交 Git，中文 `*-cn.md` 本地维护但不提交。
2. `docs/`：用户、部署者、协作者文档。英文和中文都提交。
3. 根目录：GitHub 入口、协议、环境变量示例、贡献/安全政策和项目级 Agent 规则。

## 开源协议

MIT
