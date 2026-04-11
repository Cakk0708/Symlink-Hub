# orders 模块

## 模块入口
src/modules/orders/index.ts

---

## 文件地图

| 文件 | 职责 | 关键导出 |
|------|------|---------|
| api.ts | 所有订单接口 | fetchOrders, cancelOrder |
| store.ts | 订单筛选条件状态 | useOrderStore |
| types.ts | 类型定义 | Order, OrderStatus |
| hooks/useOrders.ts | 列表查询（React Query） | useOrders |
| hooks/useOrderDetail.ts | 详情查询 | useOrderDetail |
| components/OrderList.tsx | 订单列表展示 | — |
| components/OrderCard.tsx | 单条订单卡片 | — |
| components/OrderFilter.tsx | 筛选栏 | — |
| components/StatusBadge.tsx | 状态标签 | — |

---

## 数据流

\```
用户操作 OrderFilter
    → useOrderStore 更新筛选条件
    → useOrders(filters) 触发 React Query
    → api.fetchOrders(filters)
    → 渲染 OrderList → OrderCard
\```

---

## 块树说明
\```
* 导航栏
   * logo
   * 路由列表
* 内容栏
   * navbar
   * 动作条
      * 新增
      * 删除
      * 业务操作
         * 启用
         * 禁用
   * 数据表
      * 筛选栏
         * 编码搜索
         * 名称搜索
      * 数据列表
         * ID
         * 名称
         * 编码
         * 禁用状态
   * 分页器
\```



## 状态说明

### useOrderStore（Zustand）
\```typescript
// 只存 UI 状态和筛选条件，不存服务端数据
{
  filters: { status, dateRange, keyword },
  selectedOrderId: string | null
}
\```

### React Query 缓存键
\```typescript
['orders', filters]          // 列表
['orders', orderId]          // 详情
\```

---

## 对外暴露（index.ts 导出）
\```typescript
export { OrderList } from './components/OrderList'
export { useOrders } from './hooks/useOrders'
export type { Order, OrderStatus } from './types'
\```

## 依赖
- modules/auth → 获取当前用户 ID（useCurrentUser）
- shared/ui → Table, Badge, DatePicker

## 禁止事项
- 禁止在 OrderList.tsx 里直接调用 fetch
- 禁止其他模块引用 components/OrderCard（非导出项）
- 禁止在 store 里存服务端返回的订单数据（交给 React Query）