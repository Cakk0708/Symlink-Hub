# Login 模块 - 用户登录

## 概述

Login (用户登录) 模块处理用户身份认证和授权。

## 前端页面

### 登录页
**路径**: `/login`
**布局**: BlankLayout

**功能**:
- 用户名/密码登录
- 记住密码复选框
- 成功后自动跳转到仪表盘
- 错误信息显示

**API**:
```javascript
POST /SM/user/login
{
  username: string,
  password: string
}

响应:
{
  msg: "success",
  data: {
    user: { /* 用户信息 */ },
    token: {
      refresh_token: string,
      access_token: string
    }
  }
}
```

**组件**: `pages/Login/index.vue`

---

## 状态管理

### 认证 Store (`stores/auth.js`)

```javascript
import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('access_token') || null,
    refreshToken: localStorage.getItem('refresh_token') || null,
    user: JSON.parse(localStorage.getItem('user') || 'null')
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    userOrganization: (state) => state.user?.organizationName
  },

  actions: {
    async login(credentials) {
      const { data } = await request.post('/SM/user/login', credentials)
      this.token = data.data.token.access_token
      this.refreshToken = data.data.token.refresh_token
      this.user = data.data.user

      localStorage.setItem('access_token', this.token)
      localStorage.setItem('refresh_token', this.refreshToken)
      localStorage.setItem('user', JSON.stringify(this.user))
    },

    logout() {
      this.token = null
      this.refreshToken = null
      this.user = null
      localStorage.clear()
      router.push('/login')
    }
  }
})
```

---

## 路由配置

```javascript
{
  path: '/login',
  name: 'Login',
  component: () => import('@/pages/Login/index.vue'),
  meta: { layout: 'blank', requiresAuth: false }
}
```

---

## 数据结构

### 登录请求类型

```typescript
interface LoginPayload {
  username: string
  password: string
}

interface LoginResponse {
  user: {
    id: number
    username: string
    nickname?: string
    organization: {
      id: number
      name: string
    }
  }
  token: {
    access_token: string
    refresh_token: string
  }
}
```

---

## 常用模式

### Token 管理

Token 自动管理:
1. 登录时将 token 存储到 localStorage
2. Axios 拦截器添加 `Authorization` 请求头
3. 401 响应触发 token 刷新
4. 刷新失败重定向到登录页

### 路由守卫

```javascript
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')

  if (to.meta.requiresAuth && !token) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.name === 'Login' && token) {
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})
```

---

## API 模块

**文件**: `api/auth.js`

```javascript
import request from './index'

export const login = (credentials) => {
  return request.post('/SM/user/login', credentials)
}

export const refresh = (refreshToken) => {
  return request.post('/SM/user/refresh', { refresh_token: refreshToken })
}

export const logout = () => {
  return request.post('/SM/user/logout')
}
```

---

## UI 组件

### 登录表单组件

```vue
<template>
  <van-form @submit="handleSubmit">
    <van-cell-group inset>
      <van-field
        v-model="formData.username"
        name="username"
        label="用户名"
        placeholder="请输入用户名"
        :rules="[{ required: true, message: '请输入用户名' }]"
      />
      <van-field
        v-model="formData.password"
        type="password"
        name="password"
        label="密码"
        placeholder="请输入密码"
        :rules="[{ required: true, message: '请输入密码' }]"
      />
    </van-cell-group>

    <div style="margin: 16px">
      <van-button round block type="primary" native-type="submit">
        登录
      </van-button>
    </div>

    <div style="text-align: center; margin-top: 16px">
      <span style="color: #999">还没有账号？</span>
      <router-link to="/register" style="color: #1989fa">立即注册</router-link>
    </div>
  </van-form>
</template>

<script setup>
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { showToast } from 'vant'

const router = useRouter()
const authStore = useAuthStore()
const formData = reactive({
  username: '',
  password: ''
})

const handleSubmit = async () => {
  try {
    await authStore.login(formData)
    showToast({ type: 'success', message: '登录成功' })
    const redirect = router.currentRoute.value.query.redirect || '/dashboard'
    router.push(redirect)
  } catch (error) {
    showToast({ type: 'fail', message: error.message || '登录失败' })
  }
}
</script>
```

---

## 说明

- 登录接口不需要认证
- 登录成功后获取 access_token 和 refresh_token
- access_token 有效期 30 天
- token 过期时使用 refresh_token 自动刷新
- 用户资料管理计划在未来版本中实现
- 注册功能见 [Register 模块文档](./register.md)
- 仪表盘功能见 [Dashboard 模块文档](./dashboard.md)
