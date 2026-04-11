# 目录结构

> 详细的项目文件结构说明

```
pms_frontend/
├── App.vue                 # 应用入口
├── main.js                 # 主入口文件
├── env.js                  # 环境配置
├── pages.json              # 页面路由配置
├── manifest.json           # uni-app 应用配置
│
├── common/                 # 公共模块
│   ├── auth.js             # Token 管理（获取、保存、刷新）
│   ├── global.js           # 全局方法（登录、工具函数）
│   ├── util/               # 工具函数
│   │   ├── request.js      # 统一请求封装
│   │   ├── date.js         # 日期处理
│   │   ├── index.js        # 工具函数集合
│   │   └── uploadFile.js   # 文件上传
│   ├── auth/               # 认证模块
│   │   ├── index.js        # 认证入口
│   │   ├── core/           # 核心认证类
│   │   ├── providers/      # OAuth 提供者
│   │   └── callback/       # 回调处理
│   ├── config/             # 配置文件
│   └── fsSDK.js            # 飞书 SDK
│
├── store/                  # Vuex 状态管理
│   └── index.js            # Store 配置
│
├── pages/                  # 主包页面
│   ├── index/              # 首页
│   │   ├── index.vue
│   │   └── components/     # 首页组件
│   └── auth/               # 认证页面
│       ├── login-select.vue    # 登录方式选择
│       └── callback.vue        # OAuth 回调
│
├── pagesProject/           # 项目详情页（子包）
│   ├── index/
│   │   └── index.vue       # 项目详情主页面（横屏）
│   ├── components/         # 项目详情组件
│   │   ├── basic-info.vue      # 基本信息标签页
│   │   ├── delivery-flie.vue   # 文件管理标签页
│   │   ├── requirement.vue     # 需求标签页
│   │   ├── defect.vue          # 缺陷标签页
│   │   ├── records.vue         # 操作记录标签页
│   │   ├── project-evaluate.vue # 评价标签页
│   │   ├── project-settlement.vue # 结算标签页
│   │   ├── flow-chart/         # 节点流程图（Canvas）
│   │   ├── node-details/       # 节点详情组件
│   │   ├── form/               # 表单组件
│   │   └── tree/               # 树形组件
│   └── mixin/
│       └── index.js        # 项目混入
│
├── pagesTask/              # 任务页面（子包）
├── pagesProgress/          # 进度页面（子包）
├── pagesSigning/           # 签署页面（子包）
├── pagesDemand/            # 需求页面（子包）
├── pagesVerify/            # 验证页面（子包）
├── pagesPool/              # 报表页面（子包）
│
├── components/             # 全局公共组件
│   ├── ly-input/           # 输入框组件
│   ├── ly-nav-bar/         # 导航栏组件
│   ├── ly-dialog/          # 对话框组件
│   ├── ly-drawer/          # 抽屉组件
│   ├── ly-select/          # 选择器组件
│   ├── ly-date/            # 日期组件
│   ├── ly-tooltip/         # 提示组件
│   ├── task-createlists/   # 创建任务弹窗
│   ├── project-enum/       # 项目枚举弹窗
│   └── ...
│
├── static/                 # 静态资源
│   └── ...
│
└── uni_modules/            # uni-app 插件模块
    └── ...
```
