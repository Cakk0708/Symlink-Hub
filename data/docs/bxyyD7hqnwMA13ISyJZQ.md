# APS - Order Execution Log 接口文档

> 最后更新：2026-03-25
> App: `APS` | Model: `OrderExecutionLog`
> Base URL: `/aps`

---

## 认证说明

所有接口均需在请求头中携带 JWT Token：

```
Authorization: Bearer YOUR_JWT_TOKEN
```

**权限说明**：所有日志查询均会自动过滤当前用户所属组织的数据。

---

## 模块说明

订单执行日志模块用于记录订单定时执行的结果，只在订单执行成功或失败时创建日志记录。

**日志记录时机**：

| 场景 | 是否记录日志 |
|------|------------|
| 未到计划执行时间 | ❌ 不记录 |
| 未到执行时间 | ❌ 不记录 |
| 订单已完成 | ❌ 不记录 |
| 3倍经验效果持续中 | ❌ 不记录 |
| 今天已打卡 | ❌ 不记录 |
| 执行成功 | ✅ 记录成功 |
| 执行失败 | ✅ 记录失败 |

---

## 接口列表

| 方法 | 路径 | 描述 | 需要认证 |
|------|------|------|----------|
| GET | `/order-logs` | 获取订单执行日志列表 | ✅ |
| GET | `/order-logs/order/<order_id>` | 获取指定订单的执行日志 | ✅ |
| GET | `/order-logs/<id>` | 获取订单执行日志详情 | ✅ |
| GET | `/order-logs/stats` | 获取订单执行日志统计 | ✅ |

---

## 接口详情

### 1. 获取订单执行日志列表

**GET** `/aps/order-logs`

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，从 1 开始，默认 1 |
| pageSize | int | 否 | 每页数量，默认 20 |
| orderId | int | 否 | 订单 ID（精确匹配） |
| category | string | 否 | 订单类别（exp/gems/3x_xp/sign） |
| status | string | 否 | 执行状态（success/failed） |
| dateStart | string | 否 | 开始日期（YYYY-MM-DD） |
| dateEnd | string | 否 | 结束日期（YYYY-MM-DD） |

**执行状态枚举 (status)**

| 值 | 说明 |
|----|------|
| success | 成功 |
| failed | 失败 |

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
    "list": [
      {
        "id": 1,
        "code": "L20250325001",
        "orderId": 10,
        "orderCode": "O20250323001",
        "category": "exp",
        "categoryLabel": "经验",
        "status": "success",
        "statusLabel": "成功",
        "resultValue": 50,
        "errorMessage": null,
        "executionDuration": 30,
        "extraData": {
          "targetQuantity": 50
        },
        "executedAt": "2026-03-25 10:30:00",
        "createdAt": "2026-03-25 10:30:30"
      }
    ],
    "total": 100,
    "page": 1,
    "pageSize": 20
  }
}
```

**响应字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 日志 ID |
| code | string | 日志编号（自动生成，前缀 L） |
| orderId | int | 关联订单 ID |
| orderCode | string | 关联订单编号 |
| category | string | 订单类别 |
| categoryLabel | string | 订单类别显示名称 |
| status | string | 执行状态 |
| statusLabel | string | 执行状态显示名称 |
| resultValue | int | 结果值（获得的经验/宝石数量等） |
| errorMessage | string | 错误信息（失败时） |
| executionDuration | int | 执行耗时（秒） |
| extraData | object | 额外数据（JSON 格式） |
| executedAt | string | 执行时间 |
| createdAt | string | 创建时间 |

---

### 2. 获取指定订单的执行日志

**GET** `/aps/order-logs/order/<order_id>`

获取指定订单的所有执行日志，按创建时间倒序排列。

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| order_id | int | 订单 ID |

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，从 1 开始，默认 1 |
| pageSize | int | 否 | 每页数量，默认 20 |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "list": [
      {
        "id": 15,
        "code": "L20250326001",
        "orderId": 10,
        "orderCode": "O20250323001",
        "category": "exp",
        "categoryLabel": "经验",
        "status": "success",
        "statusLabel": "成功",
        "resultValue": 50,
        "errorMessage": null,
        "executionDuration": 30,
        "extraData": {
          "targetQuantity": 50
        },
        "executedAt": "2026-03-26 08:00:00",
        "createdAt": "2026-03-26 08:00:30"
      }
    ],
    "total": 25,
    "page": 1,
    "pageSize": 20
  }
}
```

**错误示例**

```json
{
  "msg": "用户未关联组织",
  "data": []
}
```

---

### 3. 获取订单执行日志详情

