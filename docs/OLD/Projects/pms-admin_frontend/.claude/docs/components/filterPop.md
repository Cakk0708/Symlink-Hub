# filterPop 过滤悬浮窗组件

## 基本信息

- **组件名称**: filterPop
- **所在路径**: `src/components/filterPop/index.vue`
- **一句话描述**: 点击图标弹出多选过滤面板，支持关键字搜索、全选/反选、勾选计数及"确定/清除"回调。
- **组件类型**: 交互型

## 适用场景举例

- 表格工具栏中的列筛选（如按状态、类型等字段过滤）
- 多条件组合筛选场景

## Props

| 属性 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `dataList` | `Array` | 否 | `[]` | 可选项列表，每项包含 `{ label, value }` |
| `type` | `String` | 否 | `""` | 过滤器类型标识，会在 `confirm`/`clear` 事件中回传，用于区分多个 filterPop 实例 |

## Events

| 事件名 | 参数 | 描述 |
|--------|------|------|
| `confirm` | `{ data: Array, type: String }` | 点击"确定"时触发，`data` 为选中的项列表 |
| `clear` | `{ type: String }` | 点击"清除"时触发 |
| `open` | 无 | 弹窗打开时触发 |

## Expose

| 方法 | 参数 | 描述 |
|------|------|------|
| `clear()` | 无 | 清除所有选中状态和搜索关键字 |
| `close()` | 无 | 关闭弹窗 |
| `open()` | 无 | 打开弹窗并回显已选状态 |

## 职责边界

- 负责过滤面板的交互（搜索、全选、勾选计数、确定/清除）
- 不负责实际的数据过滤逻辑，由父组件监听 `confirm` 事件后处理
- 打开弹窗时会回显上次确认后的选择状态

## 内部状态管理

- `tempList` 保存确认后的选择态，用于下次打开时回显
- `showList` 当前显示的列表（经过搜索过滤后）
- `originList` 原始列表（搜索过滤的基准）

## 基本使用示例

```vue
<template>
  <filterPop
    :dataList="statusOptions"
    type="status"
    @confirm="handleFilterConfirm"
    @clear="handleFilterClear"
  />
</template>

<script setup>
const statusOptions = [
  { label: '进行中', value: 'active' },
  { label: '已完成', value: 'done' },
  { label: '已暂停', value: 'paused' },
]

const handleFilterConfirm = ({ data, type }) => {
  // data: [{ label: '进行中', value: 'active', checked: true }, ...]
  console.log('选中项:', data)
}

const handleFilterClear = ({ type }) => {
  console.log('清除:', type)
}
</script>
```
