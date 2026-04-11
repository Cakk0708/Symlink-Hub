# Pagination 分页组件

## 基本信息

- **组件名称**: Pagination
- **所在路径**: `src/components/Pagination/index.vue`
- **一句话描述**: 封装 `el-pagination`，统一 `page`/`limit` 双向绑定及滚动到顶部行为。
- **组件类型**: 交互型

## 适用场景举例

- 所有列表页底部的分页控制
- 配合 LYTable 使用

## Props

| 属性 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `total` | `Number` | 是 | — | 数据总条数 |
| `page` | `Number` | 否 | `1` | 当前页码，支持 `v-model:page` |
| `limit` | `Number` | 否 | `20` | 每页条数，支持 `v-model:limit` |
| `pageSizes` | `Array` | 否 | `[10, 20, 30, 50]` | 可选的每页条数列表 |
| `pagerCount` | `Number` | 否 | 响应式（移动端 5，桌面端 7） | 页码按钮数量 |
| `layout` | `String` | 否 | `"total, sizes, prev, pager, next, jumper"` | 分页组件布局 |
| `background` | `Boolean` | 否 | `true` | 是否显示背景色 |
| `autoScroll` | `Boolean` | 否 | `true` | 分页切换后是否自动滚动到顶部 |
| `hidden` | `Boolean` | 否 | `false` | 是否隐藏分页组件 |

## Events

| 事件名 | 参数 | 描述 |
|--------|------|------|
| `update:page` | `val: Number` | 当前页码变化时触发（支持 `v-model:page`） |
| `update:limit` | `val: Number` | 每页条数变化时触发（支持 `v-model:limit`） |
| `pagination` | `{ page: Number, limit: Number }` | 页码或条数变化时触发，携带完整的分页参数 |

## 职责边界

- 负责分页 UI 和参数管理
- 自动处理切换每页条数时当前页超出范围的修正（重置为第 1 页）
- 自动滚动到顶部使用 `@/utils/scroll-to` 工具函数
- 继承 `$attrs` 传递给 `el-pagination`

## 基本使用示例

```vue
<template>
  <Pagination
    v-model:page="queryParams.page"
    v-model:limit="queryParams.limit"
    :total="total"
    @pagination="getList"
  />
</template>

<script setup>
const queryParams = reactive({ page: 1, limit: 20 })
const total = ref(0)

const getList = ({ page, limit }) => {
  queryParams.page = page
  queryParams.limit = limit
  // 调用 API 获取数据
}
</script>
```
