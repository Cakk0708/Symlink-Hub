# LYSpace 间隔布局组件

## 基本信息

- **组件名称**: LYSpace
- **所在路径**: `src/components/LYSpace/index.vue`
- **一句话描述**: 基于 `el-space`，默认使用竖向分割线（`el-divider`）作为子元素间的分隔符。
- **组件类型**: 布局型

## 适用场景举例

- 工具栏按钮组之间的分隔
- 操作区域多项并列展示时的视觉分隔

## Props

无额外 Props，继承 `el-space` 的默认配置（`size=0`）。

## Slots

| 插槽名 | 描述 |
|--------|------|
| `default` | 需要排列的子元素 |

## 职责边界

- 仅封装 `el-space` 并预设竖向分割线分隔符，不添加额外逻辑

## 基本使用示例

```vue
<LYSpace>
  <el-button>按钮A</el-button>
  <el-button>按钮B</el-button>
  <el-button>按钮C</el-button>
</LYSpace>
```
