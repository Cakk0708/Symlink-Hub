---
name: project-detail-node_deliverable
description: 节点详情交付物模块专家，负责节点交付物的上传、下载、冻结、版本管理、状态流转以及与文件管理的交互。当用户提到"交付物"、"deliverable"、"上传附件"、"文件状态"、"冻结交付物"、"交付物版本"或相关术语时激活此技能。
---

# 节点详情交付物模块 (Node Detail Deliverable)

## 模块定位

节点详情交付物模块是 PMS 项目管理系统中负责管理节点级别交付物文件的核心组件。它位于 `pagesProject/components/node-details/node-details.vue`，处理交付物的完整生命周期：上传、存储、版本管理、状态控制和下载。

## 核心数据模型

### 交付物定义 (Deliverable Definition)
```javascript
// 交付物定义模板（从节点规则继承）
{
  id: Number,                    // 定义ID
  name: String,                  // 交付物名称
  required: Boolean,             // 是否必填
  classes: Array,                // 允许的文件扩展名 ['pdf', 'docx']
  has_template: Boolean,         // 是否有模板
  node_definition_deliverable_mapping_id: Number  // 映射关系ID
}
```

### 交付物实例 (Deliverable Instance)
```javascript
// 实际上传的交付物实例
{
  value: {
    id: Number,                  // 实例ID（关键）
    name: String,                // 文件名
    state: String,               // 状态: 'NORMAL' | 'FROZEN' | 'INITIAL_FROZEN'
    review: Number,              // 评审状态: 2=被拒绝
    has_template: Boolean        // 是否有模板
  },
  version: String,               // 当前版本
  tempVersion: String,           // 编辑中的版本
  note: String,                  // 备注
  tempNote: String,              // 编辑中的备注
  create_time: String,           // 创建时间
  focus: Boolean                 // 是否处于编辑状态
}
```

### 交付物状态枚举
| 状态值 | 说明 | 图标 | 可操作 |
|--------|------|------|--------|
| 'NORMAL' | 正常 | icon-a-lianjie11 | 上传、下载、冻结、删除 |
| 'FROZEN' | 冻结 | icon-a-dongjie1 | 仅解冻、下载 |
| 'INITIAL_FROZEN' | 初始冻结 | icon-a-bukejian11 | 仅解冻、下载 |

## API 接口规范

### 1. 文件上传
```
POST /pm/deliverables/file/upload
Content-Type: multipart/form-data

Response: { file_id: Number }
```

### 2. 创建交付物实例
```
POST /pm/deliverable/instances
Content-Type: application/json

Request: {
  projectNodeId: Number,
  definitionId: Number,
  nodeDefinitionDeliverableMappingId: Number,
  fileId: Number,
  url: null,
  version: '',
  remark: ''
}
```

### 3. 更新交付物实例
```
PATCH /pm/deliverable/instances/{instance_id}
Content-Type: application/json

// 更新文件
Request: { fileId: Number }

// 更新版本
Request: { version: String }

// 删除文件（fileId置null）
Request: { fileId: null }

// 更新备注
Request: { remark: String }
```

### 4. 删除交付物实例
```
DELETE /pm/deliverable/instances/{instance_id}
```

### 5. 冻结/解冻交付物
```
PATCH /project/at/freeze/{instance_id}
Content-Type: application/json

Request: {
  state: 'NORMAL' | 'FROZEN',
  node_id: Number
}
```

## 核心业务逻辑

### 上传流程
```javascript
// 判断是创建新实例还是更新已有实例
if (sub.value && sub.value.id) {
  // 已有实例 → PATCH 更新
  await updateDeliverableInstance(fileId, sub)
} else {
  // 新实例 → POST 创建
  await createDeliverableInstance(fileId, item)
}
// 刷新节点详情
await getNodeDetail(true)
```

### 删除流程
```javascript
// 清除文件（保留实例）
PATCH /pm/deliverable/instances/{id}
{ fileId: null }
// 刷新节点详情
```

