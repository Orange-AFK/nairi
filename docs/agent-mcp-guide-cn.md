# Nairi

## Agent 与 MCP 使用说明

### 作用

本文档说明 Agent 如何通过 MCP 和 API 支撑的工具接入 Nairi。

## 关系

### API 与 MCP

1. FastAPI 提供产品能力。
2. OpenAPI 描述标准 API 行为。
3. MCP 暴露 Agent 友好工具，并由已文档化 API 支撑。

## 计划工具

### 文章工具

1. `create_article_draft_from_project_summary`
2. `explain_mdx_risks`
3. `publish_article_after_review`

## 规则

MCP 不能创建 API 契约中不存在的产品能力。
