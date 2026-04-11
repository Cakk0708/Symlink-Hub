# Duolingo H5 - 项目地图

## 地图概述

本文档提供 Duolingo H5 前端应用的高层架构概览。

### Customer
- 路径: `/customer`
- 别名: 客户管理/客户列表/客户详情/customer list
- 模块说明: `modules/customer.md`
- 接口文档: `../backend/.claude/docs/api/bdm-customer.md`

### Account
- 路径: `/account`
- 别名: 账户管理/账户列表/account list
- 模块说明: `modules/account.md`
- 接口文档: `../backend/.claude/docs/api/bdm-account.md`

### Order
- 路径: `/order`
- 别名: 订单管理/订单列表/order list
- 模块说明: `modules/order.md`
- 接口文档: `../backend/.claude/docs/api/aps-order.md`
- 页面布局: `.layouts/order.md`

### Dashboard
- 路径: `/dashboard`
- 别名: 仪表盘/dashboard/项目首页/首页
- 模块说明: `modules/dashboard.md`
- 接口文档: `../backend/.claude/docs/api/sm-dashboard.md`

### Login
- 路径: `/login`
- 别名: 登录/login
- 模块说明: `modules/login.md`

### Register
- 路径: `/register`
- 别名: 注册/register
- 模块说明: `modules/register.md`

## 参数说明

### 路径
- 意指项目访问 url 路径

### 别名
- 模块的其他名称

### 模块说明
- 模块的功能和作用描述
- 涉及到模块的开发内容时必须阅读该文档

### 接口文档
- 模块涉及的接口文档
- 涉及到模块的接口内容时必须阅读接口文档

### 页面布局
- 模块的页面布局说明
- 涉及到模块的页面布局时必须阅读该文档
- 用户描述的每一个页面改动点提到的页面位置都可以参考该文档