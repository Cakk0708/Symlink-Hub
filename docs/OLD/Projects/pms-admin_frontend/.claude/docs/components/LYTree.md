# LYTree 可搜索树组件

## 基本信息

- **组件名称**: LYTree
- **所在路径**: `src/components/LYTree/index.vue`
- **一句话描述**: 支持输入框过滤、当前节点高亮以及节点新增/删除操作菜单的树形组件。
- **组件类型**: 交互型

## 适用场景举例

- 左侧面板的部门树/分类树导航
- 地区分类、产品分类等层级数据的筛选

## Props

| 属性 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `treeData` | `Object` | 是 | — | 树形数据 |
| `isOperate` | `Boolean` | 否 | `false` | 是否显示节点操作菜单（新增/删除） |
| `specialOperate` | `Boolean` | 否 | `false` | 特殊操作标识（预留） |
| `placeholder` | `String` | 否 | `"请输入地区分类"` | 搜索输入框占位文字 |
| `currentNodeKey` | `String \| Number` | 否 | `""` | 当前高亮节点的 key |
| `nodeKey` | `String` | 否 | `"id"` | 节点唯一标识字段 |
| `defaultProps` | `Object` | 否 | `{ children: 'children', label: 'label' }` | 树节点字段映射 |
| `isFilter` | `Boolean` | 否 | `true` | 是否显示搜索输入框 |

## Events

| 事件名 | 参数 | 描述 |
|--------|------|------|
| `clickAdd` | `node: TreeNode` | 点击"新增"菜单项时触发 |
| `clickEdit` | `node: TreeNode` | 点击"编辑"菜单项时触发（代码中已注释） |
| `clickRemove` | `node: TreeNode` | 点击"删除"菜单项时触发 |
| `nodeClick` | `node: TreeNode` | 点击树节点时触发 |

## Expose

| 方法/属性 | 描述 |
|-----------|------|
| `filterText` | `Ref<string>` 搜索关键字，可直接修改以触发过滤 |
| `clearCurrentKey()` | 清除当前高亮节点 |

## 操作菜单逻辑

- "新增"仅对 `id == 0` 的根节点显示
- "删除"对 `id !== 0` 的非根节点显示
- 操作图标默认隐藏，hover 节点时显示

## 职责边界

- 负责树形展示、搜索过滤、节点高亮和操作菜单
- 不负责数据的 CRUD 操作，通过事件抛出由父组件处理

## 基本使用示例

```vue
<LYTree
  :treeData="departmentTree"
  :is-operate="true"
  placeholder="请输入部门名称"
  node-key="id"
  @nodeClick="handleNodeClick"
  @clickAdd="handleAddDept"
  @clickRemove="handleRemoveDept"
/>
```
