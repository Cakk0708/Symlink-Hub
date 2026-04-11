# PM 交付物实例模块专家

## 模块定位

`apps/PM/deliverable/instance/` 是 PM 项目管理系统中**交付物实例**的核心业务模块。

本模块负责管理项目节点中实际上传的交付物文件的业务逻辑，与文件存储层（`file/`）和权限验证层（`authority/`）协同工作，确保交付物从创建到使用的全生命周期管理。

### 核心职责

- **交付物业务管理**：创建、更新、删除、查询交付物实例
- **权限控制**：多层级权限验证（基于角色、部门、项目状态）
- **状态管理**：处理交付物状态（正常、冻结、初始冻结、评审拒绝）
- **评审节点联动**：处理评审节点回滚逻辑
- **异步处理**：使用 Celery 处理文件上传和移动的异步任务
- **🆕 信号驱动**（Since 2026-03-06）：通过 Django 信号监听交付物实例创建事件，自动触发临时文件迁移
- **🆕 解析序列化器**（Since 2026-03-12）：解析交付物下载链接，简化权限验证流程
- **🆕 重新上传**（Since 2026-03-18）：评审拒绝后重新上传交付物，状态切换为正常

## 模块边界

### 职责范围

- ✅ 交付物实例的 CRUD 操作
- ✅ 交付物权限验证
- ✅ 交付物状态管理（冻结/解冻）
- ✅ 交付物删除权限检查
- ✅ 评审节点回滚处理
- ✅ 交付物历史版本查询
- ✅ 🆕 临时文件迁移信号处理
- ✅ 🆕 解析交付物下载链接
- ✅ 🆕 重新上传评审拒绝的交付物

### 不负责

- ❌ 文件物理存储（由 `apps/PM/deliverable/file/` 负责）
- ❌ 飞书文件夹管理（由 `apps/PM/deliverable/folder/` 负责）
- ❌ 交付物定义配置（由 `apps/PSC/deliverable/` 负责）
- ❌ 硬件交付物关联（由 `apps/PM/hardwares/deliverable/` 负责）
- ❌ 交付物冻结操作（由 `apps/PM/deliverable/freeze/` 负责）

## 触发条件

当用户提到以下术语时，应该激活此技能：

- **关键词**：交付物实例、DeliverableInstance、交付物上传、交付物检查、交付物删除
- **操作场景**：上传交付物、获取交付物、删除交付物、更新交付物版本号
- **相关问题**：交付物权限、交付物状态、交付物冻结、交付物评审
- **文件操作**：项目文件、节点文件、附件管理
- **🆕 信号处理**（Since 2026-03-06）：临时文件迁移、信号监听、自动触发任务
- **🆕 解析下载**（Since 2026-03-12）：解析序列化器、下载链接、权限解析
- **🆕 重新上传**（Since 2026-03-18）：评审拒绝后重新上传、状态切换

## 核心数据模型

### DeliverableInstance（交付物实例）

**主表模型**：`apps/PM/deliverable/instance/models.py:12`

