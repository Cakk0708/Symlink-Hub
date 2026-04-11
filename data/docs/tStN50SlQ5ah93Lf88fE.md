# BDM - Account 接口文档

> 最后更新：2026-04-09
> App: `BDM` | Model: `Account`
> Base URL: `/api/bdm`

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
| GET | `/account` | 获取账户列表 | ✅ |
| POST | `/account` | 创建账户 | ✅ |
| GET | `/account/simple` | 获取账户简表（下拉列表） | ✅ |
| GET | `/account/{id}` | 获取账户详情 | ✅ |
| POST | `/account/{id}` | 主动同步账户信息 | ✅ |
| PATCH | `/account/{id}` | 更新账户 | ✅ |
| PATCH | `/account/{id}/disable` | 禁用/启用账户 | ✅ |
| GET | `/account/{id}/leaderboard` | 获取排行榜数据 | ✅ |
| POST | `/account/credentials/verify` | 统一账户验证（用户名/手机/Token） | ✅ |
| POST | `/account/verification-codes` | 发送验证码 | ✅ |

---

## 接口详情

### 1. 获取账户列表

**GET** `/account`

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，从 0 开始，默认 0 |
| phone | string | 否 | 按手机号筛选（模糊匹配） |
| name | string | 否 | 按用户名筛选（模糊匹配） |
| customer | int | 否 | 按客户 ID 筛选 |
| search | string | 否 | 全局搜索（用户名/手机号/昵称） |

**响应示例**

```json
{
  "msg": "success",
  "items": [
    {
      "id": 1,
      "code": "A20250308001",
      "email": "test@example.com",
      "username": "test_user",
      "nickname": "测试用户",
      "phone": "13800138000",
      "remark": "备注信息",
      "exp": 1000,
      "gems": 500,
      "customer": 1,
      "organizationName": "示例组织",
      "createdAt": "2024-01-01 00:00:00",
      "updatedAt": "2024-01-01 00:00:00",
      "lastSign": "2024-01-01"
    }
  ],
  "pagination": {
    "page": 0,
    "page_size": 10,
    "total": 100
  }
}
```

---

### 2. 创建账户

**POST** `/account`

**请求体**

```json
{
  "cacheKey": "abc123...",
  "customerId": 1,
  "remark": "备注信息（可选）"
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| cacheKey | string | ✅ | 缓存 Key，从账户验证接口获取 |
| customerId | int | ✅ | 客户 ID |
| remark | string | 否 | 备注信息 |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "username": "test_user",
    "uuid": "abc-123-def-456"
  }
}
```

---

### 3. 获取账户简表（下拉列表）

**GET** `/account/simple?customer_id={id}`

用于前端下拉选择组件，支持按客户 ID 过滤。

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| customer_id | int | 否 | 客户 ID，用于过滤指定客户的账户 |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "items": [
      {
        "value": 1,
        "label": "test_user",
        "nickname": "测试用户",
        "phone": "13800138000",
        "organization": {
          "id": 1,
          "name": "示例组织"
        }
      }
    ],
    "count": 10
  }
}
```

---

### 4. 获取账户详情

**GET** `/account/{id}`

获取账户详细信息。

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 账户 ID |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "document": {
      "code": "A20250308001",
      "uuid": "abc-123-def-456",
      "username": "test_user",
      "nickname": "测试用户",
      "email": "test@example.com"
    },
    "accountData": {
      "gems": 500,
      "exp": 1000,
      "checkInStreak": 7,
      "isTodayCheckedIn": true,
      "lastSign": "2024-03-22"
    },
    "others": {
      "remark": "备注信息",
      "createdAt": "2024-01-01 00:00:00",
      "updatedAt": "2024-03-22 12:00:00"
    }
  }
}
```

