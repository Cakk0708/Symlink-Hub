# SM 权限管理模块

## 模块定位

sm-perm 是系统管理 (SM) 模块的权限配置子模块，负责管理后台的三 Tab 权限配置页面。采用左侧角色树 + 右侧三 Tab 权限配置的布局，支持 BUILTIN（内置流程角色）和 CUSTOM（自定义角色）两种角色类型的权限管理。

**核心职责：**
- 权限配置页面（三 Tab 结构）
- 角色权限分配（按 Tab 分类）
- 交付物权限管理（查看/编辑联动）
- 内置角色权限约束

## 模块职责边界

### 核心功能范围

1. **权限配置页面**
   - 左侧角色树（BUILTIN / CUSTOM 分组）
   - 右侧三 Tab 权限配置（项目管理 / 交付物管理 / 后台管理）
   - 角色切换与权限加载

2. **角色权限管理**
   - BUILTIN 角色：仅允许配置 PROJECT / DELIVERABLE Tab
   - CUSTOM 角色：可配置所有 Tab
   - Tab 独立保存（不影响其他 Tab）

3. **交付物权限管理**
   - 查看权限与编辑权限联动
   - 勾选"编辑"时自动勾选"查看"
   - 取消"查看"时自动取消"编辑"

### 职责边界 (不负责)

- **不负责** 角色的增删改查（由 `sm-role` 模块负责）
- **不负责** 权限的定义（由后端 `PermissionConfig` 模型负责）
- **不负责** 权限验证逻辑（由后端 `AuthorityVerifier` 负责）

## 页面结构

### 整体布局

```
┌─────────────────────────────────────────────────────────────┐
│                      权限配置页面                              │
├──────────────┬──────────────────────────────────────────────┤
│              │                                              │
│   角色树     │           三 Tab 权限配置                      │
│              │  ┌────────────────────────────────────────┐  │
│  ┌────────┐  │  │ 项目管理 | 交付物管理 | 后台管理         │  │
│  │ 内置   │  │  ├────────────────────────────────────────┤  │
│  │ 流程   │  │  │                                        │  │
│  │ 角色   │  │  │       权限列表/表格                    │  │
│  │        │  │  │                                        │  │
│  │ • 项目 │  │  │                                        │  │
│  │   负责人│  │  │                                        │  │
│  │ • 节点 │  │  │                                        │  │
│  │   负责人│  │  │                                        │  │
│  │ • 节点 │  │  │                                        │  │
│  │   协助者│  │  │                                        │  │
│  │        │  │  │                                        │  │
│  ├────────┤  │  │                                        │  │
│  │ 自定义 │  │  │                                        │  │
│  │ 角色   │  │  │                                        │  │
│  │        │  │  │                                        │  │
│  │ • 软件组│  │  │                                        │  │
│  │ • 硬件组│  │  │                                        │  │
│  └────────┘  │  └────────────────────────────────────────┘  │
│              │                                              │
│              │  [重置]                                      │
│              │           [保存]                             │
└──────────────┴──────────────────────────────────────────────┘
```

### 左侧角色树

**数据源：** `GET /sm/roles/perm-tree`（通过 `src/api/sm/role.js` 的 `getRolePermTree`）

**结构：**
```json
{
  "builtin": [
    {"id": 1, "code": "PROJECT_OWNER", "name": "项目负责人", "roleType": "BUILTIN"},
    {"id": 2, "code": "NODE_OWNER", "name": "节点负责人", "roleType": "BUILTIN"},
    {"id": 3, "code": "NODE_ASSISTOR", "name": "节点协助者", "roleType": "BUILTIN"},
    {"id": 4, "code": "MANAGER", "name": "管理者", "roleType": "BUILTIN"}
  ],
  "custom": [
    {"id": 5, "code": "ROL00005", "name": "软件组", "roleType": "CUSTOM"},
    {"id": 6, "code": "ROL00006", "name": "硬件组", "roleType": "CUSTOM"}
  ]
}
```

