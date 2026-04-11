# AppLink 应用链接组件

## 基本信息

- **组件名称**: AppLink
- **所在路径**: `src/components/AppLink/index.vue`
- **一句话描述**: 根据地址是否为外链，自动切换 `<a>` 或 `<router-link>`，统一处理导航链接。
- **组件类型**: 展示型 / 导航型

## 适用场景举例

- 侧边栏菜单项渲染，部分菜单指向外部链接（如飞书文档），部分指向内部路由
- 页面内的链接按钮需要兼容外部跳转和内部路由

## Props

| 属性 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `to` | `Object` | 是 | — | 路由对象，必须包含 `path` 字段。当 `path` 为外链时渲染 `<a>`，否则渲染 `<router-link>` |

## Slots

| 插槽名 | 描述 |
|--------|------|
| `default` | 链接文本内容 |

## 职责边界

- 仅负责区分内外链并渲染对应元素，不处理鉴权、权限控制等逻辑
- 外链判断依赖 `@/utils/index` 中的 `isExternal` 工具函数

## 注意事项

- `to` 属性类型为 `Object` 而非 `String`，使用时需传入对象形式，如 `{ path: '/dashboard' }` 或 `{ path: 'https://example.com' }`
- 外链默认 `target="_blank"` 并附加 `rel="noopener noreferrer"` 安全属性

## 基本使用示例

```vue
<!-- 内部路由 -->
<AppLink :to="{ path: '/dashboard' }">首页</AppLink>

<!-- 外部链接 -->
<AppLink :to="{ path: 'https://feishu.cn/doc/xxx' }">飞书文档</AppLink>
```
