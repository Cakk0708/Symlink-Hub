# SM - 权限管理模块 API 文档

## 模块概述

提供三 Tab 分类的权限查询、角色权限分配、交付物权限管理等功能。

**应用：** SM（系统管理）
**路径前缀：** `/api/sm/permissions`
**认证方式：** 需要 JWT Token

**架构说明：**
- 后台管理 Tab (ADMIN) — 直接从 SYSTEM_MODULE_CONFIG 定义的模块查询 Django Permission 表，无需映射表
- 项目管理 Tab (PROJECT) — 由 `init_pm_permissions` 命令初始化 ProjectPermission，通过 ProjectPermissionMapping 映射到角色
- 交付物管理 Tab (DELIVERABLE) — 每个交付物定义的查看/编辑权限，通过 DeliverablePermissionMapping 映射到角色

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

### 2. 获取角色权限列表（统一接口，含 granted 状态）

**接口：** `GET /api/sm/permissions/{category}/roles/{roleId}`

**权限：** 需要认证

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| category | string | 权限类别：PROJECT / DELIVERABLE / ADMIN |
| roleId | number | 角色 ID |

**说明：** 返回指定类别下的权限列表，并标注该角色是否拥有每项权限（granted 字段）。前端无需再单独调用 `GET /sm/roles/{roleId}` 获取权限列表。

#### 2.1 项目管理 (category=PROJECT)

**响应示例：**

```json
{
  "msg": "success",
  "data": {
    "roleId": 101,
    "module": "project",
    "permissions": [
      {
        "categoryId": "项目管理",
        "categoryName": "项目管理",
        "items": [
          { "id": 101, "name": "暂停项目", "codename": "pm.pause_project", "granted": true },
          { "id": 102, "name": "完成项目", "codename": "pm.complete_project", "granted": false }
        ]
      },
      {
        "categoryId": "节点管理",
        "categoryName": "节点管理",
        "items": [
          { "id": 201, "name": "完成节点", "codename": "pm.complete_node", "granted": true }
        ]
      }
    ]
  }
}
```

#### 2.2 交付物管理 (category=DELIVERABLE)

**响应示例：**

```json
{
  "msg": "success",
  "data": {
    "roleId": 101,
    "module": "deliverable",
    "permissions": {
      "items": [
        {
          "defId": 1,
          "name": "BOM表",
          "version": "1.0",
          "isActive": true,
          "viewPermId": 201,
          "editPermId": 202,
          "viewGranted": true,
          "editGranted": false
        }
      ]
    }
  }
}
```

**字段说明：**

| 字段 | 类型 | 说明 |
|------|------|------|
| defId | number | 交付物定义 ID |
| name | string | 交付物名称 |
| version | string | 当前版本号 |
| isActive | boolean | 是否启用 |
| viewPermId | number | 查看权限 ID |
| editPermId | number | 编辑权限 ID |
| viewGranted | boolean | 该角色是否拥有查看权限 |
| editGranted | boolean | 该角色是否拥有编辑权限 |

#### 2.3 后台管理 (category=ADMIN)

**响应示例：**

```json
{
  "msg": "success",
  "data": {
    "roleId": 101,
    "module": "admin",
    "permissions": {
      "系统管理": {
        "用户管理": [
          {
            "group": "view",
            "groupLabel": "查询",
            "list": [
              {
                "id": 10,
                "name": "查看用户",
                "codename": "view_user",
                "appLabel": "SM",
                "appName": "系统管理",
                "model": "user",
                "modelName": "用户",
                "granted": true
              }
            ]
          }
        ]
      }
    }
  }
}
```

---

### 3. 分配角色权限（统一接口）

**接口：** `PUT /api/sm/permissions/{category}/roles/{roleId}`

**权限：** 超级用户 或 具有 `SM.change_perm` 权限

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| category | string | 权限类别：PROJECT / DELIVERABLE / ADMIN |
| roleId | number | 角色 ID |

**请求体：**

```json
{
  "permission": [101, 102, 201, 202]
}
```

**参数说明：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| permission | number[] | 否 | 权限 ID 列表，为空时清空该类别下所有权限 |

**行为：**
- 仅移除/添加指定 `category` 下的权限
- 不影响其他类别已有权限

**响应示例：**

```json
{
  "msg": "success"
}
```

---

### 4. 获取权限列表（按 Tab 分类，旧接口）

**接口：** `GET /api/sm/perm?tab_type={tab_type}`

