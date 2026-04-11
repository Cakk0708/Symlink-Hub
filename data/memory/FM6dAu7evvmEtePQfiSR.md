# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此代码库中工作时提供指导。

## 快速导航

以下是详细的项目文档链接。当你需要了解特定方面的信息时，请阅读对应的文档。

### 核心文档

| 文档 | 说明 | 何时阅读 |
|------|------|----------|
| [项目地图](.claude/docs/map.md) | 项目核心地图介绍 | 涉及所有项目相关模块定位路径都必须阅读该文档 |
| [项目概述](.claude/docs/overview.md) | 项目定位、核心功能、业务模块 | 需要了解项目基本情况时 |
| [技术栈](.claude/docs/tech-stack.md) | 框架、工具、平台配置 | 需要了解技术选型时 |
| [开发命令](.claude/docs/development.md) | npm 脚本、构建命令 | 需要运行项目或构建时 |
| [项目架构](.claude/docs/architecture.md) | 目录结构、模块组织 | 需要了解代码组织时 |

### 开发指南

| 文档 | 说明 | 何时阅读 |
|------|------|----------|
| [代码规范](.claude/docs/coding-standards.md) | 命名规范、组件结构、导入顺序 | 编写代码前必读 |
| [API 集成](.claude/docs/api-integration.md) | 请求模式、响应格式、拦截器 | 调用 API 或修改请求逻辑时 |
| [认证](.claude/docs/authentication.md) | Token 管理、认证流程 | 处理登录、权限相关功能时 |
| [移动端适配](.claude/docs/mobile-adaptation.md) | 视口配置、触控交互、性能优化 | 开发移动端特性时 |

### 业务逻辑

| 文档 | 说明 | 何时阅读 |
|------|------|----------|
| [核心业务逻辑](.claude/docs/business-logic.md) | 账户验证、订单状态机、多租户 | 开发业务功能前必读 |
| [错误处理](.claude/docs/error-handling.md) | 错误类型、提示方式、全局处理 | 处理错误或异常时 |
| [路由守卫](.claude/docs/routing.md) | 路由配置、认证检查、导航 | 添加新页面或修改路由时 |
| [测试](.claude/docs/testing.md) | 测试框架、测试建议、命令覆盖 | 编写或运行测试时 |

## 重要说明

- 这是 **H5 移动端** 应用 - 始终在移动设备上测试
- Vant 组件专为移动端设计 - 优先使用而非桌面组件
- 后端所有命令需要 `DJANGO_ENVIRONMENT=dev` 或 `prod`
- 所有 API 响应使用驼峰式命名字段
- 图片和静态资源放在 `src/assets/`

## 相关项目

- **后端 Django API**: `../Duolingo_backend/`
- **PC 前端**: `../Duolingo_frontend/`
- **PRD 文档**: `./PRD.md`
