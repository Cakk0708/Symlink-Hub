# 项目架构

## 模块组织

H5 前端按后端模块组织：

- **SM (系统管理)**: 登录、注册、仪表盘
- **BDM (业务数据管理)**: 客户、Duolingo 账户
- **APS (异步处理系统)**: 订单、任务执行

## 目录结构

```
src/
├── api/                 # API 接口模块
│   ├── index.js         # Axios 实例配置
│   ├── auth.js          # 认证相关接口
│   ├── customer.js      # 客户管理接口
│   ├── account.js       # 账户管理接口
│   └── order.js         # 订单管理接口
├── assets/              # 静态资源
│   └── styles/          # 全局样式 (变量、mixins)
├── components/          # 可复用组件
├── composables/         # 组合式函数
│   ├── useAuth.js       # 认证逻辑
│   ├── useList.js       # 列表分页逻辑
│   └── useRequest.js    # 请求封装
├── layouts/             # 布局组件
│   ├── DefaultLayout/   # 默认布局 (带导航)
│   └── BlankLayout/     # 空白布局 (登录/注册页)
├── pages/               # 页面组件 (按模块)
│   ├── Login/
│   ├── Register/
│   ├── Dashboard/
│   ├── Customer/
│   ├── Account/
│   └── Order/
├── router/              # Vue Router 配置
├── stores/              # Pinia stores
│   ├── auth.js          # 认证状态
│   ├── user.js          # 用户状态
│   └── app.js           # 应用状态
└── utils/               # 工具函数
    ├── request.js       # HTTP 请求封装
    ├── storage.js       # LocalStorage 封装
    └── format.js        # 数据格式化工具
```

## 架构特点

1. **模块化**: 按业务模块组织代码
2. **组合式**: 使用 Vue 3 组合式 API
3. **分层架构**: API、组件、页面、工具函数清晰分层
4. **可复用性**: composables 提供可复用的逻辑