### 状态判断模式
```javascript
// 判断是否冻结
const isFrozen = state => ['FROZEN', 'INITIAL_FROZEN'].includes(state)

// 判断是否可操作
const canOperate = state => state === 'NORMAL'

// 冻结切换
const toggleState = state => state === 'NORMAL' ? 'FROZEN' : 'NORMAL'
```

## 权限验证

| 权限码 | 功能 | 说明 |
|--------|------|------|
| 2009 | 上传/删除交付物 | permission(2009) |
| 2300 | 冻结/解冻交付物 | permission(2300) |
| 2001 | 编辑节点信息 | permission(2001) |

### 权限校验流程
```javascript
// 上传前校验
if (!permission(2009)) {
  uni.showToast({ title: '当前用户无操作权限', icon: 'none' })
  return
}

// 冻结前校验
if (!permission(2300)) {
  uni.showToast({ title: '当前用户无操作权限', icon: 'none' })
  return
}

// 超级管理员豁免
if (getUserInfo.is_superuser) {
  // 跳过权限校验
}
```

## 与其他模块关系

### 1. 节点模块
- **数据来源**: `nodeDetail.showList` 从节点规则生成交付物定义
- **状态依赖**: 节点完成后 (`nodeDetail.state.code == 2`) 禁止上传

### 2. 文件管理模块
- **共享存储**: 交付物文件存储在统一文件管理系统
- **file_id**: 通过上传接口获得文件ID，交付物实例引用该ID

### 3. 评审模块
- **评审拒绝**: `review == 2` 时显示"重新提交"按钮
- **状态联动**: 评审通过后交付物可被冻结

### 4. 任务模块
- **特殊交付物**: id=10001 的交付物跳转至飞书任务清单
- **GUID关联**: `getTaskListGuid` 用于任务跳转

## 常见业务场景

### 场景1: 首次上传交付物
```
1. 用户点击"上传附件"
2. 选择本地文件
3. 前端验证文件格式和大小
4. 调用 uploadFile() 获取 file_id
5. 调用 createDeliverableInstance() 创建实例
6. 刷新节点详情显示新上传的文件
```

### 场景2: 替换已有交付物
```
1. 检测到 sub.value.id 存在
2. 上传新文件获取新 file_id
3. 调用 updateDeliverableInstance() 更新 fileId
4. 刷新节点详情
```

### 场景3: 冻结交付物
```
1. 点击"冻结交付物"按钮
2. 确认对话框
3. 调用 freeze API 将状态改为 'FROZEN'
4. 更新前端状态和图标
5. 禁用上传和删除操作
```

### 场景4: 解冻交付物
```
1. 检测到 state 为 'FROZEN' 或 'INITIAL_FROZEN'
2. 点击"解冻交付物"直接执行（无需确认）
3. 调用 freeze API 将状态改为 'NORMAL'
4. 恢复操作权限
```

## 技术实现建议

### Django 后端
```python
# models.py
class DeliverableState(models.TextChoices):
    NORMAL = 'NORMAL', '正常'
    FROZEN = 'FROZEN', '冻结'
    INITIAL_FROZEN = 'INITIAL_FROZEN', '初始冻结'

class DeliverableInstance(models.Model):
    project_node = models.ForeignKey(ProjectNode, on_delete=models.CASCADE)
    definition = models.ForeignKey(DeliverableDefinition, on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.SET_NULL, null=True)
    state = models.CharField(max_length=20, choices=DeliverableState.choices, default=DeliverableState.NORMAL)
    version = models.CharField(max_length=50, blank=True)
    remark = models.TextField(blank=True)

# serializers.py
class DeliverableInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliverableInstance
        fields = ['id', 'file', 'state', 'version', 'remark', 'created_at']

# views.py
class DeliverableInstanceViewSet(viewsets.ModelViewSet):
    queryset = DeliverableInstance.objects.select_related('project_node', 'definition', 'file')
    serializer_class = DeliverableInstanceSerializer
    permission_classes = [IsAuthenticated, DeliverablePermission]

    def perform_update(self, serializer):
        # 状态变更审计
        if 'state' in serializer.validated_data:
            log_state_change(self.request.user, self.get_object(), serializer.validated_data['state'])
        serializer.save()
```