**响应字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 账户 ID |
| document | object | 基本信息 |
| document.code | string | 账户编码 |
| document.uuid | string | Duolingo 用户 UUID |
| document.username | string | 用户名 |
| document.nickname | string | 昵称 |
| document.email | string | 邮箱 |
| accountData | object | 游戏数据 |
| accountData.gems | int | 宝石数量 |
| accountData.exp | int | 经验值 |
| accountData.checkInStreak | int | 连续打卡天数 |
| accountData.isTodayCheckedIn | bool | 今天是否已打卡 |
| accountData.lastSign | string | 最后学习日期（YYYY-MM-DD） |
| others | object | 系统信息 |
| others.remark | string | 备注信息 |
| others.createdAt | string | 创建时间 |
| others.updatedAt | string | 更新时间 |

---

### 5. 主动同步账户信息

**POST** `/account/{id}`

从 Duolingo API 获取最新数据并更新账户信息。

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 账户 ID |

**响应示例（成功）**

```json
{
  "msg": "success",
  "message": "账户 test_user 同步成功",
  "data": {
    "id": 1,
    "document": {
      "code": "A20250308001",
      "uuid": "abc-123-def-456",
      "username": "test_user",
      "nickname": "测试用户",
      "email": "test@example.com"
    },
    "accountData": {
      "gems": 500,
      "exp": 1000,
      "checkInStreak": 7,
      "isTodayCheckedIn": true,
      "lastSign": "2024-03-22"
    },
    "others": {
      "remark": "备注信息",
      "createdAt": "2024-01-01 00:00:00",
      "updatedAt": "2024-03-22 12:00:00"
    }
  }
}
```

**响应示例（失败）**

```json
{
  "msg": "error",
  "data": "账户 test_user 同步失败"
}
```

---

### 6. 更新账户

**PATCH** `/account/{id}`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 账户 ID |

**请求体**

```json
{
  "remark": "更新后的备注"
}
```

**响应示例**

```json
{
  "msg": "success"
}
```

---

### 7. 统一账户验证

**POST** `/account/credentials/verify`

支持三种验证方式：
1. 用户名密码验证 (`type=username`)
2. 手机验证码验证 (`type=phone`)
3. Token 验证 (`type=token`)

**请求体（用户名密码验证）**

```json
{
  "type": "username",
  "username": "test_user",
  "password": "password123"
}
```

**请求体（手机验证码验证）**

```json
{
  "type": "phone",
  "verificationKey": "abc123...",
  "code": "123456"
}
```

**请求体（Token 验证）**

```json
{
  "type": "token",
  "token": "jwt_token_here"
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | ✅ | 验证类型：`username`、`phone` 或 `token` |
| username | string | type=username 时必填 | Duolingo 用户名 |
| password | string | type=username 时必填 | Duolingo 密码 |
| verificationKey | string | type=phone 时必填 | 验证码 Key，从 verification-codes 接口获取 |
| code | string | type=phone 时必填 | 验证码 |
| token | string | type=token 时必填 | JWT Token |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "checkPassed": true,
    "cacheKey": "abc123..."
  }
}
```

**注意**：`cacheKey` 有效期为 1 小时，用于后续创建账户。

---

### 8. 发送验证码

**POST** `/account/verification-codes`

发送验证码到手机号或邮箱。

**请求体**

```json
{
  "target": "13800138000",
  "type": "sms",
  "scene": "login"
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| target | string | ✅ | 目标地址（手机号或邮箱） |
| type | string | ✅ | 发送类型：`sms`（短信）或 `mail`（邮件） |
| scene | string | 否 | 使用场景：`login`（默认） |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "key": "abc123..."
  }
}
```

**注意**：
- `key` 有效期为 10 分钟
- 目前仅支持短信验证码，邮箱验证码暂不支持

---

### 9. 禁用/启用账户

**PATCH** `/account/{id}/disable`

切换账户的禁用状态。

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 账户 ID |

**请求体**

