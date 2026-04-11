---
name: project-detail
description: PMS 项目详情模块专家，负责项目详情页面的横屏布局、节点流程图、权限验证、状态管理和标签页组件的架构理解。当用户提到"项目详情"、"pagesProject"、"节点流程图"、"项目权限"、"节点负责人"、"基本信息"、"node-details"、"flow-chart"、"项目状态"或相关术语时激活此技能。
---

# PMS 项目详情模块架构

## 模块定位

项目详情模块是 PMS（项目管理系统）的核心页面，采用**横屏布局**设计，提供项目全生命周期的管理功能。

### 路由与文件位置
- **路由**: `pagesProject/index/index.vue`
- **布局方向**: 横屏 (landscape)
- **环境**: H5 (localhost:8001) 为主开发环境

## 模块职责边界

### 核心职责
| 职责 | 说明 | 对应组件 |
|------|------|----------|
| 项目概览展示 | 项目名称、状态、时间线、角色管理 | `main-header` |
| 节点可视化 | Canvas 绘制的节点流程图 | `flow-chart` |
| 节点详情编辑 | 节点负责人、排期、工时管理 | `node-details` |
| 项目信息管理 | 基本信息、文件管理、结算等 | 标签页组件 |
| 权限控制 | 基于权限码的功能访问控制 | `permission()` |

### 边界界定
- **不负责**: 项目列表展示（由 `pages/index` 负责）
- **不负责**: 需求详情页（由 `pagesDemand` 负责）
- **不负责**: 独立的订单签署（由 `pagesSigning` 负责）

## 核心数据模型

### 项目状态 (state)
| 状态码 | 值 | 颜色 | 说明 |
|--------|-----|------|------|
| 1 | 进行中 | 蓝色 `rgba(54, 115, 232, 0.2)` | 项目正在进行 |
| 2 | 已完成 | 绿色 `rgba(61, 188, 47, 0.2)` | 项目已完成 |
| 3 | 变更中 | 紫色 `rgba(121, 58, 255, 0.2)` | 项目正在变更 |
| 4 | 已暂停 | 灰色 `rgba(110, 118, 118, 0.2)` | 项目已暂停 |
| 5 | 已归档 | 黄色 `rgba(245, 180, 0, 0.2)` | 项目已归档 |

### 节点状态 (code)
| 状态码 | 值 | 颜色 | 说明 |
|--------|-----|------|------|
| 0 | 已完成 | 绿色 `#68b948` | 节点已完成 |
| 1 | 进行中 | 蓝色 `#3A75FF` | 节点正在进行 |
| 4 | 未开始 | 灰色 | 节点未开始 |

### 节点类型 (category)
| 类型值 | 名称 | 图标 | 说明 |
|--------|------|------|------|
| 1 | 里程碑 | `&#xe676;` | 项目关键节点 |
| 2 | 主节点 | `&#xe677;` | 项目主要阶段 |
| 3 | 子节点 | `&#xe678;` | 主节点下的具体任务 |

### 接口数据结构
```javascript
{
  "id": 21,
  "name": "项目名称",
  "state": 1,  // 项目状态
  "owner": {   // 项目负责人（注意：使用 id 字段而非 open_id）
    "id": 1,
    "nickname": "范凯强",
    "avatar": "https://..."
  },
  "creator": { // 创建者
    "id": 1,
    "nickname": "范凯强",
    "avatar": "https://..."
  },
  "nodes": {
    "current": { "id": 33, "name": "节点2" },
    "list": [ /* 节点列表 */ ]
  },
  "authority": { /* 权限码映射 */ }
}
```

## 权限验证流程

### 权限码系统
模块使用**数字权限码**进行细粒度权限控制：

#### 项目级权限 (前缀 1xxx)
| 权限码 | 功能 | 位置 |
|--------|------|------|
| 1001 | 编辑项目名称 | basic-info |
| 1002 | 编辑项目描述 | basic-info |
| 1003 | 编辑机型 | basic-info |
| 1004 | 编辑优先级 | basic-info |
| 1005 | 编辑交付日期 | basic-info |
| 1106 | 编辑下单标识 | basic-info |
| 1200 | 编辑项目负责人 | basic-info |
| 2400 | 编辑时间线 | index |
| 2600 | 批量编辑节点负责人 | role 弹窗 |

#### 节点级权限 (前缀 2xxx)
| 权限码 | 功能 | 位置 |
|--------|------|------|
| 2001 | 编辑节点负责人 | node-details |
| 2002 | 添加/删除节点任务 | node-details |
| 2004 | 编辑工时 | node-details |
| 2005 | 节点评分 | node-details |
| 2008 | 编辑节点排期 | node-details |

