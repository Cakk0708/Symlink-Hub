# Symlink-Hub 模块地图

## 概述

本文档记录了 Symlink-Hub 项目各模块的详细文档位置。在开始任何开发任务前，请先阅读此地图，找到相关模块的文档并详细阅读。

## 模块文档索引

| 模块 | 文档路径 | 职责描述 |
|------|----------|----------|
| **core** | `.claude/docs/core.md` | 核心类型定义（ContentType、ContentItem、BuildPlan 等） |
| **config** | `.claude/docs/config.md` | 配置文件加载与解析 |
| **content** | `.claude/docs/content.md` | 内容扫描与 Frontmatter 解析 |
| **selector** | `.claude/docs/selector.md` | 内容选择逻辑（标签过滤、目标匹配） |
| **mapper** | `.claude/docs/mapper.md` | 路径映射（内容类型到输出路径） |
| **planner** | `.claude/docs/planner.md` | 构建计划生成 |
| **manifest** | `.claude/docs/manifest.md` | Manifest 管理（同步记录） |
| **distributor** | `.claude/docs/distributor.md` | 文件分发（symlink/copy 操作） |

## 模块依赖关系

```
┌─────────────┐
│    core     │  ← 所有模块的基础
└──────┬──────┘
       │
       ├──────────────────────────────────────┐
       │                                      │
┌──────▼──────┐                      ┌───────▼────────┐
│   config    │                      │    content     │
└─────────────┘                      └────────┬───────┘
       │                                      │
       │                              ┌───────▼────────┐
       │                              │    selector     │
       │                              └────────┬───────┘
       │                                      │
       │         ┌────────────────────────────┤
       │         │                            │
┌──────▼──────┐─▼──┐                   ┌──────▼──────┐
│   mapper    │    │                   │   planner   │
└──────┬──────┘    │                   └──────┬──────┘
       │           │                          │
       └───────┬───┴──────────────────────────┤
               │                              │
         ┌─────▼──────┐              ┌────────▼────────┐
         │  manifest  │              │  distributor    │
         └────────────┘              └─────────────────┘
```

## 使用指南

### 1. 任务开始前

1. 阅读本文档，了解项目模块结构
2. 识别任务涉及的模块
3. 阅读相关模块的详细文档

### 2. 根据任务类型查找模块

| 任务类型 | 相关模块 | 文档 |
|----------|----------|------|
| 添加新的内容类型 | `core`, `mapper` | core.md, mapper.md |
| 修改配置格式 | `config` | config.md |
| 修改选择逻辑 | `selector` | selector.md |
| 修改路径规则 | `mapper` | mapper.md |
| 添加新的操作类型 | `core`, `planner`, `distributor` | core.md, planner.md, distributor.md |
| Manifest 相关功能 | `manifest` | manifest.md |
| 文件操作问题 | `distributor` | distributor.md |
| Frontmatter 解析 | `content` | content.md |

### 3. 跨模块任务

如果任务涉及多个模块，按依赖顺序阅读文档：

1. 先阅读 `core.md`（了解基础类型）
2. 再阅读相关模块文档
3. 最后阅读执行模块文档（如 `distributor.md`）

### 4. 快速参考

- **数据结构定义** → `core.md`
- **配置文件格式** → `config.md`
- **内容选择规则** → `selector.md`
- **路径映射规则** → `mapper.md`
- **构建流程** → `planner.md`
- **文件操作** → `distributor.md`

## 文档维护

当添加新模块或修改现有模块时，请更新此地图。

### 添加新模块

1. 创建对应的 `.md` 文档
2. 在上表中添加条目
3. 更新依赖关系图（如果需要）

### 修改现有模块

1. 更新对应的 `.md` 文档
2. 如果职责发生变化，更新此地图中的描述
