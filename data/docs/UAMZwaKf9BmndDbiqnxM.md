# PM 节点列表模块 (PM NodeList Module)

## 模块定位

PM/nodelist 是项目管理系统的核心模块，负责项目节点的完整生命周期管理。节点是项目执行的基本单位，具有层级结构、状态流转、负责人分配和时间规划等特性。

## 核心职责

1. **节点管理**：节点的创建、读取、更新、删除
2. **状态流转**：管理节点从待处理→进行中→已完成的状态转换
3. **负责人管理**：分配节点主要负责人和协作者
4. **时间管理**：设置和修改节点的开始时间、结束时间
5. **权限验证**：细粒度的节点操作权限控制
6. **树形结构**：支持节点的层级关系（里程碑→主节点→子节点）

## 模块边界

### 包含的功能
- 节点详情查询 (`GET /pm/nodelist/{id}`)
- 🆕 节点完成 (`PATCH /pm/nodelist/{id}/state/complete`) - Since 2026-03-11
- 🆕 节点回滚 (`PATCH /pm/nodelist/{id}/state/rollback`) - Since 2026-03-11
- ⚠️ 节点状态修改 (`PATCH /pm/nodelist/{id}/state`) - 已废弃 Since 2026-03-11
- 节点时间修改 (`PATCH /pm/nodelist/{id}/schedule`)
- 节点负责人管理 (`POST/DELETE/PATCH /pm/nodelist/owner/set`)
- 节点催办 (`type=10100`)
- 节点操作 (`views_node`)

### 不包含的功能
- 节点定义管理（PSC/node/definition）
- 项目模板管理（PSC/project/template）
- 交付物管理（PM/deliverable）
- 项目变更管理（PM/change）

## 核心数据模型

### Project_Node（项目节点）

**🆕 Since 2026-03-10**：节点模型架构重构，去掉了中间层 `ProjectTemplateNodeMapping`。

```
核心字段：
- id: 主键
- name: 节点名称
- node_guid: 节点任务guid
- list: 外键→Project_List（项目）
- node_definition: 外键→PSC.NodeDefinitionVersion（节点定义版本）
  🆕 直接关联，不再通过 ProjectTemplateNodeMapping
  🆕 允许为 null，支持动态节点（完全自定义的节点）
- review_rule: JSON字段，评审规则
- start_time/end_time/complete_time: 时间字段
- state: 节点状态（0:待处理, 1:进行中, 2:已完成, 4:项目变更中）
- is_first_completion: 是否首次完成
- parent: 🆕 外键→self（父节点，自关联）
- sort: 🆕 排序字段

属性方法：
- node_category: 节点类型（MILESTONE/MAIN_NODE/SUB_NODE）
  🆕 直接从 node_definition.category 获取
- is_milestone: 是否里程碑节点
- node_rule: 兼容旧代码属性，直接返回 node_definition
- rule_id: 🆕 兼容旧代码属性，返回 node_definition.rule_id
- grouped: 节点分组信息（从节点类型推导）
- node_parent_id: 🆕 获取父节点 ID（直接使用 parent_id）
- project_role: 🆕 获取节点所属角色
```

**架构变更说明**：
- **变更前**：`Project_Node → ProjectTemplateNodeMapping → NodeDefinitionVersion`
- **变更后**：`Project_Node → NodeDefinitionVersion`
- **影响**：
  - 访问路径简化：`node_definition.xxx` 而非 `node_definition.node_definition_version.xxx`
  - 层级关系自包含：通过 `parent` 字段而非模板映射的 `parent` 字段
  - 支持动态节点：`node_definition` 可为 null

### Project_Node_Owners（节点负责人）
```
核心字段：
- node: 外键→Project_Node
- user: 外键→SM.User
- standard_time: 标准工时
- is_major: 是否主要负责人
```

## 节点状态流转

### 状态定义
```
0 - 待处理（灰色）
1 - 进行中（黄色）
2 - 已完成（绿色）
3 - 暂停（红色）
4 - 项目变更中（紫色）
5 - 申请中（蓝色）
6 - 已取消（灰色）
```

