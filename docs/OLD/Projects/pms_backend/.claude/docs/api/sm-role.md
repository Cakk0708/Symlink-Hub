# SM - 角色管理模块 API 文档

## 模块概述

提供角色的创建、查询、更新、删除功能，支持 BUILTIN（内置流程角色）和 CUSTOM（自定义角色）两种角色类型。

**应用：** SM（系统管理）
**路径前缀：** `/api/sm/roles`
**认证方式：** 需要 JWT Token

**角色类型说明：**
- **BUILTIN** — 系统预设的流程角色（项目负责人、节点负责人、节点协助者、管理者）
- **CUSTOM** — 用户创建的自定义角色

---

## 接口列表

### 1. 获取角色树（权限配置页专用）

**接口：** `GET /api/sm/roles/perm-tree`

**权限：** 需要认证

**说明：** 返回按类型分组的角色列表（排除系统管理员），用于权限配置页左侧角色树

**响应示例：**

```json
{
  "msg": "success",
  "data": {
    "builtin": [
      {
        "id": 1,
        "code": "PROJECT_OWNER",
        "name": "项目负责人",
        "roleType": "BUILTIN"
      },
      {
        "id": 2,
        "code": "NODE_OWNER",
        "name": "节点负责人",
        "roleType": "BUILTIN"
      },
      {
        "id": 3,
        "code": "NODE_ASSISTOR",
        "name": "节点协助者",
        "roleType": "BUILTIN"
      },
      {
        "id": 4,
        "code": "MANAGER",
        "name": "管理者",
        "roleType": "BUILTIN"
      }
    ],
    "custom": [
      {
        "id": 5,
        "code": "ROL00005",
        "name": "软件组",
        "roleType": "CUSTOM"
      },
      {
        "id": 6,
        "code": "ROL00006",
        "name": "硬件组",
        "roleType": "CUSTOM"
      }
    ]
  }
}
```

**数据结构：**
- `builtin`: 内置流程角色（系统预设），BUILTIN 类型
- `custom`: 自定义角色（用户创建），CUSTOM 类型
- 系统管理员角色 (SUPER_ADMIN) 不在列表中返回

---

### 2. 获取简化角色列表

**接口：** `GET /api/sm/role/simple`

**权限：** 需要认证

**说明：** 返回所有角色的简化列表（id, code, name, roleType），无分页，用于下拉选择框

**响应示例：**

```json
{
  "msg": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "code": "PROJECT_OWNER",
        "name": "项目负责人",
        "roleType": "BUILTIN"
      },
      {
        "id": 5,
        "code": "ROL00005",
        "name": "软件组",
        "roleType": "CUSTOM"
      }
    ],
    "total": 2
  }
}
```

---

### 3. 获取角色列表

**接口：** `GET /api/sm/role/list`

**权限：** 需要认证

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | number | 否 | 页码，默认 1 |
| pageSize | number | 否 | 每页数量，默认 10 |
| name | string | 否 | 角色名称（模糊查询） |
| code | string | 否 | 角色编码（精确查询） |
| roleType | string | 否 | 角色类型：BUILTIN / CUSTOM |
| disableFlag | boolean | 否 | 是否禁用（软删除） |

**响应示例：**

```json
{
  "msg": "success",
  "data": {
    "items": [
      {
        "id": 5,
        "code": "ROL00005",
        "name": "软件组",
        "roleType": "CUSTOM",
        "disableFlag": false,
        "remark": "软件部门角色",
        "createdAt": "2024-03-01T10:00:00+08:00",
        "updatedAt": "2024-03-15T14:30:00+08:00"
      }
    ],
    "total": 1,
    "page": 1,
    "pageSize": 10
  }
}
```

---

### 4. 获取角色详情

**接口：** `GET /api/sm/role/{id}`

**权限：** 需要认证

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | number | 角色 ID |

**说明：** 返回角色完整信息，包括权限 ID 列表

**响应示例：**

