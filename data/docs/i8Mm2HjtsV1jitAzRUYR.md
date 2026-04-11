# PSC - ProjectRole 接口文档

> 最后更新：2026-03-21
> App: `PSC` | Model: `ProjectRole`
> Base URL: `/api/psc/role`

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
| GET | `/role` | 获取列表 | ✅ |
| GET | `/role/simple` | 获取简单列表 | ✅ |
| POST | `/role` | 创建 | ✅ |
| GET | `/role/{id}` | 获取详情 | ✅ |
| PUT | `/role/{id}` | 更新 | ✅ |
| PATCH | `/role/{id1,id2,...}` | 批量更新禁用状态 | ✅ |
| DELETE | `/role/{id1,id2,...}` | 批量删除 | ✅ |

---

## 接口详情

### 1. 获取项目角色列表

**GET** `/role`

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 否 | 按角色名称模糊搜索 |
| code | string | 否 | 按角色编码模糊搜索 |
| disableFlag | boolean | 否 | 按禁用状态筛选 |
| pageNum | int | 否 | 页码，从 1 开始，默认 1 |
| pageSize | int | 否 | 每页数量，默认 10 |
| pageSort | string | 否 | 排序，格式：`FIELD:ORDER`，如 `ID:DESC`，默认 `ID:DESC` |

**响应示例**

```json
{
  "msg": "success",
  "data": [
    {
      "id": 1,
      "code": "PROJROLE001",
      "name": "项目经理",
      "isEvaluatable": true,
      "isEvaluated": true,
      "disableFlag": false,
      "creator": "admin",
      "createTime": "2024-01-01T00:00:00+08:00"
    }
  ],
  "total": 100
}
```

---

### 2. 获取项目角色简单列表

**GET** `/role/simple`

获取所有启用状态的角色简单列表（无分页）。

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "name": "项目经理",
        "isEvaluatable": true,
        "isEvaluated": true,
        "hasEvaluationConfig": true
      }
    ],
    "total": 10
  }
}
```

---

### 3. 创建项目角色

**POST** `/role`

**请求体**

```json
{
  "code": "PROJROLE001",
  "name": "项目经理",
  "isEvaluatable": true,
  "isEvaluated": true
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | string | 否 | 角色编码，留空自动生成（格式：PROJROLE+序号） |
| name | string | ✅ | 角色名称 |
| isEvaluatable | boolean | ✅ | 是否可评价其他角色 |
| isEvaluated | boolean | ✅ | 是否可被其他角色评价 |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "insertId": 1
  }
}
```

---

### 4. 获取项目角色详情

**GET** `/role/{id}`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 项目角色 ID |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "code": "PROJROLE001",
    "name": "项目经理",
    "isEvaluatable": true,
    "isEvaluated": true,
    "disableFlag": false,
    "creator": "admin",
    "createTime": "2024-01-01T00:00:00+08:00"
  }
}
```

---

### 5. 更新项目角色

**PUT** `/role/{id}`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 项目角色 ID |

**请求体**

```json
{
  "name": "项目经理（更新）",
  "isEvaluatable": false,
  "isEvaluated": true
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | ✅ | 角色名称 |
| isEvaluatable | boolean | ✅ | 是否可评价其他角色 |
| isEvaluated | boolean | ✅ | 是否可被其他角色评价 |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "insertId": 1
  }
}
```

---

### 6. 批量更新禁用状态

**PATCH** `/role/{id1,id2,...}`

批量更新多个角色的禁用状态。

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | string | 多个角色 ID，用逗号分隔，如 `1,2,3` |

**请求体**

```json
{
  "disableFlag": true
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| disableFlag | boolean | ✅ | 禁用状态，`true` 禁用，`false` 启用 |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "updated": {
      "count": 3,
      "ids": [1, 2, 3]
    }
  }
}
```

---

### 7. 批量删除项目角色

**DELETE** `/role/{id1,id2,...}`

批量删除（软删除）多个角色。预置角色或存在评价配置的角色无法删除。

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | string | 多个角色 ID，用逗号分隔，如 `1,2,3` |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "deleted": {
      "count": 3,
      "ids": [1, 2, 3]
    }
  }
}
```

**错误示例**

```json
{
  "msg": "删除失败，共发现 2 个错误",
  "errors": {
    "项目经理": "该角色为预置角色，无法删除",
    "技术负责人": "该角色存在评价配置，无法删除"
  }
}
```

---

## 权限说明

接口需要以下权限（Django Permission 格式）：

| 操作 | 权限 Codename |
|------|--------------|
| 创建 | `PM.add_projectrole` |
| 查看 | `PM.view_projectrole` |
| 修改 | `PM.change_projectrole` |
| 删除 | `PM.delete_projectrole` |
| 禁用/启用 | `PM.disable_projectrole` |

---

## 错误响应

所有接口错误时统一返回：

```json
{
  "msg": "error",
  "data": "错误描述信息"
}
```

或验证失败时：

```json
{
  "msg": "数据验证失败",
  "errors": {
    "字段名": ["错误信息"]
  }
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
curl -X GET "http://your-domain/api/psc/role?pageNum=1&pageSize=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 2. 获取简单列表
curl -X GET "http://your-domain/api/psc/role/simple" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 3. 创建
curl -X POST "http://your-domain/api/psc/role" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "项目经理",
    "isEvaluatable": true,
    "isEvaluated": true
  }'

# 4. 获取详情
curl -X GET "http://your-domain/api/psc/role/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 5. 更新
curl -X PUT "http://your-domain/api/psc/role/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "项目经理（更新）",
    "isEvaluatable": false,
    "isEvaluated": true
  }'

# 6. 批量更新禁用状态
curl -X PATCH "http://your-domain/api/psc/role/1,2,3" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"disableFlag": true}'

# 7. 批量删除
curl -X DELETE "http://your-domain/api/psc/role/1,2,3" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 数据模型

### ProjectRole

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| code | string | 角色编码，唯一 |
| name | string | 角色名称 |
| is_evaluatable | boolean | 是否可评价其他角色 |
| is_evaluated | boolean | 是否可被其他角色评价 |
| disable_flag | boolean | 禁用状态 |
| creator | User (FK) | 创建人 |
| update_by | User (FK) | 最后修改人 |
| create_time | datetime | 创建时间 |
| update_time | datetime | 最后修改时间 |
| is_active | boolean | 是否为有效数据（软删除标记） |
| is_preset | boolean | 是否预设数据 |
| is_special_score | boolean | 分数是否特殊处理 |