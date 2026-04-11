# PM - EvaluationV2 接口文档

> 最后更新：2026-03-21
> App: `PM` | Model: `Project_Performance_Rework`, `Project_Performance_Contribution`, `Project_Performance_Settled`, `Project_Performance_Delivery`
> Base URL: `/pm/evaluation/v2`

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
| POST | `/pm/evaluation/rework` | 创建返工记录 | ✅ |
| PUT | `/pm/evaluation/rework/<code>` | 更新返工记录 | ✅ |
| PATCH | `/pm/evaluation/rework/<code>` | 部分更新返工记录 | ✅ |
| DELETE | `/pm/evaluation/rework/<codes>` | 批量删除返工记录 | ✅ |
| POST | `/pm/evaluation/contribution` | 创建贡献度记录 | ✅ |
| PUT | `/pm/evaluation/contribution/<code>` | 更新贡献度记录 | ✅ |
| DELETE | `/pm/evaluation/contribution/<codes>` | 批量删除贡献度记录 | ✅ |
| GET | `/pm/evaluation/<code>` | 获取项目绩效详情 | ✅ |
| POST | `/pm/evaluation/<code>` | 项目结算/取消结算 | ✅ |
| PUT | `/pm/evaluation/v2/delivery/<id>` | 更新项目交付情况 | ✅ |

---

## 接口详情

### 1. 创建返工记录

**POST** `/pm/evaluation/rework`

创建项目返工记录，支持指定多个责任人。

**权限要求**

- 项目未结算时才能创建
- 创建者自动记录为当前用户

**请求体**

```json
{
  "project_id": 1,
  "rework_time": "2024-01-01T10:00:00+08:00",
  "content": "需求理解偏差导致返工",
  "loss_amount": 500,
  "owners": [1, 2, 3]
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_id | int | ✅ | 项目 ID |
| rework_time | string | ✅ | 返工时间（ISO 8601 格式） |
| content | string | ✅ | 返工内容描述 |
| loss_amount | int | 否 | 损失金额（默认 0） |
| owners | array[int] | 否 | 责任人 ID 列表 |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "is_operator": true
  }
}
```

**错误响应示例**

```json
{
  "msg": "项目积分已结算，不允许修改"
}
```

---

### 2. 更新返工记录

**PUT** `/pm/evaluation/rework/<code>`

完整更新返工记录。

**权限要求**

- 仅创建者或超级用户可更新
- 项目未结算时才能更新

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| code | int | 返工记录 ID |

**请求体**

```json
{
  "project_id": 1,
  "rework_time": "2024-01-02T10:00:00+08:00",
  "content": "需求理解偏差导致返工（更新）",
  "loss_amount": 800,
  "owners": [1, 2]
}
```

**响应示例**

```json
{
  "msg": "success"
}
```

**错误响应示例**

```json
{
  "msg": "权限不足，用户权限组不正确"
}
```

---

### 3. 部分更新返工记录

**PATCH** `/pm/evaluation/rework/<code>`

部分更新返工记录字段。

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| code | int | 返工记录 ID |

**请求体**

```json
{
  "loss_amount": 1000
}
```

**响应示例**

```json
{
  "msg": "success"
}
```

---

### 4. 批量删除返工记录

**DELETE** `/pm/evaluation/rework/<codes>`

批量删除返工记录，多个 ID 用逗号分隔。

**权限要求**

- 仅创建者或超级用户可删除
- 项目未结算时才能删除

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| codes | string | 返工记录 ID 列表（逗号分隔），如：`1,2,3` |

**响应示例**

```json
{
  "msg": "success"
}
```

**错误响应示例**

```json
{
  "msg": "项目积分已结算，不允许修改"
}
```

---

### 5. 创建贡献度记录

**POST** `/pm/evaluation/contribution`

创建项目成员贡献度记录。

**权限要求**

- 需要 `3001` 权限（铁三角权限）
- 项目未结算时才能创建
- 所有人贡献度比例总和不能超过 100%

**请求体**

```json
{
  "project_id": 1,
  "owner_id": 2,
  "proportion": 30,
  "content": "负责前端开发工作"
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_id | int | ✅ | 项目 ID |
| owner_id | int | ✅ | 贡献者用户 ID |
| proportion | int | ✅ | 贡献度比例（1-100） |
| content | string | 否 | 贡献内容描述 |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 1
  }
}
```

**错误响应示例**

```json
{
  "msg": "错误，分成比例不正确"
}
```

---

### 6. 更新贡献度记录

**PUT** `/pm/evaluation/contribution/<code>`

更新贡献度记录。

**权限要求**

- 需要 `3001` 权限（铁三角权限）
- 项目未结算时才能更新

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| code | int | 贡献度记录 ID |

**请求体**

```json
{
  "project_id": 1,
  "owner_id": 2,
  "proportion": 40,
  "content": "负责前端和部分后端开发工作"
}
```

**响应示例**

