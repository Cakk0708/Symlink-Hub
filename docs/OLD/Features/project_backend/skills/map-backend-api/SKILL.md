---
name: map-backend-api
description: 自动生成和更新 Django 后端项目模块 API 接口文档。当完成一个 Django 模块开发后调用此技能，Claude Code 将读取该模块代码（views、urls、serializers），与现有 .md 文档对比差异，然后更新或创建标准格式的接口文档。文档保存在 .claude/docs/api/ 目录下，命名规则为 {app_name}_{model_name}.md。凡是提到"生成接口文档"、"更新API文档"、"模块文档"、"写接口文档"、"同步文档"时，务必触发此技能。
---

# Django API 接口文档生成技能

## 概述

完成一个 Django 模块开发后，使用此技能自动分析代码并生成/更新标准 API 接口文档。

---

## 变量说明
- `{app_name}`：Django app 名称（如 `SM`、`BDM`）
- `{model_name}`：核心模型名称（如 `Organization`、`User`）
- `{root}`：项目根目录绝对路径，如果项目是多 agent 目录时则为该 agent 的工作目录，如 backend-agent 的工作目录则为他规则引导下定义的目录，{root}/backend/.claude/docs/ 为 backend-agent 的文档目录
- `{base_url}`：API 基础 URL，如 `http://localhost:8000/api/v1`，通常从 settings 或 .env 文件中获取

## 第一步：收集信息

在开始前，根据当前上下文总结如下主要信息：

1. **app 名称**：Django apps 的名称（如 `SM`、`BDM`）
2. **model 名称**：核心模型名称（如 `Organization`、`User`）
3. **项目根路径**：默认当前目录 `./`
4. **可二次确认**：如不确定 app 名称或 model 名称，请先询问用户

---

## 第二步：读取模块代码

按顺序读取以下文件（路径根据实际项目结构调整）：

```bash
# 读取 URL 路由
cat {app_name}/urls.py

# 读取视图逻辑
cat {app_name}/views.py
# 或 ViewSet
cat {app_name}/viewsets.py

# 读取序列化器（字段定义）
cat {app_name}/serializers.py

# 读取模型定义
cat {app_name}/models.py

# 如有权限类
cat {app_name}/permissions.py

# 如有过滤器
cat {app_name}/filters.py
```

如果项目使用了子目录结构（如 `views/`、`serializers/`），则递归读取对应目录下所有文件。

---

## 第三步：检查现有文档

```bash
# 检查文档是否已存在
ls {root}/.claude/docs/api/{app_name}_{model_name}.md 2>/dev/null || echo "NOT_EXISTS"

# 若存在，读取现有文档
cat {root}/.claude/docs/api/{app_name}_{model_name}.md
```

**对比分析：**
- 现有文档中的接口 vs 代码中的实际路由
- 找出新增、删除、变更的接口
- 检查请求参数、响应字段是否有变化

---

## 第四步：生成/更新文档

```bash
# 确保目录存在
mkdir -p {root}/.claude/docs/api
```

按照下方【文档模板】生成内容，写入文件（app和model名称都转换为小写）：

```
{root}/.claude/docs/api/{app_name}-{model_name}.md
```

**更新策略：**
- 若文档不存在 → 全量创建
- 若文档已存在 → 对比差异，仅更新变更部分，保留人工备注（`<!-- NOTE: ... -->`）

### 文件夹命名
- 文件夹命名为 `{app_name}-{model_name}`，如 `sm-organization`
- 多文件夹类型使用 `_` 连接，如 `sm-organization_user`


---

## 文档模板

````markdown
# {AppName} - {ModelName} 接口文档

> 最后更新：{YYYY-MM-DD}  
> App: `{app_name}` | Model: `{ModelName}`  
> Base URL: `{base_url}`

---

## 认证说明

所有接口均需在请求头中携带 JWT Token：

```
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## 接口列表

| 方法 | 路径 | 描述 | 需要认证 |
|------|------|------|----------|
| GET | `/{app_name}` | 获取列表 | ✅ |
| POST | `/{app_name}` | 创建 | ✅ |
| GET | `/{app_name}/{id}` | 获取详情 | ✅ |
| PUT | `/{app_name}/{id}` | 更新 | ✅ |
| DELETE | `/{app_name}` | 批量删除 | ✅ |

---

## 接口详情

> ⚠️ 生成此章节前，请先读取参考模板：
> `references/api-detail-templates.md`
> 根据代码中实际存在的路由，从模板中选取对应类型（LIST / CREATE / RETRIEVE / UPDATE / BULK DELETE / 自定义 Action），
> 替换占位符后逐一填入，不存在的接口类型不写入文档。

{按实际接口逐一展开，参考 references/api-detail-templates.md}

---

## 错误响应

所有接口错误时统一返回：

```json
{
  "msg": "error",
  "data": "错误描述信息"
}
```

**常见错误码**

| HTTP 状态码 | 说明 |
|-------------|------|
| 400 | 请求参数错误 |
| 401 | 未认证或 Token 已过期 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 完整 cURL 示例

```bash
# 1. 获取列表
curl -X GET "{base_url}/{app_name}?page=0" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 2. 创建
curl -X POST "{base_url}/{app_name}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"{field}":"{value}"}'

# 3. 获取详情
curl -X GET "{base_url}/{app_name}/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 4. 更新
curl -X PUT "{base_url}/{app_name}/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"{field}":"{new_value}"}'

# 5. 批量删除
curl -X DELETE "{base_url}/{app_name}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"ids":[1,2,3]}'
```
````

---

## 第五步：输出变更摘要

文档写入后，向用户报告：

```
✅ 文档已生成/更新：{root}/.claude/docs/api/{app_name}_{model_name}.md

📋 变更摘要：
  - 新增接口：{count} 个（{方法} {路径}，...）
  - 更新接口：{count} 个（{变更说明}）
  - 删除接口：{count} 个
  - 无变化：{count} 个
```

---

## 注意事项

1. **字段提取优先级**：Serializer > Model > View 中的手动处理
2. **分页参数**：从 `PageNumberPagination` 或 `LimitOffsetPagination` 配置中提取，若无则标注"无分页"
3. **过滤参数**：从 `FilterSet`、`filter_backends`、或 view 中的 `request.query_params` 提取
4. **权限说明**：从 `permission_classes` 提取，标注哪些接口需要特殊权限
5. **嵌套序列化器**：若字段为嵌套对象，在响应示例中展开完整结构
6. **保留人工注释**：文档中 `<!-- NOTE: ... -->` 标记的内容在更新时保留不覆盖
7. **ViewSet 路由推断**：若使用 Router 注册 ViewSet，根据 `router.register` 推断所有标准路由

---

## 项目结构适配

支持以下常见 Django 项目结构，自动识别：

```
# 标准结构
{app_name}/
├── models.py
├── views.py
├── urls.py
└── serializers.py

# 拆分结构
{app_name}/
├── models/
├── views/
├── serializers/
└── urls.py

# DRF ViewSet 结构
{app_name}/
├── models.py
├── viewsets.py
├── serializers.py
└── urls.py  (使用 Router)
```

## 第六步：检查项目地图

### 描述

当所有接口文档生成完成后，检查项目地图，确保所有接口都已覆盖。如接口文档不存在，需要补充。

### 目标

**项目地图**：

- 地图路径：*.claude/docs/map.md

**地图格式**：

- 每个接口文档都应在项目地图中有所记录，检查后更新

```
### {app_name}
#### {module_name}
##### {model_name}
- 路径: `...`
- 别名：`...`
- 模块说明：`...`
- 接口文档：`结果路径` ✅ 需同步的接口文档路径
```