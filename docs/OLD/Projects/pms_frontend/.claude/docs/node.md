# 节点系统

## 系统概述

节点系统是 PMS 项目管理的核心，用于管理项目的里程碑和任务节点。

### 节点类型
| 类型值 | 说明 | 颜色 |
|--------|------|------|
| 1 | 里程碑 | 红色 |
| 2 | 主节点 | 蓝色 |
| 3 | 子节点 | 绿色 |

### 节点状态
| 状态值 | 说明 |
|--------|------|
| 1 | 进行中 |
| 2 | 已完成 |
| 4 | 未开始 |

---

## 节点流程图

### 组件位置
`pagesProject/components/flow-chart/flow-chart.vue`

### 渲染方式
使用 **Canvas** 绘制节点树

### 核心功能
- 节点可视化展示
- 节点间连线
- 节点状态指示
- 节点选择交互
- 滚动同步

### 节点数据结构
```javascript
{
	id: String,              // 节点ID
	name: String,            // 节点名称
	type: Number,            // 节点类型 (1/2/3)
	state: Number,           // 节点状态 (1/2/4)
	owner: Object,           // 负责人
		{
			id: String,
			nickname: String,
			avatar: String
		},
	parent_id: String,      // 父节点ID
	children: Array,         // 子节点列表
	start_time: String,      // 开始时间
	end_time: String,        // 结束时间
	actual_end_time: String, // 实际完成时间
	sort: Number,            // 排序
	deliverables: Array,     // 交付物列表
	approvals: Array         // 审批记录
}
```

### Canvas 绘制逻辑
```javascript
// 1. 计算节点位置
// 2. 绘制节点矩形
// 3. 绘制节点连线
// 4. 绘制节点内容
// 5. 处理点击事件
```

---

## 节点详情

### 组件位置
`pagesProject/components/node-details/node-details.vue`

### 详情区域
```
┌──────────────────────────────────────────────┐
│  节点基本信息                                 │
│  - 节点名称                                  │
│  - 节点类型                                  │
│  - 节点状态                                  │
│  - 负责人                                    │
│  - 时间计划                                  │
├──────────────────────────────────────────────┤
│  节点交付物                                   │
│  - 文件列表                                  │
│  - 上传/下载                                 │
│  - 版本管理                                  │
├──────────────────────────────────────────────┤
│  审批反馈                                     │
│  - 审批记录                                  │
│  - 反馈意见                                  │
├──────────────────────────────────────────────┤
│  软件配置                                     │
│  - 配置列表                                  │
│  - 配置项管理                                │
├──────────────────────────────────────────────┤
│  时间线预设                                   │
│  - 时间节点                                  │
│  - 预设时间                                  │
├──────────────────────────────────────────────┤
│  变更文档附件                                 │
│  - 变更记录                                  │
│  - 附件管理                                  │
└──────────────────────────────────────────────┘
```

### 子组件
| 组件 | 功能 |
|------|------|
| module-info-section | 模块基本信息 |
| node-review-section | 审批反馈 |
| approval-feedback-section | 审批反馈详细 |
| software-config-list-section | 软件配置列表 |
| software-config-edit-section | 软件配置编辑 |
| timeline-preset-section | 时间线预设 |
| node-remark-section | 节点备注 |
| node-deliverable-section | 节点交付物 |
| change-doc-attachment-section | 变更文档附件 |

---

## 节点操作

### 节点权限
| 权限码 | 说明 |
|--------|------|
| 2001 | 编辑节点信息 |
| 2002 | 更改节点状态 |
| 2003 | 上传节点交付物 |
| 2004 | 审批节点 |
| 2005 | 分配节点负责人 |
| 2006 | 删除节点 |

### 更改节点状态
```javascript
async changeNodeState(nodeId, newState) {
	const res = await request({
		url: `pm/node/${nodeId}/state`,
		method: 'POST',
		data: { state: newState }
	})
	// 刷新节点数据
}
```

