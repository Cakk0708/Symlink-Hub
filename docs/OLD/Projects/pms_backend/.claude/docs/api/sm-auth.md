# SM - 认证模块 API 文档

## 模块概述

提供用户认证、OAuth 2.0 飞书登录集成、Token 管理等功能。

**应用：** SM（系统管理）
**路径前缀：** `/api/sm/auth`
**认证方式：** 部分接口无需认证（AllowAny），部分需要 JWT Token

---

## 接口列表

### 1. 用户登录

**接口：** `POST /api/sm/auth/login`

**权限：** 无需认证（AllowAny）

**请求体：**

```json
{
  "provider": "FEISHU" | "OTHER",
  "loginType": "OAUTH" | "REQUEST_ACCESS" | "PASSWORD",
  "code": "string",
  "username": "string",
  "mobile": "string",
  "password": "string"
}
```

**参数说明：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| provider | string | 是 | 认证提供方：`FEISHU`(飞书)、`OTHER`(其他) |
| loginType | string | 是 | 登录类型：`OAUTH`、`REQUEST_ACCESS`(飞书请求访问)、`PASSWORD`(账号密码) |
| code | string | 条件 | 飞书授权码，provider=FEISHU 时必填 |
| username | string | 条件 | 用户名，provider=OTHER 时可填 |
| mobile | string | 条件 | 手机号，provider=OTHER 时可填 |
| password | string | 条件 | 密码，loginType=PASSWORD 时必填 |

**响应示例：**

```json
{
  "code": 0,
  "msg": "登录成功",
  "data": {
    "userinfo": {
      "id": 1,
      "username": "zhangsan",
      "avatar": "https://...",
      "disableFlag": false,
      "roles": [{"id": 1, "name": "管理员"}],
      "others": {
        "initialPassword": false,
        "createdAt": "2024-01-01 12:00:00",
        "lastLogin": "2024-03-31 18:00:00"
      }
    },
    "tokenData": {
      "access_token": "eyJ...",
      "refresh_token": "eyJ...",
      "token_type": "Bearer"
    },
    "authority": {
      "items": ["PM.add_project", "SM.change_user"],
      "total": 2
    }
  }
}
```

**错误响应：**

```json
{
  "code": -1,
  "msg": "参数错误：...",
  "errors": {...}
}
```

---

### 2. 刷新 Token

**接口：** `POST /api/sm/auth/refresh`

**权限：** 无需认证

**请求体：**

```json
{
  "token": "string"
}
```

**参数说明：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| token | string | 是 | refresh_token |

**响应示例：**

```json
{
  "msg": "success",
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ..."
  }
}
```

**错误响应：**

```json
{
  "code": -1,
  "msg": "Token 无效或已过期"
}
```

---

### 3. 飞书 OAuth 登录入口

**接口：** `GET /api/sm/auth/oauth/feishu/login`

**权限：** 无需认证（AllowAny）

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| redirect_uri | string | 是 | 前端回调地址 |

**行为：**
- 生成 OAuth state 参数
- 重定向到飞书授权页面

---

### 4. 飞书 OAuth 回调

**接口：** `GET /api/sm/auth/oauth/feishu/callback`

**权限：** 无需认证（AllowAny）

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | string | 是 | 飞书授权码 |
| state | string | 是 | OAuth state 参数 |

**行为：**
- 验证 state 参数
- 用 code 换取飞书 token
- 获取用户信息
- 处理/创建用户
- 重定向到前端并携带 ticket 和 state

---

### 5. 票据兑换

**接口：** `POST /api/sm/auth/oauth/exchange-ticket`

**权限：** 无需认证（AllowAny）

**请求体：**

```json
{
  "ticket": "string"
}
```

**参数说明：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| ticket | string | 是 | OAuth 回调获取的 ticket |

**响应示例：**

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "userinfo": {...},
    "tokenData": {...},
    "authority": {...}
  }
}
```

---

### 6. 认证枚举

**接口：** `GET /api/sm/auth/enums`

**权限：** 无需认证（AllowAny）

**响应示例：**

```json
{
  "msg": "success",
  "data": {
    "provider": [
      {"value": "FEISHU", "label": "飞书"},
      {"value": "OTHER", "label": "其他"}
    ],
    "loginType": [
      {"value": "OAUTH", "label": "OAuth"},
      {"value": "REQUEST_ACCESS", "label": "请求"},
      {"value": "PASSWORD", "label": "账号密码"}
    ]
  }
}
```

---

## 登录流程说明

### 飞书 OAuth 登录流程

1. 前端调用 `/api/sm/auth/oauth/feishu/login?redirect_uri=<前端地址>`
2. 后端重定向到飞书授权页面
3. 用户在飞书页面完成授权
4. 飞书回调到 `/api/sm/auth/oauth/feishu/callback`
5. 后端处理用户信息，生成 ticket，重定向回前端
6. 前端调用 `/api/sm/auth/oauth/exchange-ticket` 兑换完整用户信息

### 飞书请求访问码登录流程

1. 前端通过飞书 SDK 获取授权码
2. 前端调用 `/api/sm/auth/login`，provider=FEISHU, loginType=REQUEST_ACCESS
3. 后端用授权码换取 token 并获取用户信息
4. 返回完整的用户信息和 JWT token

### 账号密码登录流程

1. 前端调用 `/api/sm/auth/login`，provider=OTHER, loginType=PASSWORD
2. 后端验证用户名/手机号和密码
3. 返回用户信息和 JWT token

---

## 用户状态校验

登录时会校验以下用户状态：

| 状态 | 字段 | 校验条件 | 错误提示 |
|------|------|----------|----------|
| 禁用 | `disable_flag` | 为 True | "用户已被禁用" |
| 离职 | `is_in_service` | 为 False | "用户已离职" |
| 停用 | `is_active` | 为 False | "用户已被停用" |

---

## 数据模型

### LoginSerializer

登录序列化器，处理多种登录方式。

**字段验证规则：**

- `provider`：必选，FEISHU 或 OTHER
- `loginType`：必选，OAUTH、REQUEST_ACCESS 或 PASSWORD
- 飞书登录时必须提供 `code`
- 账号密码登录时必须提供 `password` 和 `username`/`mobile`（至少一个）

### OAuthCallbackSerializer

OAuth 回调序列化器。

**处理流程：**
1. 验证 state 参数（防止 CSRF）
2. 用 code 换取飞书 token
3. 获取用户信息
4. 创建/更新用户记录
5. 生成 ticket 返回

---

## 工具函数

### `_process_feishu_userinfo(token_data, userinfo)`

处理飞书用户信息，创建或更新用户记录。

### `_create_jwt_token(user_instance)`

为用户生成 JWT access_token 和 refresh_token。

### `generate_oauth_state(redirect_uri)`

生成 OAuth state 参数，存储到 Redis。

### `validate_oauth_state(state)`

验证 OAuth state 参数，从 Redis 获取原始数据。

### `create_login_ticket(userinfo, token_data)`

生成登录 ticket，存储到 Redis。

### `exchange_ticket(ticket)`

从 Redis 兑换 ticket 获取完整用户信息。

---

## 相关模块

- **SM.user**：用户管理模块
- **SM.permission**：权限管理模块
- **SM.role**：角色管理模块

---

## 更新日志

- 2024-03-31：初始版本，支持飞书 OAuth 2.0 登录、账号密码登录