```json
{
  "disableFlag": true
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| disableFlag | boolean | ✅ | `true` 禁用，`false` 启用 |

**响应示例**

```json
{
  "msg": "success"
}
```

---

### 10. 获取排行榜数据

**GET** `/account/{id}/leaderboard`

获取该账户在 Duolingo 排行榜中的联赛数据。

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 账户 ID |

**响应示例**

```json
{
  "msg": "success",
  "data": [
    {
      "display_name": "阿祥",
      "score": 6085,
      "user_id": 632304158564190,
      "avatar_url": "https://simg-ssl.duolingo.com/ssr-avatars/...",
      "has_plus": false,
      "streak_extended_today": false,
      "has_recent_activity_15": false,
      "duolingo_score_info": {
        "course_id": "DUOLINGO_EN_ZH-CN",
        "score": 59
      },
      "reaction": "NONE"
    }
  ]
}
```

**响应字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| display_name | string | 用户昵称 |
| score | int | 排行榜积分 |
| user_id | int | Duolingo 用户 ID |
| avatar_url | string | 头像 URL |
| has_plus | boolean | 是否有 Plus 订阅 |
| streak_extended_today | boolean | 今日是否已打卡 |
| has_recent_activity_15 | boolean | 近 15 分钟是否有活动 |
| duolingo_score_info | object | Duolingo 分数信息 |
| duolingo_score_info.course_id | string | 课程 ID |
| duolingo_score_info.score | int/null | 课程分数 |
| reaction | string | 反应类型 |

**错误响应**

| HTTP 状态码 | 说明 |
|-------------|------|
| 400 | 获取排行榜数据失败 |
| 404 | 账户不存在 |
| 500 | 获取排行榜数据异常（Duolingo API 调用失败） |

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
# 1. 获取账户列表
curl -X GET "http://localhost:8101/api/bdm/account?page=0&phone=138" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 2. 用户名密码验证
curl -X POST "http://localhost:8101/api/bdm/account/credentials/verify" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"type":"username","username":"test_user","password":"password123"}'

# 3. 发送验证码
curl -X POST "http://localhost:8101/api/bdm/account/verification-codes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"target":"13800138000","type":"sms"}'

# 4. 手机验证码验证
curl -X POST "http://localhost:8101/api/bdm/account/credentials/verify" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"type":"phone","verificationKey":"abc123...","code":"123456"}'

# 5. 创建账户
curl -X POST "http://localhost:8101/api/bdm/account" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"cacheKey":"abc123...","customerId":1}'

# 6. 获取账户简表
curl -X GET "http://localhost:8101/api/bdm/account/simple" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 7. 获取账户详情
curl -X GET "http://localhost:8101/api/bdm/account/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 8. 主动同步账户信息
curl -X POST "http://localhost:8101/api/bdm/account/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 9. 更新账户
curl -X PATCH "http://localhost:8101/api/bdm/account/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"remark":"更新备注"}'

# 10. 禁用/启用账户
curl -X PATCH "http://localhost:8101/api/bdm/account/1/disable" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"disableFlag":true}'

# 11. 获取排行榜数据
curl -X GET "http://localhost:8101/api/bdm/account/1/leaderboard" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 业务流程说明

### 账户创建完整流程

1. **验证凭证** → 调用 `/account/credentials/verify` 获取 `cacheKey`
2. **创建账户** → 调用 `/account` 使用 `cacheKey` 创建账户

### 手机号登录流程

1. **发送验证码** → 调用 `/account/verification-codes` 获取 `key`
2. **验证码登录** → 调用 `/account/credentials/verify` 使用 `key` 和验证码获取 `cacheKey`
3. **创建账户** → 调用 `/account` 使用 `cacheKey` 创建账户

---

## 模型字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 ID |
| code | string | 账户编码（自动生成，格式：A + 日期 + 序号） |
| uuid | string | Duolingo 用户 UUID |
| email | string | 邮箱 |
| username | string | Duolingo 用户名 |
| nickname | string | 昵称 |
| password | string | Duolingo 密码（加密存储） |
| phone | string | 手机号 |
| token | string | Duolingo API Token |
| remark | string | 备注信息 |
| customer | int | 关联客户 ID |
| organization | int | 所属组织 ID |
| gems | int | 宝石数量 |
| exp | int | 经验值 |
| check_in_streak | int | 连续打卡天数 |
| is_today_checked_in | bool | 今天是否已打卡 |
| last_sign | date | 最后学习日期 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |
| disable_flag | boolean | 禁用标志 |
