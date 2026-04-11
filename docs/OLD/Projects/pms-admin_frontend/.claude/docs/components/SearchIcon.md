# SearchIcon 搜索图标组件

## 基本信息

- **组件名称**: SearchIcon
- **所在路径**: `src/components/SearchIcon/index.vue`
- **一句话描述**: 通用搜索图标，点击时触发 `clickIcon` 事件。
- **组件类型**: 交互型

## 适用场景举例

- 作为 `searchSelect` 组件的内部图标
- 表格搜索栏、筛选区域的搜索触发按钮

## Props

无。

## Events

| 事件名 | 参数 | 描述 |
|--------|------|------|
| `clickIcon` | 无 | 点击图标时触发 |

## 职责边界

- 仅负责渲染搜索图标和抛出点击事件，不包含搜索逻辑
- 内部使用 `LYIcon` 组件（`iconClass="a-sousuo2"`，`size="14"`）

## 基本使用示例

```vue
<SearchIcon @clickIcon="handleSearch" />
```
