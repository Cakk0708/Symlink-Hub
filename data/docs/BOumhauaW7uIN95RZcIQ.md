# APS - Order 接口文档

> 最后更新：2026-03-29
> App: `APS` | Model: `Order`
> Base URL: `/APS/orders`

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
| GET | `/APS/orders` | 获取订单列表 | ✅ |
| POST | `/APS/orders` | 创建订单 | ✅ |
| GET | `/APS/orders/enums` | 获取订单枚举 | ✅ |
| GET | `/APS/orders/<id>` | 获取订单详情 | ✅ |

---

## 接口详情

### 1. 获取订单列表

**GET** `/APS/orders`

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keywords | string | 否 | 关键词搜索（用户名/昵称/邮箱/手机/备注/客户名） |
| orderNo | string | 否 | 订单编号精确匹配 |
| status | string | 否 | 订单状态筛选：`waiting` / `doing` / `done` / `pause` / `cancel` / `error` |
| category | string | 否 | 订单类型筛选：`exp` / `gems` / `3x_xp` / `sign` |
| goofishName | string | 否 | 客户名称模糊匹配 |
| page | int | 否 | 页码，从 0 开始，默认 0（每页 10 条） |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "code": "O202503290001",
        "category": "exp",
        "status": "waiting",
        "business": "paid",
        "price": "0.00",
        "version": 2,
        "plannedQty": 0,
        "completedQty": 0,
        "accountUsername": "user01",
        "accountNickname": "昵称",
        "customerName": "客户A",
        "organizationName": "组织1",
        "typeDetail": {
          "beforeValue": 1500,
          "planDuration": 60,
          "scheduleAt": "2025-03-29 15:00:00",
          "plannedQty": 0,
          "completedQty": 0
        },
        "createdAt": "2025-03-29 15:00:00"
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

**typeDetail 字段说明**

根据 `category` 不同，`typeDetail` 返回结构不同：

| category | 字段 |
|----------|------|
| `exp` | `beforeValue`, `planDuration`, `scheduleAt`, `plannedQty`, `completedQty` |
| `gems` | `beforeValue`, `plannedQty`, `completedQty` |
| `3x_xp` | `plannedQty`, `completedQty` |
| `sign` | `startDate`, `endDate`, `executionTime`, `plannedQty`, `completedQty` |

---

### 2. 创建订单

**POST** `/APS/orders`

**请求体**

```json
{
  "accountId": 1,
  "category": "exp",
  "business": "paid",
  "price": "100.00",
  "planDuration": 60,
  "scheduleAt": "2025-03-29T15:00:00Z",
  "plannedQty": 10
}
```

**请求参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| accountId | int | ✅ | Duolingo 账户 ID |
| category | string | ✅ | 订单类型：`exp` / `gems` / `3x_xp` / `sign` |
| business | string | 否 | 业务类型：`paid`（默认）/ `free` |
| price | decimal | 否 | 价格，默认 0 |
| planDuration | int | 否 | 计划持续时间（分钟），`exp` 类型必填 |
| scheduleAt | string | 否 | 计划执行时间（ISO 8601） |
| plannedQty | int | 否 | 计划数量，默认 0 |
| startDate | string | 否 | 签到开始日期（`sign` 类型必填，格式 `YYYY-MM-DD`） |
| endDate | string | 否 | 签到结束日期（`sign` 类型必填，格式 `YYYY-MM-DD`） |
| executionTime | string | 否 | 签到执行时间（`sign` 类型必填，如 `08:00`） |

**响应示例**

```json
{
  "msg": "success"
}
```

**各类型必填字段汇总**

| category | 必填字段 |
|----------|----------|
| `exp` | `accountId`, `category`, `planDuration` |
| `gems` | `accountId`, `category` |
| `3x_xp` | `accountId`, `category` |
| `sign` | `accountId`, `category`, `startDate`, `endDate`, `executionTime` |

---

### 3. 获取订单枚举

