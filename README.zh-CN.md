# Symlink-Hub

> 本地 AI 配置内容中枢与分发 CLI

[English](README.md) | [简体中文](README.zh-CN.md)

## 概述

Symlink-Hub 是一个本地工具，用于统一管理 AI 编程配置（agents、skills、rules、docs、commands），并根据规则自动分发到多个项目。

## 技术栈

- **Go 1.26+** - 核心 CLI 实现
- **YAML** - 配置格式
- **Markdown + Frontmatter** - 内容格式

## 特性

- **集中管理**：在一个仓库中管理所有 AI 配置内容
- **多 Agent 支持**：Codex、Claude 及其他 AI 工具
- **灵活分发**：支持软链接和复制两种模式
- **标签过滤**：通过标签组织和分发内容
- **预览模式**：应用前预览变更
- **清单跟踪**：记录同步历史，支持清理回滚

## 项目结构

```
Symlink-Hub/
├── cmd/symlink-hub/     # CLI 入口
├── internal/
│   ├── core/           # 核心类型
│   ├── config/         # 配置加载
│   ├── content/        # 内容扫描与解析
│   ├── selector/       # 内容选择逻辑
│   ├── mapper/         # 路径映射
│   ├── planner/        # 构建计划生成
│   ├── manifest/       # 同步记录管理
│   └── distributor/    # 文件操作
├── fixtures/
│   ├── content/        # 示例内容
│   └── projects/       # 示例项目
└── .claude/docs/       # 模块文档
```

## 快速开始

```bash
# 构建
go build -o symlink-hub cmd/symlink-hub/main.go

# 检查配置
./symlink-hub doctor

# 预览变更
./symlink-hub dry-run

# 同步内容
./symlink-hub sync

# 清理已分发文件
./symlink-hub clean
```

## 命令

| 命令 | 说明 |
|------|------|
| `doctor` | 检查配置健康状态 |
| `dry-run` | 预览构建计划，不执行变更 |
| `sync` | 分发内容到项目 |
| `clean` | 清理已分发的文件 |
| `status` | 显示同步状态（即将推出） |

## 配置

创建 `symlink-hub.config.yaml`：

```yaml
contentRoot: ./content
stateRoot: ./.symlink-hub
defaultMode: symlink

agents:
  codex:
    agentFileName: CODEX.md
    roots:
      skill: .codex/skills
      rule: .codex/rules
      doc: .codex/docs
      command: .codex/commands

projects:
  - name: backend
    path: ./projects/backend
    agents: [codex]
    includeTags: [global, backend]
    excludeTags: [experimental]
```

## 内容格式

内容文件使用 Markdown + Frontmatter：

```markdown
---
id: auth-login
title: 认证登录技能
type: skill
targets:
  - codex
tags:
  - backend
  - auth
projects:
  - backend
status: active
---

# 认证登录

认证登录流程的实现指南。
```

## 文档

- [产品需求文档](docs/v1.0/PRD.md)
- [系统设计](docs/v1.0/System-Design.md)
- [模块文档](.claude/docs/map.md)

## 许可证

MIT
