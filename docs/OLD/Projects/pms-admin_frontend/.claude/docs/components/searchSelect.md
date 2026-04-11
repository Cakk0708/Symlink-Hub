# searchSelect 搜索选择组件

## 基本信息

- **组件名称**: searchSelect
- **所在路径**: `src/components/searchSelect/index.vue`
- **一句话描述**: 在 `el-select` 基础上叠加搜索图标按钮，支持点击图标触发搜索、下拉展示控制等场景。
- **组件类型**: 表单型 / 交互型

## 适用场景举例

- 表单中选择框，需要点击搜索图标触发远程搜索（如搜索客户、搜索员工）
- 需要在搜索后才展开下拉选项的场景

## Props

| 属性 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `data` | `Object` | 否 | `[]` | 选项数据（预留） |
| `disabled` | `Boolean` | 否 | `false` | 是否禁用下拉选择 |
| `iconDisabled` | `Boolean` | 否 | `false` | 是否禁用搜索图标 |
| `valueKey` | `String` | 否 | `"value"` | 值标识字段 |
| `placeholder` | `String` | 否 | `""` | 占位文字 |
| `searchStr` | `String` | 否 | `""` | 搜索关键字 |
| `showOnSearch` | `Boolean` | 否 | `false` | 是否仅在搜索时展开下拉（有搜索关键字时才允许展开） |

## Events

| 事件名 | 参数 | 描述 |
|--------|------|------|
| `clickSearch` | 无 | 点击搜索图标时触发 |
| `change` | `val: any` | 下拉选项变化时触发 |

## Expose

| 属性/方法 | 类型 | 描述 |
|-----------|------|------|
| `refElSelect` | `Ref<Component>` | 内部 `el-select` 组件实例引用 |

## Slots

| 插槽名 | 描述 |
|--------|------|
| `default` | `el-select` 的下拉选项 |
| `label` | 自定义选中项的显示，参数 `{ label, value }` |

## 职责边界

- 负责 `el-select` + 搜索图标的组合渲染和交互
- `el-select` 内部 `disabled`（始终为 true），所有交互通过搜索图标和 `clickSearch` 事件触发
- `showOnSearch` 模式下，无搜索关键字时阻止下拉展开

## 注意事项

- 搜索图标默认透明度为 0，hover select 时会显示
- 图标按钮 hover 检测是否为 disabled 状态，自动切换光标样式

## 基本使用示例

```vue
<searchSelect
  placeholder="请搜索客户"
  :show-on-search="true"
  :search-str="searchKeyword"
  @clickSearch="handleSearch"
  @change="handleSelect"
>
  <el-option
    v-for="item in customerList"
    :key="item.value"
    :label="item.label"
    :value="item.value"
  />
</searchSelect>
```
