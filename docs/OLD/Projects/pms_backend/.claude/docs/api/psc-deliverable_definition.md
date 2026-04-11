# PSC - DeliverableDefinition 接口文档

> 最后更新：2026-03-27
> App: `PSC` | Model: `DeliverableDefinition`
> Base URL: `/psc/deliverable/definitions`

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
| GET | `/psc/deliverable/definitions/simple` | 获取简化列表 | ✅ |
| GET | `/psc/deliverable/definitions/list` | 获取分页列表 | ✅ |
| POST | `/psc/deliverable/definitions/list` | 创建交付物定义 | ✅ |
| PATCH | `/psc/deliverable/definitions/list` | 批量更新（启用状态） | ✅ |
| DELETE | `/psc/deliverable/definitions/list` | 批量删除 | ✅ |
| GET | `/psc/deliverable/definitions/<id>` | 获取详情 | ✅ |
| PUT | `/psc/deliverable/definitions/<id>` | 版本迭代 | ✅ |

---

## 接口详情

### 1. 获取简化列表

**GET** `/psc/deliverable/definitions/simple`

获取所有启用状态的交付物定义简化信息，仅返回 `id`、`code`、`name`、`currentVersionId` 等关键字段。适用于下拉选择等场景。

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "code": "DELIV001",
        "currentName": "需求文档",
        "currentVersionId": 1,
        "currentDisplayVersion": "1.0"
      }
    ],
    "total": 1
  }
}
```

**响应字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 交付物定义 ID |
| code | string | 唯一标识 |
| currentName | string | 当前版本名称 |
| currentVersionId | int | 当前版本 ID |
| currentDisplayVersion | string | 当前版本号 |

---

### 2. 获取分页列表

**GET** `/psc/deliverable/definitions/list`

**Query 参数**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| code | string | 否 | - | 搜索关键词（匹配唯一标识） |
| currentName | string | 否 | - | 搜索关键词（匹配当前版本名称） |
| pageNum | int | 否 | 1 | 页码 |
| pageSize | int | 否 | 10 | 每页数量 |
| pageSort | string | 否 | createdAt:DESC | 排序字段（格式：字段:方向） |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "code": "DELIV001",
        "isActive": true,
        "currentName": "需求文档",
        "currentVersionId": 1,
        "currentDisplayVersion": "1.0",
        "currentCreatedByNickname": "张三",
        "createdAt": "2024-01-01T00:00:00+08:00",
        "updatedAt": "2024-01-01T00:00:00+08:00"
      }
    ],
    "pagination": {
      "pageNum": 1,
      "pageSize": 10,
      "total": 100,
      "totalPages": 10
    }
  }
}
```

**响应字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 交付物定义 ID |
| code | string | 唯一标识 |
| isActive | boolean | 是否启用 |
| currentName | string | 当前版本名称 |
| currentVersionId | int | 当前版本 ID |
| currentDisplayVersion | string | 当前版本号 |
| currentCreatedByNickname | string | 当前版本创建人昵称 |
| createdAt | string | 创建时间 |
| updatedAt | string | 更新时间 |

---

### 3. 创建交付物定义

**POST** `/psc/deliverable/definitions/list`

创建交付物定义和第一个版本，`isActive` 默认为 `true`。

**请求体**

```json
{
  "code": "DELIV001",
  "name": "需求文档",
  "displayVersion": "1.0",
  "remark": "项目需求规格说明书",
  "isLinkFirst": true,
  "allowedFileExtensionsIds": [1, 2, 3],
  "feishuTemplate": {
    "title": "需求文档模板",
    "token": "abc123",
    "category": "document",
    "original_url": "https://example.com/template"
  }
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | string | 否 | 唯一标识（不传则自动生成，格式：DELIV+序号） |
| name | string | ✅ | 交付物定义名称 |
| displayVersion | string | 否 | 版本号（默认：1.0） |
| remark | string | 否 | 备注 |
| isLinkFirst | boolean | 否 | 是否链接优先（默认：false） |
| allowedFileExtensionsIds | array[int] | 否 | 允许的文件扩展名类型 ID 列表 |
| feishuTemplate | object | 否 | 飞书模板信息 |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "insertId": 1
  }
}
```

