# PSC 项目模板模块 (Project Template)

## 模块定位

项目模板模块是 PSC（项目配置系统）的核心模块，负责定义项目执行的标准流程和规范。通过预配置的节点树、触发事件和标签，为新项目创建提供标准化模板。

## 核心数据模型

### Template（项目模板）
```
{
  id: number,                    // 模板ID
  code: string,                  // 模板编码（系统自动生成）
  name: string,                  // 模板名称
  currentName: string,           // 当前名称（列表显示用）
  remark: string,                // 备注说明
  initialStatus: string,         // 初始状态（枚举值）
  isActive: boolean,             // 启用状态（true=启用, false=禁用）
  labels: number[],              // 关联标签ID数组
  nodeList: TemplateNode[],      // 节点树结构
  events: TriggerEvent[],        // 触发事件配置
  others: object,                // 其他扩展信息
  createdAt: string,             // 创建时间
}
```

### TemplateNode（模板节点）
```
{
  id: string | number,           // 节点ID（前端临时用 `node-${nextId}` 格式）
  label: string,                 // 显示名称
  type: string,                  // 节点类型: 'root' | 'milestone' | 'main' | 'child'
  nodeDefinitionId: number,      // 节点定义ID
  nodeDefinitionVersionId: number, // 节点定义版本ID
  nodeCode: string,              // 节点编码
  nodeName: string,              // 节点名称
  category: string,              // 节点分类: MILESTONE | MAIN_NODE | SUB_NODE
  parent: number | string,       // 父节点ID
  sortOrder: number,             // 排序序号
  children: TemplateNode[],      // 子节点数组
}
```

### TriggerEvent（触发事件）
```
{
  id: string,                    // 事件ID
  content: string,               // 事件描述
  config: {                      // 事件配置（来自TriggerEventDialog）
    triggerScope: string,        // 触发范围: PROJECT | NODE
    projectStatus: string,       // 项目状态: NOT_START | IN_PROGRESS | CHANGING | FINISHED
    node: string,                // 节点标识
    status: string,              // 节点状态
    actions: string[],           // 动作类型: AUTO_SHOW | AUTO_HIDE | SECOND_CONFIRM
    targetNode: string,          // 目标节点
    targetPosition: string,      // 显示位置: BEFORE | AFTER
  }
}
```

### TemplateLabel（模板标签）
```
{
  id: number,                    // 标签ID
  name: string,                  // 标签名称
}
```

## 节点类型与层级关系

项目模板采用三级节点树结构：

1. **root（根节点）**: 虚拟根节点，显示为模板名称
2. **milestone（里程碑）**: 第一级子节点，对应 `MILESTONE` 分类
3. **main（主节点）**: 里程碑的子节点，对应 `MAIN_NODE` 分类
4. **child（子节点）**: 主节点的子节点，对应 `SUB_NODE` 分类

**拖拽规则：**
- 子节点只能拖到主节点下（inner）或在同一主节点下排序（prev/next）
- 主节点只能拖到里程碑下（inner）或在同一里程碑下排序（prev/next）
- 里程碑只能在根节点下同级排序（prev/next），不允许作为子节点

## API 端点规范

### 基础CRUD

#### GET /psc/project/templates
获取项目模板列表

**Query参数：**
```typescript
{
  code?: string,                 // 模板编码（模糊搜索）
  currentName?: string,          // 模板名称（模糊搜索）
  pageNum?: number,              // 页码（默认1）
  pageSize?: number,             // 每页数量（默认10）
  pageSort?: string,             // 排序（格式：FIELD:ORDER，如 ID:DESC）
}
```

**响应示例：**
```json
{
  "data": {
    "items": [
      {
        "id": 1,
        "code": "TPL001",
        "currentName": "标准研发项目模板",
        "isActive": false,
        "createdAt": "2024-01-15T10:30:00Z"
      }
    ],
    "pagination": {
      "total": 25
    }
  }
}
```

#### GET /psc/project/templates/{id}
获取项目模板详情

