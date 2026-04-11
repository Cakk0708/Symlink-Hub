# APS - Order 接口文档

> 最后更新：2026-03-30
> App: `APS` | Model: `Order`
> Base URL: `/aps`

---

## 认证说明

所有接口均需在请求头中携带 JWT Token：

```
Authorization: Bearer YOUR_JWT_TOKEN
```

**权限说明**：所有订单操作均会自动过滤当前用户所属组织的数据。

---

## 接口列表

| 方法 | 路径 | 描述 | 需要认证 |
|------|------|------|----------|
| GET | `/orders` | 获取订单列表 | ✅ |
| POST | `/orders` | 创建订单 | ✅ |
| GET | `/orders/<id>` | 获取订单详情 | ✅ |
| PATCH | `/orders/<id>` | 更新订单状态 | ✅ |
| GET | `/orders/enums` | 获取订单枚举值 | ✅ |

---

## 接口详情

### 1. 获取订单列表

**GET** `/aps/orders`

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，从 0 开始，默认 0 |
| orderNo | string | 否 | 订单编号（code 字段，精确匹配） |
| status | string | 否 | 订单状态，可选值见下方枚举 |
| category | string | 否 | 订单类别，可选值见下方枚举 |
| goofishName | string | 否 | 客户名称（模糊搜索） |
| keywords | string | 否 | 关键词搜索（账号/昵称/邮箱/手机/备注/客户名称） |

**订单状态枚举 (status)**

| 值 | 说明 |
|----|------|
| waiting | 等待 |
| doing | 进行中 |
| done | 完成 |
| pause | 暂停 |
| cancel | 取消 |
| error | 错误 |

**订单类别枚举 (category)**

