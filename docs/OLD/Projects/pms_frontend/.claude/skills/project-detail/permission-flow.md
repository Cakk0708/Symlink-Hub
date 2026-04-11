# PMS 项目详情模块 - 权限验证流程

## 权限系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        权限验证流程                          │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  用户操作     │ ──→ │  权限检查     │ ──→ │  允许/拒绝    │
│  User Action │     │  Permission  │     │  Allow/Deny  │
└──────────────┘     └──────────────┘     └──────────────┘
                          │
                          ├─→ 项目级权限 (1xxx)
                          │   └─→ authority.project[权限码]
                          │
                          └─→ 节点级权限 (2xxx)
                              └─→ authority.node[权限码]
```

## 权限验证入口函数

### permission() 函数定义

```javascript
// 位置: pagesProject/index/index.vue
permission(param, type = 'node') {
  const authorityMap = type === 'project'
    ? this.getAuthority.project
    : this.getAuthority.node

  return authorityMap[param] === true
}
```

### 使用方式

```vue
<!-- 1. 禁用控件 -->
<button :disabled="!permission(2001, 'project')">
  编辑负责人
</button>

<!-- 2. 条件渲染 -->
<view v-if="permission(1200, 'project')">
  管理按钮
</view>

<!-- 3. 事件拦截 -->
<button @click="handleEdit">
  <script>
  handleEdit() {
    if (!this.permission(1001, 'project')) {
      uni.showToast({ title: '无操作权限', icon: 'none' })
      return
    }
    // 执行编辑逻辑
  }
  </script>
</button>
```

## 权限码完整列表

### 项目级权限 (1xxx)

| 权限码 | 功能 | 组件 | 说明 |
|--------|------|------|------|
| 1001 | 编辑项目名称 | basic-info | 修改项目名称 |
| 1002 | 编辑项目描述 | basic-info | 修改项目描述 |
| 1003 | 编辑机型 | basic-info | 修改客户机型 |
| 1004 | 编辑优先级 | basic-info | 修改项目优先级 |
| 1005 | 编辑交付日期 | basic-info | 修改项目交付日期 |
| 1006 | 编辑关注人 | basic-info | 添加/删除关注人 |
| 1007 | 编辑项目信息 | basic-info | 通用项目信息编辑 |
| 1008 | 编辑时间线 | index | 编辑项目时间线 |
| 1100 | 需求管理权限 | requirement | 管理项目需求 |
| 1101 | 编辑需求 | requirement | 编辑具体需求 |
| 1102 | 删除需求 | requirement | 删除需求 |
| 1103 | 需求状态管理 | requirement | 修改需求状态 |
| 1104 | 需求优先级 | requirement | 修改需求优先级 |
| 1105 | 需求分配 | requirement | 分配需求负责人 |
| 1106 | 编辑下单标识 | basic-info | 修改是否下单 |
| 1200 | 编辑项目负责人 | basic-info | 修改项目负责人 |
| 1201 | 编辑项目创建者 | - | 修改项目创建者 |
| 1202 | 项目结算权限 | settlement | 项目结算操作 |
| 1300 | 需求管理权限 | requirement | 需求模块总权限 |
| 2400 | 编辑时间线 | index | 编辑项目时间线 |
| 2600 | 批量编辑节点负责人 | role 弹窗 | 批量分配节点负责人 |
| 3000 | 项目评价 | project-evaluate | 项目评价权限 |
| 3001 | 查看评价 | project-evaluate | 查看项目评价 |
| 3002 | 编辑评价 | project-evaluate | 编辑项目评价 |

### 节点级权限 (2xxx)

| 权限码 | 功能 | 组件 | 说明 |
|--------|------|------|------|
| 2001 | 编辑节点负责人 | node-details | 修改节点负责人 |
| 2002 | 添加/删除节点任务 | node-details | 管理节点任务 |
| 2003 | 编辑节点名称 | task-node | 修改节点名称 |
| 2004 | 编辑工时 | node-details | 修改标准工时 |
| 2005 | 节点评分 | node-details | 对节点进行评分 |
| 2006 | 编辑节点状态 | node-details | 修改节点状态 |
| 2007 | 编辑交付物 | node-details | 管理节点交付物 |
| 2008 | 编辑节点排期 | node-details | 修改节点排期 |
| 2009 | 添加节点 | task-node | 添加新节点 |
| 2010 | 删除节点 | task-node | 删除节点 |
| 2011 | 节点排序 | task-node | 调整节点顺序 |
| 2012 | 节点复制 | task-node | 复制节点 |
| 2013 | 编辑节点描述 | task-node | 修改节点描述 |
| 2200 | 文件管理权限 | delivery-file | 文件管理总权限 |
| 2201 | 上传文件 | delivery-file | 上传项目文件 |
| 2202 | 删除文件 | delivery-file | 删除项目文件 |
| 2203 | 编辑文件 | delivery-file | 编辑文件信息 |
| 2205 | 文件夹管理 | delivery-file | 创建/删除文件夹 |
| 2300 | 缺陷管理权限 | defect | 缺陷管理总权限 |
| 2500 | 项目结算权限 | settlement | 结算相关权限 |
| 2600 | 批量编辑节点负责人 | role 弹窗 | 批量分配负责人 |

## 权限验证场景

### 场景 1: 节点负责人编辑

```javascript
// 组件: node-details.vue
// 权限码: 2001

