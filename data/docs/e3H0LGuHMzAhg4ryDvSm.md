# 套餐管理 - 列表页布局说明

## 布局概述

列表页采用标准的卡片式搜索 + 表格布局，包含搜索筛选、数据表格、批量操作、分页和新增弹窗。

## 布局结构

```
Package List Layout
├── el-card
│   ├── Header: 标题 "套餐管理" + "新增套餐"按钮
│   ├── el-form (inline): 搜索区域
│   ├── el-table: 数据表格
│   ├── 批量删除栏 (条件显示)
│   └── el-pagination: 分页
└── el-dialog: 新增套餐弹窗
```

## 详细布局

```
+--------------------------------------------------+
|  套餐管理                          [新增套餐]      |
+--------------------------------------------------+
|                                                  |
|  套餐名称 [________] 分类 [▼] 状态 [▼] [搜索] [重置]  |
|                                                  |
+--------------------------------------------------+
| ☐ | ID | 套餐编号 | 套餐名称 | 分类 | 金额 | 目标数量 | 状态 | 备注 | 创建时间 | 操作    |
+---+----+---------+---------+----+------+---------+----+------+---------+--------+
| ☐ | 1  | P...01  | 经验套餐 | 经验 | ¥50  | 1000   | 启用 | ...  | ...     | 详情 删除|
| ☐ | 2  | P...02  | 宝石套餐 | 宝石 | ¥30  | 500    | 禁用 | ...  | ...     | 详情 删除|
+---+----+---------+---------+----+------+---------+----+------+---------+--------+
|                                                  |
|  已选择 2 项              [批量删除]               |  ← 条件显示
|                                                  |
|                          < 1 2 3 >                |
+--------------------------------------------------+
```

## 组件说明

### 搜索区域 (el-form :inline)

| 字段 | 组件 | 说明 |
|------|------|------|
| 套餐名称 | el-input | 支持清除，模糊搜索 |
| 分类 | el-select | 经验/宝石/三倍经验/签到，可清除 |
| 状态 | el-select | 启用/禁用，可清除 |
| 操作 | el-button | 搜索 + 重置 |

### 数据表格 (el-table)

| 列 | 属性 | 宽度 | 说明 |
|----|------|------|------|
| 多选 | type="selection" | 55 | 复选框 |
| ID | prop="id" | 60 | 主键 |
| 套餐编号 | 自定义模板 | 140 | el-link 可点击，跳转详情页 |
| 套餐名称 | prop="name" | 自适应 | 普通文本 |
| 分类 | prop="categoryDisplay" | 100 | 枚举显示值 |
| 金额 | 自定义模板 | 90 | 右对齐，¥ 前缀 |
| 目标数量 | prop="plannedQty" | 90 | 右对齐 |
| 状态 | 自定义模板 | 80 | el-tag，启用=success，禁用=info |
| 备注 | prop="remark" | 150 | show-overflow-tooltip |
| 创建时间 | prop="createdAt" | 170 | 本地化时间字符串 |
| 操作 | 自定义模板 | 130 | fixed="right"，详情/删除按钮 |

**表格高度**: `calc(100vh - 330px)`

**交互行为**:
- `@row-dblclick`: 双击行跳转详情页
- 套餐编号 `el-link` 点击跳转详情页（`@click.stop` 阻止冒泡）
- `@selection-change`: 多选变更

### 批量删除栏

- 条件显示: `v-if="selectedRows.length > 0"`
- 左侧: 已选择数量文本
- 右侧: 批量删除按钮（type="danger"）
- 背景: `#f5f7fa`，圆角 4px

### 分页 (el-pagination)

- 布局: `background`，`layout="prev, pager, next"`
- 容器: 右对齐，高度 60px

### 新增套餐弹窗 (el-dialog)

- 标题: "新增套餐"
- 宽度: 500px
- 关闭策略: `:close-on-click-modal="false"`

**表单字段**:

| 字段 | 组件 | 必填 | 校验 |
|------|------|------|------|
| 套餐名称 | el-input | 是 | 2-50 字符 |
| 分类 | el-select | 是 | - |
| 金额 | el-input-number | 是 | min=0, precision=2 |
| 目标数量 | el-input-number | 是 | min=1 |
| 状态 | el-select | 是 | 默认 active |
| 备注 | el-input (textarea) | 否 | rows=3 |

**底部**: 取消 + 确定按钮

## 交互设计

- 双击表格行 → 跳转详情页 (`router.push`)
- 点击套餐编号链接 → 跳转详情页 (`@click.stop`)
- 勾选多行 → 显示批量删除栏
- 删除操作 → ElMessageBox.confirm 二次确认
- 新增成功 → 刷新列表，关闭弹窗，ElMessage 成功提示

## API 调用

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | /BDM/package | 分页查询，支持 name/category/status 筛选 |
| POST | /BDM/package | 创建套餐 |
| DELETE | /BDM/package | 批量删除，body: { ids } |

## 样式要点

```css
.package-container          height: 100%
.layout-container            flex, column, gap: 10px, height: 100%
.card-header                flex, space-between, center
:deep(.el-card)             height: 100%
:deep(.el-card__body)       height: calc(100% - 60px), overflow-y: auto
.search-form                margin-bottom: 20px
.batch-delete-bar           flex, space-between, bg: #f5f7fa, radius: 4px
.container-pagination       flex, align-end, justify-end, height: 60px
.operation-buttons          flex, gap: 8px, button height: 24px
```