### 状态流转规则
```
待处理(0) → 进行中(1)
  - 需要：权限2201
  - 验证：节点不能已经是进行中状态

进行中(1) → 已完成(2)
  - 🆕 Since 2026-03-11：使用专用完成接口
  - 接口：PATCH /pm/nodelist/{id}/state/complete
  - 需要：权限2200
  - 验证：使用 NodeCompletionValidator 统一验证
    1. 用户权限 2200（可完成节点）
    2. 节点状态必须为"进行中"（state = 1）
    3. 不能是里程碑节点
    4. 主节点不能直接完成（需通过子节点完成带动）
    5. 子节点需要检查前置节点是否完成（通过 parent 字段查询）
    6. 如果包含 TIMELINE_PRESET 功能，所有里程碑节点必须已分配时间

进行中(1) → 待处理(0) [回滚]
已完成(2) → 进行中(1) [回滚]
  - 🆕 Since 2026-03-11：使用专用回滚接口
  - 接口：PATCH /pm/nodelist/{id}/state/rollback
  - 需要：权限2201 + 回滚原因
  - 验证：使用 NodeRollbackValidator 统一验证
    1. 用户权限 2201（可回滚节点）
    2. 项目未完成且未暂停
    3. 根据项目状态自动判断回滚目标
  - 效果：记录回滚日志

任何状态 → 设计变更中(4)
  - 🆕 Since 2026-03-11：使用专用回滚接口（自动判断目标状态）
  - 接口：PATCH /pm/nodelist/{id}/state/rollback
  - 需要：权限2201 + 回滚原因
  - 条件：项目必须处于变更状态(3) + 节点必须在变更范围内
```

## 权限验证

### 权限码定义
```
2001 - 节点负责人管理权限
2200 - 节点完成权限
2201 - 节点回滚权限
1007 - 项目编辑权限（用于节点可编辑判断）
1008 - 节点删除权限
```

### 权限验证方式
```python
from apps.PM.authority import authority as authority_project

# 使用方式
authority = authority_project.permission(node_id, userinfo, 'project_node')
if not authority.verify(2200):
    raise serializers.ValidationError({'msg': '权限不匹配'})
```

## 节点详情序列化器

### ReadSerializer 结构

**文件位置**：`apps/PM/nodelist/serializers.py`

```python
class ReadSerializer(serializers.ModelSerializer):
    # 基础字段
    category = serializers.CharField(source='node_category')
    project_state = serializers.IntegerField(source='list.state')
    state = serializers.IntegerField()

    # 功能聚合字段
    features = serializers.SerializerMethodField()
    special_data = serializers.SerializerMethodField()
    attach_rule = serializers.SerializerMethodField()
    owners = serializers.SerializerMethodField()
    node_state_list = serializers.SerializerMethodField()
    authority = serializers.SerializerMethodField()
    canComplete = serializers.SerializerMethodField()  # 🆕 Since 2026-03-11
    canDelete = serializers.SerializerMethodField()    # 🆕 Since 2026-03-11
    canRollback = serializers.SerializerMethodField()  # 🆕 Since 2026-03-11
```

### features 字段结构

**🆕 Since 2026-03-09**：为统一字段组织，所有子功能数据逐步迁移到 `features` 字段中。

```python
def get_features(self, obj):
    return {
        'review': self._get_review_info(obj),       # 评审项信息
        'deliverable': self._get_deliverable_info(obj),  # 交付物信息
        'submitTest': self._get_submit_test_info(obj),   # 🆕 提交测试功能
        'note': self._get_note_info(obj),           # 🆕 笔记信息
    }
```

#### submitTest 字段

**🆕 Since 2026-03-10**：关联链路已简化

**关联链路**：
```
Project_Node → node_definition → feature_mappings
```

**判断逻辑**：
```python
def _get_submit_test_info(self, instance):
    from apps.PSC.node.definition.enums import Choices

    if instance.node_definition:
        return instance.node_definition.feature_mappings.filter(
            feature_code=Choices.FeatureConfig.SUBMIT_TEST,
            is_enabled=True
        ).exists()
    return False
```

**功能说明**：
- 当节点定义版本启用了 `SUBMIT_TEST` 功能配置时，返回 `True`
- 用于前端控制"提交测试"按钮的显示

#### note 字段

**🆕 Since 2026-03-09**：从独立字段迁移到 `features` 中。

**返回内容**：节点最新的一条笔记信息
```python
def _get_note_info(self, obj):
    from apps.PM.nodelist.note.models import NodeNote

    latest_note = obj.notes.order_by('-created_at').first()
    if latest_note:
        serializer = NodeNoteReadSerializer(latest_note)
        return serializer.data
    return None
```

**⚠️ Deprecated**：独立 `note` 字段已废弃，请使用 `features.note` 访问。

#### review.deliverable 字段

**🆕 Since 2026-03-11**

**说明**：评审项中绑定的交付物信息。当评审项定义关联了交付物定义时，返回该节点下该交付物定义的最新版本交付物实例。

**关联链路**：
```
ReviewDefinitionVersion → deliverable_definition_version → DeliverableInstance
```

**返回内容**：
```json
{
  "list": [
    {
      "id": 123,
      "name": "方案评审",
      "type": "fixed",  // fixed=有交付物，custom=自定义评审项
      "state": "PENDING",
      "deliverable": {
        "id": 28472,
        "name": "广元盛G20-V8-YB软件设计方案",
        "note": null,
        "createdByNickname": "王岳泰"
      }
    }
  ]
}
```

