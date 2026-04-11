# APS Order 模块文档

> 最后更新：2026-04-04
> 模块：`aps-order` | 业务域：`APS`
> API 前缀：`/APS/orders`

---

## 模块概述

PC端订单管理模块，提供订单列表查询、创建、详情查看及状态管理功能。

---

## 文件结构

```
src/
├── utils/request.js            # 请求工具封装
└── views/APS/
    └── order/
        └── index.vue           # 订单管理页（列表+新增+详情）
```

---

## 接口函数

### 获取订单列表

```javascript
request.get('/APS/orders', { params })
```

**参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | number | 是 | 页码（从0开始） |
| order_no | string | 否 | 订单编号 |
| customer | string | 否 | 客户ID |
| status | string | 否 | 订单状态 |
| category | string | 否 | 订单类型 |

---

### 创建订单

```javascript
request.post('/APS/orders', data)
```

**请求体：**
```javascript
{
  accountId: number,
  category: string,           // 'EXP' | 'GEMS' | '3x_xp' | 'sign'
  business: string,           // 'paid' | 'free'
  price: number,
  packageId?: number,         // 套餐ID（套餐模式）
  plannedQty: number,         // 计划数量（所有类型必填，必须>0）
  scheduleAt?: string,        // 执行时间（非SIGN类型）
  planDuration?: number,      // 计划周期分钟（EXP类型）
  startDate?: string,         // 开始日期（SIGN类型）
  endDate?: string,           // 结束日期（SIGN类型）
  executionTime?: string      // 执行时间（SIGN类型）
}
```

**SIGN类型注意事项：**
- `plannedQty` 字段**必填且必须大于0**
- 配合 `startDate`、`endDate`、`executionTime` 一起使用

---

### 获取订单详情

```javascript
request.get(`/APS/orders/${id}`)
```

**响应结构：**
```javascript
{
  document: { ... },          // 订单基本信息
  typeDetail: { ... },        // 类型特定信息
  progressData: { ... },      // 进度数据
  relations: { ... },         // 关联信息
  others: { ... }             // 其他信息
}
```

---

### 更新订单状态

```javascript
request.patch(`/APS/orders/${id}`, { status })
```

**状态值：**
- `waiting` - 等待中
- `doing` - 进行中
- `done` - 已完成
- `pause` - 已暂停
- `cancel` - 已取消
- `error` - 错误

---

### 删除订单

```javascript
request.delete(`/APS/orders/${id}`)
```

**说明：** 仅已取消状态的订单可以删除

---

### 获取枚举数据

```javascript
request.get('/APS/orders/enums')
```

---

## 表单验证规则

```javascript
{
  customer_id: [{ required: true, message: '请选择客户' }],
  account_id: [{ required: true, message: '请选择账户' }],
  category: [{ required: true, message: '请选择订单类型' }],
  business: [{ required: true, message: '请选择业务类型' }],
  planned: [
    { required: true, message: '请输入计划数量' },
    { validator: (rule, value, callback) => {
        if (!value || value <= 0) {
          callback(new Error('计划数量必须大于0'))
        }
      }
    }
  ]
}
```

---

## 类型定义

```javascript
// 订单数据
interface Order {
  id: number
  code: string
  category: string
  status: string
  business: string
  price: number
  plannedQty: number
  completedQty: number
  beforeValue: number
  scheduleAt: string
  customerName: string
  accountNickname: string
  typeDetail?: object
  version?: string
}

// 新增订单表单
interface OrderForm {
  order_mode: 'custom' | 'package'
  package_category: string
  package_id: number | null
  category: string
  customer_id: number | null
  account_id: number | null
  planned: number
  plan_duration: number
  schedule_at: string | null
  business: string
  price: number
  start_date: string | null
  end_date: string | null
  sign_time: string | null
}
```
