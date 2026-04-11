# PSC 评审定义模块 (reviewdefinition)

## 职责
评审定义模板的完整生命周期管理，包括基础信息配置、交付物关联、状态管理（启用/禁用）、复制功能。评审定义用于在项目节点中定义需要评审的内容和标准。

## 模块位置

### 前端视图
- **列表页**: `src/views/psc/reviewdefinition/index.vue`
- **新增页**: `src/views/psc/reviewdefinition/add.vue`
- **编辑页**: `src/views/psc/reviewdefinition/edit.vue`
- **渲染组件**: `src/views/psc/reviewdefinition/components/reviewDRender.vue`

### API 接口
- **接口文件**: `src/api/psc/reviewdefinition.js`

### 路由配置
- **路由文件**: `src/router/modules/psc.js`
- **路由路径**:
  - 列表: `/psc/reviewdefinition`
  - 新增: `/psc/reviewdefinition/add`
  - 复制: `/psc/reviewdefinition/add/:addId`
  - 编辑/查看: `/psc/reviewdefinition/edit/:id/:type`

---

## 数据模型

### 评审定义数据结构
```javascript
{
  id: string,                              // 评审定义ID
  code: string,                            // 评审项模板编码（自动生成）
  name: string,                            // 评审项模板名称
  deliverableDefinitionVersionId: string,  // 关联的交付物定义版本ID
  deliverableDefinitionName: string,       // 关联的交付物名称（用于显示）
  isActive: boolean,                       // 禁用状态（true=禁用，false=启用）
  createdAt: string,                       // 创建时间
  updatedAt: string,                       // 更新时间
  currentCreatedByNickname: string,        // 创建者昵称
  remark: string                           // 备注
}
```

### 查询参数
```javascript
{
  code: string,           // 评审项模板编码（模糊搜索）
  currentName: string,    // 评审项模板名称（模糊搜索）
  pageNum: number,        // 页码
  pageSize: number,       // 每页条数
  pageSort: string        // 排序（格式：字段:ASC/DESC，默认 ID:DESC）
}
```

---

## API 接口

### 基础 CRUD 接口

| 接口方法 | HTTP | 路径 | 说明 |
|---------|------|------|------|
| getReviewDefinitionsList | GET | /psc/review/definitions | 查询评审定义列表（分页）|
| getReviewDefinitionsSimpleList | GET | /psc/review/definitions/simple | 查询评审定义简单列表 |
| getReviewDefinitionsEnum | GET | /psc/review/definitions/enums | 查询评审定义枚举 |
| getReviewDefinitionById | GET | /psc/review/definitions/{id} | 查询评审定义详情 |
| addReviewDefinition | POST | /psc/review/definitions | 新增评审定义 |
| updateReviewDefinition | PUT | /psc/review/definitions/{id} | 修改评审定义 |
| patchReviewDefinition | PATCH | /psc/review/definitions | 修改评审定义数据状态（批量启用/禁用）|
| deleteReviewDefinition | DELETE | /psc/review/definitions | 删除评审定义（批量）|

### 接口使用示例

#### 查询列表
```javascript
import { getReviewDefinitionsList } from '@/api/psc/reviewdefinition'

const response = await getReviewDefinitionsList({
  code: 'RD001',
  currentName: '设计评审',
  pageNum: 1,
  pageSize: 10,
  pageSort: 'ID:DESC'
})

const { items, pagination } = response.data
```

#### 新增评审定义
```javascript
import { addReviewDefinition } from '@/api/psc/reviewdefinition'

const response = await addReviewDefinition({
  name: '设计阶段评审',
  deliverableDefinitionVersionId: 'version-id-123',
  remark: '用于设计阶段的交付物评审'
})

const insertId = response.data.insertId
```

#### 修改评审定义
```javascript
import { updateReviewDefinition } from '@/api/psc/reviewdefinition'

await updateReviewDefinition({
  id: 'review-id-123',
  name: '设计阶段评审（更新）',
  deliverableDefinitionVersionId: 'new-version-id',
  remark: '更新后的备注'
})
```