**权限：** 需要认证

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| tab_type | string | 否 | 权限标签页：PROJECT / DELIVERABLE / ADMIN，默认 ADMIN |

**说明：** 根据不同的 tab_type 返回对应权限列表

---

#### 2.1 后台管理 Tab (`tab_type=ADMIN`)

**响应示例：**

```json
{
  "msg": "success",
  "data": {
    "PM": {
      "project": [
        {
          "group": "查询",
          "list": [
            {
              "id": 1,
              "name": "查看",
              "codename": "view_project",
              "group": "查询",
              "appLabel": "PM",
              "appName": "项目管理",
              "model": "project",
              "modelName": "项目",
              "sort": 1
            }
          ]
        },
        {
          "group": "编辑",
          "list": [
            {
              "id": 2,
              "name": "新增",
              "codename": "add_project",
              "group": "编辑",
              "appLabel": "PM",
              "appName": "项目管理",
              "model": "project",
              "modelName": "项目",
              "sort": 2
            }
          ]
        }
      ]
    }
  }
}
```

**数据结构：**
- 第一层 key：应用标签（appLabel）
- 第二层 key：模型名称（model）
- 第三层：权限分组数组，包含 `group`（分组名称）和 `list`（权限列表）
- 排序规则：查询分组排在最前，其他分组按自然顺序

---

#### 2.2 项目管理 Tab (`tab_type=PROJECT`)

**响应示例：**

```json
{
  "msg": "success",
  "data": {
    "项目管理": [
      {
        "id": 101,
        "name": "暂停项目",
        "codename": "pm.pause_project",
        "category": "项目管理",
        "sort": 0
      },
      {
        "id": 102,
        "name": "完成项目",
        "codename": "pm.complete_project",
        "category": "项目管理",
        "sort": 1
      },
      {
        "id": 103,
        "name": "删除项目",
        "codename": "pm.delete_project",
        "category": "项目管理",
        "sort": 2
      }
    ],
    "节点管理": [
      {
        "id": 201,
        "name": "完成节点",
        "codename": "pm.complete_node",
        "category": "节点管理",
        "sort": 0
      },
      {
        "id": 202,
        "name": "回滚节点",
        "codename": "pm.rollback_node",
        "category": "节点管理",
        "sort": 1
      }
    ],
    "基本信息": [...],
    "项目结算": [...]
  }
}
```

**数据结构：**
- 第一层 key：权限分类（项目管理、节点管理、基本信息、项目结算）
- 每个分类包含权限数组

---

#### 2.3 交付物管理 Tab (`tab_type=DELIVERABLE`)

**接口：** `GET /api/sm/permissions/deliverable`

**响应示例：**

```json
{
  "msg": "success",
  "data": {
    "items": [
      {
        "defId": 1,
        "name": "BOM表",
        "version": "1.0",
        "isActive": true,
        "viewPermId": 201,
        "editPermId": 202,
        "viewChecked": false,
        "editChecked": false
      },
      {
        "defId": 2,
        "name": "原理图",
        "version": "2.1",
        "isActive": true,
        "viewPermId": 203,
        "editPermId": 204,
        "viewChecked": true,
        "editChecked": true
      }
    ]
  }
}
```

**字段说明：**

| 字段 | 类型 | 说明 |
|------|------|------|
| defId | number | 交付物定义 ID |
| name | string | 交付物名称 |
| version | string | 当前版本号 |
| isActive | boolean | 是否启用 |
| viewPermId | number | 查看权限 ID |
| editPermId | number | 编辑权限 ID |
| viewChecked | boolean | 查看权限是否勾选（当前角色） |
| editChecked | boolean | 编辑权限是否勾选（当前角色） |

---

### 3. 获取角色权限（兼容旧接口）

**接口：** `GET /api/sm/perm_role/{roleId}`

**权限：** 需要认证

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| roleId | number | 角色 ID |

**说明：** 返回指定角色已分配的权限 ID 列表（ADMIN Tab）

**响应示例：**

```json
{
  "msg": "success",
  "data": {
    "permissions": [1, 2, 3, 5]
  }
}
```

---

### 4. 分配角色权限（按 Tab）

**接口：** `PUT /api/sm/perm_role/{roleId}?tab_type={tab_type}`

**权限：** 超级用户 或 具有 `SM.change_perm` 权限

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| roleId | number | 角色 ID |

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| tab_type | string | 是 | 权限标签页：PROJECT / DELIVERABLE / ADMIN |

