# PMS 项目详情模块 - 演进路线图

## 当前状态 (v1.3.0)

### 已实现功能
- ✅ 横屏布局项目详情页
- ✅ Canvas 节点流程图可视化
- ✅ 节点负责人管理（单选/多选）
- ✅ 节点排期与工时管理
- ✅ 项目权限码系统
- ✅ 基本信息编辑
- ✅ 文件管理（树形结构）
- ✅ 项目结算功能
- ✅ 项目评价功能
- ✅ 操作记录查看
- ✅ 时间线编辑
- ✅ 角色批量分配

### 已知技术债务
- ⚠️ `owner` 对象字段不统一（`id` vs `open_id`）
- ⚠️ 节点详情组件文件过大（~6000 行）
- ⚠️ 缺少单元测试
- ⚠️ 部分组件耦合度高

## 短期优化 (v1.4.0 - 3个月内)

### 性能优化

#### 1. Canvas 流程图优化
```javascript
// 当前: 直接绘制所有节点
// 目标: 虚拟滚动 + 懒加载

class OptimizedFlowChart {
  constructor() {
    this.visibleNodes = new Set()
    this.nodeCache = new Map()
  }

  // 只绘制可视区域节点
  drawVisibleNodes(scrollTop, containerHeight) {
    const visibleRange = this.calculateVisibleRange(scrollTop, containerHeight)
    this.visibleNodes = this.nodes.filter(node =>
      node.y >= visibleRange.top && node.y <= visibleRange.bottom
    )
  }
}
```

#### 2. 组件懒加载
```javascript
// 当前: 全量导入组件
import BasicInfo from '@/pagesProject/components/basic-info.vue'
import TaskNode from '@/pagesProject/components/task-node.vue'
// ...

// 目标: 按需加载
const BasicInfo = () => import('@/pagesProject/components/basic-info.vue')
const TaskNode = () => import('@/pagesProject/components/task-node.vue')
```

#### 3. 数据缓存策略
```javascript
// 目标: 实现节点数据缓存
class NodeDataCache {
  constructor() {
    this.cache = new Map()
    this.maxAge = 5 * 60 * 1000  // 5分钟
  }

  get(key) {
    const item = this.cache.get(key)
    if (!item) return null

    if (Date.now() - item.timestamp > this.maxAge) {
      this.cache.delete(key)
      return null
    }

    return item.data
  }

  set(key, data) {
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    })
  }
}
```

### 用户体验优化

#### 1. 节点搜索功能
```vue
<!-- 目标: 添加节点搜索框 -->
<view class="node-search">
  <uni-search-bar
    v-model="searchKeyword"
    placeholder="搜索节点名称"
    @input="handleNodeSearch"
  />
</view>

<script>
methods: {
  handleNodeSearch(keyword) {
    // 1. 过滤节点列表
    // 2. 高亮匹配节点
    // 3. 自动滚动到第一个匹配项
  }
}
</script>
```

#### 2. 节点负责人搜索
```javascript
// 目标: 下拉选择支持搜索
<zxz-uni-data-select
  :filterable="true"  // ✅ 已支持
  :remote-method="searchUsers"
  :loading="searchLoading"
/>
```

#### 3. 操作快捷键
```javascript
// 目标: 支持键盘快捷键
document.addEventListener('keydown', (e) => {
  // Ctrl/Cmd + S: 保存当前编辑
  if ((e.ctrlKey || e.metaKey) && e.key === 's') {
    e.preventDefault()
    this.saveCurrentEdit()
  }

  // Ctrl/Cmd + F: 搜索节点
  if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
    e.preventDefault()
    this.focusNodeSearch()
  }
})
```

### 代码重构

#### 1. 拆分 node-details 组件
```
当前: node-details.vue (~6000 行)

目标结构:
node-details/
├── index.vue              # 主组件 (~500 行)
├── OwnerSelector.vue      # 负责人选择
├── ScheduleEditor.vue     # 排期编辑
├── WorkHourEditor.vue     # 工时编辑
├── TaskList.vue           # 任务列表
└── mixins/
    ├── owner.js           # 负责人逻辑
    ├── schedule.js        # 排期逻辑
    └── task.js            # 任务逻辑
```

