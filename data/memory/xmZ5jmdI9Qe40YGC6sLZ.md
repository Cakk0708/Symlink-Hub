# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在处理本仓库代码时提供指导。

## 快速导航

以下是详细的项目文档链接。当你需要了解特定方面的信息时，请阅读对应的文档。

### 核心文档

| 文档 | 说明 | 何时阅读 |
|------|------|----------|
| [项目地图](.claude/docs/map.md) | 项目核心地图介绍 | 涉及所有项目相关模块定位路径都必须阅读该文档 |
| [项目概述](.claude/docs/overview.md) | 项目定位、核心功能、业务模块 | 需要了解项目基本情况时 |
| [技术栈](.claude/docs/tech-stack.md) | 框架、工具、平台配置 | 需要了解技术选型时 |
| [开发命令](.claude/docs/development.md) | npm 脚本、构建命令 | 需要运行项目或构建时 |
| [项目架构](.claude/docs/architecture.md) | 目录结构、模块组织 | 需要了解代码组织时 |

### 模块文档

| 文档 | 说明 | 何时阅读 |
|------|------|----------|
| [Dashboard](.claude/docs/modules/dashboard.md) | 首页模块说明 | 开发首页功能时必读 |
| [登录](.claude/docs/modules/login.md) | 登录模块说明 | 开发登录功能时必读 |
| [系统管理](.claude/docs/modules/sm.md) | SM 模块说明 | 开发系统管理功能时必读 |
| [用户管理](.claude/docs/modules/sm-user.md) | 用户管理模块说明 | 开发用户管理时必读 |
| [基础数据](.claude/docs/modules/bdm.md) | BDM 模块说明 | 开发基础数据功能时必读 |
| [客户管理](.claude/docs/modules/bdm-customer.md) | 客户管理模块说明 | 开发客户管理时必读 |
| [账号管理](.claude/docs/modules/bdm-account.md) | 账号管理模块说明 | 开发账号管理时必读 |
| [订单管理](.claude/docs/modules/aps.md) | APS 模块说明 | 开发订单管理功能时必读 |
| [订单列表](.claude/docs/modules/aps-order.md) | 订单列表模块说明 | 开发订单列表时必读 |

### 布局文档

| 文档 | 说明 | 何时阅读 |
|------|------|----------|
| [Dashboard 布局](.claude/docs/layouts/dashboard.md) | Dashboard 页面布局设计 | 修改首页布局时必读 |

## 项目概览
- **项目类型**: PC端 Vue 3 后台管理系统
- **框架**: Vue 3 + Composition API (`<script setup>`)
- **构建工具**: Vite
- **UI 库**: Element Plus
- **路由**: Vue Router 4
- **HTTP 客户端**: Axios 自定义请求工具
- **图表**: ECharts
- **语言**: JavaScript (ES modules)
- **状态管理**: localStorage（Pinia 已安装但未使用）

## 可用命令
```bash
npm run dev      # 启动开发服务器
npm run build    # 构建生产版本
npm run preview  # 本地预览生产构建
```

## 架构设计

### 入口文件
- `src/main.js` - 应用启动文件，全局注册 Element Plus 图标

### 路由 (`src/router/index.js`)
- 使用 `import()` 实现懒加载路由
- 权限守卫检查 localStorage 中的 token
- 嵌套路由结构：`/sm` (系统管理), `/bdm` (基础数据), `/aps` (订单管理)
- 路由 meta 信息包含 `title` 和 `icon` 用于侧边栏渲染

### 布局 (`src/layout/Layout.vue`)
- 带可折叠侧边栏的主应用包装器
- 移动端响应式（768px 以下自动折叠）
- 用户下拉菜单含登出功能
- 从路由配置动态渲染菜单

### HTTP 请求 (`src/utils/request.js`)
- Axios 实例，5000ms 超时设置
- 通过 `VITE_API_BASE_URL` 环境变量设置基础 URL
- 请求拦截器：添加 `Authorization: Bearer ${token}` 请求头
- 响应拦截器：
  - 自动解包 `response.data`
  - 401 错误：清除 token，重定向到登录页
  - 400 错误：显示格式化的验证错误
  - 其他错误：显示通用错误消息

### 状态管理
- **无集中状态管理**（已安装 Pinia 但未初始化）
- 认证状态存储在 `localStorage` 中（`token`, `userinfo`）
- 组件使用本地 `ref`/`reactive` 状态

### 环境变量
- `.env.development`: `VITE_API_BASE_URL=http://127.0.0.1:8000`
- `.env.production`: `VITE_API_BASE_URL=https://duo.fuanba.cn/api`
- 通过 `import.meta.env.VITE_*` 访问

## 代码规范

### 组件结构
```vue
<template>
  <!-- 模板内容 -->
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { User } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '../../utils/request'

const loading = ref(false)
const data = reactive({})

const fetchData = async () => {
  try {
    loading.value = true
    const response = await request.get('/endpoint')
    // 处理响应数据
  } catch (error) {
    console.error('请求失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
/* 组件样式 */
</style>
```

### 导入顺序
1. Vue composition API 函数
2. Element Plus 组件/图标
3. 内部工具（如 `request`）
4. 相对路径导入

### 命名规范
- 变量/函数：`camelCase`
- 组件：`PascalCase`
- 事件处理器：`handle*` 前缀
- Ref 变量：`*Ref` 后缀
- 异步数据获取：`event_*` 前缀（观察到的模式）

### 错误处理
```javascript
try {
  const response = await request.post('/endpoint', params)
  ElMessage.success('操作成功')
} catch (error) {
  // HTTP 错误已被请求拦截器处理
  console.error('操作失败:', error)
} finally {
  loading.value = false
}
```

### 认证流程
1. 通过 `/SM/user/login` 接口登录
2. 将 token 存储在 `localStorage.setItem('token', jwt)`
3. 将用户信息存储在 `localStorage.setItem('userinfo', json)`
4. 路由守卫在导航时检查 token
5. 401 响应触发自动登出

### 添加新页面
1. 在 `src/views/[module]/index.vue` 创建组件
2. 在 `src/router/index.js` 中添加路由，包含 `meta: { title, icon }`
3. 布局会自动添加到侧边栏菜单

### Element Plus 使用规范
- 图标从 `@element-plus/icons-vue` 导入（全部全局注册）
- 使用 `ElMessage` 显示通知
- 表单验证使用 `:rules` 绑定
- 组件标签使用 `el-` 前缀

## 重要说明

- 这是 **PC端** 后台管理系统 - 主要在桌面端使用
- Element Plus 组件专为 PC 端设计 - 优先使用桌面端组件
- 后端所有命令需要 `DJANGO_ENVIRONMENT=dev` 或 `prod`
- 所有 API 响应使用驼峰式命名字段
- 图片和静态资源放在 `src/assets/`

## 相关项目

- **后端 Django API**: `../Duolingo_backend/`
- **H5 移动端**: `../Duolingo_h5/`
- **项目地图**: [详细模块说明](.claude/docs/map.md)
