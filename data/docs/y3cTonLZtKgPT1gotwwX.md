# PM 节点负责人管理模块 (pm-nodelist_owner)

## 模块定位

PM 节点负责人管理模块是 PM/nodelist 的子模块，专门负责项目节点负责人的全生命周期管理。该模块独立于节点列表核心功能，提供负责人设置、变更、删除等操作的专用接口。

**模块路径**: `apps/PM/nodelist/owner/`

## 触发条件

当用户提到以下关键词时，应激活此技能：
- "节点负责人"、"node owner"、"负责人管理"
- "Project_Node_Owners"、"PM_node_owners"
- "设置负责人"、"批量设置负责人"
- "节点负责人权限"、"权限验证 2001"
- "is_major"、"主要负责人"、"协作者"
- "standard_time"、"标准工时"

## 模块职责边界

### 核心职责
- **负责人分配**: 为项目节点分配主要负责人(is_major=True)和协作者(is_major=False)
- **批量管理**: 支持批量设置多个节点的负责人
- **权限验证**: 验证用户是否有权限修改节点负责人(权限代码 2001)
- **操作日志**: 记录所有负责人变更操作到项目日志
- **状态保护**: 已完成节点的负责人只能由超级管理员修改

### 职责边界
- **不负责**节点本身的创建、删除、状态变更(属于 nodelist 主模块)
- **不负责**节点定义(NodeDefinition)的管理(属于 PSC 模块)
- **不负责**用户管理(属于 SM 模块)
- **不负责**项目整体权限验证(属于 authority 模块)

## 核心数据模型

### Project_Node_Owners (PM_node_owners)

```python
class Project_Node_Owners(models.Model):
    id = models.AutoField(primary_key=True)
    node = models.ForeignKey('Project_Node', related_name="node_owners")
    user = models.ForeignKey('SM.User', related_name="node_owner")
    standard_time = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    is_major = models.BooleanField(default=False)  # 是否主要负责人
```

**关键字段说明**:
- `is_major`: True=主要负责人, False=协作者
- `standard_time`: 该负责人在该节点的标准工时(小时)
- `node`: 关联到 Project_Node(项目节点)
- `user`: 关联到 SM.User(系统用户)

**关系映射**:
- `node.node_owners.all()`: 获取节点的所有负责人
- `user.node_owner.all()`: 获取用户负责的所有节点

## 权限验证流程

### 权限代码 2001 - 节点负责人编辑权限

**验证路径**: `apps/PM/authority/utils.py` -> `AuthorityVerifier.verify(2001)`

**权限验证逻辑**:
```python
from apps.PM.authority import authority as authority_project

authority = authority_project.permission(node_id, userinfo, 'project_node')
if not authority.verify(2001):
    return JsonResponse({'msg': '操作失败，权限不匹配'}, status=400)
```

**权限级别**:
- 2001: 编辑节点负责人权限
- 需要用户具备该节点的负责人管理权限

**已完成节点保护**:
```python
is_node_completed = (node_instance.state == 2)
is_superuser = userinfo.get('is_superuser', False)

if is_node_completed and not is_superuser:
    raise serializers.ValidationError({
        '负责人编辑失败': '节点已完成，仅超级管理员可编辑负责人信息'
    })
```

## 与其他模块关系

### 依赖关系
```
pm-nodelist_owner
├── SM.User (用户模型)
├── PM.Project_Node (项目节点)
├── PM.authority (权限验证)
└── PM.project_log (操作日志)
```

**模块调用示例**:
```python
from apps.SM.models import User
from apps.PM.models import Project_Node, Project_Node_Owners
from apps.PM.authority import authority as authority_project
from assists import common

# 权限验证
authority = authority_project.permission(node_id, userinfo, 'project_node')

# 记录操作日志
common.projectInsertPeratorLog(project_id, content, user_id)
```

### 上游模块
- **PM/nodelist**: 节点列表主模块，owner 是其子模块
- **PM/authority**: 提供权限验证服务
- **SM**: 提供用户模型

### 下游模块
- **PM/log**: 接收操作日志记录

## API 接口说明

### 1. 批量设置节点负责人

**接口**: `POST /pm/nodelist/owner/set`

**视图**: `NodeOwnerViews.as_view()`

**序列化器**: `SetNodeOwnerSerializer`

**请求体**:
```json
[
  {
    "nodeId": 123,
    "userIds": [1, 2, 3]
  }
]
```

**业务规则**:
- 第一个用户自动设为主要负责人(is_major=True)
- 其余用户设为协作者(is_major=False)
- 先删除旧记录，再批量创建新记录
- 如果userIds为空数组，则清空该节点的所有负责人

