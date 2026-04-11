# Register 模块 - 用户注册

## 概述

Register (用户注册) 模块处理新用户注册和组织创建。

## 前端页面

### 注册页
**路径**: `/register`
**布局**: BlankLayout

**功能**:
- 新用户注册
- 组织自动创建
- 密码确认验证
- 注册后自动登录

**API**:
```javascript
POST /SM/user/register
{
  username: string,
  password: string,
  nickname: string (可选),
  organization: {
    name: string
  }
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

**验证规则**:
- username: 必填，3-20 字符
- password: 必填，6-20 字符
- confirmPassword: 必须与 password 一致
- organization.name: 必填，2-50 字符

**组件**: `pages/Register/index.vue`

---

## 路由配置

```javascript
{
  path: '/register',
  name: 'Register',
  component: () => import('@/pages/Register/index.vue'),
  meta: { layout: 'blank', requiresAuth: false }
}
```

---

## 数据结构

### 注册请求类型

```typescript
interface RegisterPayload {
  username: string           // 用户名 (3-20字符)
  password: string           // 密码 (6-20字符)
  nickname?: string          // 昵称 (可选)
  organization: {
    name: string             // 组织名称 (2-50字符)
  }
}

interface RegisterResponse {
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

## UI 组件

### 注册表单组件

```vue
<template>
  <van-form @submit="handleSubmit">
    <van-cell-group inset>
      <van-field
        v-model="formData.username"
        name="username"
        label="用户名"
        placeholder="请输入用户名"
        :rules="[
          { required: true, message: '请输入用户名' },
          { pattern: /^[a-zA-Z0-9]{3,20}$/, message: '用户名为3-20位字母或数字' }
        ]"
      />
      <van-field
        v-model="formData.password"
        type="password"
        name="password"
        label="密码"
        placeholder="请输入密码"
        :rules="[
          { required: true, message: '请输入密码' },
          { min: 6, max: 20, message: '密码长度为6-20位' }
        ]"
      />
      <van-field
        v-model="formData.confirmPassword"
        type="password"
        name="confirmPassword"
        label="确认密码"
        placeholder="请再次输入密码"
        :rules="[
          { required: true, message: '请确认密码' },
          { validator: validatePassword, message: '两次密码输入不一致' }
        ]"
      />
      <van-field
        v-model="formData.nickname"
        name="nickname"
        label="昵称"
        placeholder="请输入昵称（可选）"
      />
      <van-field
        v-model="formData.organization.name"
        name="organization"
        label="组织名称"
        placeholder="请输入组织名称"
        :rules="[
          { required: true, message: '请输入组织名称' },
          { min: 2, max: 50, message: '组织名称为2-50位字符' }
        ]"
      />
    </van-cell-group>

    <div style="margin: 16px">
      <van-button round block type="primary" native-type="submit">
        注册
      </van-button>
    </div>

    <div style="text-align: center; margin-top: 16px">
      <span style="color: #999">已有账号？</span>
      <router-link to="/login" style="color: #1989fa">立即登录</router-link>
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
  password: '',
  confirmPassword: '',
  nickname: '',
  organization: {
    name: ''
  }
})

const validatePassword = (val) => {
  return val === formData.password
}

const handleSubmit = async () => {
  try {
    await authStore.register(formData)
    showToast({ type: 'success', message: '注册成功' })
    router.push('/dashboard')
  } catch (error) {
    showToast({ type: 'fail', message: error.message || '注册失败' })
  }
}
</script>
```

---

## API 模块

**文件**: `api/auth.js`

```javascript
export const register = (userData) => {
  return request.post('/SM/user/register', userData)
}
```

---

## Store 扩展

需要在 `stores/auth.js` 中添加 register action：

```javascript
actions: {
  async register(userData) {
    const { data } = await request.post('/SM/user/register', userData)
    this.token = data.data.token.access_token
    this.refreshToken = data.data.token.refresh_token
    this.user = data.data.user

    localStorage.setItem('access_token', this.token)
    localStorage.setItem('refresh_token', this.refreshToken)
    localStorage.setItem('user', JSON.stringify(this.user))
  }
}
```

---

## 说明

- 注册成功后自动创建组织
- 注册成功后自动登录，跳转到仪表盘
- 用户名不能重复
- 组织名称在同一用户下唯一
- 已有账号的用户应使用登录页面