| 值 | 说明 |
|----|------|
| exp | 经验 |
| gems | 宝石 |
| 3x_xp | 三倍经验 |
| sign | 签到 |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "code": "O20250308001",
        "category": "exp",
        "plannedQty": 1000,
        "beforeValue": 5000,
        "completedQty": 500,
        "scheduleAt": "2026-03-15 10:30:00",
        "planDuration": 60,
        "createdAt": "2026-03-15 08:00:00",
        "accountUsername": "test_user",
        "customerName": "闲鱼客户",
        "status": "doing",
        "organizationName": "测试组织"
      }
    ],
    "pagination": {
      "page": 0,
      "pageSize": 10,
      "total": 100
    }
  }
}
```

---

### 2. 创建订单

**POST** `/aps/orders`

订单支持更精细的配置，不同类型订单有专属字段。

**通用请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| accountId | int | 是 | 关联的账号 ID |
| category | string | 条件 | 订单类别：exp/gems/3x_xp/sign（关联套餐时可省略，自动从套餐填充） |
| business | string | 否 | 业务类型：paid(默认)/free |
| price | decimal | 否 | 价格，默认 0（关联套餐时自动从套餐填充） |
| packageId | int | 否 | 关联套餐 ID（传入后自动填充 category、price、plannedQty） |

#### 3.1 EXP 订单

**请求体示例**

```json
{
  "accountId": 1,
  "category": "exp",
  "business": "paid",
  "price": 100.00,
  "plannedQty": 1000,
  "planDuration": 60,
  "scheduleAt": "2026-03-15T10:30:00Z"
}
```

**EXP 专属参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| plannedQty | int | 否 | 计划经验数量，默认 0 |
| planDuration | int | 是 | 计划持续时间（分钟），分批执行次数 |
| scheduleAt | string | 否 | 计划执行时间（ISO 8601 格式） |

**执行逻辑**
- 到达 `scheduleAt` 时间后开始执行
- 每次执行获得 `plannedQty / planDuration` 经验
- 达到目标后自动标记为完成

#### 3.2 GEMS 订单

**请求体示例**

```json
{
  "accountId": 1,
  "category": "gems",
  "business": "paid",
  "price": 50.00,
  "plannedQty": 500
}
```

**GEMS 专属参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| plannedQty | int | 否 | 计划宝石数量，默认 0 |

**执行逻辑**
- 每分钟自动执行一次
- 领取所有可用的宝石奖励
- 达到目标后自动标记为完成

#### 3.3 THREE_XP 订单

**请求体示例**

```json
{
  "accountId": 1,
  "category": "3x_xp",
  "business": "paid",
  "price": 30.00,
  "plannedQty": 10
}
```

**THREE_XP 专属参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| plannedQty | int | 否 | 计划领取次数，默认 0 |

**执行逻辑**
- 每分钟检查一次
- 使用 Redis 避免频繁执行（TTL > 120秒时跳过）
- 每次成功领取后 `completed_qty += 1`

#### 3.4 SIGN 订单

**请求体示例**

```json
{
  "accountId": 1,
  "category": "sign",
  "business": "paid",
  "price": 200.00,
  "plannedQty": 92,
  "startDate": "2026-03-15",
  "endDate": "2026-04-15",
  "executionTime": "08:00"
}
```

**SIGN 专属参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| plannedQty | int | 否 | 每日经验目标总量，默认 0 |
| startDate | string | 是 | 开始日期（YYYY-MM-DD） |
| endDate | string | 是 | 结束日期（YYYY-MM-DD） |
| executionTime | string | 是 | 执行时间（HH:MM 格式） |

**执行逻辑**
- 每分钟检查一次
- 首次执行时，订单状态从 `waiting` 转为 `doing`
- 日期和时间比较均使用 UTC+8 时区（`execution_time`、`start_date`、`end_date` 均为 UTC+8）
- 检查当前日期是否在 `startDate` 和 `endDate` 范围内
- 检查当前时间是否匹配 `executionTime`（精确到分钟）
- 循环答题累加经验值，直到累计经验 >= `plannedQty` 后结束本次执行
- 每次答题间隔 1 秒
- 每日累计经验值写入主订单 `completed_qty`
- 每次执行完毕后检查当前日期是否到达 `endDate`，到达则标记订单为 `done`

**订单业务规则**
- 自动关联当前用户的组织
- 创建对应的子订单记录（OrderExp/OrderGem/OrderThreeXP/OrderSigning）
- 自动记录初始值（exp 或 gems）

**响应示例**

```json
{
  "msg": "success"
}
```

**错误示例**

```json
{
  "msg": "error",
  "data": {
    "planDuration": ["计划持续时间必填"]
  }
}
```

---

### 3. 获取订单详情

**GET** `/aps/orders/<id>`

获取订单详情，返回包含子模型数据的结构化信息。

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 订单 ID |

**响应示例（EXP 类型）**

```json
{
  "msg": "success",
  "data": {
    "document": {
      "id": 2,
      "code": "O20250323001",
      "status": "doing",
      "category": "exp",
      "business": "paid",
      "price": "100.00",
      "version": 2
    },
    "progressData": {
      "plannedQty": 1000,
      "completedQty": 500
    },
    "typeDetail": {
      "beforeValue": 5000,
      "planDuration": 60,
      "scheduleAt": "2026-03-23 10:30:00",
      "plannedQty": 1000,
      "completedQty": 500
    },
    "relations": {
      "account": {
        "id": 1,
        "nickname": "测试账号",
        "username": "test_user",
        "phone": "13800138000",
        "email": "test@example.com",
        "remark": "备注信息"
      },
      "customer": {
        "id": 1,
        "name": "闲鱼客户",
        "code": "C20250308001"
      },
      "organization": {
        "id": 1,
        "code": "ORG001",
        "name": "测试组织"
      }
    },
    "others": {
      "createdAt": "2026-03-23 08:00:00",
      "updatedAt": "2026-03-23 10:00:00",
      "completedAt": null
    }
  }
}
```

**响应示例（SIGN 类型）**

```json
{
  "msg": "success",
  "data": {
    "document": {
      "id": 3,
      "code": "O20250323002",
      "status": "doing",
      "category": "sign",
      "business": "paid",
      "price": "200.00",
      "version": 2
    },
    "progressData": {
      "plannedQty": 92,
      "completedQty": 184
    },
    "typeDetail": {
      "startDate": "2026-03-15",
      "endDate": "2026-04-15",
      "executionTime": "08:00",
      "plannedQty": 92
    },
    "relations": {
      "account": {
        "id": 1,
        "nickname": "测试账号",
        "username": "test_user"
      },
      "customer": {
        "id": 1,
        "name": "闲鱼客户",
        "code": "C20250308001"
      },
      "organization": {
        "id": 1,
        "code": "ORG001",
        "name": "测试组织"
      }
    },
    "others": {
      "createdAt": "2026-03-23 08:00:00",
      "updatedAt": "2026-03-23 10:00:00",
      "completedAt": null
    }
  }
}
```

**错误示例**

```json
{
  "msg": "error",
  "data": "订单不存在"
}
```

---

### 4. 更新订单状态

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 订单 ID |

```json
{
  "msg": "success",
  "data": {
    "document": {
      "id": 1,
      "code": "O20250308001",
      "scheduleAt": "2026-03-15 10:30:00",
      "status": "doing",
      "category": "exp"
    },
    "progressData": {
      "plannedQty": 1000,
      "beforeValue": 5000,
      "completedQty": 500,
      "planDuration": 60
    },
    "relations": {
      "account": {
        "nickname": "测试账号",
        "username": "test_user",
        "phone": "13800138000",
        "email": "test@example.com",
        "remark": "备注信息"
      },
      "customer": {
        "name": "闲鱼客户",
        "code": "C20250308001"
      },
      "organization": {
        "id": 1,
        "code": "ORG001",
        "name": "测试组织"
      }
    },
    "others": {
      "createdAt": "2026-03-15 08:00:00",
      "updatedAt": "2026-03-15 10:00:00"
    }
  }
}
```

```json
{
  "msg": "success",
  "data": {
    "document": {
      "id": 2,
      "code": "O20250323001",
      "status": "doing",
      "category": "exp",
      "business": "paid",
      "price": "100.00",
      "version": 2
    },
    "progressData": {
      "plannedQty": 1000,
      "completedQty": 500
    },
    "typeDetail": {
      "beforeValue": 5000,
      "planDuration": 60,
      "scheduleAt": "2026-03-23 10:30:00",
      "plannedQty": 1000,
      "completedQty": 500
    },
    "relations": {
      "account": {
        "id": 1,
        "nickname": "测试账号",
        "username": "test_user",
        "phone": "13800138000",
        "email": "test@example.com",
        "remark": "备注信息"
      },
      "customer": {
        "id": 1,
        "name": "闲鱼客户",
        "code": "C20250308001"
      },
      "organization": {
        "id": 1,
        "code": "ORG001",
        "name": "测试组织"
      }
    },
    "others": {
      "createdAt": "2026-03-23 08:00:00",
      "updatedAt": "2026-03-23 10:00:00",
      "completedAt": null
    }
  }
}
```

```json
{
  "msg": "success",
  "data": {
    "document": {
      "id": 3,
      "code": "O20250323002",
      "status": "doing",
      "category": "sign",
      "business": "paid",
      "price": "200.00",
      "version": 2
    },
    "progressData": {
      "plannedQty": 30,
      "completedQty": 5
    },
    "typeDetail": {
      "startDate": "2026-03-15",
      "endDate": "2026-04-15",
      "executionTime": "08:00",
      "plannedQty": 92
    },
    "relations": {
      "account": {
        "id": 1,
        "nickname": "测试账号",
        "username": "test_user"
      },
      "customer": {
        "id": 1,
        "name": "闲鱼客户",
        "code": "C20250308001"
      },
      "organization": {
        "id": 1,
        "code": "ORG001",
        "name": "测试组织"
      }
    },
    "others": {
      "createdAt": "2026-03-23 08:00:00",
      "updatedAt": "2026-03-23 10:00:00",
      "completedAt": null
    }
  }
}
```

**响应字段说明**

| 字段分组 | 字段 | 类型 | 说明 |
|---------|------|------|------|
| document | id | int | 订单 ID |
| document | code | string | 订单编号 |
| document | status | string | 订单状态 |
| document | category | string | 订单类别 |
| document | business | string | 业务类型（paid/free） |
| document | price | string | 价格 |
| document | version | int | 版本号（固定为2） |
| progressData | plannedQty | int | 计划数量（主订单） |
| progressData | completedQty | int | 已完成数量（主订单） |
| typeDetail | - | object | 类型特定字段（根据category不同而不同） |
| typeDetail (EXP) | beforeValue | int | 初始经验值 |
| typeDetail (EXP) | planDuration | int | 计划持续时间（分钟） |
| typeDetail (EXP) | scheduleAt | string | 计划执行时间 |
| typeDetail (EXP) | plannedQty | int | 计划数量 |
| typeDetail (EXP) | completedQty | int | 已完成数量 |
| typeDetail (GEMS) | beforeValue | int | 初始宝石值 |
| typeDetail (GEMS) | plannedQty | int | 计划数量 |
| typeDetail (GEMS) | completedQty | int | 已完成数量 |
| typeDetail (THREE_XP) | plannedQty | int | 计划领取次数 |
| typeDetail (THREE_XP) | completedQty | int | 已领取次数 |
| typeDetail (SIGN) | startDate | string | 开始日期 |
| typeDetail (SIGN) | endDate | string | 结束日期 |
| typeDetail (SIGN) | executionTime | string | 执行时间（HH:MM） |
| typeDetail (SIGN) | plannedQty | int | 每日经验目标总量 |
| relations | account | object | 账号信息 |
| relations | customer | object | 客户信息 |
| relations | organization | object | 组织信息 |
| relations | package | object\|null | 套餐信息（id/name/code），未关联套餐时为 null |
| others | createdAt | string | 创建时间 |
| others | updatedAt | string | 更新时间 |
| others | completedAt | string | 完成时间 |

**错误示例**

```json
{
  "msg": "error",
  "data": "订单不存在"
}
```

---

### 5. 获取订单枚举值

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 要更新的订单 ID |

**请求体**

```json
{
  "status": "doing"
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| status | string | 是 | 目标状态，可选值：waiting/doing/done/cancel/pause/error |

**状态转换规则**

| 目标状态 | 允许的源状态 |
|---------|-------------|
| waiting | doing, error, cancel, done |
| cancel | doing, waiting |
| done | doing, waiting |
| pause | -（需根据实际业务确认） |
| error | -（需根据实际业务确认） |

**响应示例**

```json
{
  "msg": "success"
}
```

**错误示例**

```json
{
  "msg": "error",
  "data": {
    "status": ["订单状态不正确，不能修改为取消"]
  }
}
```

**GET** `/aps/orders/enums`

获取订单模块所有枚举选项，用于前端下拉列表。

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "choices": {
      "status": [
        {"value": "waiting", "label": "等待"},
        {"value": "doing", "label": "进行中"},
        {"value": "done", "label": "完成"},
        {"value": "pause", "label": "暂停"},
        {"value": "cancel", "label": "取消"},
        {"value": "error", "label": "错误"}
      ],
      "category": [
        {"value": "exp", "label": "经验"},
        {"value": "gems", "label": "宝石"},
        {"value": "3x_xp", "label": "三倍经验"},
        {"value": "sign", "label": "签到"}
      ],
      "business": [
        {"value": "paid", "label": "付费"},
        {"value": "free", "label": "免费"}
      ]
    }
  }
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
| 403 | 无权限访问该组织数据 |
| 404 | 订单不存在 |
| 500 | 服务器内部错误 |

