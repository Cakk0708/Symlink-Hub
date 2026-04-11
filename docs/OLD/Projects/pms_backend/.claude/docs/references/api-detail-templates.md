# API 接口详情模板

本文档提供各类接口的详细文档模板，用于生成标准化的 API 接口文档。

---

## LIST 接口（获取列表）

### 描述

获取资源列表，支持分页、搜索、排序和过滤。

### 请求

```
GET {base_url}/{resource_path}
```

**请求头：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| Authorization | string | 是 | JWT Token，格式：`Bearer {token}` |

**查询参数：**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| page | integer | 否 | 0 | 页码 |
| page_size | integer | 否 | 10 | 每页数量 |
| search | string | 否 | - | 搜索关键词 |
| ordering | string | 否 | - | 排序字段，如 `created_at` 或 `-created_at` |
| {filter_field} | mixed | 否 | - | 过滤条件（根据实际字段填写） |

### 响应

**成功响应（200 OK）：**

```json
{
  "msg": "success",
  "data": {
    "count": 100,
    "next": "http://api.example.com/{resource_path}?page=1",
    "previous": null,
    "results": [
      {
        "id": 1,
        "{field}": "{value}",
        "created_at": "2025-01-01T00:00:00+08:00",
        "updated_at": "2025-01-01T00:00:00+08:00"
      }
    ]
  }
}
```

**响应字段说明：**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| count | integer | 总记录数 |
| next | string/null | 下一页链接 |
| previous | string/null | 上一页链接 |
| results | array | 数据列表 |

---

## CREATE 接口（创建资源）

### 描述

创建新资源。

### 请求

```
POST {base_url}/{resource_path}
```

**请求头：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| Authorization | string | 是 | JWT Token |
| Content-Type | string | 是 | `application/json` |

**请求体：**

```json
{
  "{field}": "{value}",
  "{another_field}": "{another_value}"
}
```

**请求参数说明：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| {field} | {type} | {yes/no} | {description} |
| {another_field} | {type} | {yes/no} | {description} |

### 响应

**成功响应（201 Created）：**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "{field}": "{value}",
    "created_at": "2025-01-01T00:00:00+08:00",
    "updated_at": "2025-01-01T00:00:00+08:00"
  }
}
```

**错误响应（400 Bad Request）：**

```json
{
  "msg": "error",
  "data": {
    "{field}": ["{error_message}"]
  }
}
```

---

## RETRIEVE 接口（获取详情）

### 描述

获取单个资源的详细信息。

### 请求

```
GET {base_url}/{resource_path}/{id}
```

**请求头：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| Authorization | string | 是 | JWT Token |

**路径参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | integer | 是 | 资源 ID |

### 响应

**成功响应（200 OK）：**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "{field}": "{value}",
    "created_at": "2025-01-01T00:00:00+08:00",
    "updated_at": "2025-01-01T00:00:00+08:00"
  }
}
```

**错误响应（404 Not Found）：**

```json
{
  "msg": "error",
  "data": "资源不存在"
}
```

---

## UPDATE 接口（更新资源）

### 描述

更新现有资源的全部或部分字段。

### 请求

```
PUT {base_url}/{resource_path}/{id}
```

**请求头：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| Authorization | string | 是 | JWT Token |
| Content-Type | string | 是 | `application/json` |

**路径参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | integer | 是 | 资源 ID |

**请求体：**

```json
{
  "{field}": "{new_value}",
  "{another_field}": "{new_value}"
}
```

### 响应

**成功响应（200 OK）：**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "{field}": "{new_value}",
    "updated_at": "2025-01-01T10:00:00+08:00"
  }
}
```

**错误响应（400 Bad Request）：**

```json
{
  "msg": "error",
  "data": {
    "{field}": ["{error_message}"]
  }
}
```

---

## PARTIAL UPDATE 接口（部分更新）

### 描述

部分更新资源字段（PATCH 请求）。

### 请求

```
PATCH {base_url}/{resource_path}/{id}
```

**请求体：**

```json
{
  "{field}": "{new_value}"
}
```

### 响应

同 UPDATE 接口。

---

## DELETE 接口（删除单个资源）

### 描述

删除单个资源。

### 请求

```
DELETE {base_url}/{resource_path}/{id}
```

**请求头：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| Authorization | string | 是 | JWT Token |

**路径参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | integer | 是 | 资源 ID |

### 响应

**成功响应（204 No Content）：**

无响应体

---

## BULK DELETE 接口（批量删除）

### 描述

批量删除多个资源。

### 请求

```
DELETE {base_url}/{resource_path}
```

**请求头：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| Authorization | string | 是 | JWT Token |
| Content-Type | string | 是 | `application/json` |

**请求体：**

```json
{
  "ids": [1, 2, 3]
}
```

**请求参数说明：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| ids | array | 是 | 要删除的资源 ID 列表 |

### 响应

**成功响应（200 OK）：**

```json
{
  "msg": "success",
  "data": {
    "deleted_count": 3
  }
}
```

---

## ACTION 接口（自定义操作）

### 描述

自定义操作接口（如 `@action` 装饰器定义的接口）。

### 请求

```
POST {base_url}/{resource_path}/{id}/{action_name}/
```

**请求头：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| Authorization | string | 是 | JWT Token |
| Content-Type | string | 是 | `application/json` |

**路径参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | integer | 是 | 资源 ID |

**请求体（可选）：**

```json
{
  "{param}": "{value}"
}
```

### 响应

**成功响应（200 OK）：**

```json
{
  "msg": "success",
  "data": {
    "{result_field}": "{result_value}"
  }
}
```

---

## 注意事项

1. **时间格式**：所有时间字段使用 ISO 8601 格式，时区为 `Asia/Shanghai`
2. **分页格式**：使用 `PageNumberPagination`，从 `page=0` 开始
3. **错误响应**：统一使用 `{ "msg": "error", "data": "error message" }` 格式
4. **认证**：除特殊说明外，所有接口需要 JWT 认证
5. **权限**：部分接口可能需要特定权限，详见各接口说明
