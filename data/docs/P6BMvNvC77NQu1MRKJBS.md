# Breadcrumb 面包屑组件

## 基本信息

- **组件名称**: Breadcrumb
- **所在路径**: `src/components/Breadcrumb/index.vue`
- **一句话描述**: 基于路由 `matched` 动态生成面包屑导航，支持函数型 title 和隐藏面包屑配置。
- **组件类型**: 展示型 / 导航型

## 适用场景举例

- 顶部导航栏下方的路径指示器
- 深层级页面（如项目 > 节点 > 交付物）展示当前所在位置

## Props

无外部 Props，完全基于当前路由自动计算。

## Events

无向外抛出事件。

## 职责边界

- 自动监听路由变化，从 `currentRoute.matched` 中提取面包屑项
- 支持通过路由 `meta.breadcrumb === false` 隐藏某级面包屑
- 支持通过路由 `meta.noShowBreadcrumb === true` 隐藏整条面包屑
- 支持函数型 `meta.title`，函数接收 `{ ...item, params }` 参数

## 路由 Meta 配置

| 字段 | 类型 | 描述 |
|------|------|------|
| `meta.title` | `String \| Function` | 面包屑显示文本。函数型会被调用并传入路由信息 |
| `meta.breadcrumb` | `Boolean` | 设为 `false` 时该级不出现在面包屑中 |
| `meta.noShowBreadcrumb` | `Boolean` | 设为 `true` 时第二级面包屑开始隐藏整条面包屑 |

## 注意事项

- 当前链接点击事件已被禁用（`handleLink` 函数体为空），面包屑仅作展示用途
- 使用 `animate__fadeInRight` 过渡动画
- 最后一项和 `redirect === 'noredirect'` 的项为纯文本样式，其余为灰色链接样式

## 基本使用示例

```vue
<!-- 在 layout 中直接使用，无需 props -->
<Breadcrumb />
```

```js
// 路由配置示例
{
  path: '/pm/project/:id',
  meta: {
    title: (route) => route.params.id ? `项目详情` : '项目',
    breadcrumb: true
  }
}
```
