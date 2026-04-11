# 组织详情页 布局说明

> 最后更新：2026-04-05
> 页面文件：`src/views/SM/organization/detail.vue`

---

## 页面结构

- 顶部导航栏
    - 返回按钮
    - 页面标题
- 基础信息卡片
    - 卡片标题
    - 描述列表
        - 组织 ID
        - 组织编码
        - 组织名称（跨 2 列）
        - 备注（跨 2 列）
        - 创建时间
        - 更新时间

---

## 结构说明

### 顶部导航栏
tag: .page-header
note: 详情页顶部导航区，白色背景，包含返回按钮和页面标题

### 返回按钮
tag: .page-header .el-button
note: 点击返回组织列表页，使用 ArrowLeft 图标

### 页面标题
tag: .page-title
note: 显示"组织详情"文本标题，20px 加粗

### 基础信息卡片
tag: .info-card
note: 组织基础信息展示区，加载时显示 loading 状态，数据加载后以描述列表形式展示

### 卡片标题
tag: .info-card .card-header
note: 显示"基础信息"标题

### 描述列表
tag: .el-descriptions
note: 2 列带边框的描述列表，展示组织的完整字段信息

### 组织 ID
tag: .el-descriptions-item
note: 显示组织 ID

### 组织编码
tag: .el-descriptions-item
note: 显示自动生成的组织编码（如 O202503150001）

### 组织名称
tag: .el-descriptions-item
note: 显示组织名称，跨 2 列展示

### 备注
tag: .el-descriptions-item
note: 显示组织备注内容，无备注时显示"-"，跨 2 列展示

### 创建时间
tag: .el-descriptions-item
note: 显示组织创建时间

### 更新时间
tag: .el-descriptions-item
note: 显示组织最后更新时间
