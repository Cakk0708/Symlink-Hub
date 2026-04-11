# LYIcon 图标组件

## 基本信息

- **组件名称**: LYIcon
- **所在路径**: `src/components/LYIcon/index.vue`
- **一句话描述**: 封装自定义 iconfont，统一图标类名、大小和颜色配置。
- **组件类型**: 展示型

## 适用场景举例

- 全项目通用的图标展示，如按钮图标、表单前缀图标、操作列图标等

## Props

| 属性 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `iconClass` | `String` | 是 | `""` | iconfont 图标名称（不含 `icon-` 前缀），如 `"a-sousuo2"` |
| `color` | `String` | 否 | `var(--el-text-color-regular)` | 图标颜色，支持 CSS 颜色值和 CSS 变量 |
| `size` | `String` | 否 | `"14"` | 图标大小（单位 px），如 `"14"`、`"18px"` |

## 职责边界

- 仅负责 iconfont 图标的渲染，不包含点击事件处理（由父组件通过 `@click` 绑定）
- 渲染为 `<i class="iconfont icon-{iconClass}">` 结构

## 注意事项

- `size` 属性直接拼接 `'px'` 后缀，传入 `"14"` 或 `"14px"` 效果相同
- 使用前需确保 iconfont 资源已在项目中加载

## 基本使用示例

```vue
<!-- 基础用法 -->
<LYIcon iconClass="a-sousuo2" size="14" />

<!-- 自定义颜色和大小 -->
<LYIcon iconClass="guanbi" color="#C8C8C9" size="18" />

<!-- 配合事件 -->
<LYIcon iconClass="a-shouqi1" size="18px" @click="handleClick" />
```
