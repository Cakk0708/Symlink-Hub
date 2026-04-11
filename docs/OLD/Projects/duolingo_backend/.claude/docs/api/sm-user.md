# SM - User 接口文档

> 最后更新：2026-03-15
> App: `SM` | Model: `User`
> Base URL: `/api/sm`

---

## 认证说明

除登录和注册接口外，所有接口均需在请求头中携带 JWT Token：

```
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## 接口列表

| 方法 | 路径 | 描述 | 需要认证 |
|------|------|------|----------|
| GET | `/user` | 获取用户列表 | ✅ |
| POST | `/user/<id>` | 用户登录（按ID） | ✅ |
| POST | `/user/login` | 用户登录（用户名密码） | ❌ |
| POST | `/user/register` | 用户注册 | ❌ |

---

## 接口详情

### 1. 获取用户列表

**GET** `/user`

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，从 1 开始，默认 1 |
| username | string | 否 | 按用户名模糊搜索 |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "username": "testuser",
        "nickname": "测试用户",
        "organizationName": "测试组织",
        "createdAt": "2024-01-01T00:00:00Z",
        "created_at": "2024-01-01 08:00:00"
      }
    ],
    "pagination": {
      "total": 100,
      "start": 0,
      "end": 10
    }
  }
}
```

---

### 2. 用户登录（按ID）

**POST** `/user/<id>`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 用户 ID |

**响应示例**

```json
{
  "msg": "登录成功",
  "data": {
    "user": "testuser",
    "token": {
      "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
      "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
  }
}
```

---

### 3. 用户登录（用户名密码）

**POST** `/user/login`

**请求体**

```json
{
  "username": "testuser",
  "password": "password123"
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | ✅ | 用户名 |
| password | string | ✅ | 密码 |

**响应示例**

```json
{
  "msg": "登录成功",
  "data": {
    "user": "testuser",
    "token": {
      "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
      "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
  }
}
```

---

### 4. 用户注册

**POST** `/user/register`

**请求体**

```json
{
  "username": "newuser",
  "password": "password123",
  "nickname": "新用户"
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | ✅ | 用户名 |
| password | string | ✅ | 密码 |
| nickname | string | ❌ | 昵称 |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 2,
    "username": "newuser",
    "nickname": "新用户",
    "organizationName": null,
    "createdAt": "2024-01-01T00:00:00Z"
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
# 1. 获取用户列表
curl -X GET "http://localhost:8101/api/sm/user?page=1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 2. 按用户名搜索
curl -X GET "http://localhost:8101/api/sm/user?username=test" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 3. 用户登录
curl -X POST "http://localhost:8101/api/sm/user/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'

# 4. 用户注册
curl -X POST "http://localhost:8101/api/sm/user/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"newuser","password":"password123","nickname":"新用户"}'

# 5. 按ID登录
curl -X POST "http://localhost:8101/api/sm/user/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 数据模型

### User

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 用户 ID |
| username | string | 用户名 |
| nickname | string | 昵称 |
| organization | Organization (OneToOne) | 所属组织 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

---

## 备注

<!-- NOTE: 此文档由自动生成工具创建，如有疑问请联系开发团队 -->
