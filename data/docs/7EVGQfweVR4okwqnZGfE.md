# Order 模块文档

> 最后更新：2026-04-04
> 模块：`order` | 业务域：`APS`
> API 前缀：`/APS/orders`

---

## 模块概述

订单模块负责订单列表展示、筛选、详情查看以及订单状态管理。

---

## 文件结构

```
src/
├── api/order.js                 # 接口请求定义
├── pages/Order/
    ├── List.vue                 # 订单列表页
    └── Detail.vue               # 订单详情页
```

---

## 接口函数

### 获取订单列表

```javascript
getOrders(params)
```

**参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | number | 否 | 页码（从0开始） |
| page_size | number | 否 | 每页数量 |
| keywords | string | 否 | 搜索关键词（订单号、客户名称、账户名称、手机号） |
| status | string | 否 | 订单状态筛选 |
| category | string | 否 | 订单类型筛选 |

**响应：**
```javascript
{
  items: Array,        // 订单列表
  pagination: {        // 分页信息
    total: number
  }
}
```

---

### 获取订单详情

```javascript
getOrder(id)
```

**参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | number | 是 | 订单ID |

---

### 创建订单

```javascript
createOrder(data)
```

**请求体：**
```javascript
{
  accountId: number,
  category: string,           // 'exp' | 'gems' | '3x_xp' | 'sign'
  business: string,           // 'paid' | 'free'
  price: number,
  plannedQty?: number,        // 计划数量（SIGN类型必填）
  scheduleAt?: string,        // 执行时间（非SIGN类型）
  planDuration?: number,      // 计划周期（EXP类型）
  startDate?: string,         // 开始日期（SIGN类型）
  endDate?: string,           // 结束日期（SIGN类型）
  executionTime?: string      // 执行时间（SIGN类型）
}
```

---

### 更新订单状态

```javascript
updateOrderStatus(id, status)
```

**参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | number | 是 | 订单ID |
| status | string | 是 | 目标状态 |

---

### 删除订单

```javascript
deleteOrder(id)
```

**参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | number | 是 | 订单ID |

**说明：** 仅已取消状态的订单可以删除

---

### 获取订单枚举

```javascript
getOrderEnums()
```

**响应：**
```javascript
{
  choices: {
    status: Array,      // 状态枚举
    category: Array     // 类型枚举
  }
}
```

---

## 页面功能

### 订单列表页 (List.vue)

**核心功能：**
- 订单列表展示（支持下拉刷新、无限滚动）
- 状态和类型筛选（**支持筛选状态记忆**）
- 订单号搜索
- 点击卡片查看详情

**筛选状态记忆：**
- 用户选择的筛选条件会保存到 localStorage
- 下次进入页面自动恢复上次的筛选状态
- 存储键：`order_filters`

**筛选字段：**
```javascript
{
  status: string,    // 订单状态
  category: string   // 订单类型
}
```

---

### 订单详情页 (Detail.vue)

**核心功能：**
- 订单详情展示
- 订单操作（根据状态显示）

**菜单操作：**
| 订单状态 | 可用操作 |
|---------|---------|
| waiting（等待中） | 取消订单 |
| doing（进行中） | 取消订单 |
| cancel（已取消） | 重新开始、删除订单 |
| 其他状态 | 无操作 |

---

## 类型定义

```javascript
// 订单数据类型
interface Order {
  id: number
  code: string
  category: string           // 'exp' | 'gems' | '3x_xp' | 'sign'
  status: string             // 'waiting' | 'doing' | 'done' | 'pause' | 'cancel' | 'error'
  business: string           // 'paid' | 'free'
  price: number
  plannedQty: number
  completedQty: number
  beforeValue: number
  scheduleAt: string
  customerName: string
  accountNickname: string
  accountUsername: string
  createdAt: string
  typeDetail?: object
}

// 列表查询参数
interface OrderListParams {
  page?: number
  page_size?: number
  keywords?: string
  status?: string
  category?: string
}
```