**响应示例：**
```json
{
  "data": {
    "id": 1,
    "document": {
      "code": "TPL001",
      "name": "标准研发项目模板",
      "remark": "标准研发流程模板",
      "isActive": true,
      "initialStatus": "NOT_START",
      "labels": [
        { "id": 1, "name": "研发类" }
      ]
    },
    "nodeData": {
      "list": [
        {
          "id": "node-1",
          "nodeName": "需求阶段",
          "category": "MILESTONE",
          "nodeDefinitionId": 101,
          "nodeDefinitionVersionId": 1001,
          "nodeCode": "MILESTONE_REQ",
          "parent": null,
          "sortOrder": 1,
          "children": [
            {
              "id": "node-2",
              "nodeName": "需求收集",
              "category": "MAIN_NODE",
              "nodeDefinitionId": 102,
              "nodeDefinitionVersionId": 1002,
              "nodeCode": "REQ_COLLECT",
              "parent": "node-1",
              "sortOrder": 1,
              "children": []
            }
          ]
        }
      ],
      "events": []
    },
    "initialStatus": "NOT_START",
    "others": null
  }
}
```

#### POST /psc/project/templates
新增项目模板

**请求体：**
```json
{
  "name": "新项目模板",
  "remark": "模板备注",
  "initialStatus": "NOT_START",
  "labelIds": [1, 2],
  "nodes": [
    {
      "versionId": 1001,
      "parent": null,
      "sortOrder": 1
    }
  ]
}
```

**响应示例：**
```json
{
  "data": {
    "insertId": 123
  }
}
```

#### PUT /psc/project/templates/{id}
更新项目模板

**请求体：** 同新增，但包含 id 字段

#### DELETE /psc/project/templates
删除项目模板

**请求体：**
```json
{
  "ids": [1, 2, 3]
}
```

#### PATCH /psc/project/templates
批量启用/禁用

**请求体：**
```json
{
  "ids": [1, 2],
  "isActive": true
}
```

### 枚举与标签

#### GET /psc/project/templates/enums
获取模板相关枚举

**响应示例：**
```json
{
  "data": {
    "choices": {
      "disable_flag": [
        { "value": true, "label": "是" },
        { "value": false, "label": "否" }
      ]
    },
    "initialStatus": [
      { "value": "NOT_START", "label": "未开始" },
      { "value": "IN_PROGRESS", "label": "进行中" }
    ]
  }
}
```

#### GET /psc/project/template/labels
获取标签列表

**响应示例：**
```json
{
  "data": [
    { "id": 1, "name": "研发类" },
    { "id": 2, "name": "实施类" }
  ]
}
```

#### POST /psc/project/template/labels
新增标签

**请求体：**
```json
{
  "name": "新标签"
}
```

**响应示例：**
```json
{
  "data": {
    "id": 3,
    "name": "新标签"
  }
}
```

### 节点定义关联

#### GET /psc/node/definitions/simple
获取节点定义简单列表（用于下拉选择）

**响应示例：**
```json
{
  "data": {
    "items": [
      {
        "id": 101,
        "code": "MILESTONE_REQ",
        "currentName": "需求阶段",
        "currentVersionId": 1001,
        "currentCategory": "MILESTONE"
      }
    ]
  }
}
```

## 页面路由结构

```
/psc/projecttemplate
├── /add                      # 新增模板（保存后跳转到编辑页）
├── /add/:addId              # 从已有模板复制新增
└── /edit/:id/:type          # 编辑/查看模板
                              # type: 'edit' | 'view'
```

## 组件架构

### 主页面
- **index.vue**: 模板列表页，支持搜索、排序、启用/禁用、删除、复制
- **add.vue**: 新增页容器，提交后跳转到编辑页
- **edit.vue**: 编辑页容器，仅数据传递

### 核心组件
- **temRender.vue**: 模板编辑主组件，包含节点树和基础信息
  - 左侧：可拖拽节点树（el-tree）
  - 右侧：基础信息表单、触发事件配置
- **temDetailRender.vue**: 基础信息表单组件
  - 模板编码、名称、启用状态、初始状态
  - 标签选择（支持新增标签）
  - 备注输入
  - 触发事件表格
