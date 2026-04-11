# PSC - ProjectTemplate 接口文档

> 最后更新：2026-04-09
> App: `PSC` | Model: `ProjectTemplate`
> Base URL: `/psc/project/templates`

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
| GET | `/psc/project/templates/simple` | 获取简化列表 | ✅ |
| GET | `/psc/project/templates` | 获取列表（分页） | ✅ |
| POST | `/psc/project/templates` | 创建项目模板 | ✅ |
| GET | `/psc/project/templates/<id>` | 获取详情 | ✅ |
| PUT | `/psc/project/templates/<id>` | 版本迭代 | ✅ |
| PATCH | `/psc/project/templates` | 批量更新 | ✅ |
| DELETE | `/psc/project/templates` | 批量删除 | ✅ |
| GET | `/psc/project/templates/enums` | 获取枚举数据 | ✅ |

---

## 接口详情

### 1. 获取简化列表

**GET** `/psc/project/templates/simple`

仅返回 `id`、`code`、`currentName`、`currentVersionId`、`sortOrder` 字段，适用于下拉选择等场景。

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "code": "PROJ_TMP000001",
        "currentName": "标准项目模板",
        "currentVersionId": 1,
        "sortOrder": 1
      }
    ],
    "total": 1
  }
}
```

---

### 2. 获取列表（分页）

**GET** `/psc/project/templates`

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | string | 否 | 按模板编码筛选 |
| currentName | string | 否 | 按当前版本名称筛选 |
| pageNum | int | 否 | 页码，从 1 开始，默认 1 |
| pageSize | int | 否 | 每页数量，默认 10 |
| pageSort | string | 否 | 排序，格式 `字段:方向`，默认 `createdAt:DESC` |

**pageSort 支持的字段**

- `createdAt` - 创建时间
- `updatedAt` - 更新时间（最新版本创建时间）
- `name` - 名称
- `code` - 编码
- `sortOrder` - 排序序号

**方向**: `ASC` 或 `DESC`

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "code": "PROJ_TMP000001",
        "isActive": true,
        "sortOrder": 1,
        "createdAt": "2024-01-01T00:00:00+08:00",
        "updatedAt": "2024-01-01T00:00:00+08:00",
        "currentName": "标准项目模板",
        "currentVersionId": 1,
        "currentVersionNumber": 1,
        "currentCreatedByNickname": "管理员",
        "currentRemark": "标准项目管理流程",
        "labels": "研发, 生产"
      }
    ],
    "pagination": {
      "pageNum": 1,
      "pageSize": 10,
      "total": 1,
      "totalPages": 1
    }
  }
}
```

---

### 3. 获取详情

