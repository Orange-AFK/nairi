# Nairi

[English README](./README.md)

## 项目定位

Nairi 是一个 API-first、Agent-first 的 CMS，用于把项目开发经验、工程实践、问题解决思路低摩擦地转化为可审核、可编辑、可发布、可维护的长文内容。

它不是普通博客主题。Nairi 的核心是 API 管控一切：前台、CMS 后台、MCP、Agent、Job 和自动化都必须围绕已文档化的契约运行。

## 核心原则

1. FastAPI 是产品能力唯一权威入口。
2. 前台、后台、MCP、Agent、Job、自动化不能绕过 API 权限、scope、状态机和审计。
3. 契约先于实现。
4. 文档必须随开发进度同步更新。
5. Markdown 是安全基础格式；MDX 是受治理的增强能力，依赖组件注册、权限控制、风险预警、审计和回滚。

## 计划技术栈

## 前端

### 前台展示站

1. Next.js
2. React
3. TypeScript
4. Tailwind CSS
5. shadcn/ui
6. Markdown 与受治理 MDX 渲染

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
3. SQLAlchemy 2.x
4. Alembic
5. SQLite 默认
6. PostgreSQL 生产可选

## Agent 接入

### 接口层

1. OpenAPI 作为标准 API 描述。
2. MCP Server 作为 Agent 友好工具层。
3. API Token Scope 控制能力。
4. 敏感操作必须记录审计日志。

## 仓库状态

当前处于基础文档设计阶段。在初始契约、架构、路线和守卫规则确认前，不应实现产品代码。

## 文档结构

1. `memory-bank/`：维护者和 Agent 使用的开发记忆。英文文件提交 Git，中文 `*-cn.md` 本地维护但不提交。
2. `docs/`：用户、部署者、协作者文档。英文和中文都提交。
3. 根目录：GitHub 入口、协议、环境变量示例和项目级 Agent 规则。

## 开源协议

MIT
