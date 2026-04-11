# PSC - EvaluationConfig 接口文档

> 最后更新：2026-03-21
> App: `PSC` | Model: `EvaluationConfig`
> Base URL: `/psc/evaluation`

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
| GET | `/psc/evaluation` | 获取列表 | ✅ |
| GET | `/psc/evaluation/list` | 获取列表（同上） | ✅ |
| GET | `/psc/evaluation/listAll` | 获取全部列表 | ✅ |
| GET | `/psc/evaluation/<id>` | 获取详情 | ✅ |
| POST | `/psc/evaluation` | 创建评价配置 | ✅ |
| PUT | `/psc/evaluation/<id>` | 更新评价配置 | ✅ |
| DELETE | `/psc/evaluation/<ids>` | 批量删除 | ✅ |

---

## 接口详情

### 1. 获取列表

**GET** `/psc/evaluation`

或

**GET** `/psc/evaluation/list`

或

**GET** `/psc/evaluation/listAll`

获取评价配置分页列表，支持按项目角色名称筛选。

**Query 参数**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| name | string | 否 | - | 项目角色名称（模糊搜索） |
| pageNum | int | 否 | 1 | 页码 |
| pageSize | int | 否 | 10 | 每页数量 |
| pageSort | string | 否 | ID:DESC | 排序字段（格式：字段:方向） |

**响应示例**

```json
{
  "msg": "success",
  "data": [
    {
      "id": 1,
      "projectRoleName": "项目经理",
      "isEvaluatable": true,
      "isEvaluated": true,
      "remark": "项目经理评价配置",
      "createTime": "2024-01-01 00:00:00",
      "updateTime": "2024-01-01 00:00:00",
      "itemNames": "技术能力, 管理能力, 沟通能力",
      "reviewableBy": "技术负责人, 产品负责人"
    }
  ],
  "total": 1
}
```

**响应字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 评价配置 ID |
| projectRoleName | string | 项目角色名称 |
| isEvaluatable | boolean | 项目角色是否可被评价 |
| isEvaluated | boolean | 项目角色是否参与评价 |
| remark | string | 备注 |
| createTime | string | 创建时间 |
| updateTime | string | 更新时间 |
| itemNames | string | 评价项名称列表（逗号分隔） |
| reviewableBy | string | 可评价角色列表 |

---

### 2. 获取详情

**GET** `/psc/evaluation/<id>`