```json
{
  "msg": "success",
  "data": {
    "id": 5,
    "code": "ROL00005",
    "name": "软件组",
    "roleType": "CUSTOM",
    "disableFlag": false,
    "remark": "软件部门角色",
    "permissions": [1, 2, 3, 5, 101, 102],
    "createdAt": "2024-03-01T10:00:00+08:00",
    "updatedAt": "2024-03-15T14:30:00+08:00"
  }
}
```

---

### 5. 创建角色

**接口：** `POST /api/sm/role/list`

**权限：** 超级用户 或 具有 `SM.add_role` 权限

**请求体：**

```json
{
  "name": "测试组",
  "remark": "测试部门角色"
}
```

**参数说明：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 角色名称（全局唯一） |
| remark | string | 否 | 备注说明 |
| permissionId | number[] | 否 | 权限 ID 列表 |

**行为：**
- `code` 自动生成（格式：ROL + 数字）
- `roleType` 强制设置为 `CUSTOM`
- 不允许创建 BUILTIN 类型角色

**响应示例：**

```json
{
  "msg": "success",
  "data": {
    "id": 7,
    "code": "ROL00007",
    "name": "测试组",
    "roleType": "CUSTOM",
    "remark": "测试部门角色"
  }
}
```

**错误响应：**

```json
{
  "msg": "角色名称已存在"
}
```

---

### 6. 更新角色（完整更新）

**接口：** `PUT /api/sm/role/{id}`

**权限：** 超级用户 或 具有 `SM.change_role` 权限

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | number | 角色 ID |

**请求体：**

```json
{
  "name": "测试组（更新）",
  "remark": "更新后的备注",
  "disableFlag": false
}
```

**参数说明：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 角色名称（全局唯一） |
| remark | string | 否 | 备注说明 |
| disableFlag | boolean | 否 | 是否禁用（软删除） |

**行为：**
- 不允许修改 `code`、`roleType` 字段
- 不允许修改 BUILTIN 角色的 `name` 字段

**响应示例：**

```json
{
  "msg": "success"
}
```

**错误响应：**

```json
{
  "msg": "内置角色不允许修改名称"
}
```

---

### 7. 批量删除角色

**接口：** `DELETE /api/sm/role/list`

**权限：** 超级用户 或 具有 `SM.delete_role` 权限

**请求体：**

```json
{
  "id": [5, 6, 7]
}
```

**参数说明：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | number[] | 是 | 角色 ID 列表 |

**行为：**
- BUILTIN 类型角色不允许删除（返回 400 错误）
- 删除前检查是否有用户关联该角色
- 实际执行软删除（设置 `disableFlag=true`）

**响应示例：**

```json
{
  "msg": "success"
}
```

**错误响应：**

```json
{
  "msg": "内置角色不允许删除"
}
```

```json
{
  "msg": "角色被用户使用，请先解除关联"
}
```

---

## 数据模型

### Role 模型

角色管理模型，继承自 Django `Group`。

**字段说明：**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | number | 主键（继承自 Group） |
| code | string | 角色编码（自动生成，格式：ROL + 数字） |
| name | string | 角色名称（继承自 Group，全局唯一） |
| role_type | string | 角色类型：BUILTIN / CUSTOM |
| disable_flag | boolean | 是否禁用（软删除） |
| remark | string | 备注说明 |
| permissions | M2M | 关联 Django Permission（继承自 Group） |
| created_at | DateTimeField | 创建时间 |
| updated_at | DateTimeField | 更新时间 |

**继承的 Django Group 字段：**
- `id`: 主键
- `name`: 角色名称，全局唯一
- `permissions`: M2M 到 Django Permission

---

## 序列化器说明

### SimpleSerializer

简化角色序列化器，用于下拉选择框。

**字段：**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | number | 角色 ID |
| code | string | 角色编码 |
| name | string | 角色名称 |
| roleType | string | 角色类型（BUILTIN / CUSTOM） |

### ReadSerializer

完整角色序列化器，包含权限列表。

