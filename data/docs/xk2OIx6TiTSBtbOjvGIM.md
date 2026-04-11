# SM - 用户管理模块 API 文档

## 模块概述

提供用户 CRUD、密码管理、用户查询等功能。

**应用：** SM（系统管理）
**路径前缀：** `/api/sm/user`
**认证方式：** 大部分接口需要 JWT Token

---

## 接口列表

### 1. 用户列表

**接口：** `GET /api/sm/user`

**权限：** 需要认证

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| query | string | 否 | 搜索关键词（匹配用户名/昵称） |
| role | number | 否 | 角色ID筛选 |
| pageNum | number | 否 | 页码，默认1 |
| pageSize | number | 否 | 每页条数，默认10 |
| sortField | string | 否 | 排序字段，默认id |
| sortOrder | string | 否 | 排序方向（asc/desc），默认desc |

**响应示例：**

```json
{
  "msg": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "username": "zhangsan",
        "nickname": "张三",
        "nicknamePinyin": [["zhang", "san"]],
        "avatar": "https://...",
        "mobile": "+8613800138000",
        "email": "zhangsan@example.com",
        "isSuperuser": false,
        "isInService": true,
        "roleName": "管理员, 开发者",
        "roles": [{"id": 1, "name": "管理员"}, {"id": 2, "name": "开发者"}],
        "createdAt": "2024-01-01 12:00:00"
      }
    ],
    "pagination": {
      "pageNum": 1,
      "pageSize": 10,
      "total": 4,
      "totalPages": 1
    }
  }
}
```

---

### 2. 创建用户

**接口：** `POST /api/sm/user`

**权限：** 需要认证

**请求体：**

```json
{
  "username": "string",
  "nickname": "string",
  "email": "string",
  "mobile": "string",
  "avatar": "string",
  "isSuperuser": false,
  "roles": [1, 2]
}
```

**参数说明：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名（唯一） |
| nickname | string | 否 | 昵称 |
| email | string | 否 | 邮箱（唯一） |
| mobile | string | 是 | 手机号（唯一，自动补充+86） |
| avatar | string | 否 | 头像 URL |
| isSuperuser | boolean | 否 | 是否超级管理员（仅超级用户可设置） |
| roles | number[] | 否 | 角色 ID 列表 |

**响应示例：**

```json
{
  "msg": "success",
  "data": {
    "insertId": 1
  }
}
```

**错误响应：**

```json
{
  "msg": "error",
  "errors": {
    "mobile": ["手机号已被使用"],
    "username": ["用户名已存在"]
  }
}
```

---

### 3. 批量删除用户

**接口：** `DELETE /api/sm/user`

**权限：** 仅超级用户可用

**请求体：**

```json
{
  "ids": [1, 2, 3]
}
```

**参数说明：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| ids | number[] | 是 | 用户 ID 列表 |

**行为：** 软删除（设置 `disable_flag=true`，`is_in_service=false`）

**限制：** 不能删除当前登录用户

**响应示例：**

```json
{
  "msg": "success",
  "data": null
}
```

---

### 4. 用户详情

**接口：** `GET /api/sm/user/{id}`

**权限：** 需要认证

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | number | 用户 ID |