**实现逻辑**：
```python
# 预取该项目的所有交付物实例，按版本号倒序
# 注意：交付物可能被分配到项目的多个节点中，需要查询整个项目的交付物
deliverables_queryset = DeliverableInstance.objects.filter(
    project_node__list=instance.list  # 查询整个项目的交付物
).select_related(
    'created_by',
    'definition__deliverable_definition'
).order_by('definition', '-version')

# 构建 definition -> 最新交付物实例 的映射
latest_deliverables_map = {}
for deliverable in deliverables_queryset:
    def_id = deliverable.definition_id
    if def_id not in latest_deliverables_map:
        latest_deliverables_map[def_id] = deliverable

# 在评审项循环中获取
if review_def_version.deliverable_definition_version:
    deliverable_def_id = review_def_version.deliverable_definition_version.id
    latest_deliverable = latest_deliverables_map.get(deliverable_def_id)
    if latest_deliverable:
        deliverable_info = {
            'id': latest_deliverable.id,
            'name': latest_deliverable.definition.name,
            'note': latest_deliverable.note,
            'createdByNickname': latest_deliverable.created_by.nickname
        }
```

**注意**：
- 只有 `type="fixed"` 的评审项才包含 `deliverable` 字段
- `type="custom"` 的评审项该字段为 `null`
- 返回的是该节点下该交付物定义的**最新版本**交付物实例

### 节点详情 API 响应结构

```json
{
  "id": 123,
  "name": "需求评审",
  "category": "MAIN_NODE",
  "state": 1,
  "start_time": "2026-03-01 09:00:00",
  "end_time": "2026-03-15 18:00:00",
  "project_state": 1,
  "special_data": {},
  "attach_rule": [],
  "owners": [
    {
      "id": 1,
      "is_major": true,
      "standard_time": 8.0,
      "user": {
        "id": 456,
        "name": "张三",
        "avatar": "https://..."
      }
    }
  ],
  "node_state_list": [...],
  "authority": {...},
  "canComplete": true,
  "canDelete": false,
  "canRollback": true,  # 🆕 Since 2026-03-11
  "features": {
    "review": {...},
    "deliverable": {...},
    "submitTest": false,
    "note": {
      "id": 1,
      "content": "最新笔记内容",
      "createdByName": "张三",
      "createdByAvatar": "https://...",
      "createdAt": "2026-03-09 11:23:45"
    }
  }
}
```

### 🆕 canComplete 字段

**Since 2026-03-11**

**类型**：布尔值

**说明**：标识当前用户是否可以将该节点从"进行中"状态切换到"完成"状态。

**验证逻辑**：
```python
def get_canComplete(self, obj):
    from .validators import NodeCompletionValidator

    if not self.userinfo:
        return False

    validator = NodeCompletionValidator(obj, self.userinfo)
    return validator.validate(raise_exception=False)
```

**判断条件**（全部满足才返回 `true`）：
1. 用户具有 2200 权限（可完成节点）
2. 节点当前状态为"进行中"（state = 1）
3. 节点不是里程碑节点
4. 主节点下没有未完成的子节点（主节点需通过子节点完成带动）
5. 子节点的前置节点已完成
6. 如果节点包含 TIMELINE_PRESET 功能，所有里程碑节点已分配时间

### 🆕 canDelete 字段

**Since 2026-03-11**

**类型**：布尔值

**说明**：标识当前用户是否可以删除该节点。

**验证逻辑**：
```python
def get_canDelete(self, obj):
    from .validators import NodeDeletionValidator

    if not self.userinfo:
        return False

    validator = NodeDeletionValidator(obj, self.userinfo)
    return validator.validate(raise_exception=False)
```

**判断条件**（全部满足才返回 `true`）：
1. 用户具有 1008 权限（可删除节点）
2. 节点不是里程碑节点
3. 如果是主节点，同级至少要保留一个主节点

### 🆕 canRollback 字段

**Since 2026-03-11**

**类型**：布尔值

**说明**：标识当前用户是否可以回滚该节点。

**验证逻辑**：
```python
def get_canRollback(self, obj):
    from .validators import NodeRollbackValidator

    if not self.userinfo:
        return False

    validator = NodeRollbackValidator(obj, self.userinfo)
    return validator.validate(raise_exception=False)
```

**判断条件**（全部满足才返回 `true`）：
1. 用户具有 2201 权限（可回滚节点）
2. 项目不能已完成（state != 2）
3. 项目不能已暂停（state != 4）
4. 根据项目状态判断回滚目标：
   - 项目状态为进行中时：节点不能已处于进行中状态
   - 项目状态为变更中时：节点必须在设计变更范围内且不能已处于变更中状态

## 🆕 节点验证器模块

