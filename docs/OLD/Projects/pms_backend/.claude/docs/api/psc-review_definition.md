# PSC - ReviewDefinition 接口文档

> 最后更新：2026-03-21
> App: `PSC` | Model: `ReviewDefinition`
> Base URL: `/psc/review/definitions`

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
| GET | `/psc/review/definitions/simple` | 获取简化列表 | ✅ |
| GET | `/psc/review/definitions` | 获取分页列表 | ✅ |
| GET | `/psc/review/definitions/` | 获取分页列表 | ✅ |
| POST | `/psc/review/definitions` | 创建评审项定义 | ✅ |
| POST | `/psc/review/definitions/` | 创建评审项定义 | ✅ |
| PATCH | `/psc/review/definitions` | 批量更新（启用状态） | ✅ |
| PATCH | `/psc/review/definitions/` | 批量更新（启用状态） | ✅ |
| DELETE | `/psc/review/definitions` | 批量删除 | ✅ |
| DELETE | `/psc/review/definitions/` | 批量删除 | ✅ |
| GET | `/psc/review/definitions/<id>` | 获取详情 | ✅ |
| PUT | `/psc/review/definitions/<id>` | 版本迭代 | ✅ |

---

## 接口详情

### 1. 获取简化列表

**GET** `/psc/review/definitions/simple`

获取所有启用状态的评审项定义简化信息，仅返回 `id`、`code`、`name`、`currentVersionId` 等关键字段。适用于下拉选择等场景。

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "code": "REVIEW_DEF001",
        "currentName": "技术评审",
        "currentVersionId": 1
      },
      {
        "id": 2,
        "code": "REVIEW_DEF002",
        "currentName": "需求评审",
        "currentVersionId": 2
      }
    ],
    "total": 2
  }
}
```

**响应字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 评审项定义 ID |
| code | string | 唯一编码 |
| currentName | string | 当前版本名称 |
| currentVersionId | int | 当前版本 ID |

---

### 2. 获取分页列表

**GET** `/psc/review/definitions`

或

**GET** `/psc/review/definitions/`

**Query 参数**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| code | string | 否 | - | 搜索关键词（匹配唯一编码） |
| currentName | string | 否 | - | 搜索关键词（匹配当前版本名称） |
| isActive | boolean | 否 | - | 筛选启用状态 |
| pageNum | int | 否 | 1 | 页码 |
| pageSize | int | 否 | 10 | 每页数量 |
| pageSort | string | 否 | id:DESC | 排序字段（格式：字段:方向） |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "code": "REVIEW_DEF001",
        "isActive": true,
        "createdAt": "2024-01-01T00:00:00+08:00",
        "updatedAt": "2024-01-01T00:00:00+08:00",
        "currentName": "技术评审",
        "currentVersionId": 1,
        "currentVersionNumber": 1,
        "currentCreatedByNickname": "张三",
        "currentRemark": "技术方案评审项"
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
| id | int | 评审项定义 ID |
| code | string | 唯一编码 |
| isActive | boolean | 是否启用 |
| createdAt | string | 创建时间 |
| updatedAt | string | 更新时间 |
| currentName | string | 当前版本名称 |
| currentVersionId | int | 当前版本 ID |
| currentVersionNumber | int | 当前版本号 |
| currentCreatedByNickname | string | 当前版本创建人昵称 |
| currentRemark | string | 当前版本备注 |

---

### 3. 创建评审项定义

**POST** `/psc/review/definitions`

或

**POST** `/psc/review/definitions/`

创建评审项定义和第一个版本，`isActive` 默认为 `true`。

**请求体**

```json
{
  "code": "REVIEW_DEF001",
  "name": "技术评审",
  "remark": "技术方案评审项",
  "deliverableDefinitionVersionId": 1
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | string | 否 | 唯一编码（不传则自动生成，格式：REVIEW_DEF+序号） |
| name | string | ✅ | 评审项名称 |
| remark | string | 否 | 备注 |
| deliverableDefinitionVersionId | int | 否 | 关联的交付物定义版本 ID |

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
    "name": ["\"技术评审\"已被其他模板使用，请更换名称后重试"]
  }
}
```

---

### 4. 批量更新

**PATCH** `/psc/review/definitions`

或

**PATCH** `/psc/review/definitions/`

批量更新评审项定义的启用状态。

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
| ids | array[int] | ✅ | 评审项定义 ID 列表 |
| isActive | boolean | 否 | 新的启用状态 |

**响应示例**

```json
{
  "msg": "success，更新了 3 条记录"
}
```

---

### 5. 批量删除

**DELETE** `/psc/review/definitions`

或

**DELETE** `/psc/review/definitions/`

**请求体**

```json
{
  "ids": [1, 2, 3]
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| ids | array[int] | ✅ | 评审项定义 ID 列表 |

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
    "ids": ["\"REVIEW_DEF001\" 已被节点定义使用，无法删除"]
  }
}
```

---

### 6. 获取详情

**GET** `/psc/review/definitions/<id>`

获取评审项定义详情，数据分块输出：`document`（定义主体）、`versionData`（当前版本信息）、`others`（其他信息）。

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 评审项定义 ID |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "document": {
      "code": "REVIEW_DEF001",
      "name": "技术评审",
      "isActive": true
    },
    "versionData": {
      "id": 1,
      "versionNumber": 1,
      "isCurrent": true,
      "name": "技术评审",
      "remark": "技术方案评审项",
      "deliverableDefinitionVersion": {
        "id": 1,
        "displayVersion": "1.0",
        "deliverableDefinitionId": 1,
        "deliverableDefinitionName": "需求文档"
      }
    },
    "others": {
      "createdAt": "2024-01-01 00:00:00",
      "updatedAt": "2024-01-01 00:00:00",
      "versionCount": 1,
      "createdBy": {
        "id": 1,
        "nickname": "张三"
      },
      "updatedBy": {
        "id": 1,
        "nickname": "张三"
      }
    }
  }
}
```