**日志输出**:
- 单个负责人: "为节点【{节点名}】设置了负责人：{用户名}"
- 多个负责人: "为节点【{节点名}】设置了负责人：{主要负责人}，协作者：{协作者列表}"

### 2. 节点负责人管理(兼容接口)

**接口**: `POST /pm/nodelist/owner/set` (name='set_node_owner')

**视图**: `views_node_owner.as_view()`

**序列化器**: `serializer_node_owner`

**请求体**:
```json
{
  "data": [
    {"node_id": 123, "user_id": 1, "is_major": true, "standard_time": 8.0},
    {"node_id": 123, "user_id": 2, "is_major": false, "standard_time": 4.0}
  ]
}
```

**业务规则**:
- 支持批量创建、更新、删除负责人
- 通过比较新旧列表执行增量更新
- 未在新列表中的记录会被删除
- is_major值变化的记录会被更新

### 3. 负责人详情操作

**接口**: `POST /pm/nodelist/owner/{code}`

**视图**: `views_node_owner.as_view()`

**说明**: code为逗号分隔的owner_id列表

**接口**: `DELETE /pm/nodelist/owner/{code}`

**说明**: 批量删除负责人记录

**接口**: `PATCH /pm/nodelist/owner/{code}`

**说明**: 更新单个负责人记录(如修改is_major或standard_time)

## 序列化器详解

### serializer_node_owner

**职责**: 单个负责人记录的CRUD操作

**字段映射**:
- `node_id`(write_only) -> `node`
- `user_id`(write_only) -> `user`
- `user`(read-only) -> 序列化为 `{id, name, avatar}`

**验证规则**:
- 创建时检查同一节点不能重复添加同一用户
- standard_time默认为0

**操作日志**:
- 创建: "添加 {用户名} 为 {节点名} 节点的 {负责/协助}人"
- 更新: "修改 {用户名} 为 {节点名} 节点的 {负责/协助}人"
- 删除: "移除 {用户名} 作为 {节点名} 节点的 {负责人/协助人}"

### SetNodeOwnerSerializer

**职责**: 批量设置节点负责人(简化接口)

**字段**:
- `nodeId`: 节点ID(PrimaryKeyRelatedField)
- `userIds`: 用户ID列表(ListSerializer)

**业务逻辑**:
1. 验证权限(2001)
2. 验证节点状态(已完成节点需要超级管理员权限)
3. 删除旧记录
4. 批量创建新记录(第一个is_major=True，其余False)
5. 记录操作日志

## 常见业务场景

### 场景1: 项目创建后分配默认负责人

**触发**: PM/nodelist/signals.py - `handle_node_creation`

**逻辑**:
```python
@receiver(post_save, sender=Project_Node)
def handle_node_creation(sender, instance, created, **kwargs):
    if not created or not instance.node_definition:
        return

    node_definition_version = instance.node_definition.node_definition_version
    default_owner = node_definition_version.default_owner
    if not default_owner:
        return

    # 创建默认负责人记录
    Project_Node_Owners.objects.create(
        node=instance,
        user=default_owner,
        is_major=True,
        standard_time=node_definition_version.default_workhours or 0
    )
```

### 场景2: 批量设置节点负责人

**适用**: 节点创建后批量分配负责人

**接口**: `POST /pm/nodelist/owner/set`

**特点**:
- 简洁的请求格式
- 自动设置第一个为主要负责人
- 支持清空负责人(传入空数组)

### 场景3: 完成节点修改负责人

**限制**:
- 节点状态为2(已完成)时，只有超级管理员可修改
- 普通用户修改会返回: "节点已完成，仅超级管理员可编辑负责人信息"

### 场景4: 负责人标准工时管理

**操作**: `PATCH /pm/nodelist/owner/{owner_id}`

**请求体**:
```json
{
  "standard_time": 16.5
}
```

**说明**: 修改负责人在节点的标准工时

## 技术实现建议(Django)

### 1. 使用事务确保数据一致性

```python
from django.db import transaction

with transaction.atomic():
    # 删除旧记录
    Project_Node_Owners.objects.filter(node=node).delete()
    # 创建新记录
    Project_Node_Owners.objects.bulk_create(node_owners_to_create)
```

### 2. 批量操作优化

```python
# 批量创建(推荐)
Project_Node_Owners.objects.bulk_create(node_owners_to_create)

# 批量删除(推荐)
Project_Node_Owners.objects.filter(node__in=node_ids).delete()
```

### 3. 查询优化

