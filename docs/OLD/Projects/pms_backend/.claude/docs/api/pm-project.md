# PM - Project 接口文档

> 最后更新：2026-03-20
> App: `PM` | Model: `Project_List`
> Base URL: `/pm/project`

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
| GET | `/pm/project` | 获取项目列表 | ✅ |
| POST | `/pm/project` | 创建项目 | ✅ |
| GET | `/pm/project/<id>` | 获取项目详情 | ✅ |
| PATCH | `/pm/project/<id>` | 更新项目 | ✅ |
| DELETE | `/pm/project/<id>` | 删除项目 | ✅ |
| PATCH | `/pm/project/<id>/status` | 更新项目状态 | ✅ |
| POST | `/pm/project/search` | 搜索项目 | ✅ |
| GET | `/pm/project/enums` | 获取枚举数据 | ✅ |
| GET | `/pm/project/report` | 获取项目报表 | ✅ |
| GET | `/pm/project/<id>/tree` | 获取项目节点树 | ✅ |
| GET | `/pm/project/<id>/folder` | 获取项目文件夹 | ✅ |
| GET | `/pm/project/<id>/follower` | 获取项目关注者 | ✅ |
| GET | `/pm/project/category` | 获取项目分类统计 | ✅ |

---

## 接口详情

### 1. 获取项目列表

**GET** `/pm/project`

**Query 参数**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| type | string | 否 | ALL | 项目列表类型分类 |
| owner | string | 否 | - | 项目负责人ID（逗号分隔） |
| customer | string | 否 | - | 客户ID（逗号分隔） |
| sort | string | 否 | CT:DESC | 排序规则 |
| evaluation_status | string | 否 | ALL | 评价标识 |
| order | string | 否 | ALL | 是否下单标识 |
| label | string | 否 | - | 模板标签ID（逗号分隔） |
| time_type | string | 否 | create_time | 时间类型 |
| start_time | DateTime | 否 | - | 开始时间 |
| end_time | DateTime | 否 | - | 结束时间 |
| limit | int | 否 | 10 | 每页数量 |
| skip | int | 否 | 0 | 跳过数量 |

**type 参数可选值**

| 值 | 说明 |
|----|------|
| ALL | 全部 |
| PRO | 进行中 |
| CHG | 变更中 |
| COM | 已完成 |
| SUS | 已暂停 |
| INPROG | 申请中 |
| CANCEL | 取消立项 |
| CHGS | 变更完成 |
| RPB | 我负责的 |
| FLW | 我关注的 |
| IND | 我参与的 |

**sort 参数格式**

`字段:方向`，逗号分隔多个排序规则

| 字段 | 说明 | 方向 |
|------|------|------|
| CT | 创建时间 | ASC/DESC |
| GT | 交付时间 | ASC/DESC |
| AT | 暂停时间 | ASC/DESC |
| CET | 完成时间 | ASC/DESC |
| OWN | 负责人 | ASC/DESC |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "name": "【标准模板】项目名称",
        "owner_id": 1,
        "state": "1",
        "template_id": 1,
        "deadline_time": "2026-03-20 00:00:00",
        "difficulty": "EASY",
        "workload": "W1",
        "business": "B1",
        "owner": {
          "id": 1,
          "nickname": "负责人",
          "avatar": "avatar_url"
        },
        "creator": {
          "id": 1,
          "nickname": "创建人",
          "avatar": "avatar_url"
        },
        "progress": "里程碑名称中：用户1, 用户2",
        "todo_node": {
          "name": "进行中节点",
          "is_overdue": false
        },
        "place_order_flag": false,
        "milestone": [
          {
            "id": 1,
            "name": "里程碑1",
            "state": 1
          }
        ],
        "last_updated": true,
        "expire_status": "ACTIVE",
        "change": {
          "reason": "变更原因",
          "complete_time": "2026-03-20 00:00:00",
          "type": "类型"
        },
        "customer": "客户名称",
        "temp_pause_time": "2026-03-20 00:00:00",
        "temp_change_time": "2026-03-20 00:00:00"
      }
    ]
  },
  "total": 100
}
```

---

### 2. 创建项目

**POST** `/pm/project`

**请求体**

```json
{
  "name": "项目名称",
  "modelName": "机型名称",
  "deadlineTime": "2026-03-20",
  "customerId": 1,
  "templateVersionId": 1,
  "ownerId": 1,
  "difficulty": "EASY",
  "workload": "W1",
  "business": "B1"
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | ✅ | 项目名称 |
| modelName | string | ✅ | 机型名称 |
| deadlineTime | DateTime | ✅ | 交付日期 |
| customerId | int | ✅ | 客户ID |
| templateVersionId | int | ✅ | 项目模板版本ID |
| ownerId | int | 否 | 项目负责人ID（默认为当前用户） |
| difficulty | string | 否 | 项目难度（默认EASY） |
| workload | string | 否 | 工作量（默认W1） |
| business | string | 否 | 业务类型（默认B1） |

**difficulty 可选值**

| 值 | 说明 | 积分 |
|----|------|------|
| LOW | 简单 | 0.5 |
| EASY | 一般 | 1.0 |
| MEDIUM | 中等 | 2.0 |
| HARD | 挑战 | 3.0 |

**workload 可选值**

| 值 | 说明 | 积分 |
|----|------|------|
| W1 | ≤2天 | 1.0 |
| W2 | >3天 | 2.0 |
| W3 | >7天 | 3.0 |
| W4 | >30天 | 4.0 |
| W5 | >3个月 | 5.0 |

**business 可选值**

| 值 | 说明 | 积分 |
|----|------|------|
| B1 | 经营业务类 | 1.0 |
| B2 | 拓展业务类 | 2.0 |
| B3 | 战略业务类 | 3.0 |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "projectId": 1
  }
}
```

---

### 3. 获取项目详情

**GET** `/pm/project/<id>`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 项目ID |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "name": "项目名称",
    "content": "项目描述",
    "state": "1",
    "place_order_flag": false,
    "create_time": "2026-03-20 00:00:00",
    "deadline_time": "2026-03-20 00:00:00",
    "complete_time": false,
    "last_change_time": false,
    "is_overdue": false,
    "creator": {
      "id": 1,
      "nickname": "创建人",
      "avatar": "avatar_url"
    },
    "owner": {
      "id": 1,
      "nickname": "负责人",
      "avatar": "avatar_url"
    },
    "followers": [
      {
        "id": 1,
        "nickname": "关注者",
        "avatar": "avatar_url"
      }
    ],
    "customer": {
      "id": 1,
      "name": "客户名称",
      "model_id": 1,
      "model": "机型名称"
    },
    "nodes": {
      "current": {
        "id": 1,
        "name": "进行中节点"
      },
      "list": []
    },
    "evaluationAvailable": true,
    "evaluationVisible": true,
    "evaluationStatus": "UNEVALUATED",
    "authority": {
      "1100": true,
      "1101": true,
      "1102": true
    }
  }
}
```