**响应字段说明**

**document 块**

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 唯一编码 |
| name | string | 当前版本名称 |
| isActive | boolean | 是否启用 |

**versionData 块**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 版本 ID |
| versionNumber | int | 版本号 |
| isCurrent | boolean | 是否当前版本 |
| name | string | 版本名称 |
| remark | string | 备注 |
| deliverableDefinitionVersion | object | 关联的交付物定义版本信息 |

**others 块**

| 字段 | 类型 | 说明 |
|------|------|------|
| createdAt | string | 创建时间 |
| updatedAt | string | 更新时间 |
| versionCount | int | 版本总数 |
| createdBy | object | 创建人信息 |
| updatedBy | object | 最后修改人信息 |

**错误响应示例**

```json
{
  "msg": "评审项定义不存在"
}
```

---

### 7. 版本迭代

**PUT** `/psc/review/definitions/<id>`

创建新版本（不更新 `code`、`isActive`），`name` 可在版本迭代时修改。

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 评审项定义 ID |

**请求体**

```json
{
  "name": "技术评审（更新版）",
  "remark": "更新备注",
  "deliverableDefinitionVersionId": 2
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | ✅ | 新版本名称 |
| remark | string | 否 | 备注 |
| deliverableDefinitionVersionId | int | 否 | 关联的交付物定义版本 ID |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "document": {
      "code": "REVIEW_DEF001",
      "name": "技术评审（更新版）",
      "isActive": true
    },
    "versionData": {
      "id": 2,
      "versionNumber": 2,
      "isCurrent": true,
      "name": "技术评审（更新版）",
      "remark": "更新备注",
      "deliverableDefinitionVersion": {
        "id": 2,
        "displayVersion": "2.0",
        "deliverableDefinitionId": 1,
        "deliverableDefinitionName": "需求文档"
      }
    },
    "others": {
      "createdAt": "2024-01-01 00:00:00",
      "updatedAt": "2024-01-02 00:00:00",
      "versionCount": 2,
      "createdBy": {
        "id": 1,
        "nickname": "张三"
      },
      "updatedBy": {
        "id": 1,
        "nickname": "张三"
      }
    }
  }
}
```

