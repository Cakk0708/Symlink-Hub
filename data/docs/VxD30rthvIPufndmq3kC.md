# LYTitleLabel 标题块容器组件

## 基本信息

- **组件名称**: LYTitleLabel
- **所在路径**: `src/components/LYTitleLabel/index.vue`
- **一句话描述**: 带下划线/色块的区域标题容器，支持"展开/收起"交互，常用于页面分组卡片。
- **组件类型**: 容器型

## 适用场景举例

- 表单分区块标题（如"基本信息"、"组织信息"、"其他"等）
- 详情页的信息分组标题
- 可折叠的设置面板标题

## Props

| 属性 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `title` | `String` | 否 | `""` | 标题文本 |
| `level` | `Number` | 否 | `1` | 层级。`1` 为一级标题（带下划线色块），其他值为二级标题（左侧竖条装饰） |
| `showExpand` | `String` | 否 | `true` | 是否显示展开/收起按钮（注意类型为 String，非 Boolean） |

## Slots

| 插槽名 | 描述 |
|--------|------|
| `default` | 标题下方的内容区域，展开时显示 |

## 样式差异

### level = 1（一级标题）
- 标题文字下方有 4px 主题色下划线色块
- 整行底部有 1px 浅色分割线
- 可显示展开/收起按钮

### level != 1（二级标题）
- 左侧 4px 竖条装饰
- 无下划线色块
- 不显示展开/收起按钮

## 职责边界

- 负责标题和内容的展开/收起状态管理
- 不负责内容区域的业务逻辑

## 注意事项

- `showExpand` 属性类型为 `String` 而非 `Boolean`，传 `false` 字符串时等同于 falsy
- 收起时标题下方间距增加，展开时恢复

## 基本使用示例

```vue
<!-- 一级标题，可折叠 -->
<LYTitleLabel title="基本信息" :level="1">
  <el-form>...</el-form>
</LYTitleLabel>

<!-- 一级标题，不可折叠 -->
<LYTitleLabel title="组织信息" :show-expand="false">
  <el-form>...</el-form>
</LYTitleLabel>

<!-- 二级标题 -->
<LYTitleLabel title="联系信息" :level="2">
  <el-form>...</el-form>
</LYTitleLabel>
```
