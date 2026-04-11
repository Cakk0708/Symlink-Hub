# 项目模块

## 模块概述

项目模块是 PMS 系统的核心，负责项目的全流程管理。

### 核心功能
- 项目列表展示与筛选
- 项目创建（基于模板）
- 项目详情管理
- 项目状态控制（进行中、已完成、变更中、暂停）
- 项目成员管理
- 项目权限控制

---

## 项目状态枚举

| 状态值 | 说明 | 颜色标识 |
|--------|------|----------|
| 1 | 进行中 | 蓝色 `rgba(54, 115, 232, 0.2)` |
| 2 | 已完成 | 绿色 `rgba(61, 188, 47, 0.2)` |
| 3 | 变更中 | 紫色 `rgba(121, 58, 255, 0.2)` |
| 4 | 暂停 | 灰色 `rgba(110, 118, 118, 0.2)` |
| 5 | 归档 | 黄色 `rgba(245, 180, 0, 0.2)` |

---

## 项目列表页

### 文件位置
`pages/index/components/project.vue`

### 主要功能
- 项目列表展示（分页）
- 状态筛选
- 模板筛选
- 搜索功能
- 创建项目入口

### 数据结构
```javascript
{
	id: String,              // 项目ID
	name: String,            // 项目名称
	state: Number,           // 项目状态 (1-5)
	is_archive: Number,      // 是否归档 (0/1)
	template: String,        // 模板ID
	template_name: String,   // 模板名称
	owner: Object,           // 负责人信息
		{
			id: String,
			nickname: String,
			avatar: String
		},
	creator: Object,        // 创建者信息
	progress: Number,        // 完成进度
	start_time: String,      // 开始时间
	end_time: String,        // 结束时间
	description: String      // 项目描述
}
```

### 关键接口
```javascript
// 获取项目列表
GET /pm/project/list
参数：page, size, state, template, search

// 获取项目模板列表
GET /psc/project/templates/simple

// 获取项目分类
GET /pm/project/categories

// 创建项目
POST /pm/project/create
```

---

## 项目详情页

### 文件位置
`pagesProject/index/index.vue`

### 特殊配置
- **横屏模式**：`"orientation": "landscape"`
- **核心组件**：节点流程图 + 标签页管理

### 页面结构
```
┌──────────────────────────────────────────────────────────────┐
│  头部                                                         │
│  ┌──────────┬──────────┬──────────┬──────────────────────┐  │
│  │ 关注/项目 │ 状态进度 │ 操作菜单 │ 导航按钮              │  │
│  └──────────┴──────────┴──────────┴──────────────────────┘  │
├──────────────────────────────────────────────────────────────┤
│  节点流程图 (Canvas)                                          │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  里程碑 → 主节点 → 子节点                              │  │
│  └────────────────────────────────────────────────────────┘  │
├──────────────────────────────────────────────────────────────┤
│  节点详情 + 标签页                                            │
│  ┌────────────┬────────────────────────────────────────────┐ │
│  │            │  [基本信息][文件][需求][缺陷]...           │ │
│  │  节点详情  │  ┌──────────────────────────────────────┐ │ │
│  │            │  │                                        │ │ │
│  │  基本信息  │  │         标签页内容                     │ │ │
│  │  交付物    │  │                                        │ │ │
│  │  审批记录  │  │                                        │ │ │
│  │            │  │                                        │ │ │
│  └────────────┘  └──────────────────────────────────────┘ │ │
└──────────────────────────────────────────────────────────────┘
```

### 头部操作
- **关注**：关注/取消关注项目
- **状态**：查看/切换项目状态
- **操作菜单**：暂停/继续、变更、删除
- **导航**：快速跳转到各模块

### 标签页组件
| 组件名 | 文件 | 说明 |
|--------|------|------|
| basic-info | `components/basic-info.vue` | 基本信息 |
| delivery-flie | `components/delivery-flie.vue` | 文件管理 |
| requirement | `components/requirement.vue` | 需求管理 |
| defect | `components/defect.vue` | 缺陷管理 |
| records | `components/records.vue` | 操作记录 |
| project-evaluate | `components/project-evaluate.vue` | 评价 |
| project-settlement | `components/project-settlement.vue` | 结算 |

