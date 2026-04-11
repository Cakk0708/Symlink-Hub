---
name: map-sync-vue
description: 自动生成和更新 Vue 前端项目模块接口调用文档。当完成一个 Vue 模块开发后调用此技能，Claude Code 将读取该模块的 api 定义、store、router、组件代码，与现有 .md 文档对比差异，然后更新或创建标准格式的模块文档。文档保存在 .claude/docs/module/ 下，命名规则为 {module_name}.md。凡是提到"生成前端文档"、"更新模块文档"、"写接口调用文档"、"同步前端文档"时，务必触发此技能。
---

# Vue 模块接口文档生成技能

## 概述

完成一个 Vue 前端模块开发后，使用此技能自动分析代码并生成/更新标准模块文档。文档面向前端开发者，描述该模块的接口调用方式、Store 结构、页面路由及关键组件。

---

## 第一步：收集信息

根据当前上下文总结如下主要信息：

1. **模块名称**：功能模块名（如 `customer`、`project`、`user`）
2. **所属业务域**：对应后端 app（如 `BDM`、`SM`、`PM`），从 api 文件路径或 store 命名推断
3. **项目根路径**：默认当前目录 `./`
4. **可二次确认**：如不确定模块名称或业务域，请先询问用户

---

## 第二步：读取模块代码

按顺序读取以下文件（路径根据实际项目结构调整）：

```bash
# 1. API 请求定义（最优先）
cat src/api/{module_name}.ts
# 或
cat src/api/{module_name}/index.ts
cat src/api/{module_name}/*.ts

# 2. Store 状态管理
cat src/store/modules/{module_name}.ts
# 或 Pinia
cat src/stores/{module_name}.ts

# 3. 路由定义
grep -r "{module_name}" src/router/ --include="*.ts" -l
cat src/router/modules/{module_name}.ts

# 4. 关键页面/组件（了解字段使用方式）
ls src/views/{module_name}/
cat src/views/{module_name}/index.vue
```

如果项目使用了统一 api 目录或按业务域分层结构，自动适配路径。

---

## 第三步：检查现有文档

```bash
# 检查文档是否已存在
ls .claude/docs/module/{module_name}.md 2>/dev/null || echo "NOT_EXISTS"

# 若存在，读取现有文档
cat .claude/docs/module/{module_name}.md
```

**对比分析：**
- 现有文档中的接口 vs 代码中实际调用的接口
- 找出新增、删除、变更的接口函数
- 检查请求参数类型、响应数据结构是否有变化
- Store state/actions 是否有新增或变更

---

## 第四步：生成/更新文档

```bash
# 确保目录存在
mkdir -p .claude/docs/module
```

按照下方【文档模板】生成内容，写入文件：

```
.claude/docs/module/{module_name}.md
```

**更新策略：**
- 若文档不存在 → 全量创建
- 若文档已存在 → 对比差异，仅更新变更部分，保留人工备注（`<!-- NOTE: ... -->`）

---

## 文档模板

````markdown
# {ModuleName} 模块文档

> 最后更新：{YYYY-MM-DD}  
> 模块：`{module_name}` | 业务域：`{app_name}`  
> API 前缀：`/{app_lower}/{module_name}`

---

## 模块概述

{一句话描述该模块的业务职责}

---

## 文件结构

```
src/
├── api/{module_name}.ts          # 接口请求定义
├── stores/{module_name}.ts       # Pinia Store（如有）
├── router/modules/{module_name}.ts  # 路由定义（如有）
└── views/{module_name}/
    ├── index.vue                 # 列表页
    └── detail.vue                # 详情页（如有）
```

---

## 接口函数

> ⚠️ 生成此章节前，请先读取参考模板：
> `references/api-detail-templates.md`
> 根据 api 文件中实际定义的函数，从模板中选取对应类型，替换占位符后逐一填入。

{按实际接口函数逐一展开，参考 references/api-detail-templates.md}

---

## Store 说明

> 若模块无 Store，删除此章节。

### State

| 字段 | 类型 | 说明 | 初始值 |
|------|------|------|--------|
| {field} | {type} | {说明} | {default} |

### Actions

| 方法 | 参数 | 说明 |
|------|------|------|
| `{actionName}` | `{params}` | {说明} |

---

## 路由

> 若模块无独立路由，删除此章节。

| 路径 | 组件 | 说明 |
|------|------|------|
| `/{module_name}` | `{Component}` | {说明} |
| `/{module_name}/:id` | `{Component}` | {说明} |

---

## 类型定义

```typescript
// 主数据类型
interface {ModelName} {
  id: number
  {field}: {type}
  created_at: string
  updated_at: string
}

// 列表查询参数
interface {ModelName}ListParams {
  page?: number
  page_size?: number
  {filter_field}?: {type}
}

// 创建/更新参数
interface {ModelName}Payload {
  {field}: {type}
  {optional_field}?: {type}
}
```
````

---

## 第五步：输出变更摘要

文档写入后，向用户报告：

```
✅ 文档已生成/更新：.claude/docs/module/{module_name}.md

📋 变更摘要：
  - 新增接口函数：{count} 个（{funcName}，...）
  - 更新接口函数：{count} 个（{变更说明}）
  - 删除接口函数：{count} 个
  - Store 变更：{有 / 无}
  - 无变化：{count} 个
```

---

## 注意事项

1. **类型提取优先级**：TypeScript interface/type > JSDoc 注释 > 从使用处反推
2. **请求库适配**：自动识别 axios / fetch / 项目封装的 request 工具，保持示例风格一致
3. **响应结构**：从实际调用处推断 `.data.data` / `.data` 等解包层级
4. **分页参数**：从实际传参推断 `page/pageSize`、`offset/limit`、`page/page_size` 等命名风格
5. **保留人工注释**：文档中 `<!-- NOTE: ... -->` 标记的内容在更新时保留不覆盖
6. **Store 可选**：若模块无 Pinia/Vuex Store，跳过 Store 章节

---

## 项目结构适配

支持以下常见 Vue 项目结构，自动识别：

```
# 按模块分层（推荐）
src/
├── api/{module}.ts
├── stores/{module}.ts
└── views/{module}/

# 按功能分层
src/
├── api/modules/{module}.ts
├── store/modules/{module}.ts
└── pages/{module}/

# 统一 api 入口
src/
├── api/index.ts         （所有接口集中定义）
└── views/{module}/
```