```json
{
  "msg": "success"
}
```

---

### 7. 批量删除贡献度记录

**DELETE** `/pm/evaluation/contribution/<codes>`

批量删除贡献度记录。

**权限要求**

- 需要 `3001` 权限（铁三角权限）
- 项目未结算时才能删除

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| codes | string | 贡献度记录 ID 列表（逗号分隔） |

**响应示例**

```json
{
  "msg": "success"
}
```

---

### 8. 获取项目绩效详情

**GET** `/pm/evaluation/<code>`

获取项目绩效详情，包含项目难度、工作量、业务类型、返工情况、交付情况、个人贡献度等信息，并自动计算项目积分和个人积分。

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| code | int | 项目 ID |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "delivery": {
      "value": "ON_TIME",
      "point": 1.0
    },
    "difficulty": {
      "value": "HIGH",
      "point": 1.2
    },
    "workload": {
      "value": "MEDIUM",
      "point": 1.0
    },
    "business": {
      "value": "NEW",
      "point": 1.1
    },
    "rework": {
      "list": [
        {
          "id": 1,
          "owners": [
            {
              "id": 1,
              "name": "张三",
              "avatar": "avatar_url"
            }
          ],
          "project_id": 1,
          "content": "需求理解偏差导致返工",
          "rework_time": "2024-01-01 10:00:00",
          "loss_amount": 500,
          "owner": [
            {
              "id": 1,
              "name": "张三",
              "avatar": "avatar_url"
            }
          ],
          "creator": {
            "id": 1,
            "name": "张三",
            "avatar": "avatar_url"
          },
          "is_operator": true
        }
      ],
      "point": "0.5"
    },
    "personal": [
      {
        "id": 1,
        "owner_id": 2,
        "content": "负责前端开发工作",
        "proportion": 30,
        "point": 0.2178,
        "owner": {
          "id": 2,
          "name": "李四",
          "avatar": "avatar_url",
          "in_service": true,
          "role": "前端开发"
        },
        "creator": {
          "id": 1,
          "name": "张三",
          "avatar": "avatar_url"
        },
        "is_node_owner": true
      }
    ],
    "is_decision_maker": true,
    "settled": {
      "id": 1,
      "type": "MANUAL",
      "operator": {
        "id": 1,
        "name": "张三",
        "avatar": "avatar_url"
      },
      "total": 1,
      "create_time": "2024-01-01 10:00:00"
    }
  }
}
```

**响应字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 项目 ID |
| delivery | object/null | 项目交付情况（value: 枚举值, point: 系数） |
| difficulty | object | 项目难度（value: 枚举值, point: 系数） |
| workload | object | 项目工作量（value: 枚举值, point: 系数） |
| business | object | 项目业务类型（value: 枚举值, point: 系数） |
| rework | object | 返工情况（list: 返工记录, point: 系数） |
| personal | array | 个人贡献度列表（包含自动计算的个人积分） |
| is_decision_maker | boolean | 当前用户是否为项目决策者 |
| settled | object/null | 结算信息 |

**积分计算公式**

```
项目难度系数 = difficulty.point * workload.point * business.point
项目总积分 = 项目难度系数 * rework.point * delivery.point
个人积分 = 项目总积分 * personal.proportion / 100
```

---

### 9. 项目结算/取消结算

**POST** `/pm/evaluation/<code>`

对项目进行结算或取消结算。

**权限要求**

- 需要 `3001` 权限（铁三角权限）

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| code | int | 项目 ID |

**响应示例（结算）**

```json
{
  "msg": "success",
  "data": {
    "settlement": true
  }
}
```

**响应示例（取消结算）**

```json
{
  "msg": "success",
  "data": {
    "settlement": false
  }
}
```

**结算逻辑**

1. **结算时**：
   - 创建结算记录
   - 检查被评价角色但未进行评价的情况，将个人贡献度设置为 0
   - 记录操作日志

2. **取消结算时**：
   - 删除结算记录
   - 记录操作日志

---

### 10. 更新项目交付情况

**PUT** `/pm/evaluation/v2/delivery/<id>`

更新项目交付情况评价。

**权限要求**

- 需要 `3001` 权限（铁三角权限）
- 项目未结算时才能更新

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 项目 ID |

**请求体**

```json
{
  "projectId": 1,
  "delivery": "ON_TIME"
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| projectId | int | ✅ | 项目 ID |
| delivery | string | ✅ | 交付情况枚举值 |

**交付情况枚举**

| 值 | 说明 | 系数 |
|----|------|------|
| ON_TIME | 按时交付 | 1.0 |
| EARLY | 提前交付 | 1.2 |
| DELAY | 延期交付 | 0.8 |
| SERIOUS_DELAY | 严重延期 | 0.5 |

**响应示例**

```json
{
  "msg": "success"
}
```

**错误响应示例**

```json
{
  "msg": "项目积分已结算，不允许修改"
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
# 1. 创建返工记录
curl -X POST "http://localhost:8001/pm/evaluation/rework" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "project_id": 1,
    "rework_time": "2024-01-01T10:00:00+08:00",
    "content": "需求理解偏差导致返工",
    "loss_amount": 500,
    "owners": [1, 2, 3]
  }'

# 2. 更新返工记录
curl -X PUT "http://localhost:8001/pm/evaluation/rework/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "project_id": 1,
    "rework_time": "2024-01-02T10:00:00+08:00",
    "content": "需求理解偏差导致返工（更新）",
    "loss_amount": 800,
    "owners": [1, 2]
  }'

# 3. 批量删除返工记录
curl -X DELETE "http://localhost:8001/pm/evaluation/rework/1,2,3" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 4. 创建贡献度记录
curl -X POST "http://localhost:8001/pm/evaluation/contribution" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "project_id": 1,
    "owner_id": 2,
    "proportion": 30,
    "content": "负责前端开发工作"
  }'

# 5. 更新贡献度记录
curl -X PUT "http://localhost:8001/pm/evaluation/contribution/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "project_id": 1,
    "owner_id": 2,
    "proportion": 40,
    "content": "负责前端和部分后端开发工作"
  }'

# 6. 获取项目绩效详情
curl -X GET "http://localhost:8001/pm/evaluation/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 7. 项目结算
curl -X POST "http://localhost:8001/pm/evaluation/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 8. 更新项目交付情况
curl -X PUT "http://localhost:8001/pm/evaluation/v2/delivery/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "projectId": 1,
    "delivery": "ON_TIME"
  }'
```

---

## 数据模型

### Project_Performance_Rework 模型字段

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| project | FK(Project_List) | 关联项目 |
| rework_time | DateTime | 返工时间 |
| create_time | DateTime | 创建时间 |
| content | string | 返工内容 |
| loss_amount | int | 损失金额 |
| creator | FK(User) | 创建人 |

### Project_Performance_Rework_Owner 模型字段

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| rework | FK(Project_Performance_Rework) | 关联返工记录 |
| owner | FK(User) | 责任人 |

### Project_Performance_Contribution 模型字段

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| project | FK(Project_List) | 关联项目 |
| create_time | DateTime | 创建时间 |
| content | string | 贡献内容 |
| proportion | int | 贡献度比例（1-100） |
| creator | FK(User) | 创建人 |
| owner | FK(User) | 贡献者 |

### Project_Performance_Settled 模型字段

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| type | string | 结算类型（AUTO: 自动, MANUAL: 手动） |
| project | FK(Project_List) | 关联项目 |
| operator | FK(User) | 操作人 |
| create_time | DateTime | 创建时间 |

### Project_Performance_Delivery 模型字段

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| project | OneToOneFK(Project_List) | 关联项目（一对一） |
| delivery | string | 交付情况枚举值 |
| creator | FK(User) | 创建人 |
| create_time | DateTime | 创建时间 |

### 表名

- `PM_evaluate_v2_performance_rework` - 项目返工记录表
- `PM_evaluate_v2_performance_rework_owner` - 返工责任人表
- `PM_evaluate_v2_performance_contribution` - 项目贡献记录表
- `PM_evaluate_v2_performance_settled` - 项目结算表
- `PM_evaluate_v2_performance_delivery` - 项目交付情况表

---

## 设计说明

### 返工系数计算规则

| 返工次数 | 损失金额 | 系数 |
|----------|----------|------|
| 0 | - | 1.0 |
| 1 | ≤ 500 | 0.5 |
| 1 | > 500 且 ≤ 1000 | 0.3 |
| 2 | ≤ 1000 | 0.3 |
| 其他情况 | - | 0.0 |

### 项目积分计算公式

```
项目难度系数 = difficulty.point × workload.point × business.point
项目总积分 = 项目难度系数 × rework.point × delivery.point
个人积分 = 项目总积分 × personal.proportion / 100
```

### 结算状态控制

项目结算后（`project_settleds` 存在记录）：
- 返工记录不可新增、修改、删除
- 贡献度记录不可新增、修改、删除
- 交付情况不可修改

### 权限说明

| 操作 | 权限要求 |
|------|----------|
| 创建/修改/删除返工记录 | 创建者本人或超级用户 |
| 创建/修改/删除贡献度记录 | 3001 权限（铁三角） |
| 项目结算/取消结算 | 3001 权限（铁三角） |
| 修改交付情况 | 3001 权限（铁三角） |

### 贡献度比例验证

- 所有人贡献度比例总和不能超过 100%
- 更新时会排除当前记录自身的比例进行校验

### 节点成员自动纳入

获取项目绩效详情时，会自动将项目节点的参与成员纳入 `personal` 列表：
- 如果该成员已有贡献度记录，显示实际数据
- 如果该成员无贡献度记录，显示占位数据（`proportion: null`）
- 通过 `is_node_owner` 字段标识是否为节点成员