**分组展示：**
- 内置流程角色（BUILTIN）
  - 项目负责人
  - 节点负责人
  - 节点协助者
  - 管理者
- 自定义角色（CUSTOM）
  - 软件组
  - 硬件组

**注意：** 系统管理员角色 (SUPER_ADMIN) 不在列表中显示。角色树数据在页面初始化时一次性加载，后续点击角色时不再调用角色详情接口，直接使用树中已有的角色信息（id、name、roleType）。

### 右侧三 Tab

所有三个 Tab 使用统一的 API 接口 `GET /sm/permissions/{category}/roles/{roleId}` 加载数据，响应中已包含 `granted` 授权状态，无需二次请求。

#### Tab 1: 项目管理

**数据源：** `GET /sm/permissions/PROJECT/roles/{roleId}`

**响应结构：**
```json
{
  "permissions": [
    {
      "categoryId": "project_management",
      "categoryName": "项目管理",
      "items": [
        { "id": 101, "name": "暂停项目", "codename": "pause_project", "granted": true },
        { "id": 102, "name": "完成项目", "codename": "complete_project", "granted": false }
      ]
    }
  ]
}
```

**展示形式：** 按分类合并行的表格（分类列 + 功能权限列），分类头带全选 checkbox

#### Tab 2: 交付物管理

**数据源：** `GET /sm/permissions/DELIVERABLE/roles/{roleId}`

**响应结构：**
```json
{
  "permissions": {
    "items": [
      {
        "defId": 1,
        "name": "BOM表",
        "version": "1.0",
        "isActive": true,
        "viewPermId": 201,
        "editPermId": 202,
        "viewGranted": false,
        "editGranted": false
      }
    ]
  }
}
```

**展示形式：** 表格（交付物名称 | 版本 | 状态 | 查看权限 | 编辑权限），查看和编辑列头带全选 checkbox

**交互规则：**
- 勾选"编辑"时自动勾选"查看"
- 取消"查看"时自动取消"编辑"
- 全选"编辑"时自动全选"查看"
- 保存时若 edit 被勾选，自动补勾 view（后端逻辑）

#### Tab 3: 后台管理

**数据源：** `GET /sm/permissions/ADMIN/roles/{roleId}`

**响应结构：**
```json
{
  "permissions": {
    "系统管理": {
      "用户管理": [
        {
          "group": "basic",
          "groupLabel": "基础操作",
          "list": [
            { "id": 301, "name": "查看用户", "codename": "view_user", "granted": false, "appLabel": "sm", "model": "user" }
          ]
        }
      ]
    }
  }
}
```

**展示形式：** 多级表头合并表格（业务模块 | 子系统模块 | 权限组名称 | 功能权限），前两列带全选 checkbox

```
┌──────────┬──────────┬──────────┬──────────┐
│ 业务模块  │ 子系统模块 │ 权限组名称  │ 功能权限  │
├──────────┼──────────┼──────────┼──────────┤
│          │          │ 基础操作   │ □ 查看   │
│ 产品管理  │ 产品列表  │          │ □ 新增   │
│ (PDM)    │          │──────────┼──────────┤
│          │          │ 高级操作   │ □ 导出   │
└──────────┴──────────┴──────────┴──────────┘
```

## 交互规则

### BUILTIN 角色约束

**约束规则：**
- **不可删除**：隐藏删除按钮
- **不可修改名称**：名称字段禁用
- **后台管理 Tab 禁用**：选中 BUILTIN 角色时，"后台管理" Tab 置灰不可点击
- **自动切换 Tab**：若当前在 ADMIN Tab 且切换到 BUILTIN 角色，自动跳转到 PROJECT Tab

**Tab 可用性：**
| 角色 | 项目管理 Tab | 交付物管理 Tab | 后台管理 Tab |
|------|-------------|---------------|-------------|
| 项目负责人 (BUILTIN) | 可操作 | 可操作 | 禁用 |
| 节点负责人 (BUILTIN) | 可操作 | 可操作 | 禁用 |
| 节点协助者 (BUILTIN) | 可操作 | 可操作 | 禁用 |
| 管理者 (BUILTIN) | 可操作 | 可操作 | 禁用 |
| 自定义角色 (CUSTOM) | 可操作 | 可操作 | 可操作 |

