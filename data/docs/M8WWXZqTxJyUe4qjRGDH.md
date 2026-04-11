# Dashboard 页面布局说明

## 布局概述

Dashboard 页面采用卡片式布局设计，清晰展示系统的核心统计数据和可视化图表。整体布局简洁明了，重点突出关键信息。

## 布局结构

```
Dashboard Layout
├── Header (可选，已包含在主布局中)
├── Main Content
│   ├── 统计卡片区域
│   └── 图表区域
└── Footer (可选，已包含在主布局中)
```

### 详细布局

```
+----------------------------------+
|          Dashboard 页面          |
+----------------------------------+
|                                  |
|  +------------+  +------------+  |
|  |  统计卡片  |  |  统计卡片  |  |
|  |  总用户数  |  |  昨日订单  |  |
|  |    1200    |  |     50     |  |
|  +------------+  +------------+  |
|                                  |
|  +------------+  +------------+  |
|  |  统计卡片  |  |  统计卡片  |  |
|  |  今日订单  |  |   营业额   |  |
|  |     30     |  |   ¥15.6k   |  |
|  +------------+  +------------+  |
|                                  |
|  +----------------------------------+  +------------+  |
|  |                图表区域            |  |            |  |
|  |   今日订单趋势图（折线/柱状图）    |  |  订单分类   |  |
|  |  [图表切换按钮]                   |  |  分布图     |  |
|  |                                  |  |   (环形图)  |  |
|  +----------------------------------+  +------------+  |
|                                  |
+----------------------------------+
```

## 组件结构

### 1. 统计卡片组件 (StatCard)
```vue
<template>
  <el-card class="stat-card">
    <div class="stat-content">
      <div class="stat-icon">
        <el-icon :size="24">
          <component :is="icon" />
        </el-icon>
      </div>
      <div class="stat-info">
        <div class="stat-value">{{ value }}</div>
        <div class="stat-label">{{ label }}</div>
        <div class="stat-trend" v-if="trend">
          <span :class="trend.type">
            {{ trend.type === 'up' ? '↑' : '↓' }} {{ trend.value }}%
          </span>
          <span class="trend-text">{{ trend.text }}</span>
        </div>
      </div>
    </div>
  </el-card>
</template>
```

**属性说明**:
- `value`: 统计数值
- `label`: 统计标签
- `icon`: 图标组件
- `trend`: 趋势信息（可选）

### 2. 趋势图表组件 (TrendChart)
```vue
<template>
  <el-card class="chart-card">
    <template #header>
      <div class="chart-header">
        <span>今日订单趋势</span>
        <el-radio-group v-model="chartType" size="small">
          <el-radio-button label="line">折线图</el-radio-button>
          <el-radio-button label="bar">柱状图</el-radio-button>
        </el-radio-group>
      </div>
    </template>
    <div ref="chartRef" class="chart-container"></div>
  </el-card>
</template>
```

**功能特点**:
- 支持折线图/柱状图切换
- 自动适应容器大小
- 响应式数据更新
- 平滑的动画效果

### 3. 分布图表组件 (DistributionChart)
```vue
<template>
  <el-card class="chart-card">
    <template #header>
      <span>订单分类分布</span>
    </template>
    <div ref="pieChartRef" class="chart-container"></div>
  </el-card>
</template>
```

**功能特点**:
- 环形饼图展示
- 鼠标悬停显示详情
- 自动计算百分比
- 响应式布局

## 响应式设计

### 断点配置
- **PC端 (> 768px)**: 完整布局，4列统计卡片
- **平板端 (768px - 1024px)**: 2列布局
- **移动端 (< 768px)**: 1列布局（与主布局配合）

### 样式适配
```css
/* 统计卡片响应式 */
.stat-cards {
  display: grid;
  gap: 20px;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
}

/* 图表区域响应式 */
.charts-row {
  margin-top: 20px;
}

.charts-row .el-col:first-child {
  width: 66.67%;
}

.charts-row .el-col:last-child {
  width: 33.33%;
}

/* 移动端调整 */
@media (max-width: 768px) {
  .charts-row .el-col {
    width: 100% !important;
  }
}
```

## 交互设计

### 统计卡片
- 悬停效果：轻微阴影变化
- 点击反馈：无特殊交互，保持视觉稳定
- 数据更新：数字变化动画

### 图表切换
- 平滑过渡：使用 ECharts 的动画效果
- 实时更新：数据变化时自动重绘
- 工具提示：鼠标悬停显示详细数据

### 自动刷新
- 定时器：每分钟自动更新数据
- 加载状态：图表更新时显示 loading
- 错误处理：数据获取失败时显示错误信息

## 性能优化

### 渲染优化
- 图表按需加载：只在显示时初始化
- 数据缓存：避免频繁请求
- 虚拟滚动：大数据量时考虑

### 资源管理
- 定时器清理：组件卸载时清除
- 图表实例复用：避免重复创建
- 内存泄漏防护：监听器正确清理

### 代码优化
- 组件拆分：统计卡片和图表组件化
- 抽象逻辑：提取公共图表配置
- 类型定义：完整的 TypeScript 支持

## 开发指南

### 添加新的统计卡片
1. 在 `components/` 下创建新卡片组件
2. 在 Dashboard 中引入并使用
3. 配置对应的 API 接口
4. 添加图标和样式

### 添加新图表
1. 使用 ECharts 创建新图表组件
2. 配置图表选项和数据格式
3. 实现数据获取逻辑
4. 添加响应式布局支持

### 修改现有布局
1. 调整栅格系统配置
2. 修改卡片样式和间距
3. 更新图表容器大小
4. 测试不同屏幕尺寸

## 注意事项

### 设计规范
- 保持统一的视觉风格
- 使用项目规定的颜色方案
- 图标使用 Element Plus 图标库
- 字体大小和间距遵循设计规范

### 兼容性
- 确保浏览器兼容性
- 测试不同屏幕尺寸
- 考虑低性能设备优化
- 注意移动端触摸交互

### 数据安全
- 敏感数据脱敏处理
- 防止 XSS 攻击
- API 调用错误处理
- 数据验证和过滤