```python
class DeliverableInstance(models.Model):
    """交付物实例模型 - 只负责业务逻辑"""

    # 业务关联
    project_node = models.ForeignKey('PM.Project_Node', ...)  # 所属节点
    definition = models.ForeignKey('PSC.DeliverableDefinitionVersion', ...)  # 🆕 交付物版本
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, ...)  # 创建人

    # 关联文件（改为 ForeignKey）
    file = models.ForeignKey('PM.DeliverableFile', ...)  # 🆕 改为外键关联

    # 业务属性
    version = models.CharField(max_length=255, null=True)  # 文件版本
    remark = models.CharField(max_length=255, null=True, blank=True)  # 🆕 备注（原 note）
    url = models.URLField(max_length=2000, null=True, blank=True)  # 🆕 外部链接（原 url_txt）
    state = models.CharField(...)  # 状态：normal/frozen/initial_frozen

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**表名**：`PM_deliverable_instance`

**向后兼容别名**：`ProjectAttachmentList`、`Deliverable`

### 🆕 模型字段变更（2026年更新）

| 变更类型 | 旧字段/类型 | 新字段/类型 | 说明 |
|---------|------------|-------------|------|
| 字段重命名 | `note` | `remark` | 备注字段 |
| 字段重命名 | `url_txt` | `url` | 外部链接字段 |
| 关联变更 | `definition` → `PSC.DeliverableDefinition` | `definition` → `PSC.DeliverableDefinitionVersion` | 指向交付物版本 |
| 关联变更 | `file` → `OneToOneField` | `file` → `ForeignKey` | 改为外键关联 |
| 字段删除 | `type: IntegerField` | - | 删除类型字段 |

### 关键关系

1. **文件关系**（ForeignKey）
   - `DeliverableInstance.file` → `DeliverableFile`（文件主表）
   - 通过 `DeliverableFile.feishu` 访问飞书特有字段（token、folder、path）

2. **业务关系**
   - `project_node` → `Project_Node`：所属项目节点
   - `definition` → `PSC.DeliverableDefinitionVersion`：🆕 交付物版本
   - `created_by` → `SM.User`：创建人

3. **反向关系**
   - `freeze_records`：`DeliverableFreeze` 外键反向查询
   - `hardware_relations`：`HardwareDeliverable` 多对多关系

## 状态枚举（Django TextChoices）

**位置**：`apps/PM/deliverable/instance/enums.py:7`

**🆕 新结构（2026年更新）**：

```python
class Choices:
    """枚举基类"""

    class DeliverableState(models.TextChoices):
        """交付物状态枚举"""
        NORMAL = 'NORMAL', '正常'
        FROZEN = 'FROZEN', '冻结'
        INITIAL_FROZEN = 'INITIAL_FROZEN', '初始冻结'  # 新上传的交付物，等待异步处理
        STORAGE_MIGRATION_ERROR = 'STORAGE_MIGRATION_ERROR', '储存迁移异常'  # 上传交付物储存迁移异常
        REVIEW_REJECTED = 'REVIEW_REJECTED', '评审拒绝'  # 🆕 评审项拒绝后交付物状态（Since 2026-03-18）
```

**使用方式**：
- 访问枚举值：`Choices.DeliverableState.NORMAL`（无需 `.value`）
- 获取选项：`Choices.DeliverableState.choices`

## 飞书权限验证器（🆕 Since 2026-03-19）

### FeishuPermissionValidator

**位置**：`apps/PM/deliverable/instance/validators.py:24`

**功能**：飞书文件权限验证器，验证用户对飞书交付物的访问权限，并自动赋予对应权限。

**权限规则**：

| 权限类型 | 条件 |
|---------|------|
| **编辑权限** | 用户是该交付物所属节点负责人 |
| **编辑权限** | 用户 `is_superuser=True` |
| **编辑权限** | 用户 `is_executive_core=True` |
| **浏览权限** | 其他所有情况 |

**权限等级**：

```python
PERMISSION_LEVEL = {
    'view': 1,
    'edit': 2,
    'full_access': 3,
}
```

**核心方法**：

```python
class FeishuPermissionValidator:
    @classmethod
    def validate_and_grant_permission(cls, deliverable_instance, user):
        """
        验证并授予用户对交付物的飞书文件权限

        流程：
        1. 检查是否为飞书文件
        2. 获取用户应有的权限
        3. 获取用户 open_id
        4. 检查用户是否已有权限
        5. 如权限不足则升级权限
        6. 如无权限则添加权限
        """

    @classmethod
    def _check_existing_permission(cls, category, file_token, open_id):
        """
        检查用户是否已拥有权限
        使用 permissions_get_members_list 获取权限成员列表
        返回用户当前的权限类型或 None
        """

    @classmethod
    def _permission_sufficient(cls, existing_permission, required_permission):
        """
        判断现有权限是否满足需求
        使用权限等级比较，支持权限升级
        """

    @classmethod
    def _grant_feishu_permission(cls, category, file_token, open_id,
                                 permission_type, user):
        """
        调用飞书文件管理器为用户添加权限
        使用 FeishuFileManager.permissions_add
        """