### 分配负责人
```javascript
async assignNodeOwner(nodeId, ownerId) {
	const res = await request({
		url: `pm/node/${nodeId}/owner`,
		method: 'POST',
		data: { owner_id: ownerId }
	})
}
```

### 上传交付物
```javascript
async uploadDeliverable(nodeId, file) {
	const res = await uploadFile({
		url: `pm/node/${nodeId}/deliverable`,
		filePath: file.path,
		name: 'file'
	})
}
```

---

## 节点树操作

### 添加节点
```javascript
// 通过树形组件添加
this.$refs.treeRef.addNode(nodeData)
```

### 编辑节点
```javascript
// 通过树形组件编辑
this.$refs.treeRef.editNode(nodeId, newData)
```

### 删除节点
```javascript
// 通过树形组件删除
this.$refs.treeRef.deleteNode(nodeId)
```

### 移动节点
```javascript
// 拖拽排序
this.$refs.treeRef.moveNode(nodeId, newParentId, newIndex)
```

---

## 节点交付物

### 交付物类型
- 文档文件
- 设计图纸
- 测试报告
- 其他附件

### 交付物状态
| 状态 | 说明 |
|------|------|
| draft | 草稿 |
| submitted | 已提交 |
| approved | 已通过 |
| rejected | 已驳回 |
| frozen | 已冻结 |

### 交付物操作
```javascript
// 上传交付物
async uploadDeliverable(nodeId, file) {
	// 上传文件
	// 关联到节点
}

// 下载交付物
async downloadDeliverable(deliverableId) {
	// 获取下载链接
	// 触发下载
}

// 冻结交付物
async freezeDeliverable(deliverableId) {
	await request({
		url: `pm/deliverable/${deliverableId}/freeze`,
		method: 'POST'
	})
}
```

---

## 节点审批

### 审批流程
```
节点完成
    ↓
提交审批
    ↓
审批人审批
    ↓
├─ 通过 → 节点状态变为已完成
│
└─ 驳回 → 节点状态回到进行中
```

### 审批记录
```javascript
{
	id: String,
	node_id: String,
	approver_id: String,
	approver_name: String,
	status: String,        // approved/rejected
	comment: String,
	created_at: String
}
```

---

## 节点时间管理

### 时间字段
- `start_time`：计划开始时间
- `end_time`：计划结束时间
- `actual_end_time`：实际完成时间

### 时间节点
```javascript
// 时间线预设
{
	node_id: String,
	preset_times: [
		{
			name: String,
			time: String
		}
	]
}
```

---

## 节点与项目状态

### 节点状态影响项目
- 所有节点完成 → 项目可完成
- 有节点进行中 → 项目进行中
- 项目变更中 → 节点可变更

### 节点完成度计算
```javascript
// 完成度 = 已完成节点数 / 总节点数
const progress = completedNodes / totalNodes
```

---

## 常见场景

### 场景1：创建子节点
```javascript
// 1. 选择父节点
// 2. 点击添加子节点
// 3. 填写节点信息
// 4. 保存节点
```

### 场景2：节点交付物管理
```javascript
// 1. 选择节点
// 2. 进入交付物区域
// 3. 上传文件
// 4. 提交交付物
// 5. 等待审批
```

### 场景3：节点审批
```javascript
// 1. 查看待审批节点
// 2. 查看交付物
// 3. 填写审批意见
// 4. 通过或驳回
```

---

## 关键文件索引

| 功能 | 文件路径 |
|------|----------|
| 节点流程图 | `pagesProject/components/flow-chart/flow-chart.vue` |
| 节点详情 | `pagesProject/components/node-details/node-details.vue` |
| 树形组件 | `pagesProject/components/tree/` |
| 节点基本信息 | `pagesProject/components/node-details/components/module-info-section.vue` |
| 节点交付物 | `pagesProject/components/node-details/components/node-deliverable-section.vue` |
| 节点审批 | `pagesProject/components/node-details/components/node-review-section.vue` |