获取评价配置详情，包含评价项及选项、角色等完整信息。

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 评价配置 ID |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "projectRoleId": 1,
    "projectRoleName": "项目经理",
    "isEvaluatable": true,
    "isEvaluated": true,
    "contributionTips": "请根据项目贡献度进行评分",
    "remark": "项目经理评价配置",
    "items": [
      {
        "id": 1,
        "isEvaluated": true,
        "name": "技术能力",
        "remark": "评价技术能力",
        "options": [
          {
            "id": 1,
            "name": "优秀",
            "score": 5,
            "description": "技术能力突出"
          },
          {
            "id": 2,
            "name": "良好",
            "score": 4,
            "description": "技术能力良好"
          }
        ],
        "roles": [
          {
            "id": 2,
            "name": "技术负责人"
          }
        ],
        "openNodeId": null,
        "createTime": "2024-01-01 00:00:00",
        "updateTime": "2024-01-01 00:00:00"
      }
    ],
    "creator": "admin",
    "createTime": "2024-01-01 00:00:00",
    "updateBy": "admin",
    "updateTime": "2024-01-01 00:00:00",
    "isActive": true
  }
}
```

**响应字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 评价配置 ID |
| projectRoleId | int | 项目角色 ID |
| projectRoleName | string | 项目角色名称 |
| isEvaluatable | boolean | 项目角色是否可被评价 |
| isEvaluated | boolean | 项目角色是否参与评价 |
| contributionTips | string | 项目贡献度提示 |
| remark | string | 备注 |
| items | array | 评价项列表 |
| creator | string | 创建人用户名 |
| createTime | string | 创建时间 |
| updateBy | string | 最后修改人用户名 |
| updateTime | string | 更新时间 |
| isActive | boolean | 是否有效 |

**items 字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 评价项 ID |
| isEvaluated | boolean | 是否参与评价 |
| name | string | 评价项名称 |
| remark | string | 备注 |
| options | array | 评价选项列表 |
| roles | array | 可评价角色列表 |
| openNodeId | int/null | 评价开启节点 ID |
| createTime | string | 创建时间 |
| updateTime | string | 更新时间 |

---

### 3. 创建评价配置

**POST** `/psc/evaluation`

创建评价配置及关联的评价项、选项、角色。

**权限要求**

- 需要 `PSC.evaluation_config | CREATE` 权限

**请求体**

```json
{
  "projectRoleId": 1,
  "contributionTips": "请根据项目贡献度进行评分",
  "remark": "项目经理评价配置",
  "itemData": [
    {
      "isEvaluated": true,
      "name": "技术能力",
      "remark": "评价技术能力",
      "openNodeId": null,
      "optionData": [
        {
          "name": "优秀",
          "score": 5,
          "description": "技术能力突出"
        },
        {
          "name": "良好",
          "score": 4,
          "description": "技术能力良好"
        }
      ],
      "roleData": [2, 3]
    }
  ]
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| projectRoleId | int | ✅ | 项目角色 ID |
| contributionTips | string | 否 | 项目贡献度提示（最长 500 字符） |
| remark | string | 否 | 备注（最长 500 字符） |
| itemData | array | ✅ | 评价项数据列表 |

**itemData 参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| isEvaluated | boolean | 否 | 是否参与评价（默认 true） |
| name | string | ✅ | 评价项名称 |
| remark | string | 否 | 备注（最长 500 字符） |
| openNodeId | int/null | 否 | 评价开启节点 ID |
| optionData | array | ✅ | 评价选项数据列表 |
| roleData | array[int] | ✅ | 可评价角色 ID 列表 |

**optionData 参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | ✅ | 评价等级名称 |
| score | int | ✅ | 评价分数 |
| description | string | 否 | 评价标准 |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "insertId": 1
  }
}
```

**错误响应示例**

```json
{
  "msg": "数据验证失败",
  "errors": {
    "项目经理": "该项目角色已存在评价项配置，不可重复添加",
    "评价项明细": [
      {
        "项目角色": "不能给自己添加评价"
      }
    ]
  }
}
```

---

### 4. 更新评价配置

**PUT** `/psc/evaluation/<id>`

更新评价配置及关联的评价项、选项、角色。支持增量更新：未传入的评价项会被软删除，未传入的选项和角色也会被软删除。

**权限要求**

- 需要 `PSC.evaluation_config | CHANGE` 权限

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 评价配置 ID |

**请求体**

```json
{
  "projectRoleId": 1,
  "contributionTips": "更新后的贡献度提示",
  "remark": "更新后的备注",
  "itemData": [
    {
      "id": 1,
      "isEvaluated": true,
      "name": "技术能力",
      "remark": "更新后的技术能力评价",
      "openNodeId": 5,
      "optionData": [
        {
          "id": 1,
          "name": "优秀",
          "score": 5,
          "description": "技术能力突出"
        },
        {
          "name": "一般",
          "score": 3,
          "description": "技术能力一般"
        }
      ],
      "roleData": [2]
    },
    {
      "isEvaluated": true,
      "name": "管理能力",
      "remark": "管理能力评价",
      "openNodeId": null,
      "optionData": [
        {
          "name": "优秀",
          "score": 5,
          "description": "管理能力突出"
        }
      ],
      "roleData": [2, 3]
    }
  ]
}
```

**更新策略**

1. **评价项更新**：
   - 传入 `id` 的评价项：更新现有项
   - 未传入 `id` 的评价项：创建新项
   - 已存在但未在 `itemData` 中的评价项：软删除（`is_active=False`）

2. **选项更新**：
   - 传入 `id` 的选项：更新现有选项
   - 未传入 `id` 的选项：创建新选项
   - 已存在但未在 `optionData` 中的选项：软删除

3. **角色更新**：
   - 全量替换，未传入的角色会被软删除

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "insertId": 1
  }
}
```

**错误响应示例**

```json
{
  "msg": "修改失败，数据不存在"
}
```

---

### 5. 批量删除

**DELETE** `/psc/evaluation/<ids>`

批量软删除评价配置（设置 `is_active=False`）。

**权限要求**

- 需要 `PSC.evaluation_config | DELETE` 权限

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| ids | string | 评价配置 ID 列表（逗号分隔），如：`1,2,3` |

**响应示例**

```json
{
  "msg": "success"
}
```

**错误响应示例**

```json
{
  "msg": "删除失败，数据不存在"
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

或

```json
{
  "msg": "数据验证失败",
  "errors": {
    "字段名": ["错误信息"]
  }
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
curl -X GET "http://localhost:8001/psc/evaluation?pageNum=1&pageSize=10&name=项目经理" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 2. 获取详情
curl -X GET "http://localhost:8001/psc/evaluation/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 3. 创建评价配置
curl -X POST "http://localhost:8001/psc/evaluation" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "projectRoleId": 1,
    "contributionTips": "请根据项目贡献度进行评分",
    "remark": "项目经理评价配置",
    "itemData": [
      {
        "isEvaluated": true,
        "name": "技术能力",
        "remark": "评价技术能力",
        "optionData": [
          {
            "name": "优秀",
            "score": 5,
            "description": "技术能力突出"
          },
          {
            "name": "良好",
            "score": 4,
            "description": "技术能力良好"
          }
        ],
        "roleData": [2, 3]
      }
    ]
  }'