### CUSTOM 角色行为

**无约束：**
- 可删除（需先解除用户关联）
- 可修改所有字段
- 所有 Tab 均可操作

### 角色切换流程

```
1. 用户点击左侧角色树中的某个角色
   ↓
2. 从树节点数据中直接获取角色信息（不调用角色详情接口）
   - 记录 curRoleId = node.id
   - 记录 isBuiltinRole = (node.roleType === 'BUILTIN')
   ↓
3. 判断角色类型
   - BUILTIN: 禁用"后台管理" Tab
     若当前 activeTab 为 ADMIN，自动切换为 PROJECT
   - CUSTOM: 所有 Tab 可用
   ↓
4. 调用统一 API 加载当前 Tab 的权限（含 granted 状态）
   - GET /sm/permissions/{category}/roles/{roleId}
   - category 为当前 activeTab 的值（PROJECT / DELIVERABLE / ADMIN）
   ↓
5. 响应中已包含 granted 状态，直接回显勾选状态
```

### Tab 切换流程

```
1. 用户点击不同的 Tab
   ↓
2. 切换到新 Tab (activeTab 更新)
   ↓
3. 调用统一 API 加载新 Tab 的权限（含 granted 状态）
   - GET /sm/permissions/{category}/roles/{roleId}
   - 使用当前 curRoleId 和新 Tab 的 category
   ↓
4. 将响应数据渲染到对应 Tab 的表格中
   - PROJECT: 扁平化为 [category, id, name, codename, checked] 行数组
   - DELIVERABLE: 映射 viewGranted/editGranted 到 viewChecked/editChecked
   - ADMIN: 嵌套结构扁平化为 [appName, modelName, group, name, id, checked] 行数组
   ↓
5. 同步全选 checkbox 状态（分类全选 / 交付物全选 / 业务模块全选）
```

### 保存流程

```
1. 用户点击"保存"按钮
   ↓
2. 收集当前 Tab 的所有勾选权限 ID
   - PROJECT: 从 projectPermRows 中筛选 checked=true 的 id
   - DELIVERABLE: 分别收集 viewChecked 的 viewPermId 和 editChecked 的 editPermId
   - ADMIN: 从 adminPermRows 中筛选 checked=true 的 id
   ↓
3. 调用统一 API 保存
   - PUT /sm/permissions/{category}/roles/{roleId}
   - 请求体: { permission: [101, 102, 201, 202] }
   ↓
4. 后端处理
   - 仅移除/添加指定 Tab 下的权限
   - 不影响其他 Tab 已有权限
   - 交付物 Tab 特殊逻辑：edit 自动补勾 view
   ↓
5. 显示保存成功提示
```

### 重置流程

```
1. 用户点击"重置"按钮
   ↓
2. 前端清除当前 Tab 页面上的所有 checkbox 勾选状态
   - PROJECT: 所有行 checked = false
   - DELIVERABLE: 所有行 viewChecked = false, editChecked = false + 全选状态归零
   - ADMIN: 所有行 checked = false + 全选/半选状态归零
   ↓
3. 不调用后端接口
   ↓
4. 用户可以重新勾选权限
   ↓
5. 点击"保存"时提交空数组或新勾选的权限
```

**注意：** 重置是前端行为，仅清除页面勾选状态，不实际清空角色权限。

## API 调用

### 获取角色树

```javascript
// src/api/sm/role.js
export function getRolePermTree() {
  return request({ url: 'sm/roles/perm-tree', method: 'get' })
}
```

### 获取角色权限（统一接口，三个 Tab 共用）

