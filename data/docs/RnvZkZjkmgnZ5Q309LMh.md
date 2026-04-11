# ImageUpload 图片上传组件

## 基本信息

- **组件名称**: ImageUpload
- **所在路径**: `src/components/ImageUpload/index.vue`
- **一句话描述**: 封装 `el-upload`，支持张数限制、大小/格式校验、上传进度提示及图片预览弹窗。
- **组件类型**: 表单型

## 适用场景举例

- 表单中的图片上传（如项目封面、资质图片等）
- 需要预览已上传图片的场景

## Props

| 属性 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `value` | `String \| Object \| Array` | 否 | — | 已上传图片的 URL，支持逗号分隔字符串、数组 |
| `limit` | `Number` | 否 | `5` | 最大上传张数 |
| `fileSize` | `Number` | 否 | `5` | 文件大小限制（单位 MB） |
| `fileType` | `Array` | 否 | `["png", "jpg", "jpeg"]` | 允许的文件类型后缀数组 |
| `isShowTip` | `Boolean` | 否 | `true` | 是否显示上传提示文字 |

## Events

| 事件名 | 参数 | 描述 |
|--------|------|------|
| `onRemoved` | `string` (逗号分隔的 URL 列表) | 删除图片后触发，参数为剩余图片的 URL 字符串 |
| `onUploaded` | `string` (逗号分隔的 URL 列表) | 上传成功后触发，参数为所有图片的 URL 字符串 |

## 职责边界

- 负责文件格式校验、大小限制、上传进度提示
- 负责图片预览弹窗
- 达到上传数量限制时隐藏上传按钮
- 上传地址和认证头需全局配置（代码中引用了 `uploadImgUrl`、`headers`、`baseUrl` 变量）

## 注意事项

- 组件内部使用了 `this.$modal`（Options API 风格），在 `<script setup>` 中可能存在兼容性问题
- `value` 变化时会自动同步 `fileList`
- 上传成功后通过 `listToString` 将文件列表转为逗号分隔的 URL 字符串传出

## 基本使用示例

```vue
<ImageUpload
  :value="form.coverImage"
  :limit="3"
  :fileSize="10"
  :fileType="['png', 'jpg', 'jpeg', 'webp']"
  @onUploaded="(urls) => form.coverImage = urls"
  @onRemoved="(urls) => form.coverImage = urls"
/>
```
