# 组织列表页 布局说明

> 最后更新：2026-04-05
> 页面文件：`src/views/SM/organization/index.vue`

---

## 页面结构

- 页面标题栏
    - 标题文本
    - 新增组织按钮
- 搜索栏
    - 组织名称输入框
    - 搜索按钮
    - 重置按钮
- 组织数据表格
    - 复选框列
    - ID 列
    - 组织编码列（可点击跳转详情）
    - 组织名称列
    - 备注列
    - 创建时间列
    - 更新时间列
    - 操作列
        - 详情按钮
        - 编辑按钮
        - 删除按钮
- 批量删除栏（条件显示）
    - 已选计数
    - 批量删除按钮
- 分页栏
- 新增组织对话框（浮层）
    - 组织名称输入框
    - 备注文本域
    - 取消按钮
    - 确定按钮
- 编辑组织对话框（浮层）
    - 组织名称输入框
    - 备注文本域
    - 取消按钮
    - 确定按钮

---

## 结构说明

### 页面标题栏
tag: .card-header
note: 组织管理页面顶部标题区，左侧显示"组织管理"文本，右侧提供新增组织入口

### 标题文本
tag: .card-header span
note: 显示"组织管理"模块名称

### 新增组织按钮
tag: .card-header .el-button
note: 点击打开新增组织对话框，触发新增流程

### 搜索栏
tag: .search-form
note: 组织列表搜索区域，支持按组织名称模糊搜索，包含搜索和重置操作

### 组织名称输入框
tag: .search-form .el-input
note: 输入组织名称关键词进行模糊搜索，支持一键清空

### 搜索按钮
tag: .search-form .el-button--primary
note: 点击执行搜索，重置页码到第 1 页并刷新列表

### 重置按钮
tag: .search-form .el-button
note: 清空搜索条件并刷新列表数据

### 组织数据表格
tag: .el-table
note: 组织数据列表主体，展示所有组织的核心字段，支持行选择、双击跳转详情

### 复选框列
tag: .el-table-column--selection
note: 行多选复选框，用于批量操作选择

### ID 列
tag: .el-table-column
note: 显示组织 ID，宽度 60px

### 组织编码列
tag: .el-table-column .el-link
note: 显示组织编码（如 O202503150001），以链接形式展示，点击跳转组织详情页

### 组织名称列
tag: .el-table-column
note: 显示组织名称

### 备注列
tag: .el-table-column
note: 显示组织备注信息，超长文本自动省略并显示 tooltip

### 创建时间列
tag: .el-table-column
note: 显示组织创建时间，宽度 170px

### 更新时间列
tag: .el-table-column
note: 显示组织最后更新时间，宽度 170px

### 操作列
tag: .operation-buttons
note: 行级操作按钮区，固定在表格右侧，包含详情、编辑、删除三个操作

### 详情按钮
tag: .operation-buttons .el-button--primary
note: 点击跳转至组织详情页

### 编辑按钮
tag: .operation-buttons .el-button--primary
note: 点击打开编辑组织对话框，回填当前行数据

### 删除按钮
tag: .operation-buttons .el-button--danger
note: 点击弹出确认框，确认后删除该组织并刷新列表

### 批量删除栏
tag: .batch-delete-bar
note: 当表格有选中行时显示，展示已选数量及批量删除入口

### 已选计数
tag: .batch-delete-bar span
note: 显示当前已选中的组织数量

### 批量删除按钮
tag: .batch-delete-bar .el-button--danger
note: 点击弹出确认框，确认后批量删除选中组织

### 分页栏
tag: .container-pagination
note: 列表底部分页导航，支持上一页、页码、下一页切换

### 新增组织对话框
tag: .el-dialog
note: 新增组织表单弹窗，包含组织名称（必填）和备注字段，提交后创建组织

### 编辑组织对话框
tag: .el-dialog
note: 编辑组织表单弹窗，回填已有数据，提交后更新组织信息