```

**使用场景**：

- 用户访问交付物实例详情时
- 自动分配飞书文件权限
- 权限升级（从 view 升级到 edit）

**依赖**：

- `utils/openapi/feishu/FeishuFileManager` - 飞书文件管理器
- `utils/user.py::get_user_feishu_open_id()` - 获取用户 open_id

## 序列化器架构

### 🆕 WriteDeliverableSerializer（创建交付物）

**位置**：`apps/PM/deliverable/instance/serializers.py:639`

**类型**：`ModelSerializer`

```python
class WriteDeliverableSerializer(serializers.ModelSerializer):
    """创建交付物序列化器"""
    projectNodeId = serializers.PrimaryKeyRelatedField(
        source='project_node',
        queryset=model_node.objects.all()
    )
    definitionId = serializers.PrimaryKeyRelatedField(
        source='definition',
        queryset=DeliverableDefinitionVersion.objects.all()
    )
    fileId = serializers.PrimaryKeyRelatedField(
        source='file',
        queryset=DeliverableFile.objects.all(),
        required=False, allow_null=True
    )
    url = serializers.URLField(required=False, allow_null=True, allow_blank=True, max_length=2000)
    version = serializers.CharField(required=False, allow_null=True, allow_blank=True, max_length=255)
    remark = serializers.CharField(required=False, allow_null=True, allow_blank=True, max_length=255)

    class Meta:
        model = DeliverableInstance
        fields = ['projectNodeId', 'definitionId', 'fileId', 'url', 'version', 'remark']
```

**字段映射**（camelCase → snake_case）：
- `projectNodeId` → `project_node`
- `definitionId` → `definition`
- `fileId` → `file`
- `url` → `url`
- `version` → `version`
- `remark` → `remark`

### 🆕 ResolveDeliverableSerializer（解析序列化器）

**位置**：`apps/PM/deliverable/instance/serializers.py:498`

**类型**：`Serializer`

**功能**：解析交付物下载链接，简化权限验证流程

```python
class ResolveDeliverableSerializer(serializers.Serializer):
    """解析序列化器 - 用于解析交付物下载链接"""
    id = serializers.PrimaryKeyRelatedField(
        queryset=DeliverableInstance.objects.all(),
        required=True,
        help_text='交付物实例ID'
    )
```

**流程**：
1. 接收实例ID（使用PrimaryKeyRelatedField）
2. 验证实例是否可被获取（条件验证）
3. 验证通过后返回最终数据

**最终数据**：
```python
{
    'id': 实例ID,
    'url': 下载地址
}
```

**条件验证**：
1. **冻结状态检查**：只有 `state` 为 `NORMAL` 的才可以下载（超级用户除外）
2. **获取人验证**：
   - 超级用户可下载
   - 交付物创建者可下载
   - 与创建者同部门的人可下载
   - 节点负责人可下载

**URL构造规则**：
- 优先返回交付物的 `url` 字段
- 否则拼接飞书文件下载链接：`{feishu_header}/{category}/{token}`

**🆕 飞书权限授予（Since 2026-03-19）**：

```python
def to_representation(self, instance):
    """构造返回数据，只返回 {id, url}"""
    # 如果是飞书文件，先验证并授予权限
    if instance.file and instance.file.storage_provider == 'FEISHU':
        try:
            permission_result = FeishuPermissionValidator.validate_and_grant_permission(
                instance, self.request.user
            )
            self.permission_granted = permission_result
        except serializers.ValidationError as e:
            # 权限授予失败时记录错误，但不阻止用户访问
            self.permission_error = str(e.detail)
```

**权限授予流程**：
1. 检查交付物是否为飞书文件
2. 调用 `FeishuPermissionValidator.validate_and_grant_permission()`
3. 验证器检查用户身份和应有的权限
4. 使用 `FeishuFileManager.permissions_get_members_list()` 检查现有权限
5. 如权限不足则升级权限
6. 如无权限则调用 `FeishuFileManager.permissions_add()` 添加权限
7. 根据权限类型记录不同的操作日志（编辑了/查看了）

### 其他序列化器

| 序列化器 | 用途 | 位置 |
|---------|------|------|
| `DetailSerializer` | 获取交付物详情（含权限验证、飞书权限分配） | serializers.py:25 |
| `DeleteDeliverableSerializer` | 删除交付物权限验证 | serializers.py:362 |
| `UpdateDeliverableSerializer` | 更新交付物元数据 | serializers.py:429 |
| `ResolveDeliverableSerializer` | 解析交付物下载链接 | serializers.py:517 |
| `WriteDeliverableSerializer` | 创建交付物实例 | serializers.py:682 |
| `ReuploadDeliverableSerializer` | 🆕 重新上传评审拒绝的交付物 | serializers.py:786 |

## 视图架构

### 🆕 DeliverableListView（列表视图）

**位置**：`apps/PM/deliverable/instance/views.py:19`

```python
class DeliverableListView(views.APIView):
    """交付物列表视图"""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """创建交付物实例"""
        serializer = WriteDeliverableSerializer(
            data=request.data,
            context={'request': request}
        )
        if not serializer.is_valid():
            return JsonResponse({
                'msg': common.construct_error_to_msg(serializer.errors)
            }, status=400)

        instance = serializer.save()

        return JsonResponse({
            'msg': 'success',
            'data': {'insertId': instance.id}
        }, status=201)
