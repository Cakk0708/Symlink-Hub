# LYDialog 统一对话框组件

## 基本信息

- **组件名称**: LYDialog
- **所在路径**: `src/components/LYDialog/index.vue`
- **一句话描述**: 封装 `el-dialog`，提供标题行、自定义关闭图标、底部按钮配置等，统一弹窗风格。
- **组件类型**: 容器型 / 交互型

## 适用场景举例

- 表单新增/编辑弹窗
- 确认操作弹窗
- 详情查看弹窗
- 仅展示信息 + 关闭按钮的提示弹窗

## Props

| 属性 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `title` | `String` | 否 | `""` | 弹窗标题 |
| `width` | `String` | 否 | `"500"` | 弹窗宽度（单位 px） |
| `showClose` | `Boolean` | 否 | `true` | 是否显示关闭图标和取消按钮 |
| `showControls` | `Boolean` | 否 | `true` | 是否显示底部按钮区域（取消+确定） |
| `draggable` | `Boolean` | 否 | `false` | 是否可拖拽 |
| `modal` | `Boolean` | 否 | `true` | 是否需要遮罩层 |
| `closeOnPressEsc` | `Boolean` | 否 | `true` | 是否支持 Esc 键关闭 |
| `closeOnClickModal` | `Boolean` | 否 | `true` | 是否点击遮罩层关闭 |
| `isHearLine` | `Boolean` | 否 | `false` | 标题行底部是否显示分割线 |
| `isFooterClose` | `Boolean` | 否 | `false` | 底部仅显示"关闭"按钮（替代取消+确定） |
| `titleTip` | `String` | 否 | `""` | 标题旁的提示文字，灰色小字 |

## Events

| 事件名 | 参数 | 描述 |
|--------|------|------|
| `clickDialogClose` | 无 | 点击关闭图标或取消按钮时触发 |
| `clickDialogConfirm` | 无 | 点击确定按钮时触发 |

## Expose

| 属性/方法 | 类型 | 描述 |
|-----------|------|------|
| `dialogVisible` | `Ref<boolean>` | 控制弹窗显示/隐藏，父组件通过 `ref` 访问并修改 |

## Slots

| 插槽名 | 描述 |
|--------|------|
| `default` | 弹窗主体内容 |

## 底部按钮组合逻辑

| `showControls` | `isFooterClose` | `showClose` | 效果 |
|:-:|:-:|:-:|------|
| `true` | `false` | `true` | 取消 + 确定 |
| `true` | `false` | `false` | 仅确定 |
| `false` | `true` | — | 仅关闭 |

## 职责边界

- 负责弹窗的 UI 统一风格，不负责表单校验等业务逻辑
- 通过 `defineExpose` 暴露 `dialogVisible`，父组件需手动控制显示/隐藏

## 基本使用示例

```vue
<template>
  <el-button @click="dialogVisible = true">打开弹窗</el-button>
  <LYDialog
    ref="dialogRef"
    title="新增项目"
    width="600"
    @clickDialogClose="dialogVisible = false"
    @clickDialogConfirm="handleSubmit"
  >
    <el-form>...</el-form>
  </LYDialog>
</template>

<script setup>
const dialogRef = ref()
const dialogVisible = ref(false)

// 通过 ref 控制显示
watch(dialogVisible, (val) => {
  dialogRef.value.dialogVisible.value = val
})

const handleSubmit = () => {
  // 处理提交逻辑
  dialogVisible.value = false
}
</script>
```