```python
# 使用select_related优化外键查询
owners = Project_Node_Owners.objects.select_related('node', 'user').filter(node_id=node_id)

# 使用prefetch_related优化反向查询
node = Project_Node.objects.prefetch_related('node_owners__user').get(pk=node_id)
```

### 4. 权限验证装饰器

```python
from apps.PM.uitls import project_node_operation_validator

@method_decorator(project_node_operation_validator)
def post(self, request, *args, **kwargs):
    # 视图逻辑
    pass
```

## 扩展设计策略

### 1. 负责人角色扩展

**当前**: is_major (主要负责人/协作者)

**扩展方向**:
- 添加角色类型: 设计负责人、测试负责人、审核负责人
- 支持一个节点多个不同角色的负责人

**实现建议**:
```python
class Project_Node_Owners(models.Model):
    # 新增字段
    owner_type = models.CharField(
        choices=[('MAJOR', '主要负责人'), ('DESIGN', '设计负责人'), ...]
    )
```

### 2. 负责人变更历史

**需求**: 记录负责人变更历史，支持回溯

**实现建议**:
```python
class Project_Node_Owner_History(models.Model):
    node = models.ForeignKey('Project_Node')
    user = models.ForeignKey('SM.User')
    action = models.CharField(choices=[('ADD', '添加'), ('REMOVE', '移除'), ('UPDATE', '更新')])
    change_data = models.JSONField()  # 记录变更前后的数据
    operator = models.ForeignKey('SM.User', related_name='owner_changes')
    change_time = models.DateTimeField(auto_now_add=True)
```

### 3. 负责人工作量统计

**需求**: 统计用户在各节点的标准工时总和

**实现建议**:
```python
from django.db.models import Sum

user_total_hours = Project_Node_Owners.objects.filter(
    user=user,
    node__list__project_id=project_id
).aggregate(total_hours=Sum('standard_time'))
```

### 4. 负责人权限细分

**当前**: 2001 (编辑节点负责人)

**扩展方向**:
- 2001-1: 添加负责人
- 2001-2: 删除负责人
- 2001-3: 修改标准工时
- 2001-4: 切换主要负责人

## 演进方向(Future Evolution)

### 短期目标(3个月内)
- ✅ 完成owner模块从nodelist主模块的分离
- ✅ 统一API接口风格
- 🔄 优化批量操作性能
- 🔄 完善单元测试覆盖

### 中期目标(6个月内)
- 📋 支持负责人角色扩展
- 📋 实现负责人变更历史记录
- 📋 添加负责人工作量统计API
- 📋 优化权限验证逻辑

### 长期目标(12个月内)
- 📋 支持动态负责人分配规则
- 📋 实现负责人智能推荐
- 📋 集成组织架构管理
- 📋 支持负责人交接流程

## 模块特有名词索引

当用户提到以下名词时，应快速定位到此技能：

- **主要负责人/Minor负责人**: is_major字段的两种状态
- **标准工时**: standard_time字段，表示负责人在该节点的预期工作时间
- **权限代码2001**: 节点负责人编辑权限
- **批量设置**: SetNodeOwnerSerializer提供的批量设置接口
- **节点负责人保护**: 已完成节点只能由超级管理员修改的机制
- **owner子模块**: PM/nodelist/owner/目录，负责人管理独立模块
- **Project_Node_Owners**: 节点负责人模型，存储节点与用户的关联关系
- **PM_node_owners**: 数据库表名，存储节点负责人数据

## 参考资料

- **主模块**: PM/nodelist - 节点列表管理
- **权限模块**: PM/authority - 权限验证
- **用户模块**: SM/user - 用户管理
- **节点定义**: PSC/node/definition - 节点定义模板
- **项目日志**: PM/log - 项目操作日志

## 快速参考

### 导入示例
```python
from apps.PM.nodelist.owner.views import views_node_owner, NodeOwnerViews
from apps.PM.nodelist.owner.serializers import serializer_node_owner, SetNodeOwnerSerializer
from apps.PM.models import Project_Node_Owners
```

### 常用查询
```python
# 获取节点的所有负责人
owners = node.node_owners.all().order_by('-is_major')

# 获取用户负责的所有节点
nodes = user.node_owner.all()

# 获取节点的主要负责人
major_owner = node.node_owners.filter(is_major=True).first()
```

### 权限验证模板
```python
from apps.PM.authority import authority as authority_project

authority = authority_project.permission(node_id, userinfo, 'project_node')
if not authority.verify(2001):
    return JsonResponse({'msg': '操作失败，权限不匹配'}, status=400)
```
