🧠 PRD：Symlink

AI Coding 配置中枢 & 内容编排系统

⸻

一、产品概述

1.1 背景

在使用 AI Coding 工具（如 Claude Code、Codex CLI 等）时，开发者需要在多个项目中维护：
	•	agent 指令（AGENT.md / CODEX.md）
	•	skills
	•	rules
	•	docs
	•	commands
	•	工程配置（如 .vscode）

这些内容通常：
	•	分散在不同项目中
	•	重复维护
	•	难以统一更新
	•	难以复用与组合

⸻

1.2 目标

构建一个本地工具，实现：

统一管理 AI 配置内容，并根据规则自动构建与分发到多个项目与不同 agent。

⸻

1.3 核心定位

DevWeave 不是一个简单的 symlink 工具，而是：

✅ AI 配置内容管理系统（Content Management）
✅ 构建系统（Build System）
✅ 分发系统（Distribution System）

⸻

二、核心理念

2.1 Single Source of Truth

所有内容（skills / rules / agent 等）只维护一份：
	•	存储在内容库中
	•	项目只消费，不直接维护

⸻

2.2 内容驱动（Content-driven）

系统围绕“内容”而不是“文件路径”：
	•	内容有 type + tags + metadata
	•	输出路径由构建规则决定

⸻

2.3 构建而非复制

项目中的文件是“构建产物”，而不是源文件：
	•	支持 symlink / copy / mirror
	•	支持聚合 / 拆分 / 映射

⸻

2.4 多 Agent 支持

统一支持不同 AI 工具：
	•	Claude
	•	Codex
	•	未来：Cursor / Gemini / Aider 等

⸻

三、用户角色

3.1 独立开发者（Primary）
	•	管理多个项目
	•	频繁使用 AI coding
	•	需要统一规则和技能

3.2 小团队（Secondary）
	•	共享 AI 使用规范
	•	统一工程辅助配置

⸻

四、系统整体架构

系统由四个核心模块组成：

⸻

4.1 Content Store（内容库）

负责存储所有内容项：
	•	Markdown 文件
	•	Frontmatter 元信息

⸻

4.2 Editor（编辑器）

用于：
	•	编辑内容
	•	管理标签 / 类型
	•	查看影响范围

⸻

4.3 Builder（构建器）

负责：
	•	解析内容库
	•	根据规则生成 Build Plan
	•	决定输出结构

⸻

4.4 Distributor（分发器）

负责：
	•	symlink / copy / mirror
	•	写入目标项目目录

⸻

五、核心数据模型

⸻

5.1 Content Item

id: auth-login
title: Auth Login Skill
type: skill
tags:
  - backend
  - auth
targets:
  - codex
  - claude
projects:
  - backend


⸻

5.2 Content Type

类型	说明	输出位置
agent	主指令文件	CODEX.md / CLAUDE.md
skill	技能	.codex/skills/
rule	规则	.codex/rules/
doc	文档	.codex/docs/
command	命令	.codex/commands/


⸻

5.3 Project

name: backend
path: /Users/xxx/backend
type: backend
agents:
  - codex
features:
  - global
  - backend
include_tags:
  - auth
exclude_tags:
  - experimental


⸻

5.4 Build Plan

CREATE:
  + .codex/skills/auth-login.md

REPLACE:
  - CODEX.md

SKIP:
  - existing file


⸻

5.5 Manifest

记录每次构建：
	•	时间
	•	来源内容
	•	输出文件
	•	冲突处理方式

⸻

六、核心功能

⸻

6.1 内容管理
	•	创建 / 编辑 Markdown 内容
	•	支持 frontmatter
	•	支持 type + tags
	•	标签筛选与搜索

⸻

6.2 构建系统
	•	根据内容 + 项目配置生成 Build Plan
	•	支持：
	•	agent 映射
	•	type → 路径规则
	•	tag 过滤
	•	支持聚合输出（如 SKILL.md）

⸻

6.3 分发系统

支持多种模式：
	•	symlink（默认）
	•	copy
	•	mirror
	•	overlay

⸻

6.4 冲突处理

支持策略：
	•	skip
	•	replace
	•	merge（未来）
	•	backup

⸻

6.5 CLI 功能（核心入口）

devweave sync backend --agent codex
devweave sync all --agent claude
devweave dry-run
devweave clean backend
devweave doctor
devweave status


⸻

6.6 项目导入

devweave import backend --agent claude

从目标项目中扫描已有的 AI 配置文件（skills、rules、agents 等），反向导入到内容库中。

适用于：
	•	项目首次接入 Symlink-Hub，需将现有配置迁移到统一管理
	•	从其他项目复制可复用的配置片段

行为：
	•	扫描目标项目的工作目录（.claude/ 或 .codex/）
	•	识别各类型资源（skills、rules、agents、commands、docs、memory、mcp）
	•	跳过内容库中已存在的同名资源
	•	交互式为新资源分配标签
	•	复制文件到内容库并生成配置条目

⸻

6.7 项目管理

devweave project add backend /path --type backend


⸻

6.8 状态系统
	•	查看项目同步状态
	•	检测失效链接
	•	检测配置异常

⸻

6.8 Watch 模式（进阶）

devweave watch backend

	•	监听内容变化自动同步

⸻

七、UI 设计

⸻

7.1 核心结构

Sidebar（内容/项目/标签）
Main（编辑器 + 预览 + 构建）
TopBar（操作）


⸻

7.2 核心页面

Content View
	•	内容列表
	•	标签筛选

⸻

Editor View
	•	Markdown 编辑
	•	type / tags 编辑

⸻

Build Preview（核心）

展示：

Will apply to:

backend/.codex/skills/auth.md
frontend/.claude/skills/auth.md


⸻

Build Plan

类似 Terraform：

CREATE / REPLACE / SKIP


⸻

7.3 核心交互
	•	修改内容 → 实时显示影响项目
	•	点击查看构建路径
	•	冲突可视化
	•	标签过滤

⸻

八、非功能需求

⸻

8.1 跨平台
	•	Mac / Windows
	•	Go 编译二进制

⸻

8.2 性能
	•	支持上百内容项
	•	构建 < 1s（本地）

⸻

8.3 可扩展性
	•	支持 Agent 插件
	•	支持自定义 type
	•	支持自定义构建规则

⸻

九、技术架构

⸻

9.1 技术选型
	•	核心语言：Go
	•	GUI：Wails + React（可选）

⸻

9.2 项目结构建议

cmd/
internal/
  core/
  builder/
  distributor/
  content/
  project/
  agent/
ui/（未来）


⸻

十、版本规划

⸻

MVP（第一版）
	•	内容库（Markdown + frontmatter）
	•	CLI sync
	•	Build Plan
	•	symlink / copy
	•	项目注册
	•	conflict 策略
	•	dry-run
	•	manifest

⸻

V2
	•	UI 编辑器
	•	Build Preview
	•	status / doctor
	•	batch sync
	•	标签系统增强

⸻

V3
	•	插件化 agent
	•	watch 模式
	•	聚合构建
	•	GUI 完整版

⸻

十一、产品价值总结

DevWeave 的核心价值：

让 AI Coding 的配置从“分散文件”，升级为“可管理、可组合、可构建的系统”。

⸻

十二、一句话定位（可用于 README）

DevWeave is a local content orchestration system for AI coding workflows — manage once, build everywhere.
