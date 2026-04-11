# 套餐管理 - 详情页布局说明

## 布局概述

详情页采用多卡片纵向排列布局，顶部为返回导航，依次展示基础信息和赠品管理两个区域。

## 布局结构

```
Package Detail Layout
├── 页面头部: 返回按钮 + "套餐详情" 标题
├── el-card: 基础信息 (el-descriptions)
└── el-card: 赠品管理
    ├── 添加赠品区域 (el-select + el-button)
    ├── el-table: 赠品列表
    └── el-empty: 无赠品提示 (条件显示)
```

## 详细布局

```
+--------------------------------------------------+
|  [← 返回]  套餐详情                               |
+--------------------------------------------------+
|                                                  |
|  基础信息                                         |
|  +--------------------------------------------+  |
|  | 套餐ID       | 套餐编号    |               |  |
|  | 1            | P...01     |               |  |
|  +--------------+------------+               |  |
|  | 套餐名称     | 分类       |               |  |
|  | 经验套餐     | 经验       |               |  |
|  +--------------+------------+               |  |
|  | 金额         | 目标数量   |               |  |
|  | ¥50.00       | 1000       |               |  |
|  +--------------+------------+               |  |
|  | 状态         | 创建时间   |               |  |
|  | [启用]       | 2026-04-05 |               |  |
|  +--------------+------------+               |  |
|  | 备注: 这是一个经验套餐              (span=2)  |  |
|  +--------------------------------------------+  |
|                                                  |
|  赠品列表                    [添加赠品]              |
|  +--------------------------------------------+  |
|  | [请选择要添加的赠品套餐 ▼]    [添加]         |  |
|  +--------------------------------------------+  |
|  | 序号 | 赠品编号 | 赠品名称 | 分类 | 金额 | 目标数量 | 操作 |  |
|  |  1   | P...03  | 宝石赠品 | 宝石 | ¥10 | 100    | 移除 |  |
|  +------+---------+---------+----+------+---------+-----+  |
|  |                                                  |  |
|  |          (无赠品时显示 el-empty)                  |  |
|  +--------------------------------------------------+  |
+--------------------------------------------------+
```

## 组件说明

### 页面头部 (page-header)

- 白色背景，圆角 4px
- 左侧: 返回按钮 (el-button :icon="ArrowLeft")
- 右侧: 页面标题 h2，字号 20px，font-weight 600

### 基础信息卡片 (el-card)

- el-descriptions :column="2" border
- 2 列网格布局，备注项 :span="2" 横跨两列

| 行 | 左列 | 右列 |
|----|------|------|
| 1 | 套餐ID | 套餐编号 |
| 2 | 套餐名称 | 分类 |
| 3 | 金额 (¥前缀) | 目标数量 |
| 4 | 状态 (el-tag) | 创建时间 |
| 5 | 更新时间 (条件显示) | - |
| 6 | 备注 (:span="2") | - |

- 整体 v-loading，数据加载中显示 loading

### 赠品管理卡片 (el-card)

- 卡片头部: 标题 "赠品列表" + 添加赠品按钮 (type="primary", size="small", :icon="Plus")

#### 添加赠品区域

- 背景: `#f5f7fa`，圆角 4px，padding 16px
- el-select: filterable 可搜索，宽度 400px，label 格式 `名称 (编号)`
- el-button: 添加，disabled 当未选择时
- 下拉选项自动排除当前套餐和已添加的赠品

#### 赠品表格 (el-table)

| 列 | 属性 | 宽度 | 说明 |
|----|------|------|------|
| 序号 | type="index" | 80 | 自增序号 |
| 赠品编号 | prop="code" | 140 | - |
| 赠品名称 | prop="name" | 自适应 | - |
| 分类 | prop="categoryDisplay" | 100 | - |
| 金额 | 自定义模板 | 100 | 右对齐，¥ 前缀 |
| 目标数量 | prop="plannedQty" | 100 | 右对齐 |
| 操作 | 自定义模板 | 100 | fixed="right"，移除按钮 |

- 顶部间距 margin-top: 20px
- v-loading 控制

#### 空状态 (el-empty)

- 条件: 赠品列表为空时显示
- 描述: "暂无赠品"
- image-size: 100

## 交互设计

- 返回按钮 → `router.push({ name: 'Package' })` 回到列表页
- 添加赠品 → PATCH 请求，成功后刷新详情和可选列表
- 移除赠品 → ElMessageBox.confirm 二次确认，PATCH 请求，成功后刷新

## API 调用

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | /BDM/package/:id | 获取详情（含 gifts 数组） |
| GET | /BDM/package/simple | 获取可选赠品下拉列表 |
| PATCH | /BDM/package/:id | 添加赠品 body: { actionType:'add', giftId } |
| PATCH | /BDM/package/:id | 移除赠品 body: { actionType:'remove', giftId } |

## 样式要点

```css
.package-detail-container   padding: 20px, bg: #f5f7fa, min-height: calc(100vh - 60px)
.page-header                 flex, center, gap: 16px, mb: 20px, white bg, radius: 4px
.page-title                  margin: 0, font-size: 20px, font-weight: 600
.info-card / gift-card      margin-bottom: 20px
.card-header                 flex, space-between, font-weight: 600
.add-gift-section            flex, center, padding: 16px, bg: #f5f7fa, radius: 4px
```
