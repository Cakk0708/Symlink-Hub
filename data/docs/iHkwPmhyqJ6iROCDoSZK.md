# BDM 模块 - 业务数据管理

## 概述

BDM (Business Data Management，业务数据管理) 模块处理客户管理和 Duolingo 账户管理，包括账户验证和创建。

## 前端页面

### 账户列表
**路径**: `/account`
**布局**: DefaultLayout
**需要认证**: 是

**功能**:
- 分页账户列表
- 多筛选器支持:
  - 手机号 (精确匹配)
  - 账户名 (模糊搜索)
  - 客户 (下拉选择)
- 下拉刷新
- 账户状态指示器 (禁用标志)
- 快速同步按钮

**API**:
```javascript
GET /BDM/account?page=0&phone=xxx&name=xxx&customer=1

响应:
{
  msg: "success",
  items: [
    {
      id: 1,
      code: "A20260315001",
      email: "usera@example.com",
      username: "usera",
      nickname: "用户A",
      phone: "13800138000",
      remark: "客户A的账户",
      exp: 1250,
      gems: 500,
      customer: "闲鱼客户A",
      lastSign: "2026-03-15",
      disableFlag: false,
      createdAt: "2026-03-15T10:00:00Z"
    }
  ],
  pagination: {
    page: 0,
    page_size: 10,
    total: 32
  }
}
```

**组件**: `pages/Account/List.vue`

---

### 账户验证
**路径**: `/account/verify`
**布局**: DefaultLayout
**需要认证**: 是

**功能**:
- 三种验证方式:
  1. 用户名密码
  2. 手机号 + 验证码
  3. API Token
- 表单验证
- 加载状态
- 错误处理
- 验证成功后跳转到账户创建

**API**:
```javascript
// 方式一: 用户名密码
POST /BDM/account/credentials/verify
{
  type: "username",
  username: "duolingo_username",
  password: "duolingo_password"
}

// 方式二: 手机号 + 验证码
// 步骤 1: 发送验证码
POST /BDM/account/verification-codes
{
  target: "13800138000",
  type: "sms",
  scene: "login"
}

// 步骤 2: 使用验证码验证
POST /BDM/account/credentials/verify
{
  type: "phone",
  verificationKey: "verification_key_xxx",
  code: "123456"
}

// 方式三: API Token
POST /BDM/account/credentials/verify
{
  type: "token",
  token: "duolingo_api_token"
}

// 成功响应 (所有方式)
{
  msg: "success",
  data: {
    checkPassed: true,
    cacheKey: "BDM:account:credentials:verify:xxx"
  }
}
```

**组件**: `pages/Account/Verify.vue`

**流程**:
1. 用户选择验证方式
2. 填写相应表单
3. 后端通过 Duolingo API 验证
4. 成功 → 获得 `cacheKey`
5. 携带 `cacheKey` 跳转到 `/account/create`

---

### 账户创建
**路径**: `/account/create`
**布局**: DefaultLayout
**需要认证**: 是

**功能**:
- 选择客户 (可选，通过弹窗)
- 添加备注
- 需要验证步骤的 `cacheKey`
- 自动关联到用户组织

**API**:
```javascript
POST /BDM/account
{
  cacheKey: "BDM:account:credentials:verify:xxx",
  customerId: 1,  // 可选
  remark: "客户A的账户"
}

响应:
{
  msg: "success",
  data: {
    id: 1,
    username: "duolingo_username",
    uuid: "xxx-xxx-xxx"
  }
}
```

**组件**: `pages/Account/Create.vue`

---

### 账户详情
**路径**: `/account/:id`
**布局**: DefaultLayout
**需要认证**: 是

**功能**:
- 显示账户信息（基本信息、账户数据、签到信息、其他信息）
- 从 Duolingo 同步最新数据
- 显示连续签到信息
- 账号状态展示（`others.disableFlag`，`van-tag` 红色已禁用/绿色正常）
- 更多操作菜单：
  - 同步数据
  - 转移所属客户
  - 禁用/启用账号（调用 `PATCH /BDM/account/{id}/disable`，二次确认后切换状态并刷新）

**API**:
```javascript
GET /BDM/account/:id

响应:
{
  msg: "success",
  data: {
    document: { code, username, nickname, uuid, email, phone },
    accountData: { gems, exp, checkInStreak, isTodayCheckedIn, lastSign },
    others: { disableFlag, remark, createdAt, updatedAt }
  }
}

// 禁用/启用
PATCH /BDM/account/:id/disable
{ disableFlag: true/false }
```

**组件**: `pages/Account/Detail.vue`

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

### 账户验证流程

```javascript
// 步骤 1: 验证凭据
const { data } = await verifyCredentials({
  type: 'username',
  username: 'duolingo_user',
  password: 'password123'
})

// 步骤 2: 存储 cacheKey
const cacheKey = data.data.cacheKey
localStorage.setItem('account_cache_key', cacheKey)

// 步骤 3: 跳转到创建页面
router.push({
  path: '/account/create',
  query: { cacheKey }
})

// 步骤 4: 创建账户
await createAccount({
  cacheKey: cacheKey,
  customerId: selectedCustomerId,
  remark: '备注信息'
})
```

---

## 说明

- 所有 BDM 接口都需要认证
- 客户和账户数据自动按组织过滤
- 账户验证缓存 10 分钟后过期
- 手机号显示时应脱敏 (如 `138****8000`)