#### 2. 统一数据字段
```javascript
// 当前: owner.id 和 owner.open_id 混用
// 目标: 统一使用 owner.id

// 迁移脚本
function migrateOwnerFields(data) {
  if (data.owner && data.owner.open_id) {
    data.owner.id = data.owner.open_id
    delete data.owner.open_id
  }
  return data
}
```

#### 3. 抽取通用逻辑
```javascript
// 当前: 权限检查分散在各组件
// 目标: 统一权限指令

// main.js
Vue.directive('permission', {
  inserted(el, binding, vnode) {
    const { value, arg } = binding
    const hasPermission = vnode.context.permission(value, arg || 'project')

    if (!hasPermission) {
      el.style.display = 'none'
      // 或 el.parentNode?.removeChild(el)
    }
  }
})

// 使用
<button v-permission="2001" v-permission:project>
  编辑负责人
</button>
```

## 中期规划 (v2.0.0 - 6-12个月)

### 实时协作

#### 1. WebSocket 集成
```javascript
// 目标: 实时推送节点变更
class ProjectWebSocket {
  constructor(projectId) {
    this.ws = new WebSocket(`wss://api.example.com/projects/${projectId}`)
    this.listeners = new Map()
  }

  connect() {
    this.ws.onmessage = (event) => {
      const { type, data } = JSON.parse(event.data)

      switch (type) {
        case 'NODE_UPDATED':
          this.emit('node-updated', data)
          break
        case 'NODE_OWNER_CHANGED':
          this.emit('owner-changed', data)
          break
        case 'PROJECT_STATE_CHANGED':
          this.emit('state-changed', data)
          break
      }
    }
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event).push(callback)
  }

  emit(event, data) {
    const callbacks = this.listeners.get(event) || []
    callbacks.forEach(cb => cb(data))
  }
}
```

#### 2. 协作状态指示
```vue
<template>
  <view class="collaborators">
    <view
      v-for="user in activeUsers"
      :key="user.id"
      class="user-avatar"
      :style="{ border: `2px solid ${user.color}` }"
    >
      <image :src="user.avatar" />
      <view class="status-indicator"></view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      activeUsers: []
    }
  },
  mounted() {
    this.ws.on('user-joined', (user) => {
      this.activeUsers.push(user)
    })
  }
}
</script>
```

### 节点依赖关系

#### 1. 可视化依赖图
```javascript
// 目标: 节点间依赖关系可视化
class NodeDependencyGraph {
  constructor(nodes) {
    this.nodes = nodes
    this.dependencies = this.buildDependencies()
  }

  buildDependencies() {
    // 分析节点间的依赖关系
    const deps = new Map()

    this.nodes.forEach(node => {
      const depsNodes = this.findDependentNodes(node)
      deps.set(node.id, depsNodes)
    })

    return deps
  }

  drawDependencies(ctx) {
    this.dependencies.forEach((targets, sourceId) => {
      const source = this.nodes.find(n => n.id === sourceId)

      targets.forEach(targetId => {
        const target = this.nodes.find(n => n.id === targetId)
        this.drawArrow(ctx, source, target)
      })
    })
  }
}
```

#### 2. 依赖约束检查
```javascript
// 目标: 排期时检查依赖约束
function validateNodeSchedule(node, newStartDate, newEndDate) {
  const deps = node.dependencies || []

  // 检查前置节点是否完成
  const incompleteDeps = deps.filter(dep =>
    dep.state.code !== 0 && dep.schedule.end > newStartDate
  )

  if (incompleteDeps.length > 0) {
    return {
      valid: false,
      message: '存在未完成的前置节点',
      conflictingNodes: incompleteDeps
    }
  }

  // 检查后置节点
  const dependentNodes = findDependentNodes(node)
  const conflictDeps = dependentNodes.filter(dep =>
    dep.schedule.start < newEndDate
  )

  if (conflictDeps.length > 0) {
    return {
      valid: false,
      message: '排期与后置节点冲突',
      conflictingNodes: conflictDeps
    }
  }

  return { valid: true }
}
```

### 移动端适配

#### 1. 响应式布局
```scss
// 当前: 固定横屏布局
// 目标: 响应式适配