**Since 2026-03-11**

**文件位置**：`apps/PM/nodelist/validators.py`

### 设计目的

封装节点操作的验证逻辑，使其可被多个场景复用：
- 实际操作时验证（抛出异常）
- 接口返回时判断能力（返回布尔值）

### 节点完成验证器 (NodeCompletionValidator)

**Since 2026-03-11**

**文件位置**：`apps/PM/nodelist/validators.py`

### 设计目的

封装节点完成的所有验证逻辑，使其可被多个场景复用：
- `PatchStateSerializer`：实际完成节点时验证（抛出异常）
- `ReadSerializer.canComplete`：节点详情接口判断是否可完成（返回布尔值）

### 类结构

```python
class NodeCompletionValidator:
    def __init__(self, node_instance, userinfo):
        """
        Args:
            node_instance: 要验证的 Project_Node 实例
            userinfo: 用户信息字典，包含 id、is_superuser 等
        """
        self.node = node_instance
        self.userinfo = userinfo
        self._errors = []

    def validate(self, raise_exception=False):
        """
        执行所有验证检查

        Args:
            raise_exception: True=抛出异常，False=返回布尔值

        Returns:
            bool: 节点可完成返回 True，否则返回 False

        Raises:
            serializers.ValidationError: 当 raise_exception=True 且验证失败时
        """
        # 5个验证检查...
        return len(self._errors) == 0
```

### 验证方法

| 方法 | 检查内容 |
|------|----------|
| `_check_permission()` | 用户是否有 2200 权限（可完成节点） |
| `_check_node_state()` | 节点是否为"进行中"状态（state = 1） |
| `_check_not_milestone()` | 节点是否不是里程碑节点 |
| `_check_no_uncompleted_children()` | 主节点是否没有未完成的子节点 |
| `_check_predecessor_nodes()` | 子节点的前置节点是否已完成 |
| `_check_milestone_times()` | 里程碑节点是否已分配时间（TIMELINE_PRESET） |

### 使用方式

```python
# 场景1：实际验证（抛出异常）
validator = NodeCompletionValidator(node_instance, userinfo)
validator.validate(raise_exception=True)  # 验证失败时抛出 ValidationError

# 场景2：布尔值判断
validator = NodeCompletionValidator(node_instance, userinfo)
can_complete = validator.validate(raise_exception=False)  # 返回 True/False
```

### 错误代码

| 错误代码 | 说明 |
|----------|------|
| `permission_denied` | 用户没有 2200 权限 |
| `invalid_state` | 节点状态不是"进行中" |
| `is_milestone` | 节点是里程碑节点 |
| `has_uncompleted_children` | 主节点下有未完成的子节点 |
| `predecessor_not_completed` | 前置节点未完成 |
| `milestone_time_missing` | 里程碑时间未分配 |

### 节点删除验证器 (NodeDeletionValidator)

**Since 2026-03-11**

**文件位置**：`apps/PM/nodelist/validators.py`

#### 设计目的

封装节点删除的所有验证逻辑，使其可被多个场景复用：
- `DeleteNodeSerializer`：实际删除节点时验证（抛出异常）
- `ReadSerializer.canDelete`：节点详情接口判断是否可删除（返回布尔值）

#### 类结构

```python
class NodeDeletionValidator:
    def __init__(self, node_instance, userinfo):
        """
        Args:
            node_instance: 要验证的 Project_Node 实例
            userinfo: 用户信息字典，包含 id、is_superuser 等
        """
        self.node = node_instance
        self.userinfo = userinfo
        self._errors = []

    def validate(self, raise_exception=False):
        """
        执行所有验证检查

        Args:
            raise_exception: True=抛出异常，False=返回布尔值

        Returns:
            bool: 节点可删除返回 True，否则返回 False

        Raises:
            serializers.ValidationError: 当 raise_exception=True 且验证失败时
        """
        # 3个验证检查...
        return len(self._errors) == 0
```

#### 验证方法

| 方法 | 检查内容 |
|------|----------|
| `_check_permission()` | 用户是否有 1008 权限（可删除节点） |
| `_check_not_milestone()` | 节点是否不是里程碑节点 |
| `_check_main_node_constraint()` | 如果是主节点，同级是否至少保留一个主节点 |

#### 使用方式

```python
# 场景1：实际验证（抛出异常）
validator = NodeDeletionValidator(node_instance, userinfo)
validator.validate(raise_exception=True)  # 验证失败时抛出 ValidationError

# 场景2：布尔值判断
validator = NodeDeletionValidator(node_instance, userinfo)
can_delete = validator.validate(raise_exception=False)  # 返回 True/False
```

#### 错误代码

| 错误代码 | 说明 |
|----------|------|
| `permission_denied` | 用户没有 1008 权限 |
| `is_milestone` | 节点是里程碑节点 |
| `last_main_node` | 同级只剩这一个主节点 |

