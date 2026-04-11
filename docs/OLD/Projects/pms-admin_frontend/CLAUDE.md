# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是 OMC（运营管理后台）前端项目，基于 Vue 3 + Vite + Element Plus 构建的现代化管理系统，服务于宁德岭阳电子科技。项目目标是打造高耦合、轻量化的超级 MOM 系统。

## 重要约定

⚠️ **在涉及项目模块调整、新增功能或修改架构时，必须先阅读以下文档：**

### 组件地图
当你在页面样式设计时必须阅读组件地图，了解组件地图全貌，确保要添加的内容是已有可复用情况是直接调用组件

- 路径: `.claude/docs/component-map.md`

**遵循此约定的目的**
- 确认重复功能不再重复开发
- 维护高可用逻辑直接复用已有组件

### 模块地图
当你收到任务时必须阅读模块地图，了解业务模块全景和依赖关系、各模块详细文档的导航链接以及项目架构概览

- 路径: `.claude/docs/module-map.md`

**遵循此约定的目的：**
- 确保代码变更与项目架构保持一致
- 避免破坏模块间的依赖关系
- 保持文档与代码的同步

## 开发命令

### 环境运行
- `npm run dev` - 开发环境（默认）
- `npm run dev_fkq` - fkq 环境
- `npm run dev_fwt` - fwt 环境
- `npm run localdev` - 本地开发环境
- `npm run test` - 测试环境
- `npm run prod` - 生产环境
- `npm run yadalong` - yadalong 环境

### 构建
- `npm run build:dev` - 构建开发环境
- `npm run build:dev_fkq` - 构建 fkq 环境
- `npm run build:dev_fwt` - 构建 fwt 环境
- `npm run build:test` - 构建测试环境
- `npm run build:test-cloud` - 构建测试云环境
- `npm run build:prod` - 构建生产环境
- `npm run build:yadalong` - 构建 yadalong 环境
- `npm run preview` - 预览构建结果

### 节点版本要求
Node.js 20+

## 项目架构

### 技术栈
- **框架**: Vue 3 (Composition API) + Vue Router 4 + Pinia
- **构建工具**: Vite 5.3.4
- **UI框架**: Element Plus 2.7.7
- **状态管理**: Pinia + pinia-plugin-persistedstate（持久化）
- **HTTP**: Axios（封装于 `utils/request.js`）
- **样式**: Sass + UnoCSS（原子化 CSS）
- **图表**: ECharts 5.5.1
- **甘特图**: dhtmlx-gantt 8.0.9

### 目录结构
```
src/
├── api/              # 按业务模块划分的接口
├── assets/           # 静态资源（SVG图标、图片、字体）
├── components/       # 公共组件
│   ├── LYTable/      # 封装的表格组件
│   └── LYDialog/     # 封装的对话框组件
├── layout/           # 主布局（包含 NavBar）
├── router/           # 路由配置（模块化）
├── stores/           # Pinia 状态管理
├── utils/            # 工具函数
├── views/            # 页面视图
├── styles/           # 全局样式
├── enums/            # 枚举定义
├── directive/        # 自定义指令
├── hooks/            # 组合式函数
└── composables/      # 组合式函数
```

### 路由架构
- 使用 Hash 模式（`createWebHashHistory`）
- 路由模块化组织，各业务模块独立文件位于 `router/modules/`
- 支持路由懒加载和元信息配置
- 集成权限控制系统

### 状态管理
主要 Store 模块：
- `user` - 用户信息、登录状态、权限
- `permission` - 权限控制
- `app` - 应用全局状态
- `settings` - 系统设置
- `tagsView` - 标签页管理
- `message` - 消息通知
- `enumDict` - 字典枚举

### API 组织
- 按业务模块划分（`src/api/{module}/`）
- 采用类的方式组织 API 方法
- 统一的请求/响应拦截器在 `utils/request.js`
- 自动处理 token 认证和错误处理

### 业务模块
- **SM（系统管理）**: 用户、角色、权限、组织机构
- **BDM（基础数据管理）**: 物料、BOM、供应商、客户、部门、员工、仓库、计量单位
- **WMS（仓储管理）**: 库存、入库、出库、调拨
- **CRM（客户管理）**: 客户列表、接口管理
- **PDM（产品管理）**: 产品列表
- **PM（项目管理）**: 项目节点规则、硬件规格、模型
- **PMS（项目管理系统）**: 硬件规格
- **SUB（订阅管理）**: 产品订阅
- **SMS（销售管理）**: 销售相关

## 开发规范

### 页面命名
- `index` - 列表页
- `add` - 新增页
- `edit` - 编辑页

### 组件设计
- **容器组件** - 负责处理业务逻辑
- **展示组件** - 负责样式和渲染

### Vue 风格
- 使用 Composition API（`<script setup>`）
- 使用自动导入（Vue、Element Plus 组件和 API 自动导入，无需手动 import）
- 路由使用 `<router-view>` 和路由元信息
- 状态使用 Pinia stores

### Vite 配置特性
- 自动导入 Vue、Element Plus 组件和 API
- SVG 图标支持（`~icons` 路径别名）
- IE 浏览器兼容性（@vitejs/plugin-legacy）
- Gzip 压缩
- 资源文件分类输出

## 特殊功能

### 权限系统
- 基于路由的权限控制
- 动态菜单生成
- Token 过期自动跳转登录
- 支持组织切换

### 页面缓存
- 使用 `<keep-alive>` 实现页面缓存
- 标签页管理支持

### 环境配置
- 支持多环境配置（dev、test、prod 等）
- 每个环境独立的 API 配置
- Vite 代理解决开发跨域