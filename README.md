# Symlink-Hub

本仓库用于构建一个本地 AI 配置内容中枢：统一管理 `agent`、`skill`、`rule`、`doc`、`command`，并按项目与 agent 规则分发到目标工程。

当前已补充首版设计文档：

- [PRD](/Users/cakk/Project/Symlink-Hub/docs/v1.0/PRD.md)
- [系统设计](/Users/cakk/Project/Symlink-Hub/docs/v1.0/System-Design.md)
- [实施计划](/Users/cakk/Project/Symlink-Hub/docs/v1.0/Implementation-Plan.md)

建议先按 `docs/v1.0/System-Design.md` 的目录结构初始化 TypeScript CLI 工程，再进入首期开发。

当前仓库已包含第一版 TypeScript CLI 骨架与示例配置，可先运行：

```bash
npm install
npm run dry-run -- backend --agent codex
```