.project-main {
  // 桌面端 (≥1024px)
  @media (min-width: 1024px) {
    flex-direction: row;
    .main-chart { width: 60%; }
    .main-article { width: 40%; }
  }

  // 平板端 (768-1023px)
  @media (max-width: 1023px) and (min-width: 768px) {
    flex-direction: column;
    .main-chart { height: 50vh; }
    .main-article { height: 50vh; }
  }

  // 移动端 (<768px)
  @media (max-width: 767px) {
    flex-direction: column;
    .main-chart { height: 40vh; }
    .main-article { height: 60vh; }

    // 流程图改为垂直滚动
    .flow-chart {
      flex-direction: column;
    }
  }
}
```

#### 2. 触摸交互优化
```javascript
// 目标: 支持触摸手势
class TouchGestureHandler {
  constructor(element) {
    this.element = element
    this.touchStartX = 0
    this.touchStartY = 0
  }

  init() {
    this.element.addEventListener('touchstart', (e) => {
      this.touchStartX = e.touches[0].clientX
      this.touchStartY = e.touches[0].clientY
    })

    this.element.addEventListener('touchend', (e) => {
      const deltaX = e.changedTouches[0].clientX - this.touchStartX
      const deltaY = e.changedTouches[0].clientY - this.touchStartY

      // 水平滑动切换节点
      if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {
        if (deltaX > 0) {
          this.emit('swipe-right')
        } else {
          this.emit('swipe-left')
        }
      }
    })
  }
}
```

## 长期愿景 (v3.0.0 - 1-2年)

### AI 辅助功能

#### 1. 智能排期推荐
```javascript
// 目标: 基于历史数据推荐排期
class AIDurationPredictor {
  async predictDuration(node) {
    // 1. 获取历史相似节点
    const historyNodes = await this.fetchSimilarNodes(node)

    // 2. 分析完成时间分布
    const durations = historyNodes.map(n => {
      const start = new Date(n.schedule.start)
      const end = new Date(n.schedule.end)
      return (end - start) / (1000 * 60 * 60 * 24)  // 天数
    })

    // 3. 计算推荐值
    const avg = durations.reduce((a, b) => a + b) / durations.length
    const std = Math.sqrt(durations.map(d => Math.pow(d - avg, 2)).reduce((a, b) => a + b) / durations.length)

    return {
      recommended: Math.round(avg),
      min: Math.round(avg - std),
      max: Math.round(avg + std),
      confidence: this.calculateConfidence(durations)
    }
  }
}
```

#### 2. 风险预警
```javascript
// 目标: 自动识别项目风险
class ProjectRiskAnalyzer {
  analyze(project) {
    const risks = []

    // 1. 逾期风险
    const overdueNodes = project.nodes.filter(n =>
      n.state.code === 1 &&
      new Date(n.schedule.end) < new Date()
    )
    if (overdueNodes.length > 0) {
      risks.push({
        type: 'OVERDUE',
        level: 'HIGH',
        message: `${overdueNodes.length} 个节点已逾期`,
        nodes: overdueNodes
      })
    }

    // 2. 负载不均风险
    const workload = this.calculateWorkload(project)
    const overloaded = workload.filter(w => w.hours > 40)
    if (overloaded.length > 0) {
      risks.push({
        type: 'OVERLOAD',
        level: 'MEDIUM',
        message: '部分成员工作负载过高',
        users: overloaded
      })
    }

    // 3. 关键路径风险
    const criticalPath = this.findCriticalPath(project)
    const delayedCritical = criticalPath.filter(n =>
      n.state.code !== 0 &&
      new Date(n.schedule.end) < new Date()
    )
    if (delayedCritical.length > 0) {
      risks.push({
        type: 'CRITICAL_PATH_DELAY',
        level: 'HIGH',
        message: '关键路径存在延期',
        nodes: delayedCritical
      })
    }

    return risks
  }
}
```

#### 3. 智能分配
```javascript
// 目标: 自动推荐负责人
class SmartAssigner {
  async recommendOwners(node) {
    // 1. 获取可用成员
    const members = await this.fetchAvailableMembers()

    // 2. 计算匹配度
    const scored = members.map(member => ({
      ...member,
      score: this.calculateScore(node, member)
    }))

    // 3. 排序返回
    return scored
      .sort((a, b) => b.score - a.score)
      .slice(0, 5)
  }

