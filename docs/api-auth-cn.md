# Nairi

## API 鉴权说明

### 作用

本文档说明 Nairi 计划采用的 API 认证和授权模型。

## 认证模型

### 人类管理员访问

1. 人类管理员通过后台登录流程认证。
2. 后台操作根据角色和 scope 检查权限。

### API Token 访问

1. Agent、MCP、Webhook 和自动化使用 API Token。
2. 系统存储 token 哈希，不存储明文 token。
3. Token 必须携带明确 scope。
4. 当前 FastAPI 骨架从 `Authorization` header 接收 bearer token，并检查已配置的 token 到 scope 映射。
5. 持久化 hashed token storage 仍属于后续数据库工作。

## Scope 模型

### 核心 Scope

1. `posts:read`
2. `posts:write`
3. `posts:publish`
4. `media:read`
5. `media:write`
6. `settings:read`
7. `settings:write`
8. `audit:read`
9. `agent:invoke`
10. `admin:all`

## 规则

任何客户端都不能绕过 API 鉴权、scope 检查、状态机和审计日志。

## 当前骨架行为

### 受保护 Route 契约

1. `GET /api/v1/mdx-components` 需要 `settings:read`。
2. 拥有 `admin:all` 的 token 满足该检查。
3. bearer token 缺失时返回 `401`。
4. bearer token 无效时返回 `401`。
5. 有效 token 缺少 `settings:read` 或 `admin:all` 时返回 `403`。
6. Error response 使用 `code`、`message`、`details` 和 `requestId`。
