# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 工作区概述

这是一个 **Claude 配置工作区**，用于集中管理多个项目的 Claude Code 配置文件（CLAUDE.md、.claude skills、.vscode settings 等），然后通过软连接（symlink）同步到实际的项目目录。

### 工作区结构

```
Claude/
├── Projects/                    # 项目配置目录
│   ├── mom_backend/            # MOM 后端项目配置
│   ├── pms_backend/            # PMS 后端项目配置
│   ├── pms_frontend/           # PMS 前端项目配置
│   └── pms-admin_frontend/     # PMS 管理后台前端项目配置
├── Features/                    # 共享特性和规则
│   ├── rule_backend/           # 后端代码规范（命名、注释、风格等）
│   └── skill_backend/          # Claude Skill 模板
├── Scripts/                     # 实用脚本
│   └── update_link.py          # 更新软连接脚本
└── README.md                    # 工作区使用说明
```

---

## 软连接机制

每个项目的配置文件通过软连接同步到实际项目目录：

```bash
# CLAUDE.md
ln -s "/Users/.../Claude/Projects/pms_backend/CLAUDE.md" "/path/to/pms_backend/CLAUDE.md"

# .claude 目录
ln -s "/Users/.../Claude/Projects/pms_backend/.claude" "/path/to/pms_backend/.claude"

# .vscode 目录
ln -s "/Users/.../Claude/Projects/pms_backend/.vscode" "/path/to/pms_backend/.vscode"

# .mcp.json
ln -s "/Users/.../Claude/Projects/pms_backend/.mcp.json" "/path/to/pms_backend/.mcp.json"

# skills（共享）
ln -s "/Users/.../Claude/skills" "/path/to/pms_backend/.claude/skills"

# rules（共享）
ln -s "/Users/.../Claude/Features/rule_backend" "/path/to/pms_backend/.claude/rules"
```

---

## 共享后端代码规范

`Features/rule_backend/` 目录包含适用于所有 Django 后端项目的代码规范：

| 文件 | 说明 |
|------|------|
| `naming-conventions.md` | 模型命名规范（单数 PascalCase、表名格式、REST URL kebab-case） |
| `code-style.md` | 代码格式规范（79 字符行宽、空行分隔、类名规范） |
| `comment-standards.md` | 三级注释体系（模块/类函数/局部） |
| `migrations.md` | Django 迁移文件保护规则（禁止修改已有迁移） |
| `views/` | 视图相关规范（list-view、detail-view、naming） |
| `serializers/` | 序列化器相关规范（detail-serializer、write-serializer、delete-serializer、naming） |

---

## 项目概览

### mom_backend

**技术栈**: Django 5.1.1 + DRF + MySQL 8.0+ + Redis + Celery + Django Channels

**核心模块**: SM（系统管理）、BDM（基础数据）、WMS（仓储）、MES（生产）、APS（计划）、PMS（采购）、SMS（销售）、VMS（可视化）

**关键特性**:
- 模块化应用结构
- 多 Redis 索引使用（缓存、Celery broker、WebSocket）
- 多环境配置（dev、test、prod、dev_fkq、dev_djc、dev_stk、cust_ydl）
- 飞书静默授权 + JWT 认证
- 标准化 API 响应格式
- Celery 异步任务队列

**详细配置**: `Projects/mom_backend/CLAUDE.md`

---

### pms_backend

**技术栈**: Django 5.1.1 + Python 3.10 + DRF + MySQL 9.0 + Celery + Redis + Daphne

**核心模块**: PM（项目管理）、SM（系统管理）、PSC（项目设置配置）、BDM（商务数据）、API（接口）

**关键特性**:
- 信号驱动架构（模块间事件驱动通信）
- 飞书开放平台深度集成（用户认证、消息推送、审批流）
- 异步任务（Celery 定时任务）
- WebSocket 支持（Daphne）
- 状态码系统（节点状态、项目状态）

**详细配置**: `Projects/pms_backend/CLAUDE.md`

---

### pms_frontend

**技术栈**: uni-app + Vue 2.0 + Vuex + 飞书 SDK

**核心功能**: 项目全流程管理（创建、节点、需求、缺陷、文件、结算、评价）

**关键特性**:
- 飞书静默授权 + JWT 双重认证
- 横屏详情页
- Canvas 节点流程图
- 多环境支持（H5、微信小程序、支付宝小程序、Android、iOS）
- 数字权限码系统

**详细配置**: `Projects/pms_frontend/CLAUDE.md`

---

### pms-admin_frontend

**技术栈**: Vue 3 + Vite + Element Plus + Pinia + ECharts + dhtmlx-gantt

**核心模块**: SM、BDM、WMS、CRM、PDM、PM、PMS、SUB、SMS

**关键特性**:
- Composition API（`<script setup>`）
- 自动导入（Vue、Element Plus 组件和 API）
- SVG 图标支持
- 基于路由的权限控制
- 页面缓存（`<keep-alive>`）
- 多环境配置

**详细配置**: `Projects/pms-admin_frontend/CLAUDE.md`

---

## 通用开发规范

### 后端项目（Django）

1. **Model 命名**: 单数 PascalCase，表名 `{app_label}_{model_snake_case}`
2. **通用字段**: `created_at`、`updated_at`、`remark`
3. **REST URL**: kebab-case，资源名使用复数
4. **注释**: 三级注释体系（模块块/类函数/局部说明）
5. **代码格式**: 每行不超过 79 字符，不同功能块空行分隔
6. **迁移**: 禁止修改已有 migration 文件

### 前端项目（Vue/uni-app）

1. **页面命名**: index（列表）、add（新增）、edit（编辑）
2. **组件设计**: 容器组件（业务逻辑）+ 展示组件（样式渲染）
3. **状态管理**: 使用 Pinia/Vuex stores
4. **HTTP 请求**: 通过统一的 request 客户端，自动处理 token 和 401

---

## 重要提示

1. **修改前展示计划**: 涉及多个文件或复杂逻辑的修改必须先展示完整计划，等待用户确认后执行
2. **阅读项目配置**: 开始任何任务前，先阅读对应项目的 CLAUDE.md
3. **遵循共享规范**: 后端项目必须遵循 `Features/rule_backend/` 中的规范
4. **软连接同步**: 在工作区修改会实时同步到实际项目目录（软连接特性）
