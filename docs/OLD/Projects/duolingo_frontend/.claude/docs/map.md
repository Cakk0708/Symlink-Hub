# Duolingo Frontend - 项目地图

## 地图概述

本文档提供 Duolingo PC端前端应用的高层架构概览。

### Dashboard
- 路径: `/dashboard`
- 别名: 仪表盘/dashboard/首页/项目首页
- 模块说明: `modules/dashboard.md`
- 接口文档: `../backend/.claude/docs/api/sm-dashboard.md`
- 页面布局: `.claude/docs/layouts/dashboard.md`

### Login
- 路径: `/login`
- 别名: 登录/login
- 模块说明: `modules/login.md`
- 接口文档: `../backend/.claude/docs/api/sm-user.md`

### SM (系统管理)
- 路径: `/sm`
- 别名: 系统管理/sm/user management
- 模块说明: `modules/sm.md`
- 接口文档: `../backend/.claude/docs/api/sm-user.md`

#### 用户管理
- 路径: `/sm/user`
- 别名: 用户管理/user list
- 模块说明: `modules/sm-user.md`
- 接口文档: `../backend/.claude/docs/api/sm-user.md`

#### 组织管理
- 路径: `/sm/organization`
- 别名: 组织管理/organization list
- 页面布局: `.claude/docs/layouts/organization-list.md`, `.claude/docs/layouts/organization-detail.md`

### BDM (基础数据管理)
- 路径: `/bdm`
- 别名: 基础数据/bdm/basic data
- 模块说明: `modules/bdm.md`
- 接口文档: `../backend/.claude/docs/api/bdm-customer.md`, `../backend/.claude/docs/api/bdm-account.md`

#### 客户管理
- 路径: `/bdm/customer`
- 别名: 客户管理/customer list
- 模块说明: `modules/bdm-customer.md`
- 接口文档: `../backend/.claude/docs/api/bdm-customer.md`

#### 账号管理
- 路径: `/bdm/account`
- 别名: 账号管理/account list
- 模块说明: `modules/bdm-account.md`
- 接口文档: `../backend/.claude/docs/api/bdm-account.md`
- 页面布局: `.claude/docs/layouts/account-list.md`, `.claude/docs/layouts/account-detail.md`

#### 套餐管理
- 路径: `/bdm/package`
- 别名: 套餐管理/package list
- 接口文档: `../backend/.claude/docs/api/bdm-package.md`
- 页面布局: `.claude/docs/layouts/package-list.md`, `.claude/docs/layouts/package-detail.md`

### APS (订单管理)
- 路径: `/aps`
- 别名: 订单管理/aps/order management
- 模块说明: `modules/aps.md`
- 接口文档: `../backend/.claude/docs/api/aps-order.md`

#### 订单列表
- 路径: `/aps/order`
- 别名: 订单管理/order list
- 模块说明: `modules/aps-order.md`
- 接口文档: `../backend/.claude/docs/api/aps-order.md`
- 页面布局: `.claude/docs/layouts/order-list.md`, `.claude/docs/layouts/order-detail.md`

## 参数说明

### 路径
- 指项目访问 url 路径
- 对应实际开发中的 router 配置路径

### 别名
- 模块的其他名称或业务中常用的称呼
- 帮助快速定位业务模块

### 模块说明
- 模块的功能和作用描述
- 涉及到模块的开发内容时必须阅读该文档
- 包含该模块的核心功能和业务逻辑

### 接口文档
- 模块涉及的接口文档
- 涉及到模块的接口内容时必须阅读接口文档
- 路径为相对于后端文档的相对路径

### 页面布局
- 模块的页面布局说明
- 涉及到模块的页面布局时必须阅读该文档
- 用户描述的每一个页面改动点提到的页面位置都可以参考该文档