  calculateScore(node, member) {
    let score = 0

    // 技能匹配 (+30)
    if (this.hasSkill(member, node.requiredSkills)) {
      score += 30
    }

    // 历史经验 (+25)
    const experience = this.getExperience(member, node.type)
    score += Math.min(experience * 5, 25)

    // 当前负载 (-20)
    const workload = this.getCurrentWorkload(member)
    score -= Math.min(workload / 2, 20)

    // 可用性 (+15)
    if (this.isAvailable(member, node.schedule)) {
      score += 15
    }

    return score
  }
}
```

### 跨项目分析

#### 1. 资源负载分析
```javascript
// 目标: 跨项目资源负载可视化
class ResourceAnalyzer {
  async analyzeUser(userId) {
    // 1. 获取用户参与的所有项目
    const projects = await this.fetchUserProjects(userId)

    // 2. 获取每个项目的工作负载
    const workloads = await Promise.all(
      projects.map(p => this.calculateProjectWorkload(p, userId))
    )

    // 3. 生成负载曲线
    return {
      total: workloads.reduce((a, b) => a + b, 0),
      byProject: workloads,
      timeline: this.generateTimeline(workloads),
      recommendations: this.generateRecommendations(workloads)
    }
  }
}
```

#### 2. 项目模板
```javascript
// 目标: 项目模板系统
class ProjectTemplate {
  async createFromTemplate(templateId, customData) {
    // 1. 获取模板
    const template = await this.fetchTemplate(templateId)

    // 2. 克隆节点结构
    const nodes = this.cloneNodes(template.nodes)

    // 3. 应用自定义数据
    const project = {
      ...template,
      ...customData,
      nodes: this.applyCustomData(nodes, customData)
    }

    // 4. 创建项目
    return await this.createProject(project)
  }

  saveAsTemplate(projectId, templateName) {
    // 1. 获取项目数据
    const project = await this.fetchProject(projectId)

    // 2. 移除敏感信息
    const template = this.sanitizeProject(project)

    // 3. 保存为模板
    return await this.saveTemplate({
      name: templateName,
      ...template
    })
  }
}
```

### 数据看板

#### 1. 项目仪表盘
```vue
<template>
  <view class="project-dashboard">
    <!-- 项目概览 -->
    <view class="overview">
      <stat-card title="总项目" :value="stats.total" />
      <stat-card title="进行中" :value="stats.inProgress" />
      <stat-card title="已完成" :value="stats.completed" />
      <stat-card title="逾期" :value="stats.overdue" />
    </view>

    <!-- 节点状态分布 -->
    <view class="node-distribution">
      <pie-chart :data="nodeStats" />
    </view>

    <!-- 负载分析 -->
    <view class="workload-analysis">
      <bar-chart :data="workloadData" />
    </view>

    <!-- 趋势分析 -->
    <view class="trend-analysis">
      <line-chart :data="trendData" />
    </view>
  </view>
</template>
```

## 技术栈演进

### 前端
```
当前: Vue 2.0 + uni-app
  ↓
目标: Vue 3.0 + Vite + TypeScript

优势:
- 更好的性能
- Composition API
- 类型安全
- 更小的包体积
```

### 状态管理
```
当前: Vuex
  ↓
目标: Pinia

优势:
- 更简单的 API
- TypeScript 支持
- 模块化设计
- 更好的 DevTools
```

### 构建工具
```
当前: HBuilderX
  ↓
目标: Vite + CLI

优势:
- 更快的构建
- 更好的热更新
- 更灵活的配置
- 更好的生态
```

## 迁移计划

### 阶段 1: 准备阶段 (1个月)
- [ ] 代码库分析
- [ ] 技术债务清单
- [ ] 依赖项升级计划
- [ ] 回归测试套件

### 阶段 2: 重构阶段 (3个月)
- [ ] 组件拆分
- [ ] 字段统一
- [ ] 权限系统重构
- [ ] 性能优化

### 阶段 3: 新功能阶段 (6个月)
- [ ] 实时协作
- [ ] 依赖关系
- [ ] 移动端适配

### 阶段 4: 升级阶段 (3个月)
- [ ] Vue 3 迁移
- [ ] Pinia 迁移
- [ ] TypeScript 适配

## 成功指标

### 性能指标
- [ ] 首屏加载时间 < 2s
- [ ] 节点渲染 60fps
- [ ] 内存占用 < 100MB

### 质量指标
- [ ] 单元测试覆盖率 > 80%
- [ ] E2E 测试场景 > 50
- [ ] Bug 率 < 1%

### 用户体验指标
- [ ] 操作响应时间 < 100ms
- [ ] 用户满意度 > 4.5/5
- [ ] 功能使用率 > 70%
