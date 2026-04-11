# PMS Admin Frontend 项目地图

> 本文档提供项目的高层次组件视图，详细组件说明请查看对应的组件文档。

---

## 快速导航

| 文档 | 说明 |
|------|------|
| [CLAUDE.md](/CLAUDE.md) | 项目开发指南和技术栈说明 |
| [modules/](./modules/) | 各业务模块详细文档 |
| [components/](./components/) | 公共组件详细文档 |

---

## 项目组件全景

> 组件源码位于 `src/components/`，详细文档见 `components/` 目录。

### 通用展示组件

| 组件 | 别名 | 路径 | 文档 | 类型 |
|------|------|------|------|------|
| AppLink | 应用链接 | `src/components/AppLink/index.vue` | [详情](./components/AppLink.md) | 展示型 |
| Breadcrumb | 面包屑 | `src/components/Breadcrumb/index.vue` | [详情](./components/Breadcrumb.md) | 展示型 |
| DictTag | 字典标签 | `src/components/DictTag/index.vue` | [详情](./components/DictTag.md) | 展示型 |
| LYIcon | LY图标 | `src/components/LYIcon/index.vue` | [详情](./components/LYIcon.md) | 展示型 |
| LYlabel | 标题标签 | `src/components/LYlabel/index.vue` | [详情](./components/LYlabel.md) | 展示型 |
| SvgIcon | SVG图标 | `src/components/SvgIcon/index.vue` | [详情](./components/SvgIcon.md) | 展示型 |
| LYSpace | 间隔布局 | `src/components/LYSpace/index.vue` | [详情](./components/LYSpace.md) | 布局型 |

### 交互型组件

| 组件 | 别名 | 路径 | 文档 | 类型 |
|------|------|------|------|------|
| Hamburger | 折叠按钮 | `src/components/Hamburger/index.vue` | [详情](./components/Hamburger.md) | 交互型 |
| SearchIcon | 搜索图标 | `src/components/SearchIcon/index.vue` | [详情](./components/SearchIcon.md) | 交互型 |
| filterPop | 过滤悬浮窗 | `src/components/filterPop/index.vue` | [详情](./components/filterPop.md) | 交互型 |
| Pagination | 分页 | `src/components/Pagination/index.vue` | [详情](./components/Pagination.md) | 交互型 |

### 容器型组件

| 组件 | 别名 | 路径 | 文档 | 类型 |
|------|------|------|------|------|
| LYDialog | 统一对话框 | `src/components/LYDialog/index.vue` | [详情](./components/LYDialog.md) | 容器型 |
| LYTitleLabel | 标题块容器 | `src/components/LYTitleLabel/index.vue` | [详情](./components/LYTitleLabel.md) | 容器型 |

### 表单型组件

| 组件 | 别名 | 路径 | 文档 | 类型 |
|------|------|------|------|------|
| ImageUpload | 图片上传 | `src/components/ImageUpload/index.vue` | [详情](./components/ImageUpload.md) | 表单型 |
| searchSelect | 搜索选择 | `src/components/searchSelect/index.vue` | [详情](./components/searchSelect.md) | 表单型 |
| LYOrg | 组织信息 | `src/components/LYOrg/index.vue` | [详情](./components/LYOrg.md) | 表单型 |

### 表格组件

| 组件 | 别名 | 路径 | 文档 | 类型 |
|------|------|------|------|------|
| LYTable | 通用表格 | `src/components/LYTable/index.vue` | [详情](./components/LYTable.md) | 容器型 |
| LYPopTable | 弹窗表格 | `src/components/LYPopTable/index.vue` | [详情](./components/LYPopTable.md) | 容器型 |

### 业务型组件

| 组件 | 别名 | 路径 | 文档 | 类型 |
|------|------|------|------|------|
| LYOther | 其他信息 | `src/components/LYOther/index.vue` | [详情](./components/LYOther.md) | 展示型 |
| LYTree | 可搜索树 | `src/components/LYTree/index.vue` | [详情](./components/LYTree.md) | 交互型 |
| popModal | 自定义模态窗 | `src/components/popModal/index.vue` | [详情](./components/popModal.md) | 交互型 |