---

## 完整 cURL 示例

```bash
# 1. 获取订单列表
curl -X GET "http://localhost:8101/aps/orders?page=0&status=doing" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 2. 创建订单 - EXP
curl -X POST "http://localhost:8101/aps/orders" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "accountId": 1,
    "category": "exp",
    "plannedQty": 1000,
    "planDuration": 60,
    "scheduleAt": "2026-03-15T10:30:00Z"
  }'

# 3. 创建订单 - SIGN
curl -X POST "http://localhost:8101/aps/orders" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "accountId": 1,
    "category": "sign",
    "plannedQty": 30,
    "startDate": "2026-03-15",
    "endDate": "2026-04-15",
    "executionTime": "08:00"
  }'

# 4. 获取订单详情
curl -X GET "http://localhost:8101/aps/orders/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 5. 更新订单状态
curl -X PATCH "http://localhost:8101/aps/orders/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"status": "doing"}'

# 6. 获取枚举值
curl -X GET "http://localhost:8101/aps/orders/enums" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 7. 按客户名称搜索
curl -X GET "http://localhost:8101/aps/orders?goofishName=test" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 8. 按订单编号查询
curl -X GET "http://localhost:8101/aps/orders?orderNo=O20250308001" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 9. 关键词搜索
curl -X GET "http://localhost:8101/aps/orders?keywords=test" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 数据模型

### Order 模型字段映射

| 数据库字段 | 响应字段 | 类型 | 说明 |
|-----------|---------|------|------|
| id | id | int | 订单 ID |
| code | code | string | 订单编号 |
| version | - | int | 版本号 |
| account_id | accountId | int | 关联账号 ID（内部） |
| account.username | accountUsername | string | 账号用户名（只读） |
| account.customer.name | customerName | string | 客户名称（只读） |
| planned_qty | plannedQty | int | 计划数量 |
| plan_duration | planDuration | int | 计划持续时间（分钟） |
| completed_qty | completedQty | int | 完成数量 |
| before_value | beforeValue | int | 初始值 |
| category | category | string | 订单类别 |
| status | status | string | 订单状态 |
| business | business | string | 业务类型（paid/free） |
| organization_id | - | int | 所属组织 ID（内部） |
| organization.name | organizationName | string | 组织名称（只读） |
| price | price | decimal | 价格 |
| package_id | packageId | int | 关联套餐 ID（内部） |
| package.name | packageName | string | 套餐名称（只读） |
| created_at | createdAt | string | 创建时间（本地化） |
| updated_at | - | string | 更新时间（内部） |
| completed_at | - | string | 完成时间（内部） |
| schedule_at | scheduleAt | string | 计划时间（本地化） |
| task_id | - | string | Celery 任务 ID（内部） |

### 订单子模型

**OrderExp（经验订单）**

| 字段 | 类型 | 说明 |
|------|------|------|
| order | ForeignKey | 关联主订单 |
| before_value | int | 初始经验值 |
| plan_duration | int | 计划持续时间（分钟） |
| schedule_at | datetime | 计划执行时间 |
| planned_qty | int | 计划数量 |
| completed_qty | int | 完成数量 |

**OrderGem（宝石订单）**

| 字段 | 类型 | 说明 |
|------|------|------|
| order | ForeignKey | 关联主订单 |
| before_value | int | 初始宝石值 |
| planned_qty | int | 计划数量 |
| completed_qty | int | 完成数量 |

**OrderThreeXP（三倍经验订单）**

| 字段 | 类型 | 说明 |
|------|------|------|
| order | ForeignKey | 关联主订单 |
| planned_qty | int | 计划领取次数 |
| completed_qty | int | 已领取次数 |

**OrderSigning（签到订单）**

| 字段 | 类型 | 说明 |
|------|------|------|
| order | ForeignKey | 关联主订单 |
| start_date | date | 开始日期 |
| end_date | date | 结束日期 |
| execution_time | string | 执行时间（HH:MM） |
| planned_qty | int | 每日经验目标总量 |

> **注意**：`OrderSigning` 没有 `completed_qty` 字段，每日经验累加值写入主订单 `Order.completed_qty`。

---

## 自动执行任务

**任务名称**: `celery_execute_order_v2`
**执行频率**: 每分钟
**触发条件**: 订单状态为 `waiting/doing` 时自动执行

**各类型执行规则**:

| 类型 | 触发条件 | 执行逻辑 |
|------|---------|---------|
| EXP | 到达 schedule_at 时间 | 答题获取经验，每次获得 planned_qty/plan_duration |
| GEMS | 每分钟检查 | 领取所有可用宝石奖励 |
| THREE_XP | 每分钟检查（TTL > 120秒跳过） | 领取三倍经验加成 |
| SIGN | 日期范围内(UTC+8) + 时间匹配(UTC+8) | 循环答题累加经验至 planned_qty 目标，到达 end_date 后完成 |

> **时区注意**：SIGN 订单的 `execution_time`、`start_date`、`end_date` 均为用户提交的 UTC+8 时区值。系统内部使用 UTC 时间，Celery 执行时通过 `(timezone.now() + timedelta(hours=8))` 转换后比较。

<!-- NOTE: 此文档由 Claude Code 自动生成，保留此注释以便后续更新 -->
