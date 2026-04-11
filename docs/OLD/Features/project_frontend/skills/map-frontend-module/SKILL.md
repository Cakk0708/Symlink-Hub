---
name: map-frontend-module
description: 为了保持项目文档更新保障项目基础文档结构不过期，你将维护项目地图等相关依赖文档，对于本次更新的模块总结模块内容、模块依赖关系、接口调整结果更新项目说明结构，当用户提到“项目地图”、“更新模块说明”、“更新项目地图”、“创建项目地图”、“更新map”、“创建map”时触发本技能。
references:
  - ./references/CLAUDE.md
  - ./references/module.md
  - ./references/map范例.md
---


# 文档同步指令

完成本次开发任务后，执行以下文档更新流程，确保项目文档与代码保持同步。

## 执行时机
仅在以下情况触发：
- 新增或删除了 App、Model、Service、API 接口
- 修改了跨模块的依赖关系
- 变更了对外暴露的 services.py / selectors.py 接口签名

代码重构、Bug 修复、测试补充等不触发本指令。

## 执行步骤

### Step 1：读取现有文档
在做任何修改前，先完整读取：
- `{root}/CLAUDE.md`
- `{root}/.claude/docs/map.md`
- `{root}/.claude/docs/modules/{当前 App}.md`（若存在）

### Step 2：仅更新有差异的部分
对比本次变更，只修改受影响的内容，不改动无关部分。

### Step 3：按顺序更新以下文档

#### CLAUDE.md
- 路径：`{root}/CLAUDE.md`
- 参考模板：`./references/CLAUDE.md`
- 只更新：技术栈变化、新增铁律、废弃的约定

#### 项目地图
- 路径：`{root}/.claude/docs/map.md`
- 更新范围：
  - 模块全景（新增/删除模块）
  - 依赖关系图（依赖变化）
  - 数据流（主流程变化）

#### 模块说明
- 路径：`{root}/.claude/docs/modules/{当前 App}.md`
- 参考模板：`./references/module.md`
- 若文件不存在则新建，存在则只更新差异部分
- 更新范围：对外接口、依赖列表、状态机、禁止事项

### Step 4：输出变更摘要
完成后用以下格式汇报：

\```
## 文档更新摘要
- CLAUDE.md：[有变更 / 无需更新]，变更内容：xxx
- map.md：[有变更 / 无需更新]，变更内容：xxx
- modules/{App}.md：[已更新 / 已新建 / 无需更新]，变更内容：xxx
\```

## 变量说明
- `{当前 App}`：本次开发涉及的 Django App 名称（如 orders、users）
- `{root}`：项目根目录绝对路径