# popModal 自定义模态窗组件

## 基本信息

- **组件名称**: popModal
- **所在路径**: `src/components/popModal/index.vue` + `index.js`
- **一句话描述**: 基于 `el-dialog` 的通用弹窗，支持"仅提示"及"错误详情折叠/展开"等模式，常用于批量校验失败等场景的结果展示。
- **组件类型**: 交互型 / 业务型

## 适用场景举例

- 批量操作后的错误结果展示（如批量导入失败、批量校验失败）
- 单条错误提示
- 确认对话框

## 两种使用方式

### 1. 命令式调用（推荐用于错误提示）

通过 `index.js` 导出的 `showErrorTips` 函数直接调用：

```js
import showErrorTips from '@/components/popModal/index.js'

// 展示错误
showErrorTips('操作失败', errors)
```

### 2. 模板式调用

```vue
<popModal ref="popModalRef" title="提示" :err-obj="errorData" />
```

## Props

| 属性 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `title` | `String` | 否 | `"提示"` | 弹窗标题 |
| `content` | `String` | 否 | `""` | 纯文本提示内容（`type` 为空时显示） |
| `confirmTxt` | `String` | 否 | `"确定"` | 确认按钮文字 |
| `cancelTxt` | `String` | 否 | `"取消"` | 取消按钮文字 |
| `showCancel` | `Boolean` | 否 | `true` | 是否显示取消按钮 |
| `iconColor` | `String` | 否 | `"#1A7BFF"` | 标题图标颜色 |
| `confirmType` | `String` | 否 | `"primary"` | 确认按钮类型 |
| `beforConfirm` | `Boolean` | 否 | `false` | 确认前是否拦截关闭（不自动关闭弹窗） |
| `type` | `String` | 否 | `""` | 弹窗模式：`"more"` 为错误详情模式，空为普通提示 |
| `errObj` | `Object` | 否 | `{ msg: '', errors: [] }` | 错误数据对象 |

## errObj 数据结构

```ts
interface ErrObj {
  msg?: string         // 单条错误提示文字
  errors?: ErrorItem[] // 错误列表
}

// errors 支持两种格式：
// 数组格式（批量操作）
errors: [{ "字段1": ["错误信息1", "错误信息2"] }, { "字段2": ["错误信息"] }]
// 对象格式（嵌套结构）
errors: { "BOM版本": ["格式有误"], "子项物料": [{ "子项1": ["错误"] }] }
```

## Events

| 事件名 | 参数 | 描述 |
|--------|------|------|
| `cancel` | 无 | 点击取消时触发 |
| `confirm` | 无 | 点击确认时触发 |

## Expose

| 方法 | 参数 | 描述 |
|------|------|------|
| `open()` | 无 | 打开弹窗 |
| `close()` | 无 | 关闭弹窗 |
| `setTipError(errors)` | `Array` | 设置错误列表并打开弹窗 |
| `setTipMsg(msg)` | `String` | 设置单条错误信息并打开弹窗 |

## 命令式 API（index.js）

```ts
function showErrorTips(msg?: string, errors?: any[]): Promise<void>
```

- 自动设置错误主题（红色图标、danger 按钮）
- 创建独立 Vue 应用实例挂载到 body

## 错误详情模式特性

- 多条错误时默认折叠，显示"展开详情"按钮
- 单条错误时默认展开
- 支持嵌套层级展示（通过 `key-subkey` 格式实现缩进）
- 内容超出 325px 高度时显示滚动条

## 基本使用示例

```vue
<!-- 模板式 -->
<popModal ref="popRef" title="校验结果" :show-cancel="false" />

<script setup>
const popRef = ref()

// 设置错误
popRef.value.setTipError([
  { "项目编码": ["不能为空", "格式不正确"] },
  { "项目名称": ["已存在"] }
])
</script>
```

```js
// 命令式
import showErrorTips from '@/components/popModal/index.js'

showErrorTips('批量导入失败，以下数据存在问题：', [
  { "第1行": ["编码重复", "名称为空"] },
  { "第3行": ["找不到对应分类"] }
])
```