---

### 4. 更新项目

**PATCH** `/pm/project/<id>`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 项目ID |

**请求体**

```json
{
  "name": "新项目名称",
  "content": "项目描述",
  "deadlineTime": "2026-03-20",
  "ownerId": 1,
  "placeOrderFlag": true,
  "difficulty": "EASY",
  "workload": "W1",
  "business": "B1",
  "modelName": "新机型名称"
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 否 | 项目名称 |
| content | string | 否 | 项目描述 |
| deadlineTime | DateTime | 否 | 交付日期 |
| ownerId | int | 否 | 项目负责人ID |
| placeOrderFlag | boolean | 否 | 是否已下单 |
| difficulty | string | 否 | 项目难度 |
| workload | string | 否 | 工作量 |
| business | string | 否 | 业务类型 |
| modelName | string | 否 | 机型名称 |

**响应示例**

```json
{
  "msg": "success"
}
```

---

### 5. 删除项目

**DELETE** `/pm/project/<id>`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 项目ID |

**响应示例**

```json
{
  "msg": "删除成功"
}
```

---

### 6. 更新项目状态

**PATCH** `/pm/project/<id>/status`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 项目ID |

**请求体**

```json
{
  "status": "1",
  "reason": "状态变更原因"
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| status | string | ✅ | 目标状态 |
| reason | string | 否 | 状态变更原因 |

**status 可选值**

| 值 | 说明 |
|----|------|
| 1 | 进行中 |
| 2 | 已完成 |
| 4 | 已暂停 |
| 6 | 取消立项 |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "projectId": 1,
    "state": "1"
  }
}
```

---

### 7. 搜索项目

**POST** `/pm/project/search`

**请求体**

```json
{
  "keyword": "搜索关键词"
}
```

**响应示例**

```json
{
  "msg": "success",
  "data": [
    {
      "title": "项目名称",
      "url": 1,
      "type": "项目",
      "classify": "project",
      "stringTime": "2026-03-20 00:00:00",
      "state": {
        "explain": "进行中",
        "code": 1
      },
      "keyword": {
        "describe": "机型名称"
      }
    }
  ]
}
```

---

### 8. 获取枚举数据

**GET** `/pm/project/enums`

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "difficulty": [
      {"value": "LOW", "point": "0.5", "label": "简单"},
      {"value": "EASY", "point": "1.0", "label": "一般"},
      {"value": "MEDIUM", "point": "2.0", "label": "中等"},
      {"value": "HARD", "point": "3.0", "label": "挑战"}
    ],
    "workload": [
      {"value": "W1", "point": "1.0", "label": "≤2天"},
      {"value": "W2", "point": "2.0", "label": ">3天"},
      {"value": "W3", "point": "3.0", "label": ">7天"},
      {"value": "W4", "point": "4.0", "label": ">30天"},
      {"value": "W5", "point": "5.0", "label": ">3个月"}
    ],
    "business": [
      {"value": "B1", "point": "1.0", "label": "经营业务类"},
      {"value": "B2", "point": "2.0", "label": "拓展业务类"},
      {"value": "B3", "point": "3.0", "label": "战略业务类"}
    ],
    "type": {
      "ALL": "全部",
      "PRO": "进行中",
      "CHG": "变更中",
      "COM": "已完成",
      "SUS": "已暂停",
      "INPROG": "申请中",
      "CANCEL": "取消立项",
      "CHGS": "变更完成",
      "RPB": "我负责的",
      "FLW": "我关注的",
      "IND": "我参与的"
    },
    "state": {
      "1": "进行中",
      "2": "已完成",
      "3": "项目变更中",
      "4": "已暂停",
      "5": "申请中",
      "6": "取消立项"
    },
    "expire_status": {
      "ACTIVE": "正常",
      "EXPIRING": "有超期风险",
      "EXPIRED": "已超期"
    },
    "place_order_flag": [
      {"value": "ALL", "label": "全部"},
      {"value": "TRUE", "label": "已下单"},
      {"value": "FALSE", "label": "未下单"}
    ],
    "evaluation_status": [
      {"value": "ALL", "label": "全部"},
      {"value": "EVALUATED", "label": "已完成评价"},
      {"value": "UNEVALUATED", "label": "未完成评价"}
    ],
    "templateLabel": []
  }
}
```

