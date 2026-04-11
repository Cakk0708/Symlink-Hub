# DictTag 字典标签组件

## 基本信息

- **组件名称**: DictTag
- **所在路径**: `src/components/DictTag/index.vue`
- **一句话描述**: 根据字典项值渲染文本或 `el-tag`，内置多种颜色样式，适合展示状态/类型等枚举。
- **组件类型**: 展示型

## 适用场景举例

- 表格列中展示项目状态（进行中/已完成/已暂停）
- 详情页中展示数据类型、审批状态等枚举值

## Props

| 属性 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `options` | `Array` | 否 | `null` | 字典选项数组，每项包含 `{ label, value, listClass, cssClass }` |
| `value` | `Number \| String \| Array \| Boolean` | 否 | — | 当前值，支持单个值或数组（多标签场景） |

## 字典选项格式

```ts
interface DictOption {
  label: string      // 显示文本
  value: string | number  // 字典值
  listClass?: string      // el-tag 类型：'primary' | 'success' | 'warning' | 'danger' | 'info' | 'default'
  cssClass?: string       // 自定义 CSS 类名，如 'green' | 'red' | 'blue' | 'gray' | 'purple'
}
```

## 内置颜色样式

| 类名 | 效果 |
|------|------|
| `green` | 绿色半透明背景 + 绿色文字 |
| `red` | 红色半透明背景 + 红色文字 |
| `blue` | 蓝色半透明背景 + 蓝色文字 |
| `gray` | 灰色半透明背景 + 灰色文字 |
| `purple` | 紫色半透明背景 + 紫色文字 |

## 渲染规则

- `listClass` 为 `'default'` 或空字符串时 → 渲染纯 `<span>` 文本
- `listClass` 为 `'primary'` 或其他有效 el-tag 类型时 → 渲染 `<el-tag>`
- `cssClass` 可叠加额外样式类

## 职责边界

- 仅负责字典值的展示渲染，不负责字典数据的加载
- 常与 `loadDict` 注入的字典数据配合使用

## 基本使用示例

```vue
<!-- 单值 -->
<DictTag :options="dict.type.projectStatus" :value="row.status" />

<!-- 多值 -->
<DictTag :options="dict.type.projectStatus" :value="['active', 'pending']" />
```
