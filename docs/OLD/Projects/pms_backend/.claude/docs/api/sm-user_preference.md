# SM - 用户偏好设置 API 文档

## 模块概述

提供当前登录用户的通知偏好设置读写功能。每个用户独立配置自己的偏好，无偏好记录时使用默认值。

**应用：** SM（系统管理）
**路径前缀：** `/api/sm/user-preference`
**认证方式：** 需要登录（IsAuthenticated）

---

## 接口列表

### 1. 获取当前用户偏好设置

**接口：** `GET /api/sm/user-preference`

**权限：** 需要登录

**说明：** 获取当前登录用户的偏好设置。若用户无偏好记录，返回默认值。

**响应示例：**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "notify_as_creator": false,
    "notify_as_owner": false,
    "notify_as_follower": false,
    "notify_node_start": true,
    "node_scope": "MILESTONE",
    "node_scope_label": "里程碑节点",
    "created_at": "2026-04-11 10:00:00",
    "updated_at": "2026-04-11 10:00:00"
  }
}
```

**无记录时的默认响应：**

```json
{
  "msg": "success",
  "data": {
    "notify_as_creator": false,
    "notify_as_owner": false,
    "notify_as_follower": false,
    "notify_node_start": true,
    "node_scope": "MILESTONE"
  }
}
```

**字段说明：**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | number | 偏好记录 ID（无记录时不返回） |
| notify_as_creator | boolean | 作为项目创建者时是否接收节点完成通知 |
| notify_as_owner | boolean | 作为项目负责人时是否接收节点完成通知 |
| notify_as_follower | boolean | 作为项目关注者时是否接收节点完成通知 |
| notify_node_start | boolean | 节点开始时是否接收通知（默认开启） |
| node_scope | string | 节点通知范围：MILESTONE / MAIN_NODE / SUB_NODE |
| node_scope_label | string | 节点范围中文标签（有记录时返回） |
| created_at | datetime | 创建时间（有记录时返回） |
| updated_at | datetime | 更新时间（有记录时返回） |

---

### 2. 创建/更新当前用户偏好设置

**接口：** `PUT /api/sm/user-preference`

**权限：** 需要登录

**说明：** 创建或更新当前登录用户的偏好设置。使用 update_or_create 语义，首次调用创建，后续调用更新。

**请求体：**

```json
{
  "notify_as_creator": true,
  "notify_as_owner": false,
  "notify_as_follower": true,
  "notify_node_start": true,
  "node_scope": "MAIN_NODE"
}
```

**参数说明：**

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| notify_as_creator | boolean | 否 | false | 作为项目创建者时是否通知 |
| notify_as_owner | boolean | 否 | false | 作为项目负责人时是否通知 |
| notify_as_follower | boolean | 否 | false | 作为项目关注者时是否通知 |
| notify_node_start | boolean | 否 | true | 节点开始时是否通知 |
| node_scope | string | 否 | MILESTONE | 节点通知范围 |

**node_scope 可选值：**

| 值 | 说明 |
|----|------|
| MILESTONE | 仅里程碑节点完成时通知 |
| MAIN_NODE | 仅主节点完成时通知 |
| SUB_NODE | 仅子节点完成时通知 |

**响应示例：**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "notify_as_creator": true,
    "notify_as_owner": false,
    "notify_as_follower": true,
    "notify_node_start": true,
    "node_scope": "MAIN_NODE",
    "node_scope_label": "主节点",
    "created_at": "2026-04-11 10:00:00",
    "updated_at": "2026-04-11 10:30:00"
  }
}
```

**错误响应：**

```json
{
  "msg": "error",
  "errors": {
    "node_scope": ["无效的节点范围，可选值: ['MILESTONE', 'MAIN_NODE', 'SUB_NODE']"]
  }
}
```

---

### 3. 获取偏好设置枚举

**接口：** `GET /api/sm/user-preference/enums`

**权限：** 需要登录

**响应示例：**

```json
{
  "msg": "success",
  "data": {
    "node_scope": [
      {"value": "MILESTONE", "label": "里程碑节点"},
      {"value": "MAIN_NODE", "label": "主节点"},
      {"value": "SUB_NODE", "label": "子节点"}
    ]
  }
}
```

---

## 数据模型

### UserPreference 模型

用户偏好设置模型，与 User 一对一关联。

**核心字段：**

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| id | number | 自增 | 主键 |
| user | FK(SM.User) | — | 关联用户（OneToOne） |
| notify_as_creator | boolean | false | 作为项目创建者通知 |
| notify_as_owner | boolean | false | 作为项目负责人通知 |
| notify_as_follower | boolean | false | 作为项目关注者通知 |
| notify_node_start | boolean | true | 节点开始通知 |
| node_scope | char(20) | MILESTONE | 节点通知范围 |
| extra_settings | json | {} | 预留扩展字段 |
| created_at | datetime | auto | 创建时间 |
| updated_at | datetime | auto | 更新时间 |

**表名：** `SM_user_preference`

---

## 业务逻辑

### 节点完成通知

当项目节点完成（状态 1→2 或 4→2）时，系统检查项目相关用户的偏好设置：

1. 收集项目的创建者、负责人、关注者
2. 对每个用户检查其 `UserPreference` 记录
3. 匹配条件：用户角色对应的通知开关开启 **且** `node_scope` 匹配完成节点的层级
4. 满足条件则通过飞书消息发送通知

**默认行为：** 无 `UserPreference` 记录的用户不会收到节点完成通知（所有角色开关默认 false）。

### 节点开始通知

当里程碑激活后续节点时，系统检查节点负责人的 `notify_node_start` 偏好：

- 开启或无偏好记录 → 发送通知
- 关闭 → 不发送通知

---

## 相关模块

- **SM.user**：用户管理模块（User 模型）
- **PM.nodelist**：项目节点模块（触发通知的信号和任务）
- **PM.project.follower**：项目关注者模块（ProjectFollower 模型）

---

## 更新日志

- 2026-04-11：初始版本，支持通知偏好设置读写、枚举查询
