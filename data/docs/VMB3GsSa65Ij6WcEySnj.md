# Hamburger 折叠按钮组件

## 基本信息

- **组件名称**: Hamburger
- **所在路径**: `src/components/Hamburger/index.vue`
- **一句话描述**: 左侧菜单展开/收起图标按钮，点击时通过翻转动画切换状态。
- **组件类型**: 交互型

## 适用场景举例

- 顶部导航栏左侧，控制侧边栏菜单的展开/收起

## Props

| 属性 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `isActive` | `Boolean` | 是 | `false` | 菜单是否处于激活（展开）状态，控制图标翻转方向 |

## Events

| 事件名 | 参数 | 描述 |
|--------|------|------|
| `toggleClick` | 无 | 点击图标按钮时触发，由父组件处理菜单状态切换 |

## 职责边界

- 仅负责图标展示和点击事件抛出，不管理菜单状态
- 内部使用 `LYIcon` 组件渲染 iconfont 图标 `a-shouqi1`

## 注意事项

- 图标通过 CSS `transform: scaleX(-1)` 实现翻转，`isActive` 时恢复正向

## 基本使用示例

```vue
<Hamburger :isActive="sidebar.opened" @toggleClick="toggleSideBar" />
```