### 权限验证函数
```javascript
// 使用方式
permission(权限码, 'project')

// 示例
:disabled="!permission(2001, 'project')"  // 节点负责人编辑权限
@click="clickVerifyPerm(1005, 'project')" // 交付日期编辑权限
```

### 权限存储位置
- **Vuex Store**: `store/index.js` → `authority.project` 和 `authority.node`
- **环境持久化**: 使用 `env.js` 中配置的 key 存储到 localStorage

## 认证与授权区别说明

### 认证 (Authentication)
- **方式**: 飞书静默授权 (`tt.requestAuthCode`) + JWT Token
- **Token 类型**: `{ access_token, refresh_token }`
- **管理模块**: `common/auth.js`
- **有效期**: access_token 7天，refresh_token 长期有效
- **刷新机制**: 401 自动刷新，失败则重新飞书登录

### 授权 (Authorization)
- **方式**: 基于权限码的 RBAC
- **权限来源**: 接口返回的 `authority` 对象
- **验证位置**: 各组件的 `permission()` 函数
- **粒度**: 项目级 (1xxx) 和节点级 (2xxx)

### 关键区别
| 维度 | 认证 | 授权 |
|------|------|------|
| 目的 | 验证用户身份 | 验证操作权限 |
| 数据来源 | 飞书 OAuth + JWT | 后端权限系统 |
| 检查时机 | 每次请求 | 每次操作 |
| 失败处理 | 重新登录 | 禁用操作/提示无权限 |

## 与其他模块关系

### 依赖关系
```
pagesProject (项目详情)
    ├── 依赖 common/auth.js (认证)
    ├── 依赖 store/index.js (状态管理)
    ├── 使用 components/ly-* (自定义组件)
    └── 使用 uni_modules/* (第三方组件)
```

### 数据流向
```
API 接口 → index.vue (父组件)
    ├── props 传递 → flow-chart (节点流程图)
    ├── props 传递 → node-details (节点详情)
    ├── props 传递 → basic-info (基本信息)
    ├── props 传递 → task-node (节点管理)
    └── Vuex 同步 → store/index.js
```

### 事件流向
```
子组件操作 → $emit → index.vue
    ├── 调用 API → 更新数据
    ├── 更新 Vuex → 同步其他组件
    └── uni.$emit → 跨组件通信
```

## 常见业务场景

### 场景 1: 编辑节点负责人
```javascript
// 1. 用户在 node-details 组件选择负责人
// 2. 触发 @ownerChange 事件
// 3. 调用 API: POST /pm/node/owner/set
// 4. 更新 Vuex store
// 5. 同步更新 flow-chart 显示
```

### 场景 2: 修改项目状态
```javascript
// 1. 用户点击"暂停/继续"按钮
// 2. 检查权限
// 3. 弹出原因填写对话框
// 4. 调用 API: PATCH /project/state
// 5. 更新项目状态显示
```

### 场景 3: 批量分配节点负责人
```javascript
// 1. 用户点击"角色"按钮
// 2. 打开角色弹窗 (refRolePop)
// 3. 按项目角色分组显示节点
// 4. 用户选择负责人
// 5. 调用 API: POST /pm/node/owner/set
// 6. 刷新节点列表
```

## 技术实现建议

### 前端 (Vue 2.0 + uni-app)

#### 组件通信
```javascript
// 父传子: props
<node-details :projectId="projectId" :nodeTree="getNodeListData" />

// 子传父: $emit
this.$emit('refreshEvent')

// 跨组件: uni.$emit
uni.$emit('changeOwner', { nodeId, ownerId })

// Vuex: mapMutations
...mapMutations(['setOwner', 'setProjectState'])
```

#### 状态管理
```javascript
// store/index.js 核心状态
state: {
  userinfo: {},           // 用户信息
  projectData: {
    nodeList: [],         // 节点列表
    taskListGuid: ''      // 任务清单 GUID
  },
  authority: {
    project: {},          // 项目级权限
    node: {}              // 节点级权限
  },
  projectState: {
    state: 1,             // 项目状态
    is_archive: false     // 归档状态
  }
}
```

#### Canvas 流程图优化
- 使用 `requestAnimationFrame` 优化渲染
- 节点坐标计算考虑 `pageScrollTop`
- 支持节点点击交互和状态颜色更新

### 后端 (Django)

#### API 设计建议
```python
# 项目详情接口
GET /api/projects/{project_id}/
Response: {
    "id": int,
    "name": str,
    "state": int,
    "owner": {"id": int, "nickname": str, "avatar": str},
    "creator": {"id": int, "nickname": str, "avatar": str},
    "nodes": {...},
    "authority": {int: bool, ...}  # 权限码映射
}

# 设置节点负责人接口
POST /api/pm/node/owner/set
Request: {
    "node_owners": ["{node_id}:{user_id}", ...]
}
Response: {
    "data": [{  # 返回完整的 owners 数组
        "id": int,
        "user": {"id": int, "nickname": str, "avatar": str},
        "is_major": bool,
        "standard_time": int
    }]
}
```