**错误响应示例**

```json
{
  "msg": "参数错误",
  "errors": {
    "name": ["\"需求文档\"已被其他交付物定义使用，请更换名称后重试"]
  }
}
```

---

### 4. 批量更新

**PATCH** `/psc/deliverable/definitions/list`

批量更新交付物定义的启用状态。

**请求体**

```json
{
  "ids": [1, 2, 3],
  "isActive": false
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| ids | array[int] | ✅ | 交付物定义 ID 列表 |
| isActive | boolean | 否 | 新的启用状态 |

**响应示例**

```json
{
  "msg": "success，更新了 3 条记录"
}
```

---

### 5. 批量删除

**DELETE** `/psc/deliverable/definitions/list`

**请求体**

```json
{
  "ids": [1, 2, 3]
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| ids | array[int] | ✅ | 交付物定义 ID 列表 |

**响应示例**

```json
{
  "msg": "success"
}
```

**错误响应示例**

```json
{
  "msg": "参数错误",
  "errors": {
    "ids": ["\"DELIV001\" 有交付物使用记录，请先删除交付物"]
  }
}
```

---

### 6. 获取详情

**GET** `/psc/deliverable/definitions/<id>`

获取交付物定义详情，数据分块输出：`document`（定义主体）、`versionData`（版本列表）、`others`（其他信息）。

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 交付物定义 ID |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "document": {
      "code": "DELIV001",
      "name": "需求文档",
      "isActive": true
    },
    "versionData": {
      "items": [
        {
          "id": 1,
          "displayVersion": "1.0",
          "remark": "项目需求规格说明书",
          "isLinkFirst": true,
          "isCurrent": true,
          "createdAt": "2024-01-01T00:00:00+08:00",
          "createdBy": "张三",
          "allowedFileExtensions": [
            {"id": 1, "name": ".pdf"},
            {"id": 2, "name": ".docx"}
          ],
          "template": {
            "id": 1,
            "name": "需求文档模板",
            "storageProvider": "feishu"
          }
        }
      ],
      "count": 1
    },
    "others": {
      "createdAt": "2024-01-01 00:00:00",
      "updatedAt": "2024-01-01 00:00:00",
      "versionCount": 1
    }
  }
}
```

**响应字段说明**

**document 块**

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 唯一标识 |
| name | string | 当前版本名称 |
| isActive | boolean | 是否启用 |

**versionData 块**

| 字段 | 类型 | 说明 |
|------|------|------|
| items | array | 版本列表 |
| count | int | 版本总数 |

**版本对象字段**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 版本 ID |
| displayVersion | string | 版本号 |
| remark | string | 备注 |
| isLinkFirst | boolean | 是否链接优先 |
| isCurrent | boolean | 是否当前版本 |
| createdAt | string | 创建时间 |
| createdBy | string | 创建人昵称 |
| allowedFileExtensions | array | 允许的文件扩展名类型列表 |
| template | object/null | 模板信息 |

**others 块**

| 字段 | 类型 | 说明 |
|------|------|------|
| createdAt | string | 创建时间 |
| updatedAt | string | 更新时间 |
| versionCount | int | 版本总数 |

**错误响应示例**

```json
{
  "msg": "交付物定义不存在"
}
```

---

### 7. 版本迭代

**PUT** `/psc/deliverable/definitions/<id>`

创建新版本（不更新 `code`、`isActive`），`name` 可在版本迭代时修改。

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 交付物定义 ID |

**请求体**

```json
{
  "name": "需求文档（更新版）",
  "displayVersion": "2.0",
  "remark": "更新备注",
  "isLinkFirst": false,
  "allowedFileExtensionsIds": [1, 2],
  "feishuTemplate": {
    "title": "新模板",
    "token": "xyz789",
    "category": "document",
    "original_url": "https://example.com/new-template"
  }
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 否 | 新版本名称（不传则使用上一个版本的 name） |
| displayVersion | string | 否 | 版本号（默认：1.0） |
| remark | string | 否 | 备注 |
| isLinkFirst | boolean | 否 | 是否链接优先 |
| allowedFileExtensionsIds | array[int] | 否 | 允许的文件扩展名类型 ID 列表 |
| feishuTemplate | object | 否 | 飞书模板信息 |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "document": {
      "code": "DELIV001",
      "name": "需求文档（更新版）",
      "isActive": true
    },
    "versionData": {
      "items": [
        {
          "id": 2,
          "displayVersion": "2.0",
          "remark": "更新备注",
          "isLinkFirst": false,
          "isCurrent": true,
          "createdAt": "2024-01-02T00:00:00+08:00",
          "createdBy": "张三",
          "allowedFileExtensions": [
            {"id": 1, "name": ".pdf"},
            {"id": 2, "name": ".docx"}
          ],
          "template": {
            "id": 2,
            "name": "新模板",
            "storageProvider": "feishu"
          }
        }
      ],
      "count": 2
    },
    "others": {
      "createdAt": "2024-01-01 00:00:00",
      "updatedAt": "2024-01-02 00:00:00",
      "versionCount": 2
    }
  }
}
```

**错误响应示例**

```json
{
  "msg": "参数错误",
  "errors": {
    "name": ["\"需求文档（更新版）\"已被该交付物定义的其他版本使用，请更换名称后重试"]
  }
}
```

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
# 1. 获取简化列表
curl -X GET "http://localhost:8001/psc/deliverable/definitions/simple" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 2. 获取分页列表
curl -X GET "http://localhost:8001/psc/deliverable/definitions/list?pageNum=1&pageSize=10&currentName=需求" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 3. 创建交付物定义
curl -X POST "http://localhost:8001/psc/deliverable/definitions/list" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "需求文档",
    "isLinkFirst": true
  }'

# 4. 获取详情
curl -X GET "http://localhost:8001/psc/deliverable/definitions/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 5. 版本迭代
curl -X PUT "http://localhost:8001/psc/deliverable/definitions/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "需求文档 v2.0",
    "displayVersion": "2.0"
  }'

# 6. 批量更新
curl -X PATCH "http://localhost:8001/psc/deliverable/definitions/list" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "ids": [1, 2, 3],
    "isActive": false
  }'

# 7. 批量删除
curl -X DELETE "http://localhost:8001/psc/deliverable/definitions/list" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "ids": [1, 2, 3]
  }'
```