**GET** `/psc/project/templates/<id>`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 项目模板 ID |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "document": {
      "code": "PROJ_TMP000001",
      "name": "标准项目模板",
      "isActive": true,
      "sortOrder": 1,
      "initialStatus": "APPLYING",
      "remark": "标准项目管理流程",
      "labels": [
        {
          "id": 1,
          "code": "LABEL001",
          "name": "研发"
        },
        {
          "id": 2,
          "code": "LABEL002",
          "name": "生产"
        }
      ]
    },
    "nodeData": {
      "list": [
        {
          "id": 1,
          "nodeDefinitionId": 1,
          "nodeDefinitionVersionId": 1,
          "nodeCode": "NODE001",
          "nodeName": "项目立项",
          "category": "APPROVAL",
          "parent": null,
          "sortOrder": 1,
          "children": [
            {
              "id": 2,
              "nodeDefinitionId": 2,
              "nodeDefinitionVersionId": 2,
              "nodeCode": "NODE002",
              "nodeName": "需求分析",
              "category": "TASK",
              "parent": 1,
              "sortOrder": 1,
              "children": []
            }
          ]
        }
      ]
    },
    "others": {
      "createdAt": "2024-01-01T00:00:00+08:00",
      "updatedAt": "2024-01-01T00:00:00+08:00",
      "versionCount": 1,
      "createdBy": {
        "id": 1,
        "nickname": "管理员"
      },
      "updatedBy": {
        "id": 1,
        "nickname": "管理员"
      }
    }
  }
}
```

---

### 4. 创建项目模板

**POST** `/psc/project/templates`

创建项目模板和第一个版本（`isActive` 默认为 `true`）

**请求体**

```json
{
  "code": "PROJ_TMP000002",
  "name": "新产品开发模板",
  "sortOrder": 1,
  "remark": "新产品开发标准流程",
  "initialStatus": "APPLYING",
  "labelIds": [1, 2],
  "nodes": [
    {
      "versionId": 1,
      "sortOrder": 1,
      "parent": null
    },
    {
      "versionId": 2,
      "sortOrder": 1,
      "parent": 1
    }
  ]
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | string | ✅ | 模板编码，唯一 |
| name | string | ✅ | 模板名称 |
| sortOrder | int | 否 | 排序序号，默认 1 |
| remark | string | 否 | 备注 |
| initialStatus | string | 否 | 初始状态，`APPLYING` 或 `IN_PROGRESS`，默认 `APPLYING` |
| labelIds | array | 否 | 标签 ID 列表 |
| nodes | array | 否 | 节点列表（树形结构） |
| nodes[].versionId | int | ✅ | 节点定义版本 ID |
| nodes[].sortOrder | int | 否 | 节点排序序号 |
| nodes[].parent | int | 否 | 父节点 ID |

**校验规则**

- `code` 必须唯一，已存在则拒绝
- `name` 必须唯一，其他模板的当前版本已使用则拒绝
- 所有 `nodes` 中，不允许两个不同节点引用相同的"编辑"（`EDIT`）交付物定义。即两个节点对应的 `NodeDefinitionVersion` 的 `deliverable_mappings` 中不能出现相同的 `deliverable_definition_version` 且 `function_restriction` 均为 `EDIT`

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "insertId": 2
  }
}
```

---

### 5. 版本迭代

**PUT** `/psc/project/templates/<id>`

创建新版本（可更新 `sortOrder`，不更新 `code`、`isActive`）

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 项目模板 ID |

**请求体**

```json
{
  "name": "新产品开发模板 V2",
  "sortOrder": 2,
  "remark": "更新后的流程说明",
  "initialStatus": "IN_PROGRESS",
  "labelIds": [1, 2, 3],
  "nodes": [
    {
      "versionId": 1,
      "sortOrder": 1,
      "parent": null
    },
    {
      "versionId": 3,
      "sortOrder": 2,
      "parent": null
    }
  ]
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 否 | 模板名称（不传则使用上一版本的名称） |
| sortOrder | int | 否 | 排序序号 |
| remark | string | 否 | 备注 |
| initialStatus | string | 否 | 初始状态 |
| labelIds | array | 否 | 标签 ID 列表（更新模板的标签） |
| nodes | array | 否 | 节点列表（更新版本的节点配置） |

**注意事项**

- 此接口会创建新版本，旧版本保留
- `code` 和 `isActive` 不能通过此接口修改
- 所有 `nodes` 中，不允许两个不同节点引用相同的"编辑"（`EDIT`）交付物定义（与 POST 校验规则一致）

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 2,
    "document": {
      "code": "PROJ_TMP000002",
      "name": "新产品开发模板 V2",
      "isActive": true,
      "initialStatus": "IN_PROGRESS",
      "remark": "更新后的流程说明",
      "labels": [
        {
          "id": 1,
          "code": "LABEL001",
          "name": "研发"
        }
      ]
    },
    "nodeData": {
      "list": []
    },
    "others": {
      "createdAt": "2024-01-01T00:00:00+08:00",
      "updatedAt": "2024-01-02T00:00:00+08:00",
      "versionCount": 2,
      "createdBy": {
        "id": 1,
        "nickname": "管理员"
      },
      "updatedBy": {
        "id": 1,
        "nickname": "管理员"
      }
    }
  }
}
```

---

### 6. 批量更新

**PATCH** `/psc/project/templates`

仅能更新 `isActive` 字段

**请求体**

```json
{
  "ids": [1, 2],
  "isActive": false
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| ids | array | ✅ | 项目模板 ID 列表 |
| isActive | boolean | ✅ | 是否启用 |

**响应示例**

```json
{
  "msg": "success，更新了 2 条记录"
}
```

---

### 7. 批量删除

**DELETE** `/psc/project/templates`

**请求体**

```json
{
  "ids": [1, 2]
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| ids | array | ✅ | 项目模板 ID 列表 |

**注意事项**

- 删除前会检查该模板是否已被项目使用
- 如果已被使用，则无法删除

**响应示例**

```json
{
  "msg": "success"
}
```

---

### 8. 获取枚举数据

**GET** `/psc/project/templates/enums`

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "initialStatus": [
      {
        "value": "IN_PROGRESS",
        "label": "进行中"
      },
      {
        "value": "APPLYING",
        "label": "申请中"
      }
    ]
  }
}
```

---

## 字段权限说明

| 字段 | POST 创建 | PUT 版本迭代 | PATCH 批量更新 |
|------|-----------|-------------|---------------|
| code | ✅ 可设置 | ❌ 不可修改 | ❌ 不可修改 |
| name | ✅ 必填 | ✅ 可修改（不传则使用上一版本） | ❌ 不可修改 |
| sortOrder | ✅ 可选（默认 1） | ✅ 可修改 | ❌ 不可修改 |
| isActive | ✅ 默认 true | ❌ 不可修改 | ✅ 可修改 |
| remark | ✅ 可选 | ✅ 可修改 | ❌ 不可修改 |
| initialStatus | ✅ 可选 | ✅ 可修改 | ❌ 不可修改 |
| labelIds | ✅ 可选 | ✅ 可修改 | ❌ 不可修改 |
| nodes | ✅ 可选 | ✅ 可修改 | ❌ 不可修改 |

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

**业务错误示例**

```json
{
  "msg": "参数错误",
  "errors": {
    "code": [
      "\"PROJ_TMP000001\"已被使用，请更换编码后重试"
    ],
    "name": [
      "\"标准项目模板\"已被其他模板使用，请更换名称后重试"
    ]
  }
}
```

```json
{
  "msg": "参数错误",
  "errors": {
    "PROJ_TMP000001": "\"PROJ_TMP000001\" 已被项目使用，无法删除"
  }
}
```

```json
{
  "msg": "参数错误",
  "errors": {
    "nonFieldErrors": [
      "节点「需求分析、方案设计」存在相同的\"编辑\"交付物，不允许保存"
    ]
  }
}
```

---

## 数据模型说明

### ProjectTemplate（项目模板）

**字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| code | string | 唯一编码，自动生成，前缀 `PROJ_TMP` |
| sort_order | int | 排序序号，默认 1 |
| is_active | boolean | 是否启用 |
| created_at | DateTime | 创建时间 |

### ProjectTemplateVersion（项目模板版本）

**字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| version_number | int | 版本号（内部） |
| project_template | ForeignKey | 关联项目模板 |
| name | string | 模板名称 |
| remark | string | 备注 |
| is_current | boolean | 是否当前版本 |
| initial_status | string | 初始状态 |
| created_by | ForeignKey | 创建人 |
| created_at | DateTime | 创建时间 |

---

## 完整 cURL 示例

```bash
# 1. 获取简化列表
curl -X GET "http://your-domain.com/psc/project/templates/simple" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 2. 获取列表（分页）
curl -X GET "http://your-domain.com/psc/project/templates?pageNum=1&pageSize=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 3. 获取详情
curl -X GET "http://your-domain.com/psc/project/templates/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 4. 创建项目模板
curl -X POST "http://your-domain.com/psc/project/templates" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "code": "PROJ_TMP000002",
    "name": "新产品开发模板",
    "sortOrder": 1,
    "remark": "新产品开发标准流程",
    "initialStatus": "APPLYING",
    "labelIds": [1, 2],
    "nodes": [
      {
        "versionId": 1,
        "sortOrder": 1,
        "parent": null
      }
    ]
  }'

# 5. 版本迭代
curl -X PUT "http://your-domain.com/psc/project/templates/2" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "新产品开发模板 V2",
    "remark": "更新后的流程说明",
    "labelIds": [1, 2, 3]
  }'

# 6. 批量更新
curl -X PATCH "http://your-domain.com/psc/project/templates" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "ids": [1, 2],
    "isActive": false
  }'

# 7. 批量删除
curl -X DELETE "http://your-domain.com/psc/project/templates" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "ids": [1, 2]
  }'

# 8. 获取枚举数据
curl -X GET "http://your-domain.com/psc/project/templates/enums" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```