// 模板
<zxz-uni-data-select
  :permission="!permission(2001, 'project')"
  :disabled="nodeDetail.state.code == 2"
  v-model="nodeDetail.owners"
  @change="handleOwnerChange"
/>

// 逻辑
handleOwnerChange(newOwners) {
  // 1. 检查权限
  if (!this.permission(2001, 'project')) {
    uni.showToast({
      title: '当前用户无操作权限',
      icon: 'none'
    })
    return
  }

  // 2. 检查节点状态
  if (this.nodeDetail.state.code == 2 && !this.getUserInfo.is_superuser) {
    uni.showToast({
      title: '已完成节点不可修改',
      icon: 'none'
    })
    return
  }

  // 3. 调用 API
  this.callSetOwnerAPI(newOwners)
}
```

### 场景 2: 项目负责人修改

```javascript
// 组件: basic-info.vue
// 权限码: 1200

// 模板
<zxz-uni-data-select
  :disabled="!permission(1200, 'project')"
  :permission="!permission(1200, 'project')"
  v-model="formData.owner.value"
  @change="changeOwner"
/>

// 逻辑
async changeOwner(e) {
  // 1. 检查权限
  if (!this.permission(1200, 'project')) {
    uni.showToast({
      title: '当前用户无操作权限',
      icon: 'none'
    })
    return
  }

  // 2. 调用 API（注意使用 user_id）
  let res = await this.$util.request({
    url: 'project/list?type=10005',
    data: {
      project_id: this.projectId,
      user_id: e.id  // ✅ 使用 user_id
    },
    method: 'POST'
  })

  // 3. 更新权限
  this.setAuthority({ project: res.data.authority })
}
```

### 场景 3: 批量分配节点负责人

```javascript
// 组件: index.vue (角色弹窗)
// 权限码: 2600

// 模板
<zxz-uni-data-select
  :permission="!permission(2600, 'project')"
  :multiple="true"
  :localdata="ownerList"
  :value="mapNodeOwners(node)"
  @change="onNodeOwnersChange($event, node)"
/>

// 逻辑
onNodeOwnersChange(newOwners, node) {
  // 1. 检查权限
  if (!this.permission(2600, 'project')) {
    uni.showToast({
      title: '当前用户无批量分配权限',
      icon: 'none'
    })
    return
  }

  // 2. 检查节点状态
  if (node.state.code == 2 && !this.getUserInfo.is_superuser) {
    uni.showToast({
      title: '已完成节点不可修改负责人',
      icon: 'none'
    })
    return
  }

  // 3. 构建请求数据
  const nodeOwners = newOwners.map(owner =>
    `${node.id}:${owner.id}`
  )

  // 4. 调用 API
  this.$util.request({
    url: 'pm/node/owner/set',
    data: { node_owners: nodeOwners },
    method: 'POST',
    contentType: 'json'
  })
}
```

## 权限与状态组合验证

### 节点状态限制

某些操作需要同时满足**权限**和**节点状态**：

```javascript
// 规则: 已完成节点 (code=2) 不可编辑负责人
// 例外: 超级管理员可以编辑

if (node.state.code == 2 && !this.getUserInfo.is_superuser) {
  // 禁用编辑
  :disabled="true"

  // 显示遮罩
  <view class="owner-selector-mask"
    @click.stop="onCompletedNodeOwnerClick(node)"></view>

  // 点击提示
  onCompletedNodeOwnerClick(node) {
    uni.showToast({
      title: '该节点已完成，如需修改请联系超级管理员',
      icon: 'none'
    })
  }
}
```

### 项目状态限制

```javascript
// 规则: 变更中项目 (state=3) 禁止部分操作

if (this.getProjectState.state == 3) {
  // 禁用节点操作
  return
}

// 规则: 已归档项目 (is_archive=true) 禁止编辑

if (this.getProjectState.is_archive) {
  uni.showToast({
    title: '项目已归档，无法编辑',
    icon: 'none'
  })
  return
}
```

## 权限数据流向

```
┌─────────────────────────────────────────────────────────────┐
│                       权限数据流向                           │
└─────────────────────────────────────────────────────────────┘