```javascript
// src/api/sm/perm.js
export function getRolePermissions(category, roleId) {
  return request({
    url: `sm/permissions/${category}/roles/${roleId}`,
    method: 'get',
  })
}
// category: 'PROJECT' | 'DELIVERABLE' | 'ADMIN'
// 响应中已包含 granted 状态，无需二次请求
```

### 更新角色权限（统一接口，三个 Tab 共用）

```javascript
// src/api/sm/perm.js
export function updateRolePermissions(category, roleId, data) {
  return request({
    url: `sm/permissions/${category}/roles/${roleId}`,
    method: 'put',
    data,  // { permission: number[] }
  })
}
```

### 获取权限枚举

```javascript
// src/api/sm/perm.js
export function getPermEnums() {
  return request({
    url: 'sm/permissions/enums',
    method: 'get',
  })
}
```

## 技术实现

### 角色树渲染

```vue
<template>
  <el-tree
    :data="treeData"
    node-key="id"
    default-expand-all
    :filter-node-method="filterNode"
    :expand-on-click-node="false"
    :highlight-current="true"
    :props="{ children: 'children', label: 'name' }"
    @node-click="handleNodeClick"
  >
    <template #default="{ node, data }">
      <span v-if="data.isGroup" class="tree-group-header">
        {{ data.name }}
        <el-tag size="small" type="info">{{ (data.children || []).length }}</el-tag>
      </span>
      <span v-else>{{ data.name }}</span>
    </template>
  </el-tree>
</template>

<script setup>
import { getRolePermTree } from '@/api/sm/role'

const treeData = ref([])

const initRoleTree = async () => {
  const res = await getRolePermTree()
  const data = res.data
  // Build tree with two group nodes
  treeData.value = [
    {
      id: 'builtin_group',
      name: '内置流程角色',
      isGroup: true,
      children: (data.builtin || []).map(role => ({
        ...role,
        roleType: 'BUILTIN',
      })),
    },
    {
      id: 'custom_group',
      name: '自定义角色',
      isGroup: true,
      children: (data.custom || []).map(role => ({
        ...role,
        roleType: 'CUSTOM',
      })),
    },
  ]
}

const handleNodeClick = (node) => {
  if (node.isGroup) return // Ignore group header clicks
  curRoleId.value = node.id
  isBuiltinRole.value = node.roleType === 'BUILTIN'
  // Auto-switch tab if needed
  if (isBuiltinRole.value && activeTab.value === 'ADMIN') {
    activeTab.value = 'PROJECT'
  }
  loadRoleData()
}

onMounted(initRoleTree)
</script>
```

### Tab 渲染与权限加载

```vue
<template>
  <el-tabs v-model="activeTab" @tab-click="handleTabClick">
    <el-tab-pane label="项目管理" name="PROJECT">
      <!-- Project perm table -->
    </el-tab-pane>
    <el-tab-pane label="交付物管理" name="DELIVERABLE">
      <!-- Deliverable perm table -->
    </el-tab-pane>
    <el-tab-pane
      label="后台管理"
      name="ADMIN"
      :disabled="isBuiltinRole"
    >
      <!-- Admin perm table -->
    </el-tab-pane>
  </el-tabs>
</template>

<script setup>
import { getRolePermissions, updateRolePermissions } from '@/api/sm/perm'

const activeTab = ref('PROJECT')

const handleTabClick = (tab) => {
  loadTabData(tab.paneName)
}

const loadTabData = async (tab) => {
  loading.value = true
  try {
    switch (tab) {
      case 'PROJECT': await loadProjectData(); break
      case 'DELIVERABLE': await loadDeliverableData(); break
      case 'ADMIN': await loadAdminData(); break
    }
  } finally {
    loading.value = false
  }
}
</script>
```

### 各 Tab 数据加载（统一使用 getRolePermissions）