---

### 9. 获取项目报表

**GET** `/pm/project/report`

获取项目待办报表飞书表格链接。

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "status": true,
    "token": "sheet_token",
    "url": "https://feishu.cn/sheets/sheet_token"
  }
}
```

---

### 10. 获取项目节点树

**GET** `/pm/project/<id>/tree`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 项目ID |

**响应示例**

```json
{
  "msg": "success",
  "data": []
}
```

---

### 11. 获取项目文件夹

**GET** `/pm/project/<id>/folder`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 项目ID |

**响应示例**

```json
{
  "msg": "success",
  "data": []
}
```

---

### 12. 获取项目关注者

**GET** `/pm/project/<id>/follower`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 项目ID |

**响应示例**

```json
{
  "msg": "success",
  "data": []
}
```

---

### 13. 获取项目分类统计

**GET** `/pm/project/category`

获取项目分类统计数据。

**响应示例**

```json
{
  "msg": "success",
  "data": []
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
# 1. 获取项目列表
curl -X GET "http://localhost:8001/pm/project?type=PRO&limit=10&skip=0" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 2. 创建项目
curl -X POST "http://localhost:8001/pm/project" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "新项目",
    "modelName": "机型A",
    "deadlineTime": "2026-03-20",
    "customerId": 1,
    "templateVersionId": 1
  }'

# 3. 获取项目详情
curl -X GET "http://localhost:8001/pm/project/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 4. 更新项目
curl -X PATCH "http://localhost:8001/pm/project/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "更新后的项目名称"
  }'

# 5. 更新项目状态
curl -X PATCH "http://localhost:8001/pm/project/1/status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "status": "1"
  }'

# 6. 删除项目
curl -X DELETE "http://localhost:8001/pm/project/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 7. 搜索项目
curl -X POST "http://localhost:8001/pm/project/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "keyword": "项目"
  }'

# 8. 获取枚举数据
curl -X GET "http://localhost:8001/pm/project/enums" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 数据模型

### Project_List 模型字段

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键 |
| name | string(255) | 项目名称 |
| content | string(255) | 项目描述 |
| business | string(255) | 业务类型 |
| difficulty | string(255) | 项目难度 |
| workload | string(255) | 工作量 |
| customer | FK(Customer) | 客户 |
| model | FK(CustomerModel) | 客户机型 |
| template | FK(ProjectTemplateVersion) | 项目模板版本 |
| create_time | DateTime | 创建时间 |
| deadline_time | DateTime | 截止时间（交付日期） |
| complete_time | DateTime | 交付时间（完成时间） |
| place_order_date | DateTime | 下单时间 |
| place_order_flag | boolean | 是否已下单 |
| state | int | 项目状态 |
| creator | FK(User) | 创建人 |
| owner | FK(User) | 项目负责人 |
| owner_role_enabled | boolean | 项目负责人所属项目角色是否启用 |

### 表名

`PM_project_list`

### 项目状态说明

| 值 | 说明 |
|----|------|
| 0 | - |
| 1 | 进行中 |
| 2 | 已完成 |
| 3 | 项目变更中 |
| 4 | 已暂停 |
| 5 | 申请中 |
| 6 | 取消立项 |