**请求体：**

```json
{
  "permissionId": [101, 102, 201, 202]
}
```

**参数说明：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| permissionId | number[] | 否 | 权限 ID 列表，为空或不存在时清空该 Tab 下权限 |

**行为：**
- 仅移除/添加指定 `tab_type` 下的权限
- 不影响其他 Tab 已有权限
- 交付物 Tab 特殊逻辑：保存时若 edit 被勾选，自动补勾 view

**响应示例：**

```json
{
  "msg": "success"
}
```

**错误响应：**

```json
{
  "msg": "内置角色不允许修改后台管理权限"
}
```

```json
{
  "msg": "角色不存在"
}
```

---

## 数据模型

### ProjectPermissionMapping 模型

项目权限映射模型，角色与项目权限的多对多关系表。由 `init_pm_permissions` 命令创建。

**字段说明：**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | number | 主键 |
| role | ForeignKey | 关联角色（SM.Role） |
| project_permission | ForeignKey | 关联项目权限（PM.ProjectPermission） |

**表名：** `SM_permission_project_mapping`

### DeliverablePermissionMapping 模型

交付物权限映射模型，角色对交付物定义的查看/编辑权限。

**字段说明：**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | number | 主键 |
| role | ForeignKey | 关联角色（SM.Role） |
| deliverable_definition | ForeignKey | 关联交付物定义（PSC.DeliverableDefinition） |
| can_view | BooleanField | 查看权限 |
| can_edit | BooleanField | 编辑权限 |

**表名：** `SM_permission_deliverable_mapping`
**唯一约束：** (role, deliverable_definition)

> **注意：** 后台管理 (ADMIN) 权限不使用映射表，直接从 `SYSTEM_MODULE_CONFIG` 定义的全部模块实时查询 Django Permission 表。角色通过 Django Group.permissions 多对多字段关联。

### ProjectPermission 模型（PM）

项目操作权限定义。

**字段说明：**

| 字段 | 类型 | 说明 |
|------|------|------|
| code | IntegerField | 权限代码（旧系统兼容） |
| codename | CharField | 权限标识（语义化，如 pm.edit_project_name） |
| name | CharField | 权限名称 |
| category | CharField | 权限分类 |
| sort | IntegerField | 排序字段 |

### DeliverablePermission 模型

交付物权限定义，每个交付物定义对应查看/编辑两条权限。由 `sync_deliverable_perms` 命令创建。

**字段说明：**

| 字段 | 类型 | 说明 |
|------|------|------|
| deliverable_definition | ForeignKey | 关联交付物定义 |
| view_permission | OneToOneField | 查看权限（Django Permission） |
| edit_permission | OneToOneField | 编辑权限（Django Permission） |

---

## 权限分类

### 后台管理 (ADMIN)

**数据源：** `SYSTEM_MODULE_CONFIG` (home/settings/module.py)，直接查询 Django Permission 表（不依赖配置表记录）

**权限分组：**

| 分组值 | 显示名称 | 说明 |
|--------|----------|------|
| 查询 | 查询 | 查看类权限 |
| 编辑 | 编辑 | 增删改类权限 |
| 业务操作 | 业务操作 | 审核等业务操作权限 |
| 其他 | 其他 | 打印等其他权限 |

### 项目管理 (PROJECT)

**数据源：** `PM.ProjectPermission` 表

**权限分类：**

| 分类 | 权限数量 | 说明 |
|------|----------|------|
| 项目管理 | 10 | 项目级操作（暂停、完成、删除、变更等） |
| 节点管理 | 12 | 节点级操作（完成、回滚、负责人等） |
| 基本信息 | 15 | 项目基本信息编辑（名称、描述、机型等） |
| 项目结算 | 6 | 交付物、工时、评分等 |

**权限命名规范：** `pm.{action}_{resource}`

示例：
- `pm.pause_project` — 暂停项目
- `pm.complete_node` — 完成节点
- `pm.edit_project_name` — 编辑项目名称

### 交付物管理 (DELIVERABLE)

**数据源：** `PSC.DeliverableDefinition` + `SM.DeliverablePermissionMapping`

**权限命名规范：** `psc_view_deliv_{def_id}` / `psc_edit_deliv_{def_id`

**交互规则：**
- 勾选"编辑"时自动勾选"查看"
- 取消"查看"时自动取消"编辑"

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
- 不允许修改"后台管理" Tab 权限
- 仅允许修改 PROJECT / DELIVERABLE Tab 权限

