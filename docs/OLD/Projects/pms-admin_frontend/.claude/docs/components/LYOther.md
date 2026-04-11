# LYOther 其他信息组件

## 基本信息

- **组件名称**: LYOther
- **所在路径**: `src/components/LYOther/index.vue`
- **一句话描述**: 统一展示创建人/创建时间/最后更新人/最后更新时间/禁用状态等"其他信息"区域，仅展示不编辑。
- **组件类型**: 展示型 / 业务型

## 适用场景举例

- 各详情页底部的"其他"信息区域
- 编辑页/新增页的底部信息展示（创建人、更新人等系统字段）

## Props

| 属性 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `othersData` | `Object` | 否 | `{}` | 其他信息数据对象 |

## othersData 数据结构

| 字段 | 类型 | 描述 | 是否显示 |
|------|------|------|----------|
| `createdBy` | `Object \| String` | 创建人。支持对象（`{ nickname }`）或字符串 | `creatorHidden` 不为 true 时显示 |
| `createdAt` | `String` | 创建时间 | 同上 |
| `updatedBy` | `Object` | 最后更新人。对象含 `nickname` / `username` 字段 | 字段有值时显示 |
| `updatedAt` | `String` | 最后更新时间 | 字段有值时显示 |
| `disableFlag` | `Any` | 禁用标志，配合 `disableFlag` 字典渲染 | 字段存在时显示 |
| `creatorHidden` | `Boolean` | 是否隐藏创建人/创建时间 | — |
| `approval.approver.username` | `String` | 审批人 | 组件内部处理但未渲染 |

## 职责边界

- 负责数据格式转换（将 `createdBy.nickname` 转为 `creatorName` 等）
- 内部使用 `LYTitleLabel title="其他"` 作为容器
- 内部使用 `inject("loadDict")` 加载 `disableFlag` 字典
- 表单全局 `disabled`，仅供展示

## 注意事项

- 组件内部自包含标题"其他"，无需外部添加
- 依赖 `loadDict` 注入，使用该组件的页面需提供 `loadDict` 函数

## 基本使用示例

```vue
<LYOther :othersData="{
  createdBy: { nickname: '张三' },
  createdAt: '2025-01-01 10:00:00',
  updatedBy: { nickname: '李四' },
  updatedAt: '2025-01-02 14:00:00',
  disableFlag: 0
}" />
```
