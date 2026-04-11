---
name: vue-layout-doc
description: 读取 Vue 前端页面组件代码，汇总页面元素结构并生成标准布局说明文档。文档保存在 {submodule}/.claude/docs/layouts/*.md，并同步更新 .claude/docs/map.md 中的"元素布局"章节。凡是提到"生成布局文档"、"页面元素说明"、"整理页面结构"、"元素布局"、"生成 layout 文档"时，务必触发此技能。
---

# Vue 页面布局文档生成技能

## 概述

读取指定 Vue 页面的组件代码，提取页面中所有可见区块的层级结构、CSS 选择器标识与功能说明，生成标准格式的布局说明文档，并在 `{submodule}/.claude/docs/map.md` 中建立索引。

---

## 第一步：收集信息

从当前上下文确认：

1. **页面名称**：如 `首页`、`项目列表页`（用于文档标题和 map.md 索引）
2. **页面路径**：对应的 Vue 文件路径，如 `src/views/home/index.vue`
3. **文档文件名**：默认使用路由路径或组件名，如 `home.md`、`project-list.md`

如不确定，询问用户确认后继续。

---

## 第二步：读取页面代码

```bash
# 读取主页面组件
cat {page_path}

# 如页面引用了子组件，逐一读取
grep -E "import .* from" {page_path} | grep -v "node_modules"
# 根据 import 路径读取关键子组件
cat {component_path}
```

**重点提取：**
- `<template>` 中每个有意义的区块（有 class、id、语义标签的元素）
- 区块的层级嵌套关系
- class 名称、id 名称（优先取最具语义的那一层）
- 元素的功能描述（从 `v-if` 条件、事件名、文本内容、组件名推断）
- 重复列表元素（`v-for`）归为一个条目描述

---

## 第三步：检查现有文档

```bash
# 检查布局文档目录
ls {submodule}/.claude/docs/layouts/ 2>/dev/null || echo "NOT_EXISTS"

# 若目标文档已存在，读取对比
cat {submodule}/.claude/docs/layouts/{doc_name}.md 2>/dev/null
```

- 文档已存在 → 对比现有结构，仅更新变更部分，保留人工备注 `<!-- NOTE: ... -->`
- 文档不存在 → 全量创建

---

## 第四步：生成布局文档

```bash
mkdir -p {submodule}/.claude/docs/layouts
```

按照下方【文档模板】写入文件：

```
.claude/docs/layouts/{doc_name}.md
```

> ⚠️ 文档模板与结构说明格式请读取：`references/layout-doc-template.md`

---

## 第五步：更新 map.md

```bash
# 读取 map.md
cat {submodule}/.claude/docs/map.md 2>/dev/null || echo "NOT_EXISTS"
```

**定位模块 `- 元素布局说明`：**

- 模块已存在 → 在模块内查找该页面条目：
  - 条目已存在 → 更新链接（如文件名变化）
  - 条目不存在 → 追加新行
- 模块不存在 → 在 map.md 模块下末尾追加元素布局说明

**条目格式：**

```markdown
## 元素布局

- [{页面名称}](.claude/docs/layouts/{doc_name}.md) - {一句话描述}
```

---

## 第六步：输出操作摘要

```
✅ 布局文档已生成/更新：.claude/docs/layouts/{doc_name}.md

📐 页面结构概览：
  - 顶层区块：{count} 个
  - 已标注 tag：{count} 个
  - 未找到 tag（需人工补充）：{count} 个

🗺️ map.md 已同步：
  - 操作：{新增条目 | 更新链接 | 无变化}
  - 章节：## 元素布局

⚠️ 需人工确认：
  - {区块名}：{原因，如 class 不具语义、动态 class 无法静态分析等}
```