API 响应
   │
   ├─ authority: { 1001: true, 1002: true, ... }
   │
   ↓
Vuex Store (store/index.js)
   │
   ├─ state.authority.project
   └─ state.authority.node
   │
   ↓
Getter (getAuthority)
   │
   ↓
permission(权限码, 类型)
   │
   ↓
组件验证
   │
   ├─ :disabled="!permission(...)"
   ├─ v-if="permission(...)"
   └─ if (permission(...)) { ... }
```

## 权限刷新机制

### 触发权限刷新的场景

1. **修改项目负责人**
```javascript
async changeOwner(e) {
  // ...
  let res = await this.$util.request({
    url: 'project/list?type=10005',
    data: { project_id: this.projectId, user_id: e.id }
  })

  // 刷新权限
  this.setAuthority({ project: res.data.authority })
}
```

2. **刷新项目详情**
```javascript
async getProjectDetail() {
  let res = await this.$util.request({
    url: 'project/list',
    data: { project_id: this.projectId }
  })

  // 更新权限
  this.setAuthority({ project: res.data.authority })
}
```

### 权限持久化

```javascript
// store/index.js
const state = {
  authority: {
    project: {},
    node: {}
  }
}

// 使用 localStorage 持久化
const STORAGE_KEY = 'pms_authority'

// 保存
saveAuthority(authority) {
  uni.setStorageSync(STORAGE_KEY, authority)
  if (typeof localStorage !== 'undefined') {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(authority))
  }
}

// 读取
getAuthority() {
  return uni.getStorageSync(STORAGE_KEY) || {}
}
```

## 权限调试技巧

### 1. 查看当前权限

```javascript
// 在浏览器控制台执行
console.log('项目权限:', this.$store.getters.getAuthority.project)
console.log('节点权限:', this.$store.getters.getAuthority.node)
```

### 2. 检查特定权限

```javascript
// 检查是否有编辑节点负责人权限
const hasPermission = this.permission(2001, 'project')
console.log('是否有 2001 权限:', hasPermission)
```

### 3. 权限测试工具

```javascript
// 在组件中添加调试方法
methods: {
  debugPermission() {
    const permissions = [
      1001, 1002, 1003, 1004, 1005, 1200,
      2001, 2002, 2004, 2005, 2008
    ]

    permissions.forEach(code => {
      const has = this.permission(code, 'project')
      console.log(`权限 ${code}: ${has ? '✓' : '✗'}`)
    })
  }
}
```

## 常见权限问题

### 问题 1: 权限检查不生效

**原因**: 权限码错误或未从 authority 中获取

**解决方案**:
```javascript
// 错误
:disabled="!hasPermission(2001)"  // ❌ 函数名错误

// 正确
:disabled="!permission(2001, 'project')"  // ✅
```

### 问题 2: 权限更新后 UI 未刷新

**原因**: 未更新 Vuex store

**解决方案**:
```javascript
// API 调用后更新权限
this.setAuthority({ project: res.data.authority })

// 或强制刷新
this.$forceUpdate()
```

### 问题 3: 超级管理员权限未生效

**原因**: 未检查 `is_superuser` 字段

**解决方案**:
```javascript
// 超级管理员跳过权限检查
if (this.getUserInfo.is_superuser) {
  return true
}

return this.permission(code, type)
```

## 权限设计最佳实践

### 1. 前端验证 + 后端验证

```javascript
// 前端: 提前禁用/提示
if (!this.permission(code, 'project')) {
  uni.showToast({ title: '无操作权限', icon: 'none' })
  return
}

// 后端: 最终验证（API 返回 403）
this.$util.request({
  url: 'api/endpoint',
  method: 'POST'
}).then(res => {
  if (res.statusCode === 403) {
    uni.showToast({ title: '服务器拒绝访问', icon: 'none' })
  }
})
```

### 2. 权限码集中管理

```javascript
// common/permission.js
export const PROJECT_PERMISSIONS = {
  EDIT_NAME: 1001,
  EDIT_DESCRIPTION: 1002,
  EDIT_OWNER: 1200,
  // ...
}

export const NODE_PERMISSIONS = {
  EDIT_OWNER: 2001,
  EDIT_TASKS: 2002,
  EDIT_HOUR: 2004,
  // ...
}

// 使用
import { PROJECT_PERMISSIONS } from '@/common/permission'

:disabled="!permission(PROJECT_PERMISSIONS.EDIT_OWNER, 'project')"
```

### 3. 权限提示统一

```javascript
// 无权限提示
showNoPermissionToast() {
  uni.showToast({
    title: '当前用户无操作权限',
    icon: 'none',
    duration: 2000
  })
}

// 使用
if (!this.permission(code, 'project')) {
  this.showNoPermissionToast()
  return
}
```
