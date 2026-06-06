# 安全策略

## 支持范围

Nairi 目前处于早期 alpha。除非后续引入稳定发布分支，安全修复默认面向 `main` 分支。

## 漏洞报告

请私下报告疑似漏洞。不要为 secrets、鉴权绕过、数据暴露或部署敏感问题创建公开 GitHub issue。

可使用以下路径：

1. 如果仓库启用了 GitHub private security advisory，优先创建私有安全通告。
2. 通过维护者公开 GitHub 主页建立联系；在建立私有通道前，只提供非敏感复现上下文。

## 敏感区域

以下区域应视为高风险 surface：

- API token 解析、scope 检查和 admin 边界。
- Draft、private 和 public content 隔离。
- MCP 与 agent-facing endpoints。
- Audit logs 和 revision history。
- Deployment secrets、environment files、database files、uploads、logs 和 generated artifacts。
- GitHub Actions 权限和 release automation。

## 维护者处理规则

- 不要把 secrets 放入 issue、pull request、commit message 或日志。
- 在隔离的本地环境中复现安全报告。
- 可行时添加 regression tests 或 guard coverage。
- 优先使用小而可 review 的 pull requests 修复。
- 在公开细节前轮换任何已暴露凭据。

## 披露

公开披露应等待修复可用，或等待维护者明确同意披露时间线。
