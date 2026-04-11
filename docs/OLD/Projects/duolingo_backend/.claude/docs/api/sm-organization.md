# SM - Organization 接口文档

> 最后更新：2026-03-15
> App: `SM` | Model: `Organization`
> Base URL: `/organizations`

---

## 认证说明

所有接口均需在请求头中携带 JWT Token：

```
Authorization: Bearer YOUR_JWT_TOKEN
```

**权限要求**: 所有接口都需要超级用户权限 (`is_superuser=True`)

---

## 接口列表

| 方法 | 路径 | 描述 | 需要认证 | 需要超级用户 |
|------|------|------|----------|-------------|
| GET | `/organizations` | 获取组织列表 | ✅ | ✅ |
| POST | `/organizations` | 创建组织 | ✅ | ✅ |
| DELETE | `/organizations` | 批量删除组织 | ✅ | ✅ |
| GET | `/organizations/{id}` | 获取组织详情 | ✅ | ✅ |
| PUT | `/organizations/{id}` | 更新组织 | ✅ | ✅ |

---

## 接口详情

### 1. 获取组织列表

**GET** `/organizations`

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，从 0 开始，默认 0 |
| name | string | 否 | 按组织名称模糊搜索 |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "code": "O202503150001",
        "name": "测试组织",
        "remark": "这是一个测试组织",
        "createdAt": "2025-03-15 10:30:00",
        "updatedAt": "2025-03-15 10:30:00"
      }
    ],
    "pagination": {
      "page": 0,
      "page_size": 10,
      "total": 1
    }
  }
}
```

**响应字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 组织 ID |
| code | string | 组织编码（唯一，格式：O + 日期 + 序号） |
| name | string | 组织名称 |
| remark | string | 备注 |
| createdAt | string | 创建时间（本地时间格式） |
| updatedAt | string | 更新时间（本地时间格式） |

---

### 2. 创建组织

**POST** `/organizations`

**请求体**

```json
{
  "name": "新组织",
  "remark": "组织备注信息"
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | ✅ | 组织名称（必须唯一） |
| remark | string | 否 | 备注信息 |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 2,
    "code": "O202503150002"
  }
}
```

**错误响应**（组织名称已存在）

```json
{
  "msg": "error",
  "data": {
    "name": [
      "组织名称\"新组织\"已存在"
    ]
  }
}
```

---

### 3. 批量删除组织

**DELETE** `/organizations`

**请求体**

```json
{
  "ids": [1, 2, 3]
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| ids | array[int] | ✅ | 待删除的组织 ID 列表 |

**响应示例**

```json
{
  "msg": "success"
}
```

**错误响应**（ids 为空）

```json
{
  "msg": "error",
  "data": {
    "ids": [
      "ids 不能为空"
    ]
  }
}
```

---

### 4. 获取组织详情

**GET** `/organizations/{id}`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 组织 ID |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "code": "O202503150001",
    "name": "测试组织",
    "remark": "这是一个测试组织",
    "createdAt": "2025-03-15 10:30:00",
    "updatedAt": "2025-03-15 10:30:00"
  }
}
```

**错误响应**（组织不存在）

```json
{
  "msg": "error",
  "data": "组织不存在"
}
```

---

### 5. 更新组织

**PUT** `/organizations/{id}`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 组织 ID |

**请求体**

```json
{
  "name": "更新后的组织名",
  "remark": "更新后的备注"
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 否 | 组织名称（必须唯一） |
| remark | string | 否 | 备注信息 |

**响应示例**

```json
{
  "msg": "success"
}
```

**错误响应**（组织不存在）

```json
{
  "msg": "error",
  "data": "组织不存在"
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
| 403 | 无权限（非超级用户） |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 完整 cURL 示例

```bash
# 1. 获取组织列表
curl -X GET "http://localhost:8101/organizations?page=0&name=测试" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 2. 创建组织
curl -X POST "http://localhost:8101/organizations" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"name":"新组织","remark":"备注信息"}'

# 3. 批量删除组织
curl -X DELETE "http://localhost:8101/organizations" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"ids":[1,2,3]}'

# 4. 获取组织详情
curl -X GET "http://localhost:8101/organizations/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 5. 更新组织
curl -X PUT "http://localhost:8101/organizations/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"name":"更新名称","remark":"更新备注"}'
```

---

## 业务规则

1. **编码自动生成**: 创建组织时自动生成唯一编码，格式为 `O + 日期 + 序号`（如 O202503150001）
2. **名称唯一性**: 组织名称在系统中必须唯一
3. **批量删除**: 支持批量删除，不存在的 ID 自动跳过
4. **分页规则**: 每页固定 10 条数据
5. **权限控制**: 所有接口仅超级用户可访问

<!-- NOTE: 如需添加更多接口说明，请在此处添加 -->
