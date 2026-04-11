# APS 模块 - 异步处理系统

## 概述

APS (Async Processing System，异步处理系统) 模块处理自动化任务的订单管理。订单由后端 Celery 工作者异步执行。

## 前端页面

### 订单列表
**路径**: `/order`
**布局**: DefaultLayout
**需要认证**: 是

**功能**:
- 分页订单列表
- 多筛选器支持:
  - 订单状态 (waiting/doing/done/pause/cancel/error)
  - 订单分类 (exp/gems/3x_xp/sign)
  - 闲鱼/客户名称 (搜索)
- 订单号搜索
- 下拉刷新
- 无限滚动
- 状态徽章颜色

**API**:
```javascript
GET /APS/orders?page=0&orderNo=123&status=waiting&category=exp&goofishName=xxx

响应:
{
  msg: "success",
  data: {
    items: [
      {
        id: 12345,
        category: "exp",
        categoryDisplay: "经验",
        plannedQty: 100,
        beforeValue: 1150,
        completedQty: 0,
        scheduleAt: "2026-03-15T14:00:00Z",
        planDuration: 60,
        createdAt: "2026-03-15T10:00:00Z",
        accountUsername: "usera",
        status: "waiting",
        statusDisplay: "等待中",
        organizationName: "示例组织"
      }
    ],
    pagination: {
      page: 0,
      pageSize: 10,
      total: 50
    }
  }
}
```

**组件**: `pages/Order/List.vue`

---

### 创建订单
**路径**: `/order/create`
**布局**: DefaultLayout
**需要认证**: 是

**功能**:
- 选择账户 (弹窗/下拉)
- 禁用账户过滤: 加载账户列表时自动过滤 `disableFlag: true` 的账户，禁用账户不可选
- 选择订单类型 (单选按钮组)
- 设置计划数量
- 设置持续时间 (分钟)
- 计划执行时间 (立即或日期时间选择器)
- 表单验证

**API**:
```javascript
POST /APS/orders
{
  accountId: 1,
  plannedQty: 100,
  planDuration: 60,
  category: "exp",
  scheduleAt: "2026-03-15T14:00:00Z"  // 可选
}

响应:
{
  msg: "success",
  data: {
    id: 12345,
    orderNo: "#12345"
  }
}
```

**组件**: `pages/Order/Create.vue`

**表单验证**:
- account: 必填
- category: 必填
- plannedQty: 数字，>= 0
- planDuration: 数字，> 0
- scheduleAt: 可选

---

### 订单详情
**路径**: `/order/:id`
**布局**: DefaultLayout
**需要认证**: 是

**功能**:
- 显示订单信息
- 进度条 (已完成 / 计划)
- 状态徽章显示
- 基于状态的操作按钮:
  - waiting → 开始
  - doing → 暂停
  - pause → 继续
  - waiting/doing → 取消
  - doing → 标记完成
- 实时进度更新 (手动刷新)

**API**:
```javascript
GET /APS/orders/:id

响应:
{
  msg: "success",
  data: {
    id: 12345,
    category: "exp",
    categoryDisplay: "经验",
    status: "doing",
    statusDisplay: "进行中",
    plannedQty: 100,
    beforeValue: 1150,
    completedQty: 45,
    scheduleAt: "2026-03-15T14:00:00Z",
    planDuration: 60,
    createdAt: "2026-03-15T10:00:00Z",
    completedAt: null,
    accountUsername: "usera",
    organizationName: "示例组织"
  }
}

PATCH /APS/orders/:id
{
  status: "doing"  // 新状态
}
```

**组件**: `pages/Order/Detail.vue`

---

## 订单状态机

```
┌─────────┐
│ waiting │ ──▶ 开始 ──▶ doing
└────┬────┘                   │
     │                        │
     │ 取消                   │ 暂停 / 完成
     ▼                        ▼
   cancel ◀─────────────── pause / done
     ▲                        │
     │                        │ 错误
     └────────────────────────┘
           error
```

### 状态转换

| 当前状态 | 允许操作 | 下一状态 |
|---------|---------|---------|
| waiting | 开始 | doing |
| waiting | 取消 | cancel |
| doing | 暂停 | pause |
| doing | 取消 | cancel |
| doing | 完成 | done |
| pause | 继续 | doing |
| pause | 取消 | cancel |
| 任意 | 错误 | error |

