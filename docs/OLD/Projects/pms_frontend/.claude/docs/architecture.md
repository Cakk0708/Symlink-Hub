# 架构设计

> PMS 前端架构设计文档

## 技术栈

- **框架**：uni-app（基于 Vue 2）
- **状态管理**：Vuex
- **UI 框架**：自定义组件 + uni-ui
- **构建工具**：Vue CLI
- **支持平台**：H5、微信小程序、支付宝小程序、App

---

## 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                      应用层                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │ 首页     │  │ 项目详情 │  │ 任务管理 │  │ 报表统计 ││
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘│
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                      业务层                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │ 认证模块 │  │ 权限模块 │  │ 项目模块 │  │ 节点模块 ││
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘│
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                      服务层                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │请求封装  │  │Token管理 │  │ 权限校验 │  │ 数据缓存 ││
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘│
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                      基础层                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │  Vue 2   │  │  Vuex    │  │ uni-app  │  │ 飞书SDK  ││
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘│
└─────────────────────────────────────────────────────────┘
```

---

## 核心模块设计

### 1. 认证模块

#### 认证流程
```
用户打开应用
    │
    ▼
检查本地 Token
    │
    ├─ 有效 → 直接进入
    │
    └─ 无效 → 检测环境
                  │
                  ├─ 飞书容器 → tt.requestAuthCode()
                  │              ↓
                  │           后端登录接口
                  │              ↓
                  │           返回 JWT Token
                  │
                  └─ 浏览器 → 登录选择页
                                ↓
                             OAuth 授权
                                ↓
                              回调处理
                                ↓
                           兑换 JWT Token
```

#### Token 管理
- **存储**：localStorage + uni.storage 双写
- **刷新**：401 自动使用 refresh_token 刷新
- **注入**：request.js 自动注入 Authorization 头

### 2. 请求模块

#### 统一请求封装
```javascript
// common/util/request.js

function request(options) {
	// 1. 注入 Token
	// 2. 发送请求
	// 3. 处理响应
	// 4. 401 自动刷新并重试
}
```

#### 错误处理
- **400**：显示错误提示
- **401**：刷新 Token 并重试
- **其他**：抛出错误

### 3. 权限模块

#### 权限控制
```
前端权限检查 (UI 控制)
    │
    ▼
permission(code, type)
    │
    ▼
Vuex Store (authority)
    │
    ▼
后端 API (真实验证)
```

#### 权限存储
```javascript
// Vuex Store
state: {
	authority: {
		project: { 1001: true, 1002: false },
		node: { 2001: true, 2002: true }
	}
}
```

### 4. 状态管理

#### Store 结构
```javascript
state: {
	// 用户相关
	userinfo: {},
	login: false,
	token: '',

	// 权限
	authority: {
		project: {},
		node: {}
	},

	// 项目相关
	projectData: {
		nodeList: [],
		taskListGuid: ''
	},
	projectState: {
		state: 1,
		is_archive: 0
	},

	// 配置
	modelName: '',
	conciseEnum: []
}
```

#### 数据流
```
组件 → Action → Mutation → State → Getter → 组件
```

---

## 页面架构

### 主包页面
```
pages/
├── index/           # 首页（项目列表）
└── auth/            # 认证页面
    ├── login-select # 登录方式选择
    └── callback     # OAuth 回调
```

### 子包设计
```
子包                 大小限制    用途
pagesProject        < 500KB     项目详情（核心模块）
pagesTask           < 500KB     任务管理
pagesProgress       < 500KB     进度管理
pagesSigning        < 500KB     签署管理
pagesDemand         < 500KB     需求管理
pagesVerify         < 500KB     验证管理
pagesPool           < 500KB     报表统计
```

---

## 组件架构

### 组件分类
```
components/
├── 基础组件 (ly- 前缀)
│   ├── ly-input        # 输入框
│   ├── ly-select       # 选择器
│   ├── ly-dialog       # 对话框
│   ├── ly-drawer       # 抽屉
│   └── ...
│
├── 业务组件
│   ├── task-createlists    # 创建任务弹窗
│   ├── project-enum        # 项目枚举
│   └── ...
│
└── 页面组件（pagesProject/components/）
    ├── basic-info          # 基本信息
    ├── delivery-flie       # 文件管理
    ├── flow-chart          # 节点流程图
    └── node-details        # 节点详情