- **TriggerEventDialog.vue**: 触发事件配置弹窗
  - 触发条件配置（项目事件/节点事件）
  - 动作配置（自动弹窗/自动隐藏/二次确认）
  - 目标节点与位置配置

## 业务规则

1. **模板编码自动生成**: 新增时 code 由系统自动生成，前端显示为禁用状态
2. **节点树唯一性**: 同一节点定义不能在模板中重复使用
3. **里程碑校验**: 每个里程碑下至少要有一个主节点
4. **拖拽限制**: 遵循三级层级结构，不允许跨级拖拽
5. **标签支持**: 支持从列表选择或直接输入新名称创建
6. **初始状态**: 通过枚举接口获取可选项
7. **触发事件**: 当前版本添加事件按钮已禁用（待后端实现）

## 技术实现要点

### 节点树数据转换
```javascript
// 后端节点树 -> 前端树节点
const mapBackendNodeToTreeNode = (node) => ({
  id: node.id,
  label: node.nodeName,
  type: mapCategoryToType(node.category),
  nodeDefinitionId: node.nodeDefinitionId,
  nodeDefinitionVersionId: node.nodeDefinitionVersionId,
  // ... 其他字段
});

// 前端树节点 -> 提交数据
const buildNodesForSubmit = () => {
  // 只保留 versionId, parent, sortOrder
  return nodes.map(n => ({
    versionId: n.nodeDefinitionVersionId,
    parent: n.parentVersionId ?? null,
    sortOrder: n.sortOrder
  }));
};
```

### 拖拽权限控制
```javascript
const allowDrop = (draggingNode, dropNode, type) => {
  const dragType = draggingNode.data?.type;
  const dropType = dropNode.data?.type;

  // 子节点只能拖到主节点下
  if (dragType === 'child') {
    if (type === 'inner') return dropType === 'main';
    if (type === 'prev' || type === 'next') {
      return dragParent === dropParent && dropParent.data?.type === 'main';
    }
  }
  // ... 其他类型规则
};
```

### 已使用节点过滤
```javascript
const collectUsedNodeDefinitionIds = () => {
  // 递归遍历树结构，收集已使用的节点定义ID
  // 用于过滤下拉选项，避免重复添加
};
```

## 权限说明

当前代码中权限校验已被注释，预留以下权限标识：
- `PSC.add_template`: 新增模板
- `PSC.change_template`: 修改模板
- `PSC.delete_template`: 删除模板
- `PSC.view_template`: 查看模板

## 与其他模块关系

1. **节点定义模块**: 模板节点引用节点定义的具体版本
2. **交付物定义**: 节点可关联交付物模板
3. **审核定义**: 节点可配置审核流程
4. **事件定义**: 触发事件可引用预定义事件
5. **项目角色**: 节点可分配角色权限

## 扩展设计策略

1. **版本管理**: 未来可支持模板版本控制，形成模板历史
2. **模板继承**: 支持基于现有模板创建子模板
3. **权限细化**: 节点级别的读写权限控制
4. **可视化增强**: 节点树可视化展示（如流程图、甘特图）
5. **导入导出**: 支持模板的导入导出功能

## 演进方向（Future Evolution）

1. **智能推荐**: 基于历史项目数据推荐最优模板配置
2. **动态模板**: 支持运行时动态调整模板结构
3. **模板市场**: 建立行业模板库，支持模板共享
4. **AI辅助**: 集成AI能力自动生成项目模板建议
5. **性能优化**: 大规模节点树的渲染优化（虚拟滚动）

## 特有名词快速索引

- **项目模板/模板**: Project Template，预定义的项目流程模板
- **节点树**: Template Node Tree，模板的三级层级结构
- **里程碑**: Milestone，节点树的第一级节点
- **主节点**: Main Node，里程碑下的子节点
- **子节点**: Child Node，主节点下的子节点
- **节点定义**: Node Definition，节点的模板定义（独立模块）
- **触发事件**: Trigger Event，基于项目/节点状态的自动化动作
- **模板标签**: Template Label，用于分类和筛选模板的标签
- **初始状态**: Initial Status，项目基于此模板创建时的默认状态