### 节点回滚验证器 (NodeRollbackValidator)

**Since 2026-03-11**

**文件位置**：`apps/PM/nodelist/validators.py`

#### 设计目的

封装节点回滚的所有验证逻辑，使其可被多个场景复用：
- `PatchRollbackSerializer`：实际回滚节点时验证（抛出异常）
- `ReadSerializer.canRollback`：节点详情接口判断是否可回滚（返回布尔值）

#### 类结构

```python
class NodeRollbackValidator:
    def __init__(self, node_instance, userinfo):
        """
        Args:
            node_instance: 要验证的 Project_Node 实例
            userinfo: 用户信息字典，包含 id、is_superuser 等
        """
        self.node = node_instance
        self.userinfo = userinfo
        self._errors = []

    def validate(self, raise_exception=False):
        """
        执行所有验证检查

        Args:
            raise_exception: True=抛出异常，False=返回布尔值

        Returns:
            bool: 节点可回滚返回 True，否则返回 False

        Raises:
            serializers.ValidationError: 当 raise_exception=True 且验证失败时
        """
        # 4个验证检查...
        return len(self._errors) == 0

    def get_target_state(self):
        """获取回滚目标状态（1 或 4）"""
        return self._determine_target_state()
```

#### 验证方法

| 方法 | 检查内容 |
|------|----------|
| `_check_permission()` | 用户是否有 2201 权限（可回滚节点） |
| `_check_project_not_completed()` | 项目是否未完成（state != 2） |
| `_check_project_not_paused()` | 项目是否未暂停（state != 4） |
| `_determine_target_state()` | 根据项目状态确定回滚目标状态 |
| `_check_rollback_to_in_progress()` | 是否可以回滚到"进行中"状态 |
| `_check_rollback_to_changing()` | 是否可以回滚到"设计变更中"状态 |
| `_check_node_in_change_scope()` | 节点是否在设计变更范围内 |

#### 回滚目标状态判断逻辑

```python
def _determine_target_state(self):
    """根据项目状态确定回滚目标状态"""
    project_state = self.node.list.state

    # 项目状态为进行中(1)时，回滚到状态1
    if project_state == 1:
        return 1

    # 项目状态为变更中(3)时，回滚到状态4
    elif project_state == 3:
        return 4

    # 其他情况默认回滚到状态1
    return 1
```

#### 使用方式

```python
# 场景1：实际验证（抛出异常）
validator = NodeRollbackValidator(node_instance, userinfo)
validator.validate(raise_exception=True)  # 验证失败时抛出 ValidationError

# 场景2：布尔值判断
validator = NodeRollbackValidator(node_instance, userinfo)
can_rollback = validator.validate(raise_exception=False)  # 返回 True/False

# 场景3：获取目标状态
validator = NodeRollbackValidator(node_instance, userinfo)
target_state = validator.get_target_state()  # 返回 1 或 4
```

#### 错误代码

| 错误代码 | 说明 |
|----------|------|
| `permission_denied` | 用户没有 2201 权限 |
| `project_completed` | 项目已完成 |
| `project_paused` | 项目已暂停 |
| `already_in_progress` | 节点已处于进行中状态 |
| `already_changing` | 节点已处于设计变更中状态 |

## 异步任务（Celery Tasks）

**文件位置**：`apps/PM/nodelist/tasks.py`

### async_unfreeze_initial_frozen_deliverables

**🆕 Since 2026-03-12**

**功能说明**：当节点状态发生变化后，异步解除节点下初始冻结状态的交付物。

**任务签名**：
```python
@shared_task
def async_unfreeze_initial_frozen_deliverables(node_id):
    """
    异步解除节点下初始冻结状态的交付物

    当节点状态变化后，检查该节点下的全部交付物，
    将状态为 INITIAL_FROZEN 的交付物修改为 NORMAL

    Args:
        node_id: 项目节点 ID
    """
```

**执行逻辑**：
1. 根据 `node_id` 获取节点实例
2. 查询该节点下所有状态为 `INITIAL_FROZEN` 的交付物实例
3. 批量更新交付物状态为 `NORMAL`
4. 返回更新的交付物数量
5. 包含异常处理和日志输出

**调用触发**：由 `handle_node_status_change_after` 信号处理器自动触发

## 信号处理器（Signals）

**文件位置**：`apps/PM/nodelist/signals.py`

### handle_node_status_change_after

**🆕 Since 2026-03-12**：增强了节点状态变化后的处理逻辑

**信号类型**：`post_save`

**监听对象**：`Project_Node`

**触发条件**：节点状态发生变化时（`old_state != instance.state`）

