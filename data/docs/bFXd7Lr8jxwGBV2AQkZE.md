# 认证

## Token 管理

### Token 类型

- **access_token**: 存储在 localStorage (30天有效期)
- **refresh_token**: 存储在 localStorage 用于 token 刷新

### Token 使用

- 请求拦截器自动添加 `Authorization: Bearer {token}` 请求头
- 401 响应触发自动 token 刷新
- Token 失效后自动跳转登录页

## 认证 Store

使用 `useAuthStore` Pinia store：

```javascript
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// 登录
await authStore.login({ username, password })

// 登出
authStore.logout()

// 检查认证状态
const isAuthenticated = authStore.isAuthenticated
```

## 认证流程

1. 用户提交登录表单
2. 调用登录 API 获取 token
3. 存储 token 到 localStorage
4. 更新认证状态
5. 跳转到仪表盘

## 认证状态

认证状态存储在 Pinia store 中：

- `isAuthenticated`: 是否已认证
- `user`: 当前用户信息
- `token`: 访问令牌

## Token 刷新

当 access_token 过期时：

1. 捕获 401 响应
2. 使用 refresh_token 获取新的 access_token
3. 更新 localStorage 中的 token
4. 重试原请求
5. 刷新失败则跳转登录页