```javascript
// PROJECT Tab
const loadProjectData = async () => {
  const res = await getRolePermissions('PROJECT', curRoleId.value)
  permDataCache.PROJECT = res.data.permissions
  renderProjectRows()
}

// DELIVERABLE Tab
const loadDeliverableData = async () => {
  const res = await getRolePermissions('DELIVERABLE', curRoleId.value)
  permDataCache.DELIVERABLE = res.data.permissions.items || []
  renderDeliverableList()
}

// ADMIN Tab
const loadAdminData = async () => {
  const res = await getRolePermissions('ADMIN', curRoleId.value)
  permDataCache.ADMIN = res.data.permissions
  renderAdminRows()
}
```

### 交付物权限联动

```vue
<template>
  <el-table :data="deliverableList">
    <el-table-column prop="name" label="交付物名称" />
    <el-table-column prop="version" label="版本" />
    <el-table-column prop="isActive" label="状态">
      <template #default="{ row }">
        <el-tag :type="row.isActive ? 'success' : 'info'" size="small">
          {{ row.isActive ? '启用' : '停用' }}
        </el-tag>
      </template>
    </el-table-column>
    <el-table-column label="查看">
      <template #default="{ row }">
        <el-checkbox v-model="row.viewChecked" @change="onDeliverableViewChange(row)" />
      </template>
    </el-table-column>
    <el-table-column label="编辑">
      <template #default="{ row }">
        <el-checkbox v-model="row.editChecked" @change="onDeliverableEditChange(row)" />
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup>
const renderDeliverableList = () => {
  deliverableList.value = permDataCache.DELIVERABLE.map(item => ({
    ...item,
    viewChecked: item.viewGranted,  // granted -> checked
    editChecked: item.editGranted,
  }))
}

const onDeliverableEditChange = (row) => {
  if (row.editChecked) {
    row.viewChecked = true  // Auto-check view when edit is checked
  }
  syncDeliverableCheckedState()
}

const onDeliverableViewChange = (row) => {
  // No auto-uncheck of edit here; edit remains independent until save
  syncDeliverableCheckedState()
}
</script>
```

### 保存逻辑

```vue
<script setup>
import { getRolePermissions, updateRolePermissions } from '@/api/sm/perm'

const handleSave = async () => {
  if (!curRoleId.value) {
    modal.msgWarning('请先选择角色')
    return
  }

  saveLoading.value = true
  try {
    const tab = activeTab.value
    let permIds

    if (tab === 'DELIVERABLE') {
      // Collect view and edit perm IDs separately
      permIds = []
      for (const item of deliverableList.value) {
        if (item.viewChecked) permIds.push(item.viewPermId)
        if (item.editChecked) permIds.push(item.editPermId)
      }
    } else {
      permIds = [...checkedState[tab]]
    }

    await updateRolePermissions(tab, curRoleId.value, {
      permission: permIds,
    })
    modal.msgSuccess('保存成功')
  } finally {
    saveLoading.value = false
  }
}
</script>
```

### 重置逻辑

```vue
<script setup>
const handleReset = () => {
  switch (activeTab.value) {
    case 'PROJECT':
      projectPermRows.value.forEach(row => { row.checked = false })
      checkedState.PROJECT = []
      break
    case 'DELIVERABLE':
      deliverableList.value.forEach(item => {
        item.viewChecked = false
        item.editChecked = false
      })
      checkedState.DELIVERABLE = []
      // Reset select-all states
      deliverableSelectAll.view.checked = false
      deliverableSelectAll.view.indeterminate = false
      deliverableSelectAll.edit.checked = false
      deliverableSelectAll.edit.indeterminate = false
      break
    case 'ADMIN':
      adminPermRows.value.forEach(row => { row.checked = false })
      checkedState.ADMIN = []
      // Reset all check-all / indeterminate states
      Object.keys(allChecked.admin.business).forEach(k => { allChecked.admin.business[k] = false })
      Object.keys(allChecked.admin.son).forEach(k => { allChecked.admin.son[k] = false })
      Object.keys(isIndeterminate.admin.business).forEach(k => { isIndeterminate.admin.business[k] = false })
      Object.keys(isIndeterminate.admin.son).forEach(k => { isIndeterminate.admin.son[k] = false })
      break
  }
}
</script>
```