**GET** `/APS/orders/enums`

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "choices": {
      "status": [
        { "value": "waiting", "label": "等待" },
        { "value": "doing", "label": "进行中" },
        { "value": "done", "label": "完成" },
        { "value": "pause", "label": "暂停" },
        { "value": "cancel", "label": "取消" },
        { "value": "error", "label": "错误" }
      ],
      "category": [
        { "value": "exp", "label": "经验" },
        { "value": "gems", "label": "宝石" },
        { "value": "3x_xp", "label": "三倍经验" },
        { "value": "sign", "label": "签到" }
      ],
      "business": [
        { "value": "paid", "label": "付费" },
        { "value": "free", "label": "免费" }
      ]
    }
  }
}
```

---

### 4. 获取订单详情

**GET** `/APS/orders/<id>`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 订单 ID |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "document": {
      "id": 1,
      "code": "O202503290001",
      "status": "waiting",
      "category": "exp",
      "business": "paid",
      "price": "100.00",
      "version": 2
    },
    "progressData": {
      "plannedQty": 0,
      "completedQty": 0
    },
    "typeDetail": {
      "beforeValue": 1500,
      "planDuration": 60,
      "scheduleAt": "2025-03-29 15:00:00",
      "plannedQty": 0,
      "completedQty": 0
    },
    "relations": {
      "account": {
        "id": 1,
        "nickname": "昵称",
        "username": "user01",
        "phone": "13800138000",
        "email": "user@example.com",
        "remark": "备注"
      },
      "customer": {
        "id": 1,
        "name": "客户A",
        "code": "C202503290001"
      },
      "organization": {
        "id": 1,
        "code": "ORG001",
        "name": "组织1"
      }
    },
    "recentLogs": [
      {
        "id": 123,
        "code": "L202503290001",
        "orderId": 1,
        "orderCode": "O202503290001",
        "category": "exp",
        "categoryLabel": "经验",
        "status": "success",
        "statusLabel": "成功",
        "resultValue": 150,
        "errorMessage": null,
        "executionDuration": 45,
        "extraData": null,
        "executedAt": "2025-03-29T15:30:00Z",
        "createdAt": "2025-03-29T15:30:00Z"
      }
    ],
    "others": {
      "createdAt": "2025-03-29 15:00:00",
      "updatedAt": "2025-03-29 15:30:00",
      "completedAt": null
    }
  }
}
```

**响应字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| document | object | 订单文档信息（编号、状态、类型、业务、价格、版本） |
| progressData | object | 进度数据（计划数量、完成数量） |
| typeDetail | object | 类型特定数据，结构随 `category` 变化（见下方） |
| relations | object | 关联信息（账户、客户、组织） |
| recentLogs | array | 该订单最近 10 条执行日志，按创建时间倒序 |
| others | object | 时间信息（创建时间、更新时间、完成时间） |

**recentLogs 日志字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 日志 ID |
| code | string | 日志编号（如 `L202503290001`） |
| orderId | int | 关联订单 ID |
| orderCode | string | 关联订单编号 |
| category | string | 订单类型（`exp` / `gems` / `3x_xp` / `sign`） |
| categoryLabel | string | 订单类型中文标签 |
| status | string | 执行状态（`success` / `failed`） |
| statusLabel | string | 执行状态中文标签 |
| resultValue | int | 结果值 |
| errorMessage | string/null | 错误信息 |
| executionDuration | int | 执行耗时（秒） |
| extraData | object/null | 额外数据 |
| executedAt | string | 执行时间 |
| createdAt | string | 创建时间 |

**typeDetail 字段说明（同列表接口）**

| category | 字段 |
|----------|------|
| `exp` | `beforeValue`, `planDuration`, `scheduleAt`, `plannedQty`, `completedQty` |
| `gems` | `beforeValue`, `plannedQty`, `completedQty` |
| `3x_xp` | `plannedQty`, `completedQty` |
| `sign` | `startDate`, `endDate`, `executionTime`, `plannedQty` |

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
# 1. 获取订单列表
curl -X GET "http://localhost:8101/APS/orders?page=0&category=exp" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 2. 创建订单
curl -X POST "http://localhost:8101/APS/orders" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"accountId":1,"category":"exp","planDuration":60}'

# 3. 获取订单枚举
curl -X GET "http://localhost:8101/APS/orders/enums" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 4. 获取订单详情
curl -X GET "http://localhost:8101/APS/orders/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
