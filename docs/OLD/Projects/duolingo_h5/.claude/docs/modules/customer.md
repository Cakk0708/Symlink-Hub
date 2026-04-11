# BDM 模块 - 业务数据管理

## 概述

BDM (Business Data Management，业务数据管理) 模块处理客户管理和 Duolingo 账户管理，包括账户验证和创建。

## 前端页面

### 客户列表
**路径**: `/customer`
**布局**: DefaultLayout
**需要认证**: 是

**功能**:
- 分页客户列表
- 按客户名称搜索
- 下拉刷新
- 无限滚动/加载更多
- 滑动操作 (编辑/删除)

**API**:
```javascript
GET /BDM/customer?page=0&name=搜索关键词

响应:
{
  msg: "success",
  data: {
    items: [
      {
        id: 1,
        code: "C20260315001",
        name: "闲鱼客户A",
        category: "GOOFISH",
        categoryDisplay: "闲鱼",
        createdAt: "2026-03-15T10:00:00Z",
        orderCount: 5
      }
    ],
    count: 10
  }
}
```

**组件**: `pages/Customer/List.vue`

---

### 客户详情
**路径**: `/customer/:id`
**布局**: DefaultLayout
**需要认证**: 是

**功能**:
- 客户信息展示
- 关联账户列表
- 编辑客户
- 删除客户 (需确认)

**API**:
```javascript
GET /BDM/customer/:id

响应:
{
  msg: "success",
  data: {
    id: 1,
    code: "C20260315001",
    name: "闲鱼客户A",
    category: "GOOFISH",
    categoryDisplay: "闲鱼",
    orderCount: 5,
    accounts: [
      {
        id: 1,
        username: "usera",
        nickname: "用户A",
        email: "usera@example.com",
        phone: "138****8000"
      }
    ]
  }
}

DELETE /BDM/customer
{
  ids: [1, 2, 3]
}
```

**组件**: `pages/Customer/Detail.vue`

---

## 状态管理

### BDM Store (可选)

```javascript
import { defineStore } from 'pinia'

export const useBDMStore = defineStore('bdm', {
  state: () => ({
    customers: [],
    accounts: [],
    currentCustomer: null,
    currentAccount: null,
    cacheKey: null  // 用于账户创建流程
  }),

  actions: {
    async fetchCustomers(params) {
      const { data } = await request.get('/BDM/customer', { params })
      this.customers = data.data.items
    },

    async fetchAccounts(params) {
      const { data } = await request.get('/BDM/account', { params })
      this.accounts = data.data.items
    },

    setCacheKey(key) {
      this.cacheKey = key
    }
  }
})
```

---

## 路由配置

```javascript
{
  path: 'customer',
  name: 'CustomerList',
  component: () => import('@/pages/Customer/List.vue'),
  meta: { title: '客户管理' }
},
{
  path: 'customer/:id',
  name: 'CustomerDetail',
  component: () => import('@/pages/Customer/Detail.vue'),
  meta: { title: '客户详情' }
},
{
  path: 'account',
  name: 'AccountList',
  component: () => import('@/pages/Account/List.vue'),
  meta: { title: '账户管理' }
},
{
  path: 'account/verify',
  name: 'AccountVerify',
  component: () => import('@/pages/Account/Verify.vue'),
  meta: { title: '账户验证' }
},
{
  path: 'account/create',
  name: 'AccountCreate',
  component: () => import('@/pages/Account/Create.vue'),
  meta: { title: '创建账户' }
},
{
  path: 'account/:id',
  name: 'AccountDetail',
  component: () => import('@/pages/Account/Detail.vue'),
  meta: { title: '账户详情' }
}
```

---

## API 模块

**文件**: `api/customer.js`

```javascript
import request from './index'

export const getCustomers = (params) => {
  return request.get('/BDM/customer', { params })
}

export const getCustomer = (id) => {
  return request.get(`/BDM/customer/${id}`)
}

export const createCustomer = (data) => {
  return request.post('/BDM/customer', data)
}

export const updateCustomer = (id, data) => {
  return request.put(`/BDM/customer/${id}`, data)
}

export const deleteCustomers = (ids) => {
  return request.delete('/BDM/customer', { data: { ids } })
}
```

**文件**: `api/account.js`

```javascript
import request from './index'

export const getAccounts = (params) => {
  return request.get('/BDM/account', { params })
}

export const getAccount = (id) => {
  return request.get(`/BDM/account/${id}`)
}

export const verifyCredentials = (data) => {
  return request.post('/BDM/account/credentials/verify', data)
}

export const sendVerificationCode = (data) => {
  return request.post('/BDM/account/verification-codes', data)
}

export const createAccount = (data) => {
  return request.post('/BDM/account', data)
}

export const syncAccount = (id) => {
  return request.get(`/BDM/account/${id}`)
}
```

---

## 常用模式

### 客户选择弹窗

```vue
<template>
  <van-popup v-model:show="showCustomerPicker" position="bottom">
    <van-picker
      :columns="customerOptions"
      @confirm="onCustomerConfirm"
      @cancel="showCustomerPicker = false"
    />
  </van-popup>
</template>

<script setup>
const customerOptions = computed(() =>
  customers.map(c => ({
    text: c.name,
    value: c.id
  }))
)

const onCustomerConfirm = ({ selectedOptions }) => {
  formData.customerId = selectedOptions[0].value
  showCustomerPicker = false
}
</script>
```

---

## UI 组件

## 说明

- 所有 BDM 接口都需要认证
- 客户和账户数据自动按组织过滤
- 账户验证缓存 10 分钟后过期
- 手机号显示时应脱敏 (如 `138****8000`)
