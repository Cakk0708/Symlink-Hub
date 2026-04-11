# Dashboard 模块 - 仪表盘

## 概述

Dashboard (仪表盘) 模块展示系统统计数据和快捷操作，是用户登录后的首页。

## 前端页面

### 仪表盘
**路径**: `/dashboard`
**布局**: DefaultLayout
**需要认证**: 是

**功能**:
- 今日订单统计 (数量、金额)
- 账户总数
- 订单分类分布 (饼图)
- 订单时间趋势 (折线图)
- 快捷操作按钮

**API**:
```javascript
GET /SM/dashboard

响应:
{
  msg: "success",
  data: {
    account: {
      total: 32
    },
    order: {
      today: {
        count: 15,
        amount: 150.00,
        hour: [
          { time: "10:00", count: 5 },
          { time: "11:00", count: 3 }
        ]
      },
      yestoday: {
        count: 12,
        amount: 120.00
      },
      category: [
        { name: "经验", value: 10 },
        { name: "宝石", value: 3 },
        { name: "三倍经验", value: 2 }
      ]
    }
  }
}
```

**组件**: `pages/Dashboard/index.vue`

**图表**: 使用 Vant Chart 或 ECharts 进行可视化

---

## 路由配置

```javascript
{
  path: '/dashboard',
  name: 'Dashboard',
  component: () => import('@/pages/Dashboard/index.vue'),
  meta: { requiresAuth: true, title: '仪表盘' }
}
```

---

## 数据结构

### 仪表盘数据类型

```typescript
interface DashboardData {
  account: {
    total: number          // 账户总数
  }
  order: {
    today: {
      count: number        // 今日订单数量
      amount: number       // 今日订单金额
      hour: Array<{        // 今日每小时订单分布
        time: string       // 时间点 (HH:mm)
        count: number      // 订单数量
      }>
    }
    yestoday: {
      count: number        // 昨日订单数量
      amount: number       // 昨日订单金额
    }
    category: Array<{      // 订单分类分布
      name: string         // 分类名称
      value: number        // 数量
    }>
  }
}
```

---

## 说明

- 仪表盘数据自动按用户组织过滤
- 图表数据格式适配 Vant Chart 或 ECharts
- 时区使用用户本地时区