---

## 订单分类

| 分类 | 值 | 描述 |
|------|-----|------|
| 经验 | exp | 自动答题获取经验 |
| 宝石 | gems | 自动领取宝石奖励 |
| 三倍经验 | 3x_xp | 自动激活三倍经验加速 |
| 签到 | sign | 自动每日签到 |

---

## 状态管理

### APS Store

```javascript
import { defineStore } from 'pinia'

export const useAPSStore = defineStore('aps', {
  state: () => ({
    orders: [],
    currentOrder: null,
    filters: {
      status: '',
      category: '',
      goofishName: '',
      orderNo: ''
    }
  }),

  getters: {
    filteredOrders: (state) => {
      return state.orders.filter(order => {
        // 应用筛选器
        if (state.filters.status && order.status !== state.filters.status) return false
        if (state.filters.category && order.category !== state.filters.category) return false
        return true
      })
    },

    orderProgress: (state) => (orderId) => {
      const order = state.orders.find(o => o.id === orderId)
      if (!order) return 0
      return Math.floor((order.completedQty / order.plannedQty) * 100)
    }
  },

  actions: {
    async fetchOrders(params) {
      const { data } = await request.get('/APS/orders', { params })
      this.orders = data.data.items
    },

    async fetchOrder(id) {
      const { data } = await request.get(`/APS/orders/${id}`)
      this.currentOrder = data.data
    },

    async createOrder(orderData) {
      const { data } = await request.post('/APS/orders', orderData)
      return data.data
    },

    async updateOrderStatus(id, status) {
      await request.patch(`/APS/orders/${id}`, { status })
      // 更新本地状态
      const order = this.orders.find(o => o.id === id)
      if (order) order.status = status
    },

    setFilters(filters) {
      this.filters = { ...this.filters, ...filters }
    }
  }
})
```

---

## 路由配置

```javascript
{
  path: 'order',
  name: 'OrderList',
  component: () => import('@/pages/Order/List.vue'),
  meta: { title: '订单管理' }
},
{
  path: 'order/create',
  name: 'OrderCreate',
  component: () => import('@/pages/Order/Create.vue'),
  meta: { title: '创建订单' }
},
{
  path: 'order/:id',
  name: 'OrderDetail',
  component: () => import('@/pages/Order/Detail.vue'),
  meta: { title: '订单详情' }
}
```

---

## API 模块

**文件**: `api/order.js`

```javascript
import request from './index'

export const getOrders = (params) => {
  return request.get('/APS/orders', { params })
}

export const getOrder = (id) => {
  return request.get(`/APS/orders/${id}`)
}

export const createOrder = (data) => {
  return request.post('/APS/orders', data)
}

export const updateOrderStatus = (id, status) => {
  return request.patch(`/APS/orders/${id}`, { status })
}

export const cancelOrder = (id) => {
  return updateOrderStatus(id, 'cancel')
}

export const startOrder = (id) => {
  return updateOrderStatus(id, 'doing')
}

export const pauseOrder = (id) => {
  return updateOrderStatus(id, 'pause')
}

export const resumeOrder = (id) => {
  return updateOrderStatus(id, 'doing')
}

export const completeOrder = (id) => {
  return updateOrderStatus(id, 'done')
}
```

---

## 常用模式

### 订单创建流程

```javascript
import { ref } from 'vue'
import { createOrder } from '@/api/order'
import { showToast } from 'vant'

const formData = reactive({
  accountId: null,
  category: 'exp',
  plannedQty: 100,
  planDuration: 60,
  scheduleAt: null
})

const handleSubmit = async () => {
  try {
    const result = await createOrder(formData)

    showToast({ type: 'success', message: '订单创建成功' })

    // 跳转到订单详情
    router.push({ path: `/order/${result.id}` })
  } catch (error) {
    showToast({ type: 'fail', message: error.message || '创建失败' })
  }
}
```

### 基于状态的操作按钮