**GET** `/aps/order-logs/<id>`

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 日志 ID |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "code": "L20250325001",
    "orderId": 10,
    "orderCode": "O20250323001",
    "category": "exp",
    "categoryLabel": "经验",
    "status": "success",
    "statusLabel": "成功",
    "resultValue": 50,
    "errorMessage": null,
    "executionDuration": 30,
    "extraData": {
      "targetQuantity": 50
    },
    "executedAt": "2026-03-25 10:30:00",
    "createdAt": "2026-03-25 10:30:30"
  }
}
```

**错误示例**

```json
{
  "msg": "日志不存在",
  "data": null
}
```

---

### 4. 获取订单执行日志统计

**GET** `/aps/order-logs/stats`

获取订单执行日志的统计数据，包括成功/失败数量、按类型统计等。

**Query 参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| dateStart | string | 否 | 开始日期（YYYY-MM-DD） |
| dateEnd | string | 否 | 结束日期（YYYY-MM-DD） |

**响应示例**

```json
{
  "msg": "success",
  "data": {
    "totalCount": 500,
    "successCount": 450,
    "failedCount": 50,
    "categoryStats": [
      {
        "category": "exp",
        "count": 200,
        "successCount": 180,
        "failedCount": 20
      },
      {
        "category": "gems",
        "count": 150,
        "successCount": 140,
        "failedCount": 10
      },
      {
        "category": "3x_xp",
        "count": 100,
        "successCount": 95,
        "failedCount": 5
      },
      {
        "category": "sign",
        "count": 50,
        "successCount": 35,
        "failedCount": 15
      }
    ],
    "recentLogs": [
      {
        "id": 500,
        "code": "L20250325050",
        "orderId": 25,
        "orderCode": "O20250325005",
        "category": "sign",
        "categoryLabel": "签到",
        "status": "success",
        "statusLabel": "成功",
        "resultValue": 1,
        "errorMessage": null,
        "executionDuration": 5,
        "extraData": {
          "expGained": 15,
          "streak": 30
        },
        "executedAt": "2026-03-25 08:00:00",
        "createdAt": "2026-03-25 08:00:05"
      }
    ]
  }
}
```

**响应字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| totalCount | int | 总日志数量 |
| successCount | int | 成功数量 |
| failedCount | int | 失败数量 |
| categoryStats | array | 按订单类型统计 |
| categoryStats[].category | string | 订单类别 |
| categoryStats[].count | int | 该类型总数量 |
| categoryStats[].successCount | int | 该类型成功数量 |
| categoryStats[].failedCount | int | 该类型失败数量 |
| recentLogs | array | 最近 10 条执行记录 |

---

## 数据模型

### OrderExecutionLog 模型

**模型字段映射**

| 数据库字段 | 响应字段 | 类型 | 说明 |
|-----------|---------|------|------|
| id | id | int | 日志 ID |
| code | code | string | 日志编号（前缀 L + 日期 + 序号） |
| order_id | orderId | int | 关联订单 ID（内部） |
| order.code | orderCode | string | 关联订单编号（只读） |
| category | category | string | 订单类别 |
| status | status | string | 执行状态 |
| result_value | resultValue | int | 结果值 |
| error_message | errorMessage | string | 错误信息 |
| execution_duration | executionDuration | int | 执行耗时（秒） |
| extra_data | extraData | object | 额外数据（JSON） |
| organization_id | - | int | 所属组织 ID（内部） |
| executed_at | executedAt | string | 执行时间 |
| created_at | createdAt | string | 创建时间 |

### extraData 字段说明

不同类型订单的 `extraData` 包含不同的额外信息：

**EXP 订单**

```json
{
  "targetQuantity": 50
}
```

**GEMS 订单**

```json
{
  "previousGem": 1000,
  "currentGem": 1050,
  "rewardCount": 5
}
```

**THREE_XP 订单**

```json
{
  "remainingEffectDurationInSeconds": 3600,
  "startTime": "2026-03-25T10:00:00Z",
  "endTime": "2026-03-25T11:00:00Z"
}
```

**SIGN 订单**

```json
{
  "expGained": 15,
  "streak": 30
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
| 400 | 用户未关联组织 |
| 401 | 未认证或 Token 已过期 |
| 403 | 无权限访问该组织数据 |
| 404 | 日志不存在 |
| 500 | 服务器内部错误 |

---

## 完整 cURL 示例

```bash
# 1. 获取订单执行日志列表
curl -X GET "http://localhost:8101/aps/order-logs?page=1&pageSize=20" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 2. 按订单 ID 筛选
curl -X GET "http://localhost:8101/aps/order-logs?orderId=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 3. 按状态筛选
curl -X GET "http://localhost:8101/aps/order-logs?status=failed" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 4. 按日期范围筛选
curl -X GET "http://localhost:8101/aps/order-logs?dateStart=2026-03-01&dateEnd=2026-03-31" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 5. 按订单类型筛选
curl -X GET "http://localhost:8101/aps/order-logs?category=exp" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 6. 获取日志详情
curl -X GET "http://localhost:8101/aps/order-logs/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 7. 获取指定订单的执行日志
curl -X GET "http://localhost:8101/aps/order-logs/order/10?page=1&pageSize=20" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 8. 获取统计数据
curl -X GET "http://localhost:8101/aps/order-logs/stats" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 9. 获取指定日期范围的统计
curl -X GET "http://localhost:8101/aps/order-logs/stats?dateStart=2026-03-01&dateEnd=2026-03-31" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 使用场景

### 1. 监控订单执行情况

通过统计接口获取整体执行成功率：

```bash
GET /aps/order-logs/stats
```

响应中的 `successCount` 和 `failedCount` 可用于计算成功率。

### 2. 排查失败订单

按失败状态筛选日志：

```bash
GET /aps/order-logs?status=failed
```

查看 `errorMessage` 字段了解失败原因。

### 3. 追踪特定订单执行历史

按订单 ID 查询该订单所有日志：

```bash
GET /aps/order-logs/order/10
```

查看该订单的所有执行记录，支持分页。

### 4. 分析执行性能

查看 `executionDuration` 字段分析各类型订单的执行耗时。

---

<!-- NOTE: 此文档由 Claude Code 自动生成，保留此注释以便后续更新 -->