### CUSTOM（自定义角色）

用户创建的角色，默认为 CUSTOM 类型。

**约束：**
- 可以删除（需先解除用户关联）
- 可以修改所有 Tab 权限

---

## 权限验证

### 操作类型映射

| 操作 | Codename 后缀 | 说明 |
|------|---------------|------|
| CREATE | add_perm | 创建权限 |
| VIEW | view_perm | 查看权限 |
| CHANGE | change_perm | 修改权限 |
| DELETE | delete_perm | 删除权限 |

### 验证方法

```python
# 验证用户是否有某权限
user.has_perm('PM.add_project')

# 验证用户是否有某模块某操作权限
user.has_perm('SM.change_perm')

# 验证项目权限（语义化 codename）
user.has_perm('pm.edit_project_name')
```

---

## 权限说明

| 操作 | 权限要求 |
|------|----------|
| 查询权限列表 | 需要登录 |
| 查看角色权限 | 需要登录 |
| 分配角色权限（ADMIN Tab） | 超级用户 或 SM.change_perm |
| 分配角色权限（PROJECT/DELIVERABLE Tab） | 超级用户 或 SM.change_perm |
| 修改 BUILTIN 角色（ADMIN Tab） | 禁止（返回 403） |

---

## 相关模块

- **SM.role**：角色管理模块（role_type 字段）
- **PM.authority**：项目权限验证模块（AuthorityVerifier）
- **PSC.deliverable_definition**：交付物定义模块

---

## 权限码映射表

### 项目管理 Tab 部分映射

| 旧 code | 新 codename | name | category |
|---------|-------------|------|----------|
| 1001 | `pm.edit_project_name` | 项目名称 | 基本信息 |
| 1002 | `pm.edit_project_desc` | 项目描述 | 基本信息 |
| 1003 | `pm.edit_model_info` | 机型信息 | 基本信息 |
| 1006 | `pm.manage_followers` | 项目关注者 | 项目管理 |
| 1007 | `pm.add_node` | 添加节点 | 项目管理 |
| 1008 | `pm.delete_node` | 删除节点 | 项目管理 |
| 1100 | `pm.complete_project` | 完成项目 | 项目管理 |
| 1102 | `pm.delete_project` | 删除项目 | 项目管理 |
| 2200 | `pm.complete_node` | 完成节点 | 节点管理 |
| 2201 | `pm.rollback_node` | 回滚节点 | 节点管理 |
| 2009 | `pm.create_deliverable` | 交付物创建 | 节点管理 |

**完整映射表：** 参见 `apps/PM/management/commands/init_pm_permissions.py`

---

## 更新日志

- 2026-04-06：PermissionConfig 重构
  - 删除 `PermissionConfig` 模型，改用映射表架构
  - 新增 `ProjectPermissionMapping` 模型（角色→项目权限映射，表名 `SM_permission_project_mapping`）
  - 新增 `DeliverablePermissionMapping` 模型（角色→交付物权限映射，表名 `SM_permission_deliverable_mapping`）
  - ADMIN 权限改为从 `SYSTEM_MODULE_CONFIG` 模块直接查询 Django Permission 表，无需映射表
  - 新增 `AdminPermSerializer` 直接序列化 Permission 对象
  - 更新 `init_builtin_roles` 命令，超级管理员权限合并 PROJECT + ADMIN
  - 删除 `reset_permission_config` 管理命令（不再需要）
- 2025-04-06：接口重构
  - 新增统一接口 `GET /api/sm/permissions/{category}/roles/{roleId}`（返回权限列表 + granted 状态）
  - 新增统一接口 `PUT /api/sm/permissions/{category}/roles/{roleId}`（按类别分配角色权限）
  - 前端不再需要单独调用 `GET /sm/roles/{roleId}` 获取权限列表
  - 旧接口保留兼容（GET /sm/perm, PUT /sm/perm_role/{id}）
- 2025-04-03：重大更新
  - 删除 SM_perm 表，使用 ProjectPermissionMapping 替代
  - 新增三 Tab 权限结构（PROJECT / DELIVERABLE / ADMIN）
  - 新增交付物权限管理
  - PM 权限使用语义化 codename
  - 新增 role_type 字段（BUILTIN / CUSTOM）
  - 重构 AuthorityVerifier（role-based checking）
- 2024-03-31：初始版本，支持权限查询、角色权限分配