---

## 项目模板

### 模板接口
```javascript
// 获取简化模板列表
GET /psc/project/templates/simple

响应格式：
{
	code: 0,
	data: {
		items: [
			{
				currentVersionId: String,   // 当前版本ID
				code: String,               // 模板代码
				name: String,               // 模板名称
				currentName: String         // 当前版本名称
			}
		]
	}
}
```

### 模板数据转换
```javascript
// 转换为选项格式
template.map(item => ({
	value: item.currentVersionId,
	text: item.currentName
}))

// 转换为筛选格式
template.map(item => ({
	id: item.currentVersionId,
	code: item.code,
	name: item.name,
	label: item.name,
	value: item.currentVersionId,
	active: false
}))
```

---

## 项目权限

### 权限码
| 权限码 | 说明 |
|--------|------|
| 1001 | 编辑项目基本信息 |
| 1002 | 删除项目 |
| 1003 | 变更项目 |
| 1004 | 暂停/继续项目 |
| 1005 | 管理项目成员 |
| 1006 | 查看项目结算 |
| 1007 | 评价项目 |

### 权限检查
```javascript
// 检查是否有编辑权限
if (permission(1001, 'project')) {
	// 显示编辑按钮
}

// 检查是否有删除权限
if (permission(1002, 'project')) {
	// 显示删除按钮
}
```

---

## 项目变更流程

### 变更入口
项目详情页 → 操作菜单 → 变更

### 变更弹窗
`pagesProject/components/changes-pop.vue`

### 变更状态
项目进入"变更中"状态（state = 3）

### 变更记录
记录变更历史，可在项目结算中查看

---

## 项目结算

### 结算组件
`pagesProject/components/project-settlement.vue`

### 结算子功能
- 贡献度计算
- 变更日志
- 结算点数计算

### 结算条件
- 项目已完成（state = 2）
- 所有节点已完成
- 有结算权限（1006）

---

## 项目评价

### 评价组件
`pagesProject/components/project-evaluate.vue`

### 评价条件
- 项目已完成
- 有评价权限（1007）
- 未评价过

### 评价数据
```javascript
{
	projectId: String,
	sections: [
		{
			name: String,      // 评价维度名称
			score: Number,     // 评分
			remark: String     // 备注
		}
	]
}
```

---

## 常见操作

### 创建项目
```javascript
// 点击创建按钮
this.$refs.ref_components_createlists.open()

// 选择模板
// 填写项目信息
// 提交创建
```

### 查看项目详情
```javascript
// 跳转到项目详情页
uni.navigateTo({
	url: `/pagesProject/index/index?id=${projectId}`
})
```

### 更新项目状态
```javascript
// 暂停项目
async handlePause() {
	await request({
		url: `pm/project/${projectId}/state`,
		method: 'POST',
		data: { state: 4 }
	})
}

// 继续项目
async handleResume() {
	await request({
		url: `pm/project/${projectId}/state`,
		method: 'POST',
		data: { state: 1 }
	})
}
```

### 删除项目
```javascript
async handleDelete() {
	uni.showModal({
		title: '确认删除',
		content: '删除后无法恢复',
		success: async (res) => {
			if (res.confirm) {
				await request({
					url: `pm/project/${projectId}`,
					method: 'DELETE'
				})
				uni.navigateBack()
			}
		}
	})
}
```

---

## 关键文件索引

| 功能 | 文件路径 |
|------|----------|
| 项目列表 | `pages/index/components/project.vue` |
| 项目详情 | `pagesProject/index/index.vue` |
| 基本信息标签页 | `pagesProject/components/basic-info.vue` |
| 文件管理标签页 | `pagesProject/components/delivery-flie.vue` |
| 项目结算 | `pagesProject/components/project-settlement.vue` |
| 项目评价 | `pagesProject/components/project-evaluate.vue` |
| 创建项目弹窗 | `components/task-createlists/task-createlists.vue` |
| 变更弹窗 | `pagesProject/components/changes-pop.vue` |
