# BDM - Customer 接口文档

> 最后更新：2026-03-21
> App: `BDM` | Model: `Customer`
> Base URL: `/api`

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
| GET | `/customer` | 获取列表 | ✅ |
| GET | `/customer/<int:id>` | 获取详情 | ✅ |
| POST | `/customer` | 创建 | ✅ |
| DELETE | `/customer` | 批量删除 | ✅ |
| GET | `/customer/simple` | 简略列表（下拉选择） | ✅ |
| GET | `/customer/enums` | 获取枚举定义 | ✅ |

---

## 接口详情

### 1. 获取客户列表

**GET** `/customer`

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，从 0 开始，默认 0 |
| name | string | 否 | 按客户名称模糊搜索 |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "code": "C20250315001",
        "name": "张三",
        "categoryDisplay": "闲鱼",
        "createdAt": "2025-03-15 10:30:00",
        "updatedAt": "2025-03-15 10:30:00",
        "orderCount": 5,
        "accountCount": 2,
        "organizationName": "示例组织"
      }
    ],
    "pagination": {
      "page": 0,
      "pageSize": 10,
      "total": 100
    }
  }
}
```

**字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 客户 ID |
| code | string | 客户编码（自动生成，格式：C + 日期 + 序号） |
| name | string | 客户名称 |
| categoryDisplay | string | 类别显示名称（如"闲鱼"） |
| createdAt | string | 创建时间（本地时间格式） |
| updatedAt | string | 更新时间（本地时间格式） |
| orderCount | int | 关联订单数量 |
| accountCount | int | 关联账户数量 |
| organizationName | string | 所属组织名称 |

---

### 2. 获取客户详情

**GET** `/customer/<int:id>`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 客户 ID |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "code": "C20250315001",
    "name": "张三",
    "categoryDisplay": "闲鱼",
    "createdAt": "2025-03-15 10:30:00",
    "updatedAt": "2025-03-15 10:30:00",
    "orderCount": 5,
    "organizationName": "示例组织",
    "accounts": [
      {
        "id": 1,
        "username": "duolingo_user",
        "nickname": "多邻国用户",
        "email": "test@example.com",
        "phone": "13800138000"
      }
    ]
  }
}
```

**字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| accounts | array | 关联的 Duolingo 账户列表 |

**错误响应**

```json
{
  "msg": "error",
  "data": "客户不存在"
}
```

---

### 3. 创建客户

**POST** `/customer`

**请求体**

```json
{
  "name": "李四",
  "category": "GOOFISH"
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | ✅ | 客户名称（唯一） |
| category | string | 否 | 类别，默认 `GOOFISH`（闲鱼） |

**category 可选值**

| 值 | 显示名称 |
|----|---------|
| GOOFISH | 闲鱼 |
| WECHAT | 微信 |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "lastId": 2
  }
}
```

**注意**
- 客户 `code` 将自动生成（格式：C + 日期 + 序号，如 `C20250315001`）
- 自动关联当前用户的组织

---

### 4. 批量删除客户

**DELETE** `/customer`

**请求体**

```json
{
  "ids": [1, 2, 3]
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| ids | array | ✅ | 客户 ID 列表 |

**响应示例**

```json
{
  "msg": "success"
}
```

**错误响应示例**

```json
{
  "msg": "error",
  "data": "客户\"张三\"存在关联账户，无法删除"
}
```

---

### 5. 获取客户简略列表（下拉选择）

**GET** `/customer/simple`

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "items": [
      {
        "value": 1,
        "label": "张三",
        "code": "C20250315001",
        "category": "GOOFISH",
        "organization": {
          "id": 1,
          "name": "示例组织"
        }
      }
    ],
    "count": 50
  }
}
```

**字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| value | int | 客户 ID（用于下拉选择值） |
| label | string | 客户名称（用于下拉选择显示） |
| code | string | 客户编码 |
| category | string | 类别代码 |
| organization | object\|null | 所属组织信息 |

---

### 6. 获取枚举定义

**GET** `/customer/enums`

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "category": [
      ["GOOFISH", "闲鱼"],
      ["WECHAT", "微信"]
    ]
  }
}
```

**字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| category | array | 客户类别枚举，格式为 `[[值, 显示名], ...]` |

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
curl -X GET "http://localhost:8101/api/customer?page=0&name=张" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 2. 获取详情
curl -X GET "http://localhost:8101/api/customer/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 3. 创建客户
curl -X POST "http://localhost:8101/api/customer" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"name":"李四","category":"GOOFISH"}'

# 4. 批量删除
curl -X DELETE "http://localhost:8101/api/customer" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"ids":[1,2,3]}'

# 5. 获取简略列表
curl -X GET "http://localhost:8101/api/customer/simple" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 6. 获取枚举定义
curl -X GET "http://localhost:8101/api/customer/enums" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 数据模型

### Customer（客户）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| code | string | 客户编码（唯一，自动生成） |
| name | string | 客户名称 |
| category | string | 类别（GOOFISH: 闲鱼, WECHAT: 微信） |
| organization | Foreign Key | 所属组织 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

---

## 业务规则

1. **客户编码自动生成**：创建时自动生成，格式为 `C` + 日期（YYYYMMDD）+ 序号（如 `C20250315001`）
2. **名称唯一性**：同一客户名称不能重复
3. **组织关联**：创建客户时自动关联当前用户的组织
4. **删除限制**：存在关联账户的客户无法删除
5. **分页规则**：页码从 0 开始，默认每页 10 条