---

## 数据模型

### DeliverableDefinition 模型字段

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| code | string(255) | 唯一标识（自动生成，格式：DELIV+序号） |
| is_active | boolean | 是否启用 |
| created_at | DateTime | 创建时间 |

### DeliverableDefinitionVersion 模型字段

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| deliverable_definition | FK | 关联的交付物定义 |
| version_number | int | 版本号内部 |
| display_version | string(50) | 显示版本号 |
| name | string(255) | 交付物定义名称 |
| remark | text | 备注 |
| is_link_first | boolean | 是否链接优先 |
| is_current | boolean | 是否当前版本 |
| allowed_file_extensions | M2M | 允许的文件扩展名类型 |
| created_at | DateTime | 创建时间 |
| created_by | FK(User) | 创建人 |

### 表名

- `PSC_deliverable_definition` - 交付物定义主表
- `PSC_deliverable_definition_version` - 交付物定义版本表

---

## 设计说明

### 版本管理机制

交付物定义采用**主模型 + 版本模型**的双表设计：

1. **主模型**（DeliverableDefinition）：只保留 `code`、`isActive` 等稳定字段
2. **版本模型**（DeliverableDefinitionVersion）：存储可变业务数据（`name`、`remark` 等）
3. 每次编辑时创建新版本，旧版本保留用于历史追溯

### 字段权限说明

| 字段 | POST | PUT | PATCH |
|------|------|-----|-------|
| code | 可选（自动生成） | 禁止修改 | 禁止修改 |
| name | 必填 | 可选（版本迭代） | 禁止修改 |
| isActive | 固定 true | 禁止修改 | 可修改 |
| 版本相关字段 | 可选 | 可选 | 禁止修改 |

### 唯一性验证规则

1. **code**：全局唯一，创建后不可修改
2. **name**：
   - POST 创建时：全局唯一（不能与其他交付物定义的当前版本重名）
   - PUT 版本迭代时：同一交付物定义内唯一（不能与自己的其他版本重名）