**响应示例：**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "username": "zhangsan",
    "nickname": "张三",
    "nicknamePinyin": [["zhang", "san"]],
    "avatar": "https://...",
    "mobile": "+8613800138000",
    "email": "zhangsan@example.com",
    "isSuperuser": false,
    "isInService": true,
    "roleName": "管理员",
    "roles": [{"id": 1, "name": "管理员"}],
    "createdAt": "2024-01-01 12:00:00"
  }
}
```

---

### 5. 更新用户

**接口：** `PUT /api/sm/user/{id}`

**权限：** 需要认证

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | number | 用户 ID |

**请求体：**（所有字段可选）

```json
{
  "nickname": "string",
  "email": "string",
  "mobile": "string",
  "avatar": "string",
  "isSuperuser": false,
  "roles": [1, 2]
}
```

**可更新字段：**
- `is_superuser`（仅超级用户可修改）
- `nickname`
- `email`
- `mobile`
- `avatar`
- `roles`

**响应示例：**

```json
{
  "msg": "success",
  "data": {
    "id": 1
  }
}
```

---

### 6. 用户简化列表

**接口：** `GET /api/sm/user/simple`

**权限：** 需要认证

**说明：** 只返回 id、code、name、avatar、nicknamePinyin 等基础字段

**响应示例：**

```json
{
  "msg": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "code": "zhangsan",
        "name": "张三",
        "nickname": "张三",
        "nicknamePinyin": [["zhang", "san"]],
        "avatar": "https://...",
        "isInService": true
      }
    ],
    "total": 1
  }
}
```

---

### 7. 修改当前用户密码

**接口：** `POST /api/sm/user/password`

**权限：** 需要认证（修改当前登录用户密码）

**请求体：**

```json
{
  "oldPassword": "string",
  "password": "string"
}
```

**参数说明：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| oldPassword | string | 是 | 旧密码 |
| password | string | 是 | 新密码（最少 8 位） |

**验证规则：**
- 旧密码必须正确
- 新密码长度不少于 8 位

**响应示例：**

```json
{
  "msg": "success",
  "data": null
}
```

---

### 8. 重置用户密码

**接口：** `PATCH /api/sm/user/password/{id}`

**权限：** 仅超级用户可用

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | number | 用户 ID |

**请求体：** 无

**行为：** 将用户密码重置为系统初始密码（`INITIAL_PASSWORD` 配置项）

**响应示例：**

```json
{
  "msg": "success",
  "data": null
}
```

---

### 9. 用户枚举

**接口：** `GET /api/sm/user/enums`

**权限：** 需要认证

**响应示例：**

```json
{
  "msg": "success",
  "data": {
    "inService": [
      {"value": "1", "label": "在职"},
      {"value": "0", "label": "离职"}
    ],
    "isLeader": [
      {"value": "1", "label": "是"},
      {"value": "0", "label": "否"}
    ],
    "initialPassword": [
      {"value": "1", "label": "是"},
      {"value": "0", "label": "否"}
    ],
    "disableFlag": [
      {"value": "1", "label": "禁用"},
      {"value": "0", "label": "正常"}
    ],
    "isActive": [
      {"value": "1", "label": "激活"},
      {"value": "0", "label": "未激活"}
    ],
    "isStaff": [
      {"value": "1", "label": "是"},
      {"value": "0", "label": "否"}
    ],
    "isSuperuser": [
      {"value": "1", "label": "是"},
      {"value": "0", "label": "否"}
    ],
    "initialPasswordValue": "InitialPassword123!"
  }
}
```

---

## 数据模型

### User 模型

自定义用户模型，继承自 Django AbstractUser。

**核心字段：**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | number | 主键 |
| username | string | 用户名（唯一） |
| nickname | string | 昵称 |
| nickname_pinyin | json | 昵称拼音 |
| avatar | string | 头像 URL |
| mobile | string | 手机号（唯一） |
| email | string | 邮箱 |
| is_superuser | boolean | 是否超级管理员 |
| is_in_service | boolean | 是否在职 |
| disable_flag | boolean | 禁用标志 |
| initial_password | boolean | 是否初始密码 |
| uses | number | 使用次数 |
| date_joined | datetime | 创建时间 |
| last_login | datetime | 最后登录时间 |

### ListSerializer

用户列表序列化器。

**字段映射：**
- `createdAt` ← `date_joined`
- `nicknamePinyin` ← `nickname_pinyin`
- `isSuperuser` ← `is_superuser`
- `isInService` ← `is_in_service`
- `roleName` → SerializerMethodField（逗号拼接角色名称）
- `roles` → SerializerMethodField（角色列表 `[{id, name}]`）

### WriteSerializer

用户创建/更新序列化器。

**驼峰字段映射：**
- `isSuperuser` ← `is_superuser`（write_only）

**验证规则：**
- `username`：唯一性校验
- `email`：唯一性校验（可选）
- `mobile`：唯一性校验，自动补充 +86 前缀
- `isSuperuser`：仅超级用户可设置为 True

**创建行为：**
- 密码默认使用系统初始密码
- 支持角色分配

**更新行为：**
- 只允许更新特定字段（见上方接口 5）

### SimpleSerializer

用户简化序列化器。

**返回字段：**
- `id`、`code`（username）、`name`（nickname）、`nickname`、`nicknamePinyin`、`avatar`、`isInService`

### ChangePasswordSerializer

修改密码序列化器。

**验证规则：**
- `oldPassword`：必须与当前用户密码匹配
- `password`：长度不少于 8 位

### ResetPasswordSerializer

重置密码序列化器。

**权限：** 仅超级用户可用
**行为：** 重置为系统初始密码

### DeleteSerializer

删除用户序列化器。

**权限：** 仅超级用户可用
**行为：** 软删除（设置 disable_flag 和 is_in_service）
**限制：** 不能删除当前登录用户

---

## 权限说明

| 操作 | 权限要求 |
|------|----------|
| 查询列表/详情 | 需要登录 |
| 创建用户 | 需要登录 |
| 更新用户 | 需要登录 |
| 删除用户 | 仅超级用户 |
| 修改密码 | 修改自己的密码 |
| 重置密码 | 仅超级用户 |

---

## 相关模块

- **SM.auth**：认证登录模块
- **SM.role**：角色管理模块
- **SM.permission**：权限管理模块

---

## 更新日志

- 2026-04-09：移除 is_executive_core 字段及相关接口
- 2026-04-02：ListSerializer 增加 roleName/roles 字段；ParamsSerializer 增加 role 筛选参数；WriteSerializer 修复驼峰规范、提取角色分配函数
- 2024-03-31：初始版本，支持用户 CRUD、密码管理
