# 关键模块定位

> 项目中核心模块的位置与功能说明

## 认证流程

- **入口**：`common/global.js:oauth_login()`
- **Token 管理**：`common/auth.js`
- **登录选择页**：`pages/auth/login-select.vue`
- **OAuth 回调**：`pages/auth/callback.vue`
- **飞书登录**：`common/auth/providers/FeishuProvider.js`

## 请求处理

- **统一请求**：`common/util/request.js:request()`
- **自动刷新 Token**：`common/auth.js:handle401()`

## 项目详情页

- **主页面**：`pagesProject/index/index.vue`（横屏布局）
- **节点流程图**：`pagesProject/components/flow-chart/flow-chart.vue`
- **节点详情**：`pagesProject/components/node-details/node-details.vue`
- **文件管理**：`pagesProject/components/delivery-flie.vue`
- **操作记录**：`pagesProject/components/records.vue`

## 状态管理

- **Store 配置**：`store/index.js`
- **权限存储**：`state.authority`
- **用户信息**：`state.userinfo`