#### 批量启用/禁用
```javascript
import { patchReviewDefinition } from '@/api/psc/reviewdefinition'

// 启用
await patchReviewDefinition({
  ids: ['id1', 'id2', 'id3'],
  isActive: false  // false=启用，true=禁用
})

// 禁用
await patchReviewDefinition({
  ids: ['id1', 'id2', 'id3'],
  isActive: true
})
```

#### 删除评审定义
```javascript
import { deleteReviewDefinition } from '@/api/psc/reviewdefinition'

await deleteReviewDefinition(['id1', 'id2', 'id3'])
```

---

## 页面功能说明

### 列表页 (index.vue)

#### 功能特性
- **搜索功能**: 支持按编码、名称模糊搜索
- **数据表格**: 使用 LYTable 组件展示评审定义列表
- **排序功能**: 支持点击表头排序（默认按 ID 降序）
- **分页功能**: 支持分页查询

#### 操作按钮
- **新增**: 跳转到新增页面
- **复制**: 基于选中的评审定义创建副本（需要选中一条）
- **删除**: 批量删除选中的评审定义（需要选中至少一条）
- **启用**: 批量启用选中的评审定义（需要选中至少一条）
- **禁用**: 批量禁用选中的评审定义（需要选中至少一条）

#### 表格列配置
```javascript
[
  { type: "selection" },                    // 多选框
  { label: "评审项模板编码", prop: "code" },
  { label: "评审项模板名称", prop: "currentName" },
  { label: "禁用状态", prop: "isActive", dictType: 'disableFlag' },
  { label: "创建者", prop: "currentCreatedByNickname" },
  { label: "创建时间", prop: "createdAt" },
  { label: "更新时间", prop: "updatedAt" }
]
```

#### 交互特性
- 双击行或点击编码可跳转到编辑页
- 支持键盘回车搜索
- 搜索条件支持重置

### 新增页 (add.vue)

#### 功能特性
- 使用 `reviewDRender` 组件进行表单渲染
- 支持从现有评审定义复制（通过路由参数 `:addId`）
- 新增成功后自动跳转到编辑页

#### 初始数据
```javascript
{
  code: '',              // 编码（自动生成，用户不可编辑）
  name: '',              // 名称（必填）
  deliverableDefinitionVersionId: '',  // 关联交付物（可选）
  remark: ''             // 备注（可选）
}
```

#### 复制逻辑
当通过 `/psc/reviewdefinition/add/:addId` 访问时，会：
1. 根据 `addId` 获取源评审定义详情
2. 复制基础信息（不复制 ID）
3. 用户可修改后保存为新评审定义

### 编辑页 (edit.vue)

#### 路由参数
- `:id`: 评审定义 ID
- `:type`: 操作类型（`edit` 或 `view`）

#### 功能特性
- 使用 `reviewDRender` 组件进行表单渲染
- 根据 `:type` 参数控制编辑/只读模式
- 支持修改名称、交付物关联、备注
- 修改成功后显示成功提示

#### 数据加载逻辑
```javascript
// 从接口获取数据
const response = await getReviewDefinitionById(id)
const { document, versionData } = response.data

// 组装表单数据
formData.value = {
  id,
  code: document.code,
  name: document.name,
  deliverableDefinitionVersionId: versionData.deliverableDefinitionVersion.id,
  deliverableDefinitionName: versionData.deliverableDefinitionVersion.deliverableDefinitionName,
  isActive: document.isActive ?? versionData.isActive,
  remark: versionData.remark ?? document.remark
}
```

### 渲染组件 (reviewDRender.vue)

#### 组件职责
- 统一的评审定义表单渲染组件
- 处理表单验证
- 触发提交事件

#### Props
```javascript
{
  formData: {  // 表单数据
    type: Object,
    required: true
  }
}
```

#### Events
```javascript
{
  clickConfirm: (data) => void  // 点击确认按钮时触发，返回表单数据
}
```

---

## 业务规则

### 编码生成
- 编码由系统自动生成
- 用户不可手动编辑编码
- 编码格式由后端控制

### 状态管理
- `isActive: false` = 启用状态
- `isActive: true` = 禁用状态
- 禁用状态的评审定义不能被项目节点引用

### 交付物关联
- 一个评审定义可以关联一个交付物定义版本
- 关联后，该评审定义将用于评审对应的交付物
- 关联关系可以更改

### 删除限制
- 已被项目节点引用的评审定义不能删除
- 删除操作会校验引用关系

