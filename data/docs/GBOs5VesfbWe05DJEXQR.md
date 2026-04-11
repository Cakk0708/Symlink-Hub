# LYTable 通用表格组件

## 基本信息

- **组件名称**: LYTable
- **所在路径**: `src/components/LYTable/index.vue`
- **一句话描述**: 在 `el-table` 基础上封装列配置驱动渲染，内置字典展示、头像列、日志/消息内容展开等常用模式。
- **组件类型**: 容器型 / 展示型

## 适用场景举例

- 项目列表、客户列表、员工列表等标准业务列表页
- 日志列表（支持批量操作内容展开）
- 消息列表（支持未读状态标识）

## Props

| 属性 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `data` | `Array` | 否 | `[]` | 表格数据 |
| `tableColumns` | `Array` | 否 | `[]` | 列配置数组（见下方列配置说明） |
| `rowKey` | `String` | 否 | `"id"` | 行数据的唯一标识字段 |
| `defaultExpandAll` | `Boolean` | 否 | `false` | 是否默认展开树形结构 |
| `treeProps` | `Object` | 否 | `{ children: 'children', hasChildren: 'hasChildren' }` | 树形结构字段映射 |
| `loading` | `Boolean` | 否 | `false` | 是否加载中 |
| `tableProper` | `String` | 否 | `"matm"` | 表格所属模块标识 |
| `allowChildCheck` | `Boolean` | 否 | `false` | 是否允许选中树形子项 |

## 列配置（tableColumns 项）

| 字段 | 类型 | 描述 |
|------|------|------|
| `show` | `Boolean` | 是否显示该列（动态列控制） |
| `type` | `String` | 列类型，如 `"selection"`、`"index"` |
| `fixed` | `String \| Boolean` | 固定列 |
| `prop` | `String` | 数据字段名 |
| `label` | `String` | 列标题 |
| `width` | `Number \| String` | 列最小宽度 |
| `sortable` | `Boolean \| String` | 是否可排序 |
| `dictType` | `String` | 字典类型，设置后使用 `DictTag` 渲染 |
| `dict` | `Object` | 字典数据对象 |
| `isAvatar` | `Boolean` | 是否渲染头像列（展示 `avatar` 图片或首字母） |
| `isLog` | `Boolean` | 是否为日志列（支持批量操作内容展开） |
| `isMsg` | `Boolean` | 是否为消息列（支持未读状态、内容模型名称） |
| `isSkip` | `Boolean` | 是否可点击跳转 |
| `isHighlight` | `Boolean` | 是否高亮显示（主题色文字） |

## 列渲染模式优先级

`dictType` > `isAvatar` > `isLog` > `isMsg` > 默认文本

### 日志列（isLog）
- 批量操作：显示"批量{prop}" + 可点击展开详情（Popover）
- 单条操作：直接显示操作内容，含可点击跳转的编码/名称

### 消息列（isMsg）
- 批量操作：同日志列
- 单条操作：显示 `{modelName}数据（编码: xxx）{category}`
- 未读状态：文字使用主题色 + 红色圆点标识

### 头像列（isAvatar）
- 优先展示 `row.avatar` 图片
- 无图片时展示 `nickname` 或 `username` 的首字母

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
| `expand` | 展开行插槽 |

## Expose

无。

## 职责边界

- 负责表格的统一渲染逻辑，包括字典、头像、日志、消息等特殊列
- 不负责数据获取、分页和搜索
- 继承 `$attrs` 传递给 `el-table`

## 注意事项

- 使用 `v-horizontal-scroll` 自定义指令处理水平滚动
- `show` 属性用于动态控制列的显示/隐藏

## 基本使用示例

```vue
<LYTable
  :data="projectList"
  :tableColumns="columns"
  :loading="loading"
  row-key="id"
  @handleSelectionChange="handleSelect"
  @sortChange="handleSort"
/>

<script setup>
const columns = [
  { type: 'selection', show: true, fixed: 'left' },
  { prop: 'code', label: '项目编码', width: 150, isSkip: true, isHighlight: true, show: true },
  { prop: 'name', label: '项目名称', width: 200, show: true },
  { prop: 'statusName', label: '状态', width: 100, dictType: 'projectStatus', dict: dict, show: true },
  { prop: 'createdBy', label: '创建人', width: 120, isAvatar: true, show: true },
]
</script>
```