**错误响应示例**

```json
{
  "msg": "参数错误",
  "errors": {
    "name": ["\"技术评审（更新版）\"已被其他模板使用，请更换名称后重试"]
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
curl -X GET "http://localhost:8001/psc/review/definitions/simple" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 2. 获取分页列表
curl -X GET "http://localhost:8001/psc/review/definitions?pageNum=1&pageSize=10&currentName=技术" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 3. 创建评审项定义
curl -X POST "http://localhost:8001/psc/review/definitions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "技术评审",
    "remark": "技术方案评审项"
  }'

# 4. 获取详情
curl -X GET "http://localhost:8001/psc/review/definitions/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 5. 版本迭代
curl -X PUT "http://localhost:8001/psc/review/definitions/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "技术评审 v2.0",
    "remark": "更新备注"
  }'

# 6. 批量更新
curl -X PATCH "http://localhost:8001/psc/review/definitions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "ids": [1, 2, 3],
    "isActive": false
  }'

# 7. 批量删除
curl -X DELETE "http://localhost:8001/psc/review/definitions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "ids": [1, 2, 3]
  }'
```

---

## 数据模型

### ReviewDefinition 模型字段

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| code | string(100) | 唯一编码（自动生成，格式：REVIEW_DEF+序号） |
| is_active | boolean | 是否启用 |
| created_at | DateTime | 创建时间 |

### ReviewDefinitionVersion 模型字段

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| review_definition | FK | 关联的评审项定义 |
| version_number | int | 版本号内部 |
| name | string(255) | 评审项名称 |
| deliverable_definition_version | FK | 关联的交付物定义版本 |
| remark | text | 备注 |
| is_current | boolean | 是否当前版本 |
| created_by | FK(User) | 创建人 |
| created_at | DateTime | 创建时间 |

### 表名

- `PSC_review_definition` - 评审项定义主表
- `PSC_review_definition_version` - 评审项定义版本表

---

## 设计说明

### 版本管理机制

评审项定义采用**主模型 + 版本模型**的双表设计：

1. **主模型**（ReviewDefinition）：只保留 `code`、`isActive` 等稳定字段
2. **版本模型**（ReviewDefinitionVersion）：存储可变业务数据（`name`、`remark`、`deliverable_definition_version` 等）
3. 每次编辑时创建新版本，旧版本保留用于历史追溯

### 字段权限说明

| 字段 | POST | PUT | PATCH |
|------|------|-----|-------|
| code | 可选（自动生成） | 禁止修改 | 禁止修改 |
| name | 必填 | 必填（版本迭代） | 禁止修改 |
| isActive | 固定 true | 禁止修改 | 可修改 |
| 版本相关字段 | 可选 | 可选 | 禁止修改 |

### 唯一性验证规则

1. **code**：全局唯一，创建后不可修改
2. **name**：
   - POST 创建时：全局唯一（不能与其他评审项定义的当前版本重名）
   - PUT 版本迭代时：全局唯一（不能与其他评审项定义的任何版本重名）

### 关联说明

- `deliverableDefinitionVersionId`：关联到交付物定义版本（DeliverableDefinitionVersion）
- 用于表示该评审项与特定交付物的关联关系
- 一个评审项可以关联一个交付物定义版本

---

## 使用场景

### 1. 创建评审项定义时关联交付物

在创建评审项定义时，可以指定关联的交付物定义版本：

```json
{
  "name": "技术评审",
  "remark": "技术方案评审项",
  "deliverableDefinitionVersionId": 1
}
```

### 2. 节点定义中使用评审项

节点定义可以关联多个评审项定义，通过评审项定义版本的 ID 进行关联。

### 3. 版本迭代

当评审项的内容需要更新时（如修改名称、关联不同的交付物），可以通过 PUT 接口创建新版本，旧版本保留用于历史追溯。