## 关键文件索引

| 文件路径 | 说明 |
|---------|------|
| `src/views/sm/perm/index.vue` | 权限配置主页面（角色树 + 三 Tab + 保存/重置逻辑） |
| `src/api/sm/perm.js` | 权限相关 API（getPermEnums, getRolePermissions, updateRolePermissions） |
| `src/api/sm/role.js` | 角色相关 API（getRolePermTree） |

## 与其他模块关系

### 依赖模块

| 模块 | 关系类型 | 说明 |
|------|----------|------|
| `sm-role` | 数据源 | 角色树数据（getRolePermTree），仅在页面初始化时调用一次 |
| 后端 `SM.permission` | API | 权限配置数据（getRolePermissions / updateRolePermissions） |

### 被依赖模块

| 模块 | 关系类型 | 说明 |
|------|----------|------|
| `sm-role` | 跳转 | 角色管理页面的"配置权限"入口 |

## 开发注意事项

1. **角色类型判断**：使用 `roleType === 'BUILTIN'` 判断是否为内置角色，数据来源于角色树节点而非角色详情接口
2. **统一 API**：三个 Tab 均使用 `getRolePermissions(category, roleId)` 加载数据，使用 `updateRolePermissions(category, roleId, data)` 保存，区别仅在于 category 参数
3. **Tab 禁用逻辑**：BUILTIN 角色的"后台管理" Tab 必须禁用，切换到 BUILTIN 角色时若当前在 ADMIN Tab 需自动跳转
4. **权限独立保存**：每次保存只影响当前 Tab，不影响其他 Tab
5. **交付物权限联动**：编辑自动勾选查看，取消查看自动取消编辑
6. **重置仅前端**：重置只清除页面勾选状态，不调用后端接口
7. **不导入 getRole**：权限配置页面不再调用 `GET /sm/roles/{roleId}`，角色信息从初始化加载的角色树数据中获取

## 扩展设计策略

### 1. 权限搜索（未来扩展）

```javascript
// 支持按权限名称搜索
const searchValue = ref('')

const filteredPermissions = computed(() => {
  if (!searchValue.value) return permissions.value
  return permissions.value.filter(p =>
    p.name.includes(searchValue.value)
  )
})
```

### 2. 批量操作（未来扩展）

```javascript
// 全选/取消全选
const handleSelectAll = (checked) => {
  permissions.value.forEach(p => p.checked = checked)
}

// 批量授权（按分类）
const handleBatchGrant = (category) => {
  const permsInCategory = permissions.value.filter(
    p => p.category === category
  )
  permsInCategory.forEach(p => p.checked = true)
}
```

### 3. 权限变更历史（未来扩展）

```javascript
// 记录权限变更历史
const permissionHistory = ref([])

const logPermissionChange = (roleId, tabType, oldPerms, newPerms) => {
  permissionHistory.value.push({
    roleId,
    tabType,
    oldPerms,
    newPerms,
    timestamp: new Date(),
    operator: currentUser.value
  })
}
```

## 演进方向 (Future Evolution)

### 短期优化

1. **性能优化**
   - 权限列表懒加载
   - 虚拟滚动（大数据量）

2. **交互优化**
   - 权限搜索功能
   - 批量全选/取消

### 中期规划

1. **功能增强**
   - 权限模板（快速分配常用权限组合）
   - 权限变更历史记录
   - 权限对比（不同角色权限对比）

2. **用户体验**
   - 权限说明提示（Tooltip）
   - 权限依赖关系提示

### 长期愿景

1. **智能推荐**
   - 基于角色推荐权限
   - 基于行为模式推荐权限

2. **权限分析**
   - 权限使用率分析
   - 冗余权限检测
   - 权限安全审计

## 模块特有名词解析