**执行逻辑**：
```python
@receiver(post_save, sender=Project_Node)
def handle_node_status_change_after(sender, instance, **kwargs):
    """
    监听项目状态变化事件，在状态变化之后处理状态变化引起的节点变更
    """
    old_state = getattr(instance, '_original_state', None)
    if old_state is None or old_state == instance.state:
        return

    # 🆕 Since 2026-03-12：异步解除节点下初始冻结状态的交付物
    if old_state == 1 and instance.state == 2:
        from .tasks import async_unfreeze_initial_frozen_deliverables
        async_unfreeze_initial_frozen_deliverables.delay(node_id=instance.id)

        # 后里程碑自开启能力
        _check_and_activate_next_milestone(instance)
```

**处理内容**：
1. **🆕 解除交付物初始冻结**（Since 2026-03-12）：当节点从"进行中"变为"已完成"时，异步调用 `async_unfreeze_initial_frozen_deliverables` 处理交付物状态
2. 后里程碑自开启能力：检查并激活下一个里程碑的所有节点

### handle_node_status_change_before

**信号类型**：`pre_save`

**监听对象**：`Project_Node`

**触发条件**：节点状态发生变化前

**处理内容**：
- 父节点自完成能力：当同级全部完成时检查上级节点是否可以被完成
- 项目自完成能力：当所有节点都完成时自动完成项目
- 节点首次完成标记：设置 `is_first_completion` 为 `True`
- 已完成→进行中回滚：递归回滚所有祖先节点状态

### handle_node_creation

**信号类型**：`post_save`

**监听对象**：`Project_Node`

**触发条件**：节点创建时（`created=True`）

**处理内容**：
- 自动添加默认负责人（从 `node_definition.default_owner` 获取）

## 与其他模块关系

### 依赖的模块
```
apps.PM.authority
  └── authority.permission() - 权限验证

apps.PM.nodelist.validators
  └── NodeCompletionValidator - 🆕 Since 2026-03-11 节点完成验证器
  └── NodeDeletionValidator - 🆕 Since 2026-03-11 节点删除验证器
  └── NodeRollbackValidator - 🆕 Since 2026-03-11 节点回滚验证器

apps.PM.deliverable.instance
  ├── DeliverableInstance - 🆕 Since 2026-03-12 交付物实例模型
  └── Choices.DeliverableState - 🆕 Since 2026-03-12 交付物状态枚举

apps.PSC.node.definition
  ├── NodeDefinitionVersion - 🆕 节点定义版本（直接关联）
  └── NodeDefinitionFeatureMapping - 功能配置映射

apps.PSC.project_role
  └── ProjectRole - 项目角色

apps.SM.models
  └── User - 用户模型

apps.PM.models
  ├── Project_List - 项目列表
  └── ProjectAttachmentList - 项目附件

apps.API.feishu
  └── 飞书API接口
```

### 被依赖的模块
```
apps.PM.signals
  └── 监听节点状态变化触发其他流程

apps.PM.tasks
  └── 异步任务（催办消息、通知等）
```

## API 端点

### 节点详情
```http
GET /pm/nodelist/{id}
Response: 节点完整信息（状态、负责人、时间、features 等）
```

### 🆕 节点完成（专用接口）

**Since 2026-03-11**

```http
PATCH /pm/nodelist/{id}/state/complete
Body: {}
```

**说明**：将节点状态从"进行中"(1)切换到"已完成"(2)

**验证**：使用 `NodeCompletionValidator` 统一验证

**序列化器**：`PatchCompleteSerializer`

### 🆕 节点回滚（专用接口）

**Since 2026-03-11**

```http
PATCH /pm/nodelist/{id}/state/rollback
Body: {
  "reason": "回滚原因（必填）"
}
```

**说明**：根据项目状态自动判断回滚目标
- 项目状态为进行中时，回滚到状态1
- 项目状态为变更中时，回滚到状态4

**验证**：使用 `NodeRollbackValidator` 统一验证

**序列化器**：`PatchRollbackSerializer`

### ⚠️ 节点状态修改（已废弃）

**Deprecated Since 2026-03-11**

原有的通用状态修改接口 `PATCH /pm/nodelist/{id}/state` 已被拆分为专用接口：
- 使用 `/pm/nodelist/{id}/state/complete` 完成节点
- 使用 `/pm/nodelist/{id}/state/rollback` 回滚节点

### 节点时间修改
```http
PATCH /pm/nodelist/{id}/schedule
Body: {
  "startDate": "2026-03-01T09:00:00",
  "endDate": "2026-03-15T18:00:00"
}
验证：startDate 和 endDate 必须同时传参
```

### 节点负责人管理
```http
POST /pm/nodelist/owner/set
Body: {
  "node_id": 123,
  "users": [{"user_id": 456, "is_major": true}]
}
```