```

### 🆕 DeliverableDetailView（详情视图）

**位置**：`apps/PM/deliverable/instance/views.py:54`

```python
class DeliverableDetailView(views.APIView):
    """单个交付物详情视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request, deliverable_id):
        """获取交付物详情"""
        # 实现细节...

    def patch(self, request, deliverable_id):
        """部分更新交付物（版本号、备注、链接等）"""
        # 实现细节...

    def delete(self, request, deliverable_id):
        """删除交付物"""
        # 实现细节...
```

### 🆕 ReuploadDeliverableView（重新上传视图）

**位置**：`apps/PM/deliverable/instance/views.py:111`

**功能**：将评审拒绝状态的交付物重新切换为正常状态

```python
class ReuploadDeliverableView(views.APIView):
    """交付物重新上传视图"""
    permission_classes = [IsAuthenticated]

    def post(self, request, deliverable_id):
        """重新上传交付物（将状态从 REVIEW_REJECTED 切换为 NORMAL）"""
        # 验证状态必须为 REVIEW_REJECTED
        # 验证权限（创建者/项目负责人/超级管理员）
        # 更新状态为 NORMAL
        # 记录操作日志
```

**业务规则**：
- 交付物状态必须为 `REVIEW_REJECTED`
- 只有交付物创建者、项目负责人、超级管理员可操作

## 权限验证流程

### 1. 获取交付物权限（DetailSerializer）

**位置**：`apps/PM/deliverable/instance/serializers.py:25`

#### 权限验证层次

```
第一层：交付物状态检查
├── 冻结状态检查（state = 'FROZEN'）
│   ├── 超管直接通过
│   └── 普通用户需解冻
└── 临时token检查（token以'temp-'开头）
    └── 拒绝访问（文件正在处理中）

第二层：身份验证
├── 超级管理员（is_superuser）
├── 项目负责人（project_owner）
├── 交付物创建者（deliverable_creator）
└── 同部门成员（与节点负责人同部门）

第三层：项目/节点状态限制
├── 项目变更中（state=3）+ 节点变更中（state=4）
│   └── 拒绝获取
├── 项目已暂停（state=4）
│   └── 研发部特殊权限（对接需求节点）
└── 节点完成后编辑权限降级
    └── 编辑权限 → 查看权限

第四层：飞书权限分配
├── 检查云文档配置表
├── 匹配部门权限（查看/编辑）
├── 匹配人员权限（白名单）
└── 动态添加飞书文件权限
```

#### 特殊权限规则

**生产部特殊规则**（硬/软件资料复核节点）：

```python
# 规则映射
rule_map = {
    10611: 10612,  # 硬件交付资料 → BOM更新节点
    10613: 10622,
    10621: 10622
}

# 仅当复核节点完成后，才允许生产部查看对应的生产使用交付物资料
```

### 2. 🆕 解析交付物权限（ResolveDeliverableSerializer）

**位置**：`apps/PM/deliverable/instance/serializers.py:498`

**简化的权限验证层次**：

```
第一层：冻结状态检查
├── 只有 state = 'NORMAL' 的才可以下载
└── 超级用户可以访问任何状态的交付物

第二层：获取人验证
├── 超级用户（is_superuser）
├── 交付物创建者（created_by_id == current_user.id）
├── 节点负责人（user.open_id in node_owners）
└── 同部门用户（与创建者有相同部门ID）
```

**与 DetailSerializer 的区别**：
- ✅ 更简单的权限验证（无飞书权限分配）
- ✅ 更少的数据库查询（无需获取项目/节点详情）
- ✅ 返回数据更简洁（仅返回 id 和 url）
- ❌ 不支持项目/节点状态限制
- ❌ 不支持飞书权限动态分配

**适用场景**：
- 仅需获取下载链接，无需查看权限
- 已通过其他方式验证过用户身份
- 需要快速响应的场景

### 3. 删除交付物权限（DeleteDeliverableSerializer）

**位置**：`apps/PM/deliverable/instance/serializers.py:357`

#### 删除权限验证

1. **节点状态检查**
   - 节点已完成 → 拒绝删除

2. **节点归属检查**
   - 交付物来自其他节点 → 拒绝删除

3. **权限级别检查**
   - **首次完成后**：仅超管 + 项目负责人可删除
   - **非首次完成**：超管 + 项目负责人 + 创建人可删除

### 4. 更新交付物权限（UpdateDeliverableSerializer）

**位置**：`apps/PM/deliverable/instance/serializers.py:424`

- 通过 `AuthorityVerifier` 验证上传权限
- 权限码：`2009`（上传交付物）

## 🆕 信号处理架构（Since 2026-03-06）

### 信号处理器定义

**位置**：`apps/PM/deliverable/signals.py`

```python
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=DeliverableInstance)
def handle_deliverable_instance_created(sender, instance, created, **kwargs):
    """
    监听交付物实例创建事件

    当满足以下条件时，触发异步任务将临时文件迁移到飞书文件夹：
    1. 交付物实例为新创建
    2. 有关联的 file 对象
    3. file 是临时文件（is_temp=True）
    4. 存储服务商为 FEISHU
    """
```

### 信号触发条件

```
DeliverableInstance 创建
    ↓
检查 created == True
    ↓
检查 instance.file 存在
    ↓
检查 instance.file.is_temp == True
    ↓
检查 instance.file.storage_provider == 'FEISHU'
    ↓
触发 async_move_temp_file_to_folder_task.delay()
```

### 信号注册机制

**位置**：`apps/PM/signals.py:7`

```python
from .deliverable.signals import *
```

信号在应用启动时自动注册（通过 `apps.PM.apps.PmConfig.ready()`）。

## 与其他模块关系

### 依赖的上游模块

| 模块 | 用途 | 关键交互 |
|------|------|----------|
| `PM/deliverable/file` | 文件存储 | 通过 `ForeignKey` 关联 `DeliverableFile` |
| `PM/authority` | 权限验证 | 使用 `AuthorityVerifier` 检查操作权限 |
| `PM/deliverable/folder` | 文件夹管理 | 异步任务中确保项目文件夹存在 |
| `PSC/deliverable/` | 🆕 交付物版本 | 关联 `DeliverableDefinitionVersion` 获取规则配置 |
| `SM/user` | 🆕 用户模型 | 使用 `User.department` 属性获取部门信息 |

### 被依赖的下游模块

| 模块 | 用途 | 关键交互 |
|------|------|----------|
| `PM/deliverable/freeze` | 交付物冻结 | 通过 `freeze_records` 反向关系管理冻结记录 |
| `PM/hardwares/deliverable` | 硬件交付物 | 通过 `hardware_relations` 多对多关系关联硬件 |
| `PM/nodelist` | 节点管理 | 节点详情接口返回交付物列表 |
| `PM/signals` | 信号处理 | 监听交付物创建/删除事件 |

### 信号交互

**评审节点回滚信号**：

```python
# 当项目状态为已完成或变更中时，上传交付物需重新打开评审节点
if project_instance.state in [2, 3]:
    if node_instance.review_rule and node_instance.review_rule.get('type'):
        # 重置评审节点状态
        node_instance.review_rule['history'].append({
            'custom': node_instance.review_rule.get('custom', []),
            'state': 0  # 未评审状态
        })
        node_instance.state = 1  # 进行中
        node_instance.save()
```

**🆕 临时文件迁移信号**（Since 2026-03-06）：

```python
# 监听交付物实例创建事件
# 当交付物实例创建且文件为临时文件时，自动触发迁移任务
@receiver(post_save, sender=DeliverableInstance)
def handle_deliverable_instance_created(sender, instance, created, **kwargs):
    # 触发条件：新建实例 + 有关联文件 + 临时文件 + 飞书存储
    if created and instance.file and instance.file.is_temp and \
       instance.file.storage_provider == Choices.StorageProvider.FEISHU:
        async_move_temp_file_to_folder_task.delay(
            deliverable_id=instance.id,
            file_id=instance.file.id
        )
```

## 常见业务场景

### 场景1：上传交付物

**流程**：

1. 用户上传文件到临时目录
2. 创建 `DeliverableFile` 记录（文件主表）
3. 创建 `DeliverableFileFeishu` 记录（飞书子表，token 为临时）
4. 创建 `DeliverableInstance` 记录（业务表，状态为 `initial_frozen`）
5. 触发 Celery 异步任务 `async_upload_deliverable_task`
6. 异步任务将文件上传到飞书项目文件夹
7. 更新 token 为真实飞书 token，状态改为 `normal`

**关键代码位置**：
- `apps/PM/deliverable/file/views.py`：上传视图
- `apps/PM/deliverable/instance/tasks.py:21`：异步上传任务

### 场景2：获取交付物（完整权限验证）

**流程**：

1. 验证交付物状态（是否冻结、是否临时）
2. 验证用户身份和权限
3. 检查项目/节点状态限制
4. 动态分配飞书文件权限
5. 返回飞书文件访问 URL

**关键代码位置**：
- `apps/PM/deliverable/instance/serializers.py:25`：验证逻辑

### 场景3：🆕 解析交付物（简化权限验证）

**流程**（Since 2026-03-12）：

1. 接收交付物实例ID
2. 验证交付物状态（只有 NORMAL 状态可下载）
3. 验证用户身份（超管/创建者/节点负责人/同部门）
4. 构造下载URL（优先返回 url 字段，否则拼接飞书链接）
5. 返回 {id, url}

**关键代码位置**：
- `apps/PM/deliverable/instance/serializers.py:498`：解析序列化器

**适用场景**：
- 已通过其他方式验证用户身份
- 仅需获取下载链接
- 需要快速响应

### 场景4：删除交付物

**流程**：

1. 验证节点状态（不能已完成）
2. 验证节点归属（必须来自当前节点）
3. 验证删除权限（超管/项目负责人/创建人）
4. 执行删除（级联删除关联的 File 记录）
5. 记录操作日志

**关键代码位置**：
- `apps/PM/deliverable/instance/serializers.py:357`：验证逻辑
- `apps/PM/deliverable/instance/serializers.py:409`：执行删除

### 场景5：更新交付物元数据

**流程**：

1. 验证上传权限
2. 更新版本号（version 字段）
3. 添加备注记录（创建 `DeliverableNote`）
4. 返回更新后的数据

**关键代码位置**：
- `apps/PM/deliverable/instance/serializers.py:424`

### 场景6：创建交付物实例（触发信号）

**流程**（Since 2026-03-06）：

1. 接收 camelCase 格式的请求数据
2. 使用 `PrimaryKeyRelatedField` 验证关联对象
3. 验证上传权限
4. 创建 `DeliverableInstance` 记录
5. **自动触发信号**：如果关联文件为临时文件且存储服务商为飞书，自动触发迁移任务
6. 异步任务处理文件迁移

**关键代码位置**：
- `apps/PM/deliverable/signals.py:22`：信号处理器
- `apps/PM/deliverable/instance/tasks.py:247`：异步迁移任务
- `apps/PM/signals.py:7`：信号注册

### 场景7：🆕 重新上传评审拒绝的交付物（Since 2026-03-18）

**流程**：

1. 用户请求重新上传被评审拒绝的交付物
2. 验证交付物状态必须为 `REVIEW_REJECTED`
3. 验证用户权限（创建者/项目负责人/超级管理员）
4. 将交付物状态更新为 `NORMAL`
5. 记录操作日志

**关键代码位置**：
- `apps/PM/deliverable/instance/views.py:111`：重新上传视图
- `apps/PM/deliverable/instance/serializers.py:786`：重新上传序列化器

**接口**：
- `POST /pm/deliverable/instances/{deliverable_id}/reupload`

**适用场景**：
- 交付物被评审项拒绝后需要重新提交
- 用户修正了问题后需要重新提交评审

## 🆕 异步任务：临时文件迁移（Since 2026-03-07）

### async_move_temp_file_to_folder_task

**位置**：`apps/PM/deliverable/tasks.py:247`

**功能**：将临时文件迁移到飞书项目文件夹（四级结构）

**🆕 流程（Since 2026-03-07）**：

```
1. 获取交付物记录和文件记录
    ↓
2. 检查文件是否仍为临时文件（避免重复处理）
    ↓
3. 检查存储服务商是否为飞书
    ↓
4. 🆕 确保项目文件夹存在（包含交付物定义层级）
    ├─ 调用 async_ensure_folder_exists(project_id, deliverable_definition_code)
    └─ 返回交付物定义文件夹对象
    ↓
5. 🆕 将临时文件上传到目标文件夹
    ├─ 情况1：本地临时文件（temp_path 存在）
    │   ├─ 读取本地文件
    │   ├─ 使用 FeishuFileManager.file_upload() 上传到飞书
    │   └─ 删除本地临时文件（同时删除空父文件夹）
    └─ 情况2：飞书临时文件（temp_token 存在）
        └─ 使用 FeishuFileManager.move_file_with_retry() 移动文件
    ↓
6. 更新文件记录（标记为非临时文件）
    ├─ 清空临时字段（temp_path、temp_token）
    ├─ 设置 is_temp = False
    ├─ 更新或创建飞书子表的 token 记录
    └─ 更新交付物状态为 INITIAL_FROZEN
    ↓
7. 返回成功结果
```

**参数**：
- `deliverable_id`：交付物 ID
- 🆕 移除 `file_id` 参数（不再需要）

**返回值**：
```python
{
    'success': True,
    'deliverable_id': deliverable_id,
    'file_id': file_instance.id,
    'message': '迁移成功'
}
```

**错误处理**：
- 自动重试（最多 3 次，间隔 60 秒）
- 失败后标记交付物为 `STORAGE_MIGRATION_ERROR` 状态
- 🆕 移除创建冻结记录的逻辑（Since 2026-03-07）

**🆕 关键实现（Since 2026-03-07）**：
- 使用 `FeishuFileManager` 替代 `api_feishu.folder()`
- 根据文件来源（本地/飞书）选择不同的迁移策略
- 上传成功后删除本地临时文件和空文件夹
- 创建或更新飞书子表记录

## 技术实现建议

### Django 实践

1. **模型分离**
   - 业务模型（`DeliverableInstance`）与存储模型（`DeliverableFile`）分离
   - 🆕 使用 `ForeignKey` 替代 `OneToOneField` 关联文件

2. **序列化器设计**
   - 🆕 创建操作使用 `ModelSerializer`（`WriteDeliverableSerializer`）
   - 复杂验证使用 `Serializer`（`DetailSerializer`）
   - 🆕 解析操作使用简化 `Serializer`（`ResolveDeliverableSerializer`）
   - 验证逻辑集中在 `validate()` 方法中

3. **异步任务**
   - 文件上传使用 Celery 异步处理
   - 任务失败时自动重试（最多3次）
   - 临时文件清理机制
   - 🆕 临时文件迁移异步任务（`async_move_temp_file_to_folder_task`）

4. **权限验证**
   - 多层级权限检查（状态 → 身份 → 业务规则）
   - 动态飞书权限分配
   - 节点完成后权限降级
   - 🆕 简化权限验证（用于解析序列化器）

5. **🆕 信号驱动**（Since 2026-03-06）
   - 使用 `post_save` 信号监听模型创建
   - 自动触发异步任务
   - 通过 `apps/PM/signals.py` 统一注册

### 🆕 代码位置索引（2026年更新）

| 功能 | 文件路径 | 关键行号 |
|------|----------|----------|
| 模型定义 | `apps/PM/deliverable/instance/models.py` | 13 |
| 状态枚举 | `apps/PM/deliverable/instance/enums.py` | 7 |
| 🆕 飞书权限验证器 | `apps/PM/deliverable/instance/validators.py` | 24 |
| 获取验证（完整） | `apps/PM/deliverable/instance/serializers.py` | 25 |
| 删除验证 | `apps/PM/deliverable/instance/serializers.py` | 362 |
| 更新验证 | `apps/PM/deliverable/instance/serializers.py` | 429 |
| 解析序列化器 | `apps/PM/deliverable/instance/serializers.py` | 517 |
| 创建序列化器 | `apps/PM/deliverable/instance/serializers.py` | 682 |
| 🆕 重新上传序列化器 | `apps/PM/deliverable/instance/serializers.py` | 786 |
| 业务服务 | `apps/PM/deliverable/instance/services.py` | - |
| 列表视图 | `apps/PM/deliverable/instance/views.py` | 20 |
| 详情视图 | `apps/PM/deliverable/instance/views.py` | 54 |
| 🆕 重新上传视图 | `apps/PM/deliverable/instance/views.py` | 111 |

### 🆕 User 模型增强（Since 2026-03-12）

**位置**：`apps/SM/user/models.py:100`

```python
@property
def department(self):
    """
    返回用户的部门信息列表
    从 UserDepartment 关联关系中获取部门信息
    返回格式: [{'id': 'feishu_dept_id', 'name': 'dept_name'}, ...]
    """
    try:
        from apps.BDM.department.models import UserDepartment
        depts = UserDepartment.objects.filter(user=self).select_related('department')
        return [
            {
                'id': ud.feishu_department_id,
                'name': ud.department.name
            }
            for ud in depts
        ]
    except:
        return []
```

**用途**：
- 简化用户部门信息获取
- 用于权限验证中的同部门判断
- 替代原有的 `user.department` 字段访问方式

## 模块特有名词索引

当未来提及以下名词时，可快速定位到此技能：

| 名词 | 说明 |
|------|------|
| **DeliverableInstance** | 交付物实例模型，业务逻辑主表 |
| **交付物实例** | 本模块的业务概念，指已上传到节点的具体文件 |
| **初始冻结（initial_frozen）** | 新上传交付物的临时状态，等待异步处理完成 |
| **飞书权限动态分配** | 根据用户身份和业务状态动态添加飞书文件权限 |
| **评审节点回滚** | 项目完成后上传交付物时，自动重新打开评审节点 |
| **临时token** | 以'temp-'开头的token，表示文件正在处理中 |
| **权限降级** | 节点完成后，编辑权限自动降级为查看权限 |
| **生产部特殊规则** | 硬件/软件复核节点完成后，允许生产部查看特定交付物 |
| 🆕 **DeliverableDefinitionVersion** | 🆕 交付物版本模型，definition 字段指向的目标 |
| 🆕 **camelCase 序列化** | 🆕 前端使用 camelCase，序列化器使用 source 映射到模型字段 |
| 🆕 **信号驱动架构** | 🆕 使用 Django 信号监听交付物实例创建，自动触发异步任务 |
| 🆕 **临时文件迁移** | 🆕 交付物实例创建时，自动将临时文件迁移到飞书文件夹 |
| 🆕 **async_move_temp_file_to_folder_task** | 🆕 临时文件迁移异步任务 |
| 🆕 **ResolveDeliverableSerializer** | 🆕 解析序列化器，用于获取交付物下载链接 |
| 🆕 **解析序列化器** | 🆕 简化的权限验证序列化器，仅返回下载链接 |
| 🆕 **User.department** | 🆕 用户模型的部门属性，返回部门信息列表 |
| 🆕 **ReuploadDeliverableView** | 🆕 重新上传视图，处理评审拒绝后的重新上传 |
| 🆕 **ReuploadDeliverableSerializer** | 🆕 重新上传序列化器，验证状态和权限 |
| 🆕 **REVIEW_REJECTED 状态** | 🆕 评审拒绝状态，可通过重新上传接口切换为正常 |
| 🆕 **FeishuPermissionValidator** | 🆕 飞书权限验证器，自动授予用户飞书文件权限 |
| 🆕 **飞书权限授予** | 🆕 解析交付物时自动为用户授予飞书文件访问权限 |
| 🆕 **权限等级** | 🆕 飞书文件权限等级：view(1) < edit(2) < full_access(3) |

## 相关技能

- **pm-deliverable_file**：交付物文件存储模块
- **pm-deliverable_folder**：交付物文件夹管理模块
- **pm-deliverable_freeze**：交付物冻结管理模块
- **psc-deliverable**：🆕 交付物版本配置模块
- **pm-authority**：权限验证模块
- **pm-nodelist**：节点管理模块
- **sm-user**：🆕 用户模型模块（User.department 属性）
- **bdm-department**：🆕 部门管理模块（UserDepartment 模型）
- **utils-openapi-feishu**：🆕 飞书开放平台 API 管理器（FeishuFileManager）