| 名词 | 说明 | 关联 |
|------|------|------|
| **BUILTIN 角色** | 系统预设的流程角色（项目负责人、节点负责人等） | 不可删除、不可修改 ADMIN Tab |
| **CUSTOM 角色** | 用户创建的自定义角色 | 可删除、可修改所有 Tab |
| **三 Tab** | 项目管理、交付物管理、后台管理三个权限配置页签 | 权限按 Tab 分类，使用统一 API |
| **交付物权限联动** | 编辑权限自动勾选查看权限 | 交付物 Tab 特殊交互 |
| **重置（前端）** | 清除当前 Tab 页面上的所有 checkbox 勾选状态 | 不调用后端接口 |
| **统一权限 API** | `GET /sm/permissions/{category}/roles/{roleId}` | 三个 Tab 共用，响应含 granted 状态 |

## 触发场景

当用户遇到以下情况时，应激活本技能：

1. **权限配置相关**
   - "如何配置角色权限"
   - "BUILTIN 角色为什么不能修改后台管理"
   - "交付物权限如何联动"

2. **页面交互相关**
   - "重置按钮为什么不生效"
   - "保存是否影响其他 Tab"
   - "如何批量分配权限"

3. **API 调用相关**
   - "权限列表接口怎么调"
   - "角色树接口返回什么数据"
   - "保存权限的接口参数是什么"

## 常见问题

### Q: 为什么 BUILTIN 角色的"后台管理" Tab 被禁用？
A: 内置流程角色的后台管理权限由系统预设，不允许修改，只能配置项目管理 Tab 和交付物管理 Tab 的权限。

### Q: 重置按钮是否会删除角色的权限？
A: 不会。重置只是清除当前 Tab 页面上的勾选状态，不调用后端接口。只有点击"保存"按钮时才会实际修改权限。

### Q: 保存时是否会影响其他 Tab 的权限？
A: 不会。保存操作仅影响当前 Tab，其他 Tab 的权限不受影响。

### Q: 交付物 Tab 的编辑权限为什么自动勾选查看权限？
A: 这是业务逻辑要求，拥有编辑权限必然需要查看权限。前端交互和后端保存都会自动补勾查看权限。

### Q: 如何添加新的权限分类？
A: 需要在后端 `ProjectPermission` 模型中添加新的 `category`，然后运行 `python manage.py init_pm_permissions`。

### Q: 为什么点击角色时不再调用 getRole 接口？
A: 经过重构，角色树在页面初始化时一次性加载，已包含角色的 id、name、roleType 等信息。点击角色时直接使用树节点数据，无需额外请求角色详情，减少了不必要的网络请求。

## 相关文档

- **后端 API 文档**: `backend/.claude/docs/api/sm-permission.md`
- **后端模块文档**: `backend/.claude/docs/modules/sm-perm.md`
- **角色模块文档**: `modules/sm-role.md`
- **PM Authority 文档**: `backend/.claude/docs/modules/pm-authority.md`

## 更新日志

- 2025-04-06：API 调用重构
  - 移除角色切换时的 `GET /sm/roles/{roleId}` 调用，改为使用角色树已有数据
  - 三个 Tab 统一使用 `GET /sm/permissions/{category}/roles/{roleId}` 加载权限（含 granted 状态）
  - 保存统一使用 `PUT /sm/permissions/{category}/roles/{roleId}`，请求体为 `{ permission: number[] }`
  - API 文件精简为 `getPermEnums`、`getRolePermissions`、`updateRolePermissions` 三个函数
  - 移除 `rolePermissions` reactive 变量，权限勾选状态直接映射到表格行数据
  - 移除 `getPermListByTab`、`getDeliverablePerms`、`updateRolePermByTab` 等旧 API 函数
- 2025-04-03：重大更新
  - 左侧角色树重构（BUILTIN / CUSTOM 分组）
  - 右侧三 Tab 结构（项目管理 / 交付物管理 / 后台管理）
  - BUILTIN 角色约束（不可修改 ADMIN Tab）
  - 交付物权限联动（编辑自动勾选查看）
  - 重置功能（前端行为）
  - Tab 独立保存（不影响其他 Tab）
- 2024-XX-XX：初始版本，单一权限配置表格