#### 权限验证中间件
```python
# utils/permission.py
def check_project_permission(user, project_id, permission_code):
    """检查项目级权限"""
    # 1. 获取用户角色
    # 2. 查询角色权限配置
    # 3. 返回布尔值
    pass

def check_node_permission(user, node_id, permission_code):
    """检查节点级权限"""
    # 1. 获取节点所属项目
    # 2. 检查用户是否为节点负责人
    # 3. 返回布尔值
    pass
```

## 扩展设计策略

### 新增标签页
1. 在 `pagesProject/components/` 下创建新组件
2. 在 `index.vue` 的 `project.tabs` 数组中添加配置
3. 使用 `<component :is="project.curCom">` 动态加载

### 新增节点状态
1. 更新 `CLAUDE.md` 中的状态码文档
2. 在 `flow-chart.vue` 中添加对应颜色配置
3. 确保后端返回正确的状态码

### 新增权限码
1. 在 `CLAUDE.md` 中登记权限码含义
2. 后端在 `authority` 对象中返回该权限
3. 前端使用 `permission(新权限码, 'project')` 验证

## 演进历史 (Evolution History)

### 2026-03-11 - 节点状态管理接口重构
🆕 **节点状态操作接口变更**

节点完成和回滚接口路径重构，采用 RESTful 风格：

| 操作 | 旧接口 | 新接口 | 说明 |
|------|--------|--------|------|
| 完成节点 | `PATCH /pm/node/{id}` | `PATCH /pm/nodes/{id}/state/complete` | 将节点状态设为已完成 |
| 回滚节点 | `PATCH /pm/node/{id}` | `PATCH /pm/nodes/{id}/state/rollback` | 将节点状态回滚 |

**影响文件**：
- `pagesProject/components/node-details/node-details.vue`
  - `eventCompleteNote()` 函数 (line ~4831)
  - `confirmReasonDialog()` 函数 (line ~6276)

**旧接口调用** (已废弃)：
```javascript
// 完成节点
await this.$util.request({
    url: 'pm/node/' + this.nodeDetail.id,
    data: { state: 2 },
    method: 'PATCH'
})

// 回滚节点
await this.$util.request({
    url: 'pm/node/' + this.nodeDetail.id,
    data: { state: 1, reason },
    method: 'PATCH'
})
```

**新接口调用** (当前)：
```javascript
// 完成节点
await this.$util.request({
    url: `pm/nodes/${this.nodeDetail.id}/state/complete`,
    data: { state: 2 },
    method: 'PATCH'
})

// 回滚节点
await this.$util.request({
    url: `pm/nodes/${this.nodeDetail.id}/state/rollback`,
    data: { state: 1, reason },
    method: 'PATCH'
})
```

⚠️ **注意事项**：
- 接口路径从单数 `pm/node` 改为复数 `pm/nodes`
- 状态操作使用 `/state/{action}` 后缀模式
- 变更中的节点回滚仍使用 `PATCH /pm/node/{id}/` (eventChangeNodeRecovery 函数)

---

## 演进方向 (Future Evolution)

### 短期优化
- [ ] 节点流程图支持缩放和平移
- [ ] 节点负责人选择支持搜索
- [ ] 批量操作支持全选/反选

### 中期规划
- [ ] 实时协作（WebSocket 推送节点变更）
- [ ] 节点依赖关系可视化
- [ ] 移动端适配（当前主要为 H5 横屏）

### 长期愿景
- [ ] AI 辅助节点排期推荐
- [ ] 项目风险自动预警
- [ ] 跨项目资源负载分析

## 特有名词索引

当用户提到以下词汇时，应关联到此技能：

| 名词 | 说明 |
|------|------|
| **横屏布局** | 项目详情页采用横屏设计 |
| **节点流程图** | Canvas 绘制的节点可视化 |
| **飞书静默授权** | `tt.requestAuthCode` 认证方式 |
| **权限码** | 4位数字的功能权限标识 |
| **里程碑** | category=1 的关键节点 |
| **主节点** | category=2 的主要阶段 |
| **子节点** | category=3 的具体任务 |
| **项目状态机** | state: 1/2/3/4/5 的状态流转 |
| **节点状态机** | code: 0/1/4 的状态流转 |
| **项目详情页** | `pagesProject/index/index.vue` |

---

**参考文档**:
- `models.md` - 详细数据模型定义
- `permission-flow.md` - 权限验证流程图
- `evolution.md` - 演进路线图