### 节点催办
```http
POST /pm/nodelist?type=10100
Body: {
  "project_id": 789,
  "node_id": 123
}
特性：10分钟缓存防重复催办
```

## 常见业务场景

### 场景1：完成节点

**🆕 Since 2026-03-11**：使用专用完成接口

```
1. 调用 PATCH /pm/nodelist/{id}/state/complete
2. 🆕 使用 NodeCompletionValidator 统一验证
   - 验证用户权限 2200
   - 验证节点状态为"进行中"
   - 验证不是里程碑节点
   - 验证主节点没有未完成的子节点
   - 验证子节点的前置节点已完成（通过 parent 字段）
   - 验证里程碑时间已分配（如果包含 TIMELINE_PRESET）
3. 更新节点状态为"已完成"
4. 设置complete_time为当前时间
5. 记录操作日志
6. 触发信号完成后续流程
```

### 场景2：回滚节点

**🆕 Since 2026-03-11**：使用专用回滚接口

```
1. 调用 PATCH /pm/nodelist/{id}/state/rollback
   Body: { "reason": "回滚原因" }
2. 🆕 使用 NodeRollbackValidator 统一验证
   - 验证用户权限 2201
   - 验证项目未完成且未暂停
   - 根据项目状态自动判断回滚目标：
     * 项目状态为进行中 → 回滚到状态1
     * 项目状态为变更中 → 回滚到状态4
3. 更新节点状态为目标状态
4. 设置complete_time为当前时间
5. 记录回滚日志和原因
```

### 场景3：修改节点时间
```
1. 验证startDate和endDate同时传参
2. 验证startDate < endDate
3. 更新start_time和end_time
4. 记录时间修改日志
```

### 场景4：设置节点负责人
```
1. 验证用户有权限2001
2. 清空现有负责人（如果需要）
3. 创建新的Project_Node_Owners记录
4. 第一个用户自动设为主要负责人
5. 记录操作日志
```

## 技术实现要点

### Django ORM 使用
```python
# 🆕 Since 2026-03-10：优化后的查询（简化关联路径）
node = Project_Node.objects.select_related(
    'list',
    'node_definition',  # 🆕 直接关联，不再需要 __node_definition_version
    'parent'  # 🆕 直接使用 parent 字段
).prefetch_related(
    'node_owners__user'
).get(id=node_id)
```

### 序列化器最佳实践

**🆕 Since 2026-03-11**：使用 request 对象构造 userinfo

```python
# 推荐方式：序列化器从 request 中构造 userinfo
class PatchCompleteSerializer(serializers.ModelSerializer):
    def __init__(self, instance=None, data=..., **kwargs):
        super().__init__(instance, data, **kwargs)

        context = kwargs.get('context')
        request = context.get('request')
        if request:
            from utils.user import UserHelper
            self.userinfo = UserHelper.setup_request_userinfo(request)
            self.user_instance = request.user
        else:
            self.userinfo = None
            self.user_instance = None
```

**⚠️ Deprecated**：视图层构造 userinfo 的方式已废弃

```python
# 旧方式（不推荐）
def patch(self, request, *args, **kwargs):
    userinfo = UserHelper.setup_request_userinfo(request)
    serializer = SomeSerializer(
        instance=self.instance,
        data=request.data,
        context={'userinfo': userinfo, 'user_instance': request.user}
    )
```

### 专用序列化器设计

**Since 2026-03-11**

```python
# 节点完成序列化器
class PatchCompleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project_Node
        fields = []  # 不需要输入字段

    def validate(self, attrs):
        from .validators import NodeCompletionValidator
        validator = NodeCompletionValidator(self.instance, self.userinfo)
        validator.validate(raise_exception=True)
        return attrs

    def update(self, instance, validated_data):
        from django.utils import timezone
        instance.state = 2
        instance.complete_time = timezone.now()
        instance.save()
        common.projectInsertPeratorLog(
            instance.list.id,
            f'完成了 {instance.name}节点',
            self.userinfo['id']
        )
        return instance

# 节点回滚序列化器
class PatchRollbackSerializer(serializers.ModelSerializer):
    reason = serializers.CharField(required=True)

    class Meta:
        model = Project_Node
        fields = ['reason']

    def validate(self, attrs):
        from .validators import NodeRollbackValidator
        validator = NodeRollbackValidator(self.instance, self.userinfo)
        validator.validate(raise_exception=True)
        return attrs

    def update(self, instance, validated_data):
        from django.utils import timezone
        validator = NodeRollbackValidator(instance, self.userinfo)
        target_state = validator.get_target_state()
        instance.state = target_state
        instance.complete_time = timezone.now()
        instance.save()
        # 记录不同状态的日志...
        return instance
```

