# API 集成

## 请求模式

使用 `@/utils/request` 中的自定义 `request` 工具：

```javascript
import request from '@/utils/request'

// GET 请求
const data = await request.get('/BDM/customer')

// POST 请求
const result = await request.post('/SM/user/login', { username, password })
```

## API 响应格式

所有 API 响应遵循以下结构：

```javascript
{
  msg: "success",
  data: { /* 响应数据 */ }
}
```

## Base URL 配置

- **开发环境**: `http://127.0.0.1:8000`
- **生产环境**: `https://duo.fuanba.cn/api`

通过环境变量配置：`import.meta.env.VITE_API_BASE_URL`

## 请求拦截器

- 自动添加 `Authorization: Bearer {token}` 请求头
- 自动处理 token 过期和刷新

## 响应拦截器

- 统一处理响应格式
- 401 状态码触发 token 刷新
- 其他错误统一处理

## API 模块组织

API 接口按业务模块组织在 `src/api/` 目录：

- `index.js` - Axios 实例配置
- `auth.js` - 认证相关接口
- `customer.js` - 客户管理接口
- `account.js` - 账户管理接口
- `order.js` - 订单管理接口