**字段：**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | number | 角色 ID |
| code | string | 角色编码 |
| name | string | 角色名称 |
| roleType | string | 角色类型（BUILTIN / CUSTOM） |
| disableFlag | boolean | 是否禁用 |
| remark | string | 备注说明 |
| permissions | number[] | 权限 ID 列表 |
| createdAt | DateTimeField | 创建时间 |
| updatedAt | DateTimeField | 更新时间 |

### WriteSerializer

角色创建序列化器。

**约束：**
- `name` 全局唯一性校验
- 强制 `role_type='CUSTOM'`
- `code` 自动生成（使用 `get_unique_code('ROL', Role)`）

---

## 角色类型说明

### BUILTIN（内置流程角色）

系统预设的角色，包含：
- 项目负责人 (PROJECT_OWNER)
- 节点负责人 (NODE_OWNER)
- 节点协助者 (NODE_ASSISTOR)
- 管理者 (MANAGER)
- 系统管理员 (SUPER_ADMIN) — 页面不展示

**约束：**
- 不可删除
- 不允许修改 `name` 字段
- 不允许修改"后台管理" Tab 权限
- 仅允许修改 PROJECT / DELIVERABLE Tab 权限

**默认权限：**
- 项目负责人：所有 identity 包含 `OWNER` 的 PM 权限
- 节点负责人：所有 identity 包含 `OWNER_NODE` 的 PM 权限
- 节点协助者：所有 identity 包含 `ASSISTOR` 的 PM 权限
- 管理者：所有 identity 包含 `MANAGER` 的 PM 权限
- 系统管理员：所有权限（页面不展示）

### CUSTOM（自定义角色）

用户创建的角色，默认为 CUSTOM 类型。

**约束：**
- 可以删除（需先解除用户关联）
- 可以修改所有 Tab 权限
- `code` 自动生成（格式：ROL + 数字）

---

## 权限验证

### 操作类型映射

| 操作 | Django Codename | 说明 |
|------|-----------------|------|
| CREATE | SM.add_role | 创建角色 |
| VIEW | SM.view_role | 查看角色 |
| CHANGE | SM.change_role | 修改角色 |
| DELETE | SM.delete_role | 删除角色 |
| DISABLE | SM.disable_role | 禁用角色（自定义权限） |

### 验证方法

```python
# 验证用户是否有某权限
user.has_perm('SM.add_role')
user.has_perm('SM.change_role')
user.has_perm('SM.delete_role')
```

---

## 权限说明

| 操作 | 权限要求 |
|------|----------|
| 查询角色列表 | 需要登录 |
| 查看角色详情 | 需要登录 |
| 创建角色 | 超级用户 或 SM.add_role |
| 修改角色 | 超级用户 或 SM.change_role |
| 删除角色 | 超级用户 或 SM.delete_role |
| 修改 BUILTIN 角色 | 禁止（除 PROJECT/DELIVERABLE Tab 权限） |

---

## 相关模块

- **SM.permission**：权限管理模块（PermissionConfig）
- **PM.authority**：项目权限验证模块（AuthorityVerifier）
- **SM.user**：用户管理模块（用户-角色关联）

---

## 内置角色编码

| 编码 | 名称 | roleType | 说明 |
|------|------|----------|------|
| PROJECT_OWNER | 项目负责人 | BUILTIN | 项目所有者 |
| NODE_OWNER | 节点负责人 | BUILTIN | 节点主要负责人 |
| NODE_ASSISTOR | 节点协助者 | BUILTIN | 节点协助负责人 |
| MANAGER | 管理者 | BUILTIN | 部门管理者 |
| SUPER_ADMIN | 系统管理员 | BUILTIN | 系统管理员（页面不展示） |

---

## 更新日志

- 2025-04-03：重大更新
  - 新增 `role_type` 字段（BUILTIN / CUSTOM）
  - 新增 `GET /sm/roles/perm-tree` 接口（权限配置页专用）
  - SimpleSerializer 新增 `roleType` 字段
  - ReadSerializer 新增 `permissions` 字段
  - 新增 BUILTIN 角色约束（不可删除、不可修改 ADMIN Tab）
  - WriteSerializer 强制 `role_type='CUSTOM'`
- 2024-03-21：初始版本，支持角色 CRUD 操作