### 信号处理器
```python
@receiver(post_save, sender=Project_Node)
def handle_node_creation(sender, instance, created, **kwargs):
    if not created:
        return
    # 🆕 简化后的默认负责人设置逻辑
    if not instance.node_definition:
        return

    default_owner = instance.node_definition.default_owner
    if default_owner:
        Project_Node_Owners.objects.create(
            node=instance,
            user=default_owner,
            is_major=True,
            standard_time=instance.node_definition.default_workhours
        )
```

### 🆕 节点树构建
```python
# 🆕 Since 2026-03-10：使用 parent 字段构建树形结构
nodes = Project_Node.objects.filter(
    list=project
).select_related(
    'parent',
    'node_definition'
).order_by('sort', 'id')

# 节点数据包含 parent_id
nodes_data = [
    {
        'id': node.id,
        'name': node.name,
        'state': node.state,
        'parent_id': node.parent_id if node.parent else None,
        'sort': node.sort,
    }
    for node in nodes
]
```

## 特殊名词索引

当用户提到以下名词时，应定位到此模块：

- **节点**、**项目节点**、**Node** → PM/nodelist
- **节点状态**、**状态流转** → PM/nodelist (enums.py)
- **节点负责人**、**Node Owner** → PM/nodelist (views_node_owner.py)
- **节点时间**、**开始时间**、**结束时间** → PM/nodelist (NodeScheduleView)
- **节点催办**、**催办** → PM/nodelist (views_node type=10100)
- **里程碑节点**、**主节点**、**子节点** → PM/nodelist (node_category)
- **节点详情**、**节点信息** → PM/nodelist (DetailView)
- **节点模板**、**节点定义** → PSC/node/definition (相关模块)
- **节点笔记**、**NodeNote** → PM/nolist/note (note 子模块)
- **🆕 动态节点**、**自定义节点** → PM/nodelist (node_definition 可为 null 的节点)
- **🆕 canComplete**、**节点可完成** → PM/nodelist (ReadSerializer 字段)
- **🆕 NodeCompletionValidator**、**节点完成验证器** → PM/nodelist/validators
- **🆕 canDelete**、**节点可删除** → PM/nodelist (ReadSerializer 字段)
- **🆕 NodeDeletionValidator**、**节点删除验证器** → PM/nodelist/validators
- **🆕 canRollback**、**节点可回滚** → PM/nodelist (ReadSerializer 字段)
- **🆕 NodeRollbackValidator**、**节点回滚验证器** → PM/nodelist/validators
- **🆕 PatchCompleteSerializer**、**节点完成序列化器** → PM/nodelist/serializers
- **🆕 PatchRollbackSerializer**、**节点回滚序列化器** → PM/nodelist/serializers
- **🆕 PatchCompleteView**、**节点完成视图** → PM/nodelist/views
- **🆕 PatchRollbackView**、**节点回滚视图** → PM/nodelist/views

## 扩展设计策略

### 当前架构优势
1. **🆕 架构简化**：去掉中间层 ProjectTemplateNodeMapping，访问路径更简洁
2. **🆕 节点自包含**：层级关系通过 parent 字段直接存储，不依赖模板映射
3. **🆕 支持动态节点**：node_definition 可为 null，支持完全自定义的节点
4. **🆕 验证器复用**：Since 2026-03-11，NodeCompletionValidator、NodeDeletionValidator 和 NodeRollbackValidator 统一处理节点验证
5. **🆕 专用接口**：Since 2026-03-11，节点操作拆分为专用接口（complete/rollback），API 语义更清晰
6. **🆕 序列化器自构造 userinfo**：Since 2026-03-11，序列化器从 request 对象中构造 userinfo，职责更清晰
7. **🆕 异步交付物处理**：Since 2026-03-12，节点状态变化后自动异步处理交付物初始冻结状态
8. **模板驱动**：通过PSC模板系统管理节点定义
9. **信号驱动**：自动处理节点创建后的默认负责人设置、节点状态变化后的交付物处理
10. **权限分离**：使用专门的权限模块进行验证
11. **功能配置化**：通过 `NodeDefinitionFeatureMapping` 实现节点功能的动态配置
12. **字段聚合**：将子功能数据统一到 `features` 字段，提升 API 结构一致性

### 未来演进方向
1. **状态机重构**：考虑引入django-fsm管理复杂的状态流转
2. **异步处理扩展**：🆕 Since 2026-03-12 已实现交付物状态异步处理，可扩展更多异步场景
3. **事件驱动**：增强信号系统，实现更松耦合的模块交互
4. **性能优化**：🆕 节点树形结构查询性能已优化（通过 parent 字段）
5. **API 版本控制**：为未来的API升级预留空间
6. **features 字段扩展**：逐步将更多子功能迁移到 `features` 中（如 `special_data`）
7. **🆕 动态节点扩展**：增强动态节点的配置能力（评审项、交付物、功能配置）