# 4. 更新评价配置
curl -X PUT "http://localhost:8001/psc/evaluation/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "projectRoleId": 1,
    "contributionTips": "更新后的贡献度提示",
    "remark": "更新后的备注",
    "itemData": [
      {
        "id": 1,
        "isEvaluated": true,
        "name": "技术能力",
        "remark": "更新后的技术能力评价",
        "optionData": [
          {
            "id": 1,
            "name": "优秀",
            "score": 5,
            "description": "技术能力突出"
          }
        ],
        "roleData": [2]
      }
    ]
  }'

# 5. 批量删除
curl -X DELETE "http://localhost:8001/psc/evaluation/1,2,3" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 数据模型

### EvaluationConfig 模型字段

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| project_role | FK | 关联项目角色（PSC.ProjectRole） |
| code | string(100) | 项目评价编码（唯一，自动生成） |
| remark | string(500) | 备注 |
| creator | FK(User) | 创建人 |
| update_by | FK(User) | 最后修改人 |
| create_time | DateTime | 创建时间 |
| update_time | DateTime | 最后修改日期 |
| contribution_tips | string(500) | 项目贡献度提示 |
| is_active | boolean | 是否有效 |

### EvaluationConfigItem 模型字段

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| evaluation_config | FK | 关联评价配置 |
| is_evaluated | boolean | 参与评价 |
| name | string(100) | 评价项 |
| remark | string(500) | 备注 |
| open_node | FK(NodeDefinition) | 评价开启节点 |
| create_time | DateTime | 创建时间 |
| update_time | DateTime | 最后修改日期 |
| is_active | boolean | 是否有效 |

### EvaluationConfigItemRole 模型字段

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| evaluation_config_item | FK | 关联评价项 |
| project_role | FK(ProjectRole) | 项目角色 |
| is_active | boolean | 是否有效数据 |

### EvaluationConfigItemOption 模型字段

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| evaluation_config_item | FK | 关联评价项 |
| name | string(100) | 评价等级 |
| score | int | 评价分数 |
| description | string(255) | 评价标准 |
| create_time | DateTime | 创建时间 |
| update_time | DateTime | 最后修改日期 |
| is_active | boolean | 是否有效 |

### 表名

- `PSC_evaluation_config` - 项目评价配置主表
- `PSC_evaluation_config_item` - 项目评价项表
- `PSC_evaluation_config_item_role` - 项目评价项角色表
- `PSC_evaluation_config_item_option` - 项目评价项等级表

---

## 设计说明

### 权限说明

评价配置模块使用 Django 自定义权限进行控制：

| 权限 Codename | 权限键 | 说明 |
|---------------|--------|------|
| CREATE | `PSC.evaluation_config | CREATE` | 创建评价配置 |
| CHANGE | `PSC.evaluation_config | CHANGE` | 修改评价配置 |
| DELETE | `PSC.evaluation_config | DELETE` | 删除评价配置 |
| DISABLE | `PSC.evaluation_config | DISABLE` | 禁用评价配置 |

### 唯一性验证规则

1. **项目角色唯一性**：每个项目角色只能有一个有效的评价配置（`is_active=True`）
2. **评价项角色验证**：评价项不能给自己（所属项目角色）添加评价权限

### 软删除机制

模块采用软删除机制：
- 所有主表都有 `is_active` 字段
- 删除操作实际是将 `is_active` 设置为 `False`
- 查询时默认只返回 `is_active=True` 的数据

### 更新策略

评价配置更新采用**增量更新**策略：

1. **评价项**：
   - 传入 `id` 的项会被更新
   - 未传入 `id` 的项会被创建
   - 未在 `itemData` 中的现有项会被软删除

2. **评价选项**：
   - 传入 `id` 的选项会被更新
   - 未传入 `id` 的选项会被创建
   - 未在 `optionData` 中的现有选项会被软删除

3. **评价角色**：
   - 全量替换，所有现有角色关联会被软删除
   - 根据 `roleData` 创建新的角色关联

### 评价开启节点

- `openNodeId` 用于指定在哪个节点开启该评价项
- 当项目到达指定节点时，该评价项才会开放评价
- 为 `null` 时表示评价项始终开放

### 同步到 PM 模块

评价配置通过 `EvaluationConfigToPMSerializer` 序列化器同步到 PM 模块，用于项目绩效评价：
- 同步时不包含时间字段（`createTime`、`updateTime`）
- 角色信息只返回 ID 列表