### 复制功能
- 复制时会创建全新的评审定义
- 复制后的评审定义需要重新命名
- 交付物关联会被复制

---

## 关联模块

### 依赖的模块
- **PSC 交付物定义模块** (`deliverabledefinition`): 提供可关联的交付物定义
- **SM 字典模块**: 提供禁用状态字典 (`disableFlag`)
- **SM 用户模块**: 显示创建者信息

### 被依赖的模块
- **PSC 节点定义模块** (`nodedefinition`): 在节点定义中引用评审定义
- **PSC 项目模板模块** (`projecttemplate`): 在项目模板中引用评审定义

---

## 状态说明

### 页面状态
```javascript
{
  loading: boolean,        // 列表加载状态
  showSearch: boolean,     // 是否显示搜索栏
  single: boolean,         // 是否只选中一条（用于控制复制按钮）
  multiple: boolean,       // 是否选中多条（用于控制删除、启用、禁用按钮）
  total: number,           // 总条数
  ids: array,              // 选中的ID列表
  definitionsList: array,  // 评审定义列表数据
  queryParams: object      // 查询参数
}
```

### 评审定义状态机
```
创建 → 启用
  ↓
禁用
  ↓
删除（仅未被引用时）
```

---

## 路由配置

### 路由定义
```javascript
{
  path: "reviewdefinition/add",
  meta: { title: "评审项模板-新增", hidden: true },
  component: () => import("@/views/psc/reviewdefinition/add.vue")
},
{
  path: "reviewdefinition/add/:addId",
  meta: { title: "评审项模板-新增", hidden: true },
  component: () => import("@/views/psc/reviewdefinition/add.vue")
},
{
  path: "reviewdefinition/edit/:id/:type",
  meta: {
    title: (route) => route.params.type === "edit" ? "评审项模板-修改" : "评审项模板-查看",
    hidden: true
  },
  component: () => import("@/views/psc/reviewdefinition/edit.vue")
}
```

### 页面缓存
- 列表页使用 `keepAlive` 缓存
- 编辑页不缓存

---

## 使用场景

### 场景1: 创建新的评审定义
1. 在列表页点击"新增"按钮
2. 填写评审定义名称
3. （可选）选择关联的交付物定义
4. （可选）填写备注
5. 点击确认，系统自动生成编码
6. 自动跳转到编辑页

### 场景2: 复制现有评审定义
1. 在列表页选中要复制的评审定义
2. 点击"复制"按钮
3. 修改名称和其他信息
4. 点击确认创建副本

### 场景3: 批量禁用评审定义
1. 在列表页勾选要禁用的评审定义
2. 点击"业务操作" → "禁用"
3. 确认操作

### 场景4: 查看评审定义详情
1. 在列表页双击评审定义行
2. 或点击评审定义编码
3. 跳转到编辑页（只读模式）

---

## 开发注意事项

### 数据处理
1. **禁用状态反转**: 后端返回 `isActive`（true=禁用），前端显示时需要反转
   ```javascript
   items.forEach((item) => {
     item.isActive = !item.isActive  // 前端显示用的状态
   })
   ```

2. **时间字段**: 创建时间和更新时间由后端自动维护

3. **分页参数**: 使用 `pageNum` 和 `pageSize` 进行分页

### 表单处理
1. **新增时**: 编码不需要传给后端（自动生成）
2. **编辑时**: 只传允许修改的字段（name, deliverableDefinitionVersionId, remark）
3. **复制时**: 使用新增接口，不传递 ID

### 错误处理
1. 接口错误会通过 `modal` 插件显示错误提示
2. 表单验证在 `reviewDRender` 组件中处理

### 权限控制
- 使用 `validatePerm` 函数验证权限
- 权限标识: `PSC.change_reviewdefinition`, `PSC.change_definitions`

---

## 禁止事项
- 禁止手动修改评审定义编码（编码由系统自动生成）
- 禁止删除已被项目节点引用的评审定义
- 禁止在非编辑模式下修改评审定义数据
- 禁止将评审定义的 `isActive` 状态直接绑定到开关组件（需要反转）

---

## 变更记录
### 2026-03-13
- 创建模块文档
- 记录评审定义模块的完整功能和使用说明