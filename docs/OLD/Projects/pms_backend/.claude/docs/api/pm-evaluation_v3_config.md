# PM - EvaluationV3Config 接口文档

> 最后更新：2026-03-21
> App: `PM` | Model: `ProjectRoleEvaluationConfig`, `ProjectRoleEvaluationItem`, `ProjectRoleEvaluationScope`
> Base URL: `/pm/evaluation`

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
| GET | `/pm/evaluation/config/<project_id>/init` | 初始化项目评价配置 | ✅ |

---

## 接口详情

### 1. 初始化项目评价配置

**GET** `/pm/evaluation/config/<project_id>/init`

根据项目角色初始化评价配置，从 PSC 模块同步评价配置到 PM 模块。

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| project_id | int | 项目 ID |

**响应示例**

```json
{
  "msg": "success"
}
```

**初始化逻辑**

1. 获取项目中所有项目角色
2. 从 PSC 模块查询每个项目角色对应的评价配置（`EvaluationConfig`）
3. 为每个评价配置创建 PM 模块的关联数据：
   - `ProjectRoleEvaluationConfig`：评价配置主记录
   - `ProjectRoleEvaluationItem`：评价项记录
   - `ProjectRoleEvaluationScope`：评价范围（可评价角色）记录

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
# 初始化项目评价配置
curl -X GET "http://localhost:8001/pm/evaluation/config/1/init" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 数据模型

### ProjectRoleEvaluationConfig 模型字段

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| project | FK(Project_List) | 关联项目 |
| evaluation_config | FK(PSC.EvaluationConfig) | 关联评价配置 |
| create_time | DateTime | 创建时间 |
| update_time | DateTime | 更新时间 |

**属性方法**

| 属性 | 类型 | 说明 |
|------|------|------|
| project_role_id | int | 被评价人的项目角色 ID |
| project_role_name | string | 被评价人的项目角色名称 |

### ProjectRoleEvaluationItem 模型字段

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| evaluation_config | FK(ProjectRoleEvaluationConfig) | 关联评价配置 |
| item | FK(PSC.EvaluationConfigItem) | 关联评价项 |
| item_name | string | 评价项名称 |
| item_option_data | JSON | 评价项内容（选项数据） |

**属性方法**

| 属性 | 类型 | 说明 |
|------|------|------|
| open_node | FK(NodeDefinition) | 评价项开放节点 |

### ProjectRoleEvaluationScope 模型字段

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| evaluation_config_item | FK(ProjectRoleEvaluationItem) | 关联评价项 |
| project_role | FK(PSC.ProjectRole) | 评价者项目角色 |

**属性方法**

| 属性 | 类型 | 说明 |
|------|------|------|
| evaluated_role | ProjectRole | 被评价角色 |
| evaluation_config | EvaluationConfig | 评价配置 |

### 表名

- `PM_evaluate_v3_role_evaluation_config` - 评价配置表
- `PM_evaluate_v3_role_evaluation_item` - 评价项信息表
- `PM_evaluate_v3_role_evaluation_scope` - 开放评价角色表

---

## 设计说明

### 模块关系

EvaluationV3Config 模块是 PSC 模块 `EvaluationConfig` 的 PM 侧镜像：

```
PSC 模块（配置侧）                PM 模块（执行侧）
┌─────────────────────┐          ┌─────────────────────────────┐
│ EvaluationConfig    │ ────────▶ │ ProjectRoleEvaluationConfig │
│ (评价配置)           │          │ (项目角色评价配置)           │
└─────────────────────┘          └─────────────────────────────┘
         │                                   │
         │                                   │
         ▼                                   ▼
┌─────────────────────┐          ┌─────────────────────────────┐
│ EvaluationConfigItem│ ────────▶ │ ProjectRoleEvaluationItem   │
│ (评价项)             │          │ (项目评价项)                 │
└─────────────────────┘          └─────────────────────────────┘
         │                                   │
         │                                   │
         ▼                                   ▼
┌─────────────────────┐          ┌─────────────────────────────┐
│ EvaluationItem      │          │ ProjectRoleEvaluationScope  │
│ Option/Role         │ ────────▶ │ (评价范围)                   │
└─────────────────────┘          └─────────────────────────────┘
```

### 初始化流程

1. **触发时机**：项目创建后或需要评价时
2. **初始化内容**：
   - 复制 PSC 评价配置到 PM 项目
   - 建立项目与评价配置的关联
   - 提取评价项、选项、评价角色信息

3. **数据结构**：
   - `ProjectRoleEvaluationConfig`：项目与评价配置的关联
   - `ProjectRoleEvaluationItem`：评价项及选项数据
   - `ProjectRoleEvaluationScope`：可评价角色范围

### 与 V2 版本的区别

| 特性 | V2 | V3 |
|------|----|----|
| 配置来源 | 无固定配置 | PSC.EvaluationConfig |
| 评价项 | 灵活创建 | 基于 PSC 配置初始化 |
| 数据结构 | 独立模型 | 与 PSC 模块关联 |
| 用途 | 绩效评价 | 项目角色评价 |

### 序列化器说明

#### CreateEvaluationConfigSerializer

用于创建评价配置：

```json
{
  "evaluationConfigId": 1,
  "items": [
    {
      "id": 1,
      "name": "技术能力",
      "options": [
        {"name": "优秀", "score": 5},
        {"name": "良好", "score": 4}
      ],
      "roles": [2, 3]
    }
  ]
}
```

#### EvaluationDetailSerializer

用于获取评价详情，包含以下字段：

- `projectRoleId`：被评价人的项目角色 ID
- `projectRoleName`：被评价人的项目角色名称
- `evaluationConfigId`：评价配置 ID
- `evaluationItemId`：评价项 ID
- `itemId`：原始评价项 ID
- `itemName`：评价项名称
- `itemOptions`：评价选项列表
- `openNodeId`：开放节点 ID
- `evaluatorProjectRoleId`：评价者的项目角色 ID

### 使用场景

1. **项目初始化**：创建项目后，调用初始化接口建立评价配置
2. **评价执行**：根据初始化的配置进行评价操作
3. **数据同步**：保持 PSC 配置与 PM 项目数据的一致性
