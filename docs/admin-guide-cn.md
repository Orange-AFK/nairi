# Nairi

## CMS 后台使用说明

### 作用

本文档说明人类管理员如何使用 CMS 后台。当前实现是 `apps/admin` 下的最小 foundation shell。

## 计划区域

### 内容管理

1. 文章
2. 页面
3. 草稿
4. 修订历史
5. 发布控制

### 治理能力

1. MDX 组件注册
2. Agent 任务审核
3. API Token 管理
4. 审计日志
5. 站点设置

## API 规则

后台只使用已文档化 API，不绕过 API 权限，也不直接写数据库。

## Current Foundation

1. 当前 admin shell 是 `apps/admin` 下的 Vite React app。
2. 它渲染 `Nairi Admin` workspace，并通过 injected API client boundary 加载 draft summaries。
3. 它不执行 live writes、direct database access、token management、publication、scheduling、repair actions 或 production mutation。
4. 后续 admin modules 仍必须只使用 documented API contracts。
