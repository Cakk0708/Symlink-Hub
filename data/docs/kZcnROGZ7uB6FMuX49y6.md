# SvgIcon SVG 图标组件

## 基本信息

- **组件名称**: SvgIcon
- **所在路径**: `src/components/SvgIcon/index.vue`
- **一句话描述**: 基于 SVG symbol sprite 渲染 SVG 图标，支持前缀、自定义大小和颜色。
- **组件类型**: 展示型

## 适用场景举例

- 项目中使用 SVG sprite 管理的图标（与 `LYIcon` 的 iconfont 方案不同）
- 需要更精细颜色控制的图标展示

## Props

| 属性 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `prefix` | `String` | 否 | `"icon"` | SVG symbol 的前缀名 |
| `iconClass` | `String` | 否 | `""` | 图标名称，最终生成 `#{prefix}-{iconClass}` 作为 symbol 引用 |
| `color` | `String` | 否 | `""` | 图标填充颜色，默认使用 `currentColor`（继承父元素颜色） |
| `size` | `String` | 否 | `"1em"` | 图标大小，支持 CSS 单位（如 `"20px"`、`"1em"`） |

## 职责边界

- 仅负责 SVG 图标的渲染，不处理图标的加载和注册
- 要求 SVG sprite 已通过 `<svg style="display:none">` 引入到页面中

## 注意事项

- 与 `LYIcon` 不同，本组件使用 SVG sprite 方案，需要配合 svg-sprite-loader 使用
- 默认使用 `currentColor` 作为填充色，会继承父元素的 `color` 属性

## 基本使用示例

```vue
<!-- 基础用法 -->
<SvgIcon iconClass="user" />

<!-- 自定义大小和颜色 -->
<SvgIcon iconClass="dashboard" size="20px" color="#1A7BFF" />

<!-- 自定义前缀 -->
<SvgIcon prefix="custom" iconClass="logo" size="32px" />
```