```vue
<template>
  <div class="order-actions">
    <van-button
      v-if="order.status === 'waiting'"
      type="primary"
      @click="handleStart"
    >
      开始执行
    </van-button>

    <van-button
      v-if="order.status === 'doing'"
      type="warning"
      @click="handlePause"
    >
      暂停
    </van-button>

    <van-button
      v-if="order.status === 'pause'"
      type="primary"
      @click="handleResume"
    >
      继续
    </van-button>

    <van-button
      v-if="['waiting', 'doing'].includes(order.status)"
      type="danger"
      @click="handleCancel"
    >
      取消订单
    </van-button>
  </div>
</template>

<script setup>
import { startOrder, pauseOrder, resumeOrder, cancelOrder } from '@/api/order'

const handleStart = async () => {
  await startOrder(order.id)
  showToast({ type: 'success', message: '订单已开始' })
}

const handlePause = async () => {
  await pauseOrder(order.id)
  showToast({ type: 'success', message: '订单已暂停' })
}

const handleResume = async () => {
  await resumeOrder(order.id)
  showToast({ type: 'success', message: '订单已继续' })
}

const handleCancel = async () => {
  await showDialog({
    title: '确认取消',
    message: '确定要取消此订单吗？'
  })

  await cancelOrder(order.id)
  showToast({ type: 'success', message: '订单已取消' })
}
</script>
```

### 进度条组件

```vue
<template>
  <div class="order-progress">
    <div class="progress-info">
      <span>进度: {{ completedQty }}/{{ plannedQty }}</span>
      <span>{{ percentage }}%</span>
    </div>
    <van-progress
      :percentage="percentage"
      :color="statusColor"
      stroke-width="8"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  completedQty: Number,
  plannedQty: Number,
  status: String
})

const percentage = computed(() => {
  return Math.floor((props.completedQty / props.plannedQty) * 100)
})

const statusColor = computed(() => {
  const colors = {
    waiting: '#1989fa',
    doing: '#ff976a',
    done: '#07c160',
    pause: '#969799',
    cancel: '#ee0a24',
    error: '#ee0a24'
  }
  return colors[props.status] || '#1989fa'
})
</script>
```

---

## UI 组件

### 带筛选器的订单列表

```vue
<template>
  <div class="order-list">
    <!-- 筛选器 -->
    <van-dropdown-menu>
      <van-dropdown-item
        v-model="filters.status"
        :options="statusOptions"
        @change="handleFilterChange"
      />
      <van-dropdown-item
        v-model="filters.category"
        :options="categoryOptions"
        @change="handleFilterChange"
      />
    </van-dropdown-menu>

    <!-- 搜索 -->
    <van-search
      v-model="searchKeyword"
      placeholder="搜索订单号"
      @search="handleSearch"
    />

    <!-- 订单列表 -->
    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <van-list
        v-model:loading="loading"
        :finished="finished"
        @load="onLoad"
      >
        <van-card
          v-for="order in orders"
          :key="order.id"
          :title="order.categoryDisplay"
          :desc="`#${order.id}`"
        >
          <template #tags>
            <van-tag :type="getStatusType(order.status)">
              {{ order.statusDisplay }}
            </van-tag>
          </template>
          <template #footer>
            <div class="order-info">
              <span>账户: {{ order.accountUsername }}</span>
              <span>进度: {{ order.completedQty }}/{{ order.plannedQty }}</span>
            </div>
          </template>
        </van-card>
      </van-list>
    </van-pull-refresh>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { getOrders } from '@/api/order'

const filters = reactive({
  status: '',
  category: ''
})

const statusOptions = [
  { text: '全部状态', value: '' },
  { text: '等待中', value: 'waiting' },
  { text: '进行中', value: 'doing' },
  { text: '已完成', value: 'done' },
  { text: '已暂停', value: 'pause' },
  { text: '已取消', value: 'cancel' },
  { text: '错误', value: 'error' }
]

const categoryOptions = [
  { text: '全部类型', value: '' },
  { text: '经验', value: 'exp' },
  { text: '宝石', value: 'gems' },
  { text: '三倍经验', value: '3x_xp' },
  { text: '签到', value: 'sign' }
]

const getStatusType = (status) => {
  const types = {
    waiting: 'primary',
    doing: 'warning',
    done: 'success',
    pause: 'default',
    cancel: 'danger',
    error: 'danger'
  }
  return types[status] || 'default'
}
</script>
```

---

## 说明

- 所有 APS 接口都需要认证
- 订单自动按用户组织过滤
- 订单执行由后端 Celery 工作者处理
- 前端显示进度但不控制执行
- 实时更新需要手动刷新 (第二阶段计划使用 WebSocket)
- 订单历史保留用于审计目的
