# CLAUDE.md

## 项目概述
基于 Django 5.1.1 的项目管理系统（PMS）后端，Python 3.10。
集成飞书开放平台，用于项目管理、审批流程、消息通知。

**技术栈：** Django 5.1.1 · DRF · MySQL 9.0 · Celery + Redis · Daphne · 飞书开放平台

## 开始任何任务前
1. 阅读 `.claude/docs/map.md` — 项目模块全景、架构设计、依赖关系
2. 阅读对应规范（见下方）
3. 涉及 `apps/project` 模块内容均不修改，该模块内容已经废弃待删除

## 开发规范
- 视图开发：@.claude/rules/views/
- 序列化器：@.claude/rules/serializers/
- 通用规范（每次必须遵守）：
  - @.claude/rules/naming-conventions.md
  - @.claude/rules/migrates.md
  - @.claude/rules/code-style.md
  - @.claude/rules/comment-standards.md

## 文档索引
- 架构 & 模块地图：`.claude/docs/map.md`
- 模块说明列表：`.claude/docs/modules`
- 接口文档列表：`.claude/docs/api`

## 关键约定（高频，必须记住）
- 自定义用户模型：`AUTH_USER_MODEL = 'SM.User'`
- 禁止直接访问 `user.open_id`，使用 `get_user_feishu_open_id(user)`
- 时区：`Asia/Shanghai`，数据库驱动：PyMySQL
- 环境切换：`export DJANGO_ENVIRONMENT=dev`

## 数据模型关系

- 设计到多模块之间构建关系理解关系时必须阅读该文件
- 介绍有交互模块之间关系

文件路径:
绝对路径：@.claude/docs/data-relationship.md
相对路径：.data-relationship.md

## 数据流

系统核心数据流程，包括消息发送、状态更新等关键业务流程。

**主要流程：**
- **消息发送流程（异步）** - 使用 Celery 异步任务发送飞书消息，包含信号处理、安全判断、错误重试等机制
- **项目状态更新流程** - 使用验证器模式处理项目状态变更，确保状态转换合法性和权限控制

文件路径:
绝对路径：@.claude/docs/data-flow.md
相对路径：.data-flow.md

参考说明：
- 当涉及 Celery 推送飞书消息构造时必须阅读数据流参考文件
- 当涉及验证器模式时必须阅读数据流参考文件
