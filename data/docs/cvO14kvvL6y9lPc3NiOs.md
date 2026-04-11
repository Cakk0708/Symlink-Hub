# SM - Dashboard 接口文档

> 最后更新：2026-03-21
> App: `SM` | Model: `Dashboard`
> Base URL: `/api/sm`

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
| GET | `/dashboard` | 获取仪表盘数据 | ✅ |

---

## 接口详情

### 获取仪表盘数据

**接口地址：** `GET /api/sm/dashboard`

**描述：** 获取仪表盘统计数据，包括账户数量、订单统计等

**请求头：**
```
Authorization: Bearer YOUR_JWT_TOKEN
```

**请求参数：** 无

**响应示例：**
```json
{
  "msg": "success",
  "data": {
    "account": 10,
    "order": {
      "yestoday": {
        "count": 25,
        "amount": 250.00
      },
      "today": {
        "count": 30,
        "amount": 300.00,
        "hour": [
          {"time": "08:00", "count": 5},
          {"time": "09:00", "count": 8},
          {"time": "10:00", "count": 12},
          {"time": "14:00", "count": 5}
        ]
      },
      "category": [
        {"name": "经验值", "value": 15},
        {"name": "宝石", "value": 10},
        {"name": "3倍经验", "value": 3},
        {"name": "签到", "value": 2}
      ]
    },
    "expiring": [
      {
        "orderId": 123,
        "orderCode": "O20250308001",
        "plannedQty": 1000,
        "completedQty": 850,
        "remainingQty": 150,
        "customerName": "张三",
        "accountName": "zhangsan@example.com"
      }
    ]
  }
}
```

**响应字段说明：**

| 字段 | 类型 | 说明 |
|------|------|------|
| account | Integer | 启用状态的账户总数 |
| order | Object | 订单统计数据 |
| order.yestoday | Object | 昨日订单统计 |
| order.yestoday.count | Integer | 昨日订单数量 |
| order.yestoday.amount | Decimal | 昨日订单总金额 |
| order.today | Object | 今日订单统计 |
| order.today.count | Integer | 今日订单数量 |
| order.today.amount | Decimal | 今日订单总金额 |
| order.today.hour | Array | 今日订单按小时分布 |
| order.today.hour[].time | String | 时间点（格式：HH:00） |
| order.today.hour[].count | Integer | 该时间点订单数量 |
| order.category | Array | 订单按类别分布 |
| order.category[].name | String | 订单类别名称 |
| order.category[].value | Integer | 该类别订单数量 |
| expiring | Array | 即将到期的三倍经验订单列表 |
| expiring[].orderId | Integer | 订单 ID |
| expiring[].orderCode | String | 订单编码 |
| expiring[].plannedQty | Integer | 计划数量 |
| expiring[].completedQty | Integer | 已完成数量 |
| expiring[].remainingQty | Integer | 剩余数量 |
| expiring[].customerName | String | 客户名称 |
| expiring[].accountName | String | 账户名称（用户名或邮箱） |

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
# 获取仪表盘数据
curl -X GET "http://localhost:8101/api/sm/dashboard" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```