### 前端状态管理
```javascript
// Vuex store
state: {
  deliverables: {
    list: [],
    loading: false,
    error: null
  }
}

// 便捷 getters
getters: {
  frozenDeliverables: state => state.deliverables.list.filter(d => ['FROZEN', 'INITIAL_FROZEN'].includes(d.state)),
  normalDeliverables: state => state.deliverables.list.filter(d => d.state === 'NORMAL')
}
```

## 扩展设计策略

### 1. 版本历史
- 考虑为交付物添加版本历史表
- 支持版本回退和对比功能

### 2. 批量操作
- 支持批量上传、批量冻结
- 进度条显示批量操作状态

### 3. 自动化规则
- 基于节点状态自动冻结交付物
- 评审通过后自动版本归档

### 4. 通知集成
- 上传成功飞书通知负责人
- 冻结操作通知相关人员

## 演进历史 (Evolution History)

### 2026-03-11 - 评审项数据结构重构
🆕 **评审项字段变更**

含交付物的评审项验证节点字段从 `attach` 变更为 `deliverable`：

| 旧字段路径 | 新字段路径 | 类型变更 |
|------------|------------|----------|
| `reviewItem.attach` | `reviewItem.deliverable` | - |
| `reviewItem.attach.id` | `reviewItem.deliverable.id` | - |
| `reviewItem.attach.state` | `reviewItem.deliverable.state` | - |
| `reviewItem.attach.creator.nickname` | `reviewItem.deliverable.createdByNickname` | 字段名变更 |

**影响文件**：
- `pagesProject/components/node-details/components/node-review-section.vue`
- `pagesProject/components/node-details/node-details.vue`

**旧数据结构** (已废弃)：
```javascript
{
    "id": 96075,
    "name": "SW方案设计",
    "attach": {
        "id": 28472,
        "name": "广元盛G20-V8-YB软件设计方案",
        "note": null,
        "creator": {
            "nickname": "王岳泰"
        }
    },
    "state": 1
}
```

**新数据结构** (当前)：
```javascript
{
    "id": 24,
    "name": "评审项_1",
    "required": true,
    "type": "fixed",
    "state": "PENDING",
    "remark": null,
    "deliverable": {
        "id": 6,
        "name": "评审交付物_1",
        "createdByNickname": "Cakk"
    }
}
```

⚠️ **注意事项**：
- `state` 字段类型从数字（`1`）改为字符串（`"PENDING"`）
- API 请求参数 `attach_id` 变更为 `deliverable_id`

---

## 演进方向 (Future Evolution)

### 短期优化
1. **文件预览**: 支持在线预览常见格式（PDF、图片、Office文档）
2. **拖拽上传**: 支持拖拽文件到交付物区域直接上传
3. **快捷键支持**: Esc取消编辑、Enter确认修改

### 中期规划
1. **交付物模板系统**: 从模板库快速创建标准化交付物
2. **智能分类**: 基于文件内容自动识别交付物类型
3. **协作编辑**: 支持多人同时编辑同一交付物的备注

### 长期愿景
1. **AI 辅助审查**: 自动检查交付物完整性和规范性
2. **跨项目复用**: 交付物资产库，支持跨项目引用
3. **全链路追溯**: 从需求到交付物的完整追溯链

## 特有名词索引

| 术语 | 定义 | 相关文件 |
|------|------|----------|
| 交付物定义 | 节点规则中定义的交付物模板 | nodeDetail.showList |
| 交付物实例 | 用户实际上传的交付物文件 | sub.value |
| 初始冻结 | 系统创建时即处于冻结状态 | 'INITIAL_FROZEN' |
| 交付节点 | 标记为里程碑的节点 | victory === 1 |
| 评审拒绝 | 交付物被评审驳回需要重新提交 | review === 2 |
