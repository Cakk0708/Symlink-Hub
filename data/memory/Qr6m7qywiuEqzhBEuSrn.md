# CLAUDE.md

## 项目概述
PMS（项目管理系统）前端，基于 uni-app + Vue2 的跨平台应用。

支持平台：H5 / 微信小程序 / 支付宝小程序 / App  
核心能力：项目全流程管理（节点 / 需求 / 缺陷 / 文件 / 结算 / 评价）

---

## 开始任何任务前（必须执行）

1. 阅读项目结构：
   - @.claude/docs/map.md

2. 根据任务类型，阅读对应规范：
   - 页面开发 → @.claude/rules/pages.md
   - 组件开发 → @.claude/rules/components.md
   - 接口调用 → @.claude/rules/request.md
   - 认证相关 → @.claude/rules/auth.md

---

## 开发规范（必须遵守）

通用规范（每次开发都必须遵守）：

- @.claude/rules/naming.md
- @.claude/rules/code-style.md
- @.claude/rules/permission.md

---

## 文档索引

### 架构 & 设计
- 项目地图：`.claude/docs/map.md`
- 架构设计：`.claude/docs/architecture.md`

### 业务模块
- 项目模块：`.claude/docs/modules/project.md`
- 节点系统：`.claude/docs/modules/node.md`

### 技术专题
- 认证机制：`.claude/docs/auth.md`
- 环境配置：`.claude/docs/env.md`



## 目录结构

📄 详细文件结构：[structure.md](./structure.md)

> 项目目录树与文件说明

---

## 关键模块定位

📄 模块位置索引：[modules.md](./modules.md)

> 认证流程、请求处理、项目详情页、状态管理等核心模块的定位

---

## 页面路由映射

📄 路由配置表：[routes.md](./routes.md)

> 所有页面路由与子包的对应关系

---

## 状态枚举参考

📄 枚举值说明：[enums.md](./enums.md)

> 项目状态、节点状态、节点类型等枚举值

---

## 存储键名

📄 存储规范：[storage.md](./storage.md)

> localStorage 和 uni.storage 的键名约定


---

## 关键约定（高频，必须记住）

### 1. 认证机制（核心）
- 使用：飞书静默授权 + JWT
- access_token：7天
- refresh_token：长期
- 所有请求必须走：`common/util/request.js`

---

### 2. Token 存储（重要坑点）
- H5 必须使用：**localStorage + uni.storage 双写**
- key 固定：
  - token: `betaToken`
  - user: `betaUserInfo`

---

### 3. API 调用规范
- 禁止直接使用 `uni.request`
- 必须使用统一封装：
  - `common/util/request.js`
- 自动处理：
  - token 注入
  - 401 刷新
  - 请求重试

---

### 4. 权限系统
- 使用数字权限码：`permission(code, 'project')`
- 修改任何数据前必须校验权限

---

### 5. 页面核心结构（重要）
- 首页：`pages/index/index.vue`
- 项目详情：`pagesProject/index/index.vue`（核心复杂模块）

---

### 6. 节点系统（核心业务）
- 类型：
  - 里程碑（1）
  - 主节点（2）
  - 子节点（3）
- 使用 Canvas 渲染（flow-chart）

---

### 7. 状态枚举（高频）
#### 项目状态
- 1：进行中
- 2：已完成
- 3：变更中
- 4：暂停

#### 节点状态
- 1：进行中
- 2：已完成
- 4：未开始

---

### 8. 环境机制
- 通过 `ENV_TYPE` 控制
- 构建时动态修改 `manifest.json`

---

## 禁止事项（强约束）

- ❌ 禁止绕过 request.js 发请求
- ❌ 禁止直接操作 token（必须使用 auth.js）
- ❌ 禁止忽略权限校验
- ❌ 禁止写死环境配置

---

## 快速定位（常用入口）

| 功能 | 路径 |
|------|------|
| 请求封装 | `common/util/request.js` |
| 认证模块 | `common/auth.js` |
| 飞书登录 | `common/global.js` |
| Vuex | `store/index.js` |
| 项目详情页 | `pagesProject/index/index.vue` |

---

## 说明

详细实现、流程图、代码示例已拆分至 `.claude/docs/`  
如需深入理解，请按需查阅对应文档。