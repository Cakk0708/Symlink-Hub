# 路由守卫

## 路由配置

路由定义在 `src/router/index.js`：

```javascript
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/Login/index.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: DefaultLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/pages/Dashboard/index.vue')
      }
    ]
  }
]
```

## 路由守卫逻辑

### 认证检查

路由守卫会：

1. 检查 localStorage 中的 `access_token`
2. Token 缺失时重定向到登录页
3. 已认证用户访问登录/注册页时重定向到仪表盘

### 守卫实现

```javascript
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')

  // 需要认证的路由
  if (to.meta.requiresAuth !== false) {
    if (!token) {
      // 未认证，跳转登录页
      next({ name: 'Login', query: { redirect: to.fullPath } })
    } else {
      // 已认证，继续访问
      next()
    }
  } else {
    // 不需要认证的路由
    if (token && to.name === 'Login') {
      // 已认证用户访问登录页，跳转仪表盘
      next({ name: 'Dashboard' })
    } else {
      next()
    }
  }
})
```

## 路由元信息

使用 `meta` 字段配置路由行为：

- `requiresAuth`: 是否需要认证（默认 true）
- `title`: 页面标题
- `keepAlive`: 是否缓存组件

## 路由跳转

```javascript
import { useRouter } from 'vue-router'

const router = useRouter()

// 编程式导航
router.push({ name: 'Dashboard' })
router.push({ path: '/customer' })
router.push({ name: 'Customer', params: { id: 1 } })

// 带查询参数
router.push({ path: '/search', query: { q: 'keyword' } })

// 替换当前路由
router.replace({ name: 'Login' })

// 返回上一页
router.back()
router.go(-1)
```

## 路由传参

### 路径参数

```javascript
// 定义路由
{ path: '/customer/:id', component: CustomerDetail }

// 获取参数
import { useRoute } from 'vue-router'
const route = useRoute()
const customerId = route.params.id
```

### 查询参数

```javascript
// 设置参数
router.push({ path: '/search', query: { q: 'keyword' } })

// 获取参数
const query = route.query.q
```
