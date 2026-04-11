# APS - OrderExecutionLog 接口文档

> 最后更新：2026-03-29
> App: `APS` | Model: `OrderExecutionLog`
> Base URL: `/APS/order-logs`

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
| GET | `/APS/order-logs` | 获取订单执行日志列表 | ✅ |
| GET | `/APS/order-logs/<log_id>` | 获取日志详情 | ✅ |
| GET | `/APS/order-logs/stats` | 获取日志统计 | ✅ |

---

## 接口详情

### 1. 获取订单执行日志列表

**GET** `/APS/order-logs`

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| orderId | int | 否 | 按订单 ID 筛选 |
| category | string | 否 | 按订单类型筛选：`exp` / `gems` / `3x_xp` / `sign` |
| status | string | 否 | 按执行状态筛选：`success` / `failed` |
| dateStart | string | 否 | 起始日期（格式 `YYYY-MM-DD`） |
| dateEnd | string | 否 | 结束日期（格式 `YYYY-MM-DD`） |
| page | int | 否 | 页码，从 1 开始，默认 1 |
| pageSize | int | 否 | 每页数量，默认 20 |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "list": [
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
    "total": 200,
    "page": 1,
    "pageSize": 20
  }
}
```

**响应字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 日志 ID |
| code | string | 日志编号（如 `L202503290001`） |
| orderId | int | 关联订单 ID |
| orderCode | string | 关联订单编号 |
| category | string | 订单类型 |
| categoryLabel | string | 订单类型中文标签 |
| status | string | 执行状态 |
| statusLabel | string | 执行状态中文标签 |
| resultValue | int | 结果值 |
| errorMessage | string/null | 错误信息（失败时有值） |
| executionDuration | int | 执行耗时（秒） |
| extraData | object/null | 额外数据 |
| executedAt | string | 执行时间 |
| createdAt | string | 创建时间 |

---

### 2. 获取订单执行日志详情

**GET** `/APS/order-logs/<log_id>`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| log_id | int | 日志 ID |

**响应示例**

```json
{
  "msg": "success",
  "data": {
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
}
```

---

### 3. 获取订单执行日志统计

**GET** `/APS/order-logs/stats`

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| dateStart | string | 否 | 起始日期（格式 `YYYY-MM-DD`） |
| dateEnd | string | 否 | 结束日期（格式 `YYYY-MM-DD`） |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "totalCount": 200,
    "successCount": 180,
    "failedCount": 20,
    "categoryStats": [
      {
        "category": "exp",
        "count": 120,
        "successCount": 110,
        "failedCount": 10
      },
      {
        "category": "gems",
        "count": 50,
        "successCount": 45,
        "failedCount": 5
      },
      {
        "category": "3x_xp",
        "count": 20,
        "successCount": 18,
        "failedCount": 2
      },
      {
        "category": "sign",
        "count": 10,
        "successCount": 7,
        "failedCount": 3
      }
    ],
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
    ]
  }
}
```

**响应字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| totalCount | int | 日志总数 |
| successCount | int | 成功数量 |
| failedCount | int | 失败数量 |
| categoryStats | array | 按订单类型分组的统计数据 |
| categoryStats[].category | string | 订单类型 |
| categoryStats[].count | int | 该类型总数 |
| categoryStats[].successCount | int | 该类型成功数 |
| categoryStats[].failedCount | int | 该类型失败数 |
| recentLogs | array | 最近 10 条执行日志 |

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
| 400 | 请求参数错误 / 用户未关联组织 |
| 401 | 未认证或 Token 已过期 |
| 404 | 日志不存在 |
| 500 | 服务器内部错误 |

---

## 完整 cURL 示例

```bash
# 1. 获取日志列表
curl -X GET "http://localhost:8101/APS/order-logs?orderId=1&page=1&pageSize=20" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 2. 获取日志详情
curl -X GET "http://localhost:8101/APS/order-logs/123" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 3. 获取日志统计
curl -X GET "http://localhost:8101/APS/order-logs/stats?dateStart=2025-03-01&dateEnd=2025-03-31" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