```

### 组件通信
```
1. Props Down
   父组件 → 子组件 (props)

2. Events Up
   子组件 → 父组件 ($emit)

3. Refs 调用
   父组件 → 子组件方法 ($refs)

4. Vuex 共享
   跨组件状态共享
```

---

## 项目详情页架构

### 横屏布局设计
```javascript
// pages.json
{
	"path": "pagesProject/index/index",
	"style": {
		"orientation": "landscape"  // 横屏模式
	}
}
```

### 核心组件
```
项目详情页
    │
    ├── 头部 (项目信息、状态、操作)
    │
    ├── 节点流程图 (flow-chart)
    │   └── Canvas 渲染节点树
    │
    ├── 节点详情 (node-details)
    │   ├── 基本信息
    │   ├── 交付物
    │   ├── 审批记录
    │   └── ...
    │
    └── 标签页
        ├── 基本信息 (basic-info)
        ├── 文件管理 (delivery-flie)
        ├── 需求 (requirement)
        ├── 缺陷 (defect)
        ├── 操作记录 (records)
        ├── 评价 (project-evaluate)
        └── 结算 (project-settlement)
```

---

## 数据流设计

### 数据获取流程
```
页面加载
    │
    ▼
检查登录状态
    │
    ├─ 已登录 → 获取数据
    │             │
    │             ▼
    │          调用 API
    │             │
    │             ▼
    │          更新 State
    │             │
    │             ▼
    │          渲染组件
    │
    └─ 未登录 → 触发登录
                  │
                  ▼
               获取 Token
                  │
                  ▼
               获取数据
```

### 数据更新流程
```
用户操作
    │
    ▼
权限检查
    │
    ▼
调用 API
    │
    ▼
更新 State
    │
    ▼
刷新组件
```

---

## 性能优化

### 1. 分包加载
- 主包只包含首页和认证页
- 其他页面按功能分包子包
- 减少首屏加载时间

### 2. 组件懒加载
```javascript
components: {
	'heavy-component': () => import('./heavy-component.vue')
}
```

### 3. keep-alive 缓存
```vue
<keep-alive include="basicInfo">
	<component :is="currentTab" />
</keep-alive>
```

### 4. 防抖节流
```javascript
// 搜索输入
onSearchInput: _.debounce(function(value) {
	this.search(value)
}, 300)
```

---

## 环境配置

### 环境类型
```javascript
// env.js
{
	'h5-dev': 开发环境,
	'h5-test': 测试环境,
	'h5-prod': 生产环境
}
```

### 配置切换
- 通过 `ENV_TYPE` 环境变量控制
- 构建时动态修改 `manifest.json`
- 不同环境使用不同的 API 地址

---

## 安全设计

### 1. Token 安全
- 存储：localStorage + uni.storage 双写
- 传输：HTTPS + Authorization Bearer
- 刷新：自动刷新机制
- 过期：重新登录

### 2. 权限安全
- 前端：UI 控制（可绕过）
- 后端：真实验证（必须）
- 敏感操作：前后端双重验证

### 3. XSS 防护
- Vue 自动转义输出
- 避免使用 v-html
- 用户输入进行过滤

---

## 扩展性设计

### 1. OAuth 提供者扩展
```javascript
// common/auth/providers/
├── FeishuProvider.js
├── WechatProvider.js  (预留)
└── DingtalkProvider.js (预留)
```

### 2. 权限系统扩展
```javascript
// 支持多种权限类型
permission(code, 'project')  // 项目权限
permission(code, 'node')     // 节点权限
permission(code, 'demand')   // 需求权限 (预留)
```

### 3. 组件库扩展
- 基础组件：`ly-` 前缀
- 业务组件：按需添加
- 页面组件：模块化管理
