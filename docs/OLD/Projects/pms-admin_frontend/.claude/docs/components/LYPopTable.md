# LYPopTable 弹窗表格组件

## 基本信息

- **组件名称**: LYPopTable
- **所在路径**: `src/components/LYPopTable/index.vue`
- **一句话描述**: 用于弹窗内列表的统一封装，支持选择列、树形结构、字典渲染、排序、高亮跳转及折叠展示。
- **组件类型**: 容器型 / 展示型

## 适用场景举例

- 弹窗中选择关联数据的表格（如选择客户、选择物料等）
- 树形数据展示（如部门树、分类树）
- 带分页的弹窗内列表

## Props

| 属性 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `data` | `Array` | 否 | `[]` | 表格数据 |
| `tableColumns` | `Array` | 否 | `[]` | 列配置数组（见下方列配置说明） |
| `rowKey` | `String` | 否 | `"id"` | 行数据的唯一标识字段 |
| `defaultExpandAll` | `Boolean` | 否 | `false` | 是否默认展开树形结构 |
| `treeProps` | `Object` | 否 | `{ children: 'children', hasChildren: 'hasChildren' }` | 树形结构字段映射 |
| `loading` | `Boolean` | 否 | `false` | 是否加载中 |
| `allowChildCheck` | `Boolean` | 否 | `false` | 是否允许选中树形子项（默认禁止选中带 `-` 的子 ID） |
| `tableHeight` | `String \| Number` | 否 | `undefined` | 表格高度 |
| `maxTableHeight` | `String \| Number` | 否 | `"400px"` | 最大表格高度 |
| `selectedRowKeys` | `Array` | 否 | `[]` | 已选中的行 key 列表 |
| `isExpanded` | `Boolean` | 否 | `false` | 是否展开全部行（`false` 时只显示前 5 行） |

## 列配置（tableColumns 项）

| 字段 | 类型 | 描述 |
|------|------|------|
| `type` | `String` | 列类型，如 `"selection"`、`"index"` 等 |
| `fixed` | `String \| Boolean` | 固定列 |
| `prop` | `String` | 数据字段名 |
| `label` | `String` | 列标题 |
| `width` | `Number \| String` | 列宽度 |
| `sortable` | `Boolean \| String` | 是否可排序 |
| `dictType` | `String` | 字典类型，设置后使用 `DictTag` 渲染 |
| `dict` | `Object` | 字典数据对象，需包含 `type[dictType]` |
| `isSkip` | `Boolean` | 是否可点击跳转 |
| `isHighlight` | `Boolean` | 是否高亮显示（主题色文字） |
| `selectable` | `Function` | 行是否可选 |

## Events

| 事件名 | 参数 | 描述 |
|--------|------|------|
| `handleSelectionChange` | `selection: Array` | 选择项变化时触发 |
| `rowDblclick` | `row: Object` | 行双击时触发 |
| `cellClick` | `row: Object` | 可跳转单元格被点击时触发 |
| `sortChange` | `{ field: string, order: string }` | 排序变化时触发 |
| `toRoute` | `{ row: Object, toId: Object }` | 跳转事件 |

## Slots

| 插槽名 | 描述 |
|--------|------|
| `expand` | 展开行插槽，放置在所有列之前 |

## 职责边界

- 负责表格渲染、选择、排序、高亮等通用行为
- 不负责数据获取和分页，由父组件处理
- 加载完成时自动重置水平滚动条位置

## 基本使用示例

```vue
<LYPopTable
  :data="tableData"
  :tableColumns="columns"
  :loading="loading"
  row-key="id"
  @handleSelectionChange="handleSelect"
  @rowDblclick="handleDblClick"
/>
```

```js
const columns = [
  { type: 'selection', fixed: 'left' },
  { prop: 'code', label: '编码', width: 120, isSkip: true, isHighlight: true },
  { prop: 'name', label: '名称', width: 200 },
  { prop: 'status', label: '状态', width: 100, dictType: 'projectStatus', dict }
]
```
