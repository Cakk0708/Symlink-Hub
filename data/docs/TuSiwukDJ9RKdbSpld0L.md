# LYOrg 组织信息组件

## 基本信息

- **组件名称**: LYOrg
- **所在路径**: `src/components/LYOrg/index.vue`
- **一句话描述**: 从当前登录用户信息中渲染"使用组织"下拉选择，切换时抛出事件。
- **组件类型**: 表单型 / 业务型

## 适用场景举例

- 各业务表单（新增/编辑页）中的"组织信息"区域
- 需要用户切换当前操作组织（多组织场景）的表单

## Props

| 属性 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `disabled` | `Boolean` | 否 | `false` | 是否禁用组织下拉选择 |

## Events

| 事件名 | 参数 | 描述 |
|--------|------|------|
| `eventChangeCurrentOrg` | `e: string` (组织 ID) | 切换组织时触发，参数为选中的组织 ID |

## Slots

无。

## 职责边界

- 负责读取 localStorage 中的用户信息（`USER_KEY`），渲染组织列表和当前选中组织
- 内部固定使用 `LYlabel` 组件显示"组织信息"标题
- 不负责组织数据的增删改，仅展示和切换

## 数据来源

- 用户信息从 `localStorage.getItem(USER_KEY)` 读取
- `orgCurrent.id` → 当前选中的组织 ID
- `orgList` → 用户可用的组织列表（`[{ id, name }]`）

## 注意事项

- 组件内部自带标题 `LYlabel title="组织信息"`，无需外部额外添加标题
- 依赖 `USER_KEY` 枚举（来自 `@/enums/CacheEnum`）

## 基本使用示例

```vue
<LYOrg @eventChangeCurrentOrg="handleOrgChange" />

<!-- 禁用状态（详情页只读） -->
<LYOrg :disabled="true" />
```
