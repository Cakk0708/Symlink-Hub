# PM 交付物冻结模块专家

## 模块定位

交付物冻结模块（`apps/PM/deliverable/freeze/`）是 PM 项目管理系统中负责交付物状态控制的核心子模块。它通过交付物状态管理和冻结记录追踪，确保交付物在特定条件下不可被修改或删除，为项目变更管理、质量控制和合规性审计提供支持。

**核心职责：**
- 管理交付物冻结状态的生命周期
- 记录完整的冻结/解冻操作历史
- 与异步任务协同处理交付物异常状态
- 为前端提供冻结原因展示和操作权限判断

## 模块职责边界

### 负责范围
- ✅ 交付物冻结记录的创建与查询
- ✅ 冻结原因的存储与展示
- ✅ 冻结/解冻操作的人员与时间追踪
- ✅ 与交付物状态（`DeliverableState`）的联动
- ✅ 异步任务失败时的自动冻结处理

### 不负责范围
- ❌ 交付物上传流程（由 `instance` 模块负责）
- ❌ 文件存储管理（由 `file` 模块负责）
- ❌ 权限验证（由 `authority` 模块负责）
- ❌ 交付物检查/删除业务逻辑（由 `instance/serializers.py` 负责）

## 核心数据模型

### DeliverableFreeze 模型
```python
class DeliverableFreeze(models.Model):
    """交付物冻结记录"""
    deliverable = models.ForeignKey(
        'PM.DeliverableInstance',
        on_delete=models.CASCADE,
        verbose_name='交付物',
        related_name='freeze_records'  # 重要：通过此反向关联查询
    )
    reason = models.CharField(max_length=255, null=True, verbose_name='冻结原因')
    frozen_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='冻结人',
        related_name='frozen_deliverables'
    )
    frozen_at = models.DateTimeField(auto_now_add=True, verbose_name='冻结时间')
    unfrozen_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='解冻人',
        related_name='unfrozen_deliverables'
    )
    unfrozen_at = models.DateTimeField(null=True, blank=True, verbose_name='解冻时间')
```

**关键字段说明：**
- `deliverable`: 关联的交付物实例，通过 `freeze_records` 反向查询
- `reason`: 冻结原因，可为空（手动冻结通常需要填写）
- `frozen_by`/`unfrozen_by`: 操作人，使用 `SET_NULL` 保证用户删除后记录不丢失
- `unfrozen_at`: 为 `NULL` 时表示当前仍处于冻结状态

**数据库表：** `PM_deliverable_freeze`

## 序列化器

### FreezeDeliverableSerializer
**文件：** `apps/PM/deliverable/freeze/serializers.py`

**职责：** 处理交付物冻结/解冻切换的序列化和验证

**字段：**
- `reason`: CharField，可选，冻结/解冻原因（最大255字符）

**方法：**
- `validate()`: 验证权限（权限码2300）和状态（只允许NORMAL和FROZEN之间切换）
- `save()`: 根据当前状态执行冻结或解冻操作
- `_freeze()`: 执行冻结操作，创建冻结记录
- `_unfreeze()`: 执行解冻操作，更新冻结记录

## 视图

### DeliverableFreezeView
**文件：** `apps/PM/deliverable/freeze/views.py`

**职责：** 处理冻结/解冻请求的API视图

**端点：** `PATCH /pm/deliverable/instance/{id}/freeze`

**响应格式：**
```json
{
  "msg": "success",
  "data": {
    "id": 1,
    "state": "FROZEN",        // 或 "NORMAL"
    "stateDisplay": "冻结",    // 或 "正常"
    "action": "freeze"         // 或 "unfreeze"
  }
}
```

## URL 路由配置

**文件：** `apps/PM/deliverable/urls.py`

**路由：**
```python
path('/instances/<int:deliverable_id>/freeze', DeliverableFreezeView.as_view())
```

## 与交付物状态的关系

交付物模块定义了三种状态（`DeliverableState` 枚举）：

| 状态值 | 状态名称 | 说明 | 冻结记录状态 |
|--------|----------|------|--------------|
| `normal` | 正常 | 交付物可正常访问和修改 | 无活跃冻结记录 |
| `frozen` | 冻结 | 交付物被锁定，不可访问 | 存在 `unfrozen_at=NULL` 的记录 |
| `initial_frozen` | 初始冻结 | 新上传交付物等待异步处理 | 无冻结记录，但状态非正常 |

**关键业务规则：**
1. 冻结状态由 `DeliverableInstance.state` 控制
2. `DeliverableFreeze` 记录操作历史，不直接控制状态
3. 异步任务失败时自动创建冻结记录并设置状态为 `frozen`

## 权限验证流程

冻结模块本身不处理权限验证，依赖调用方完成：

### 在序列化器中检查冻结状态
```python
# apps/PM/deliverable/instance/serializers.py:88-97
if deliverable_instance.state == DeliverableState.FROZEN.value and not is_superuser:
    # 获取最新的冻结记录中的原因
    latest_freeze = deliverable_instance.freeze_records.filter(unfrozen_at__isnull=True).first()
    if latest_freeze and latest_freeze.reason:
        message += '，冻结原因："%s"' % latest_freeze.reason

    raise serializers.ValidationError({'当前交付物已冻结': message})
```

**权限检查要点：**
- 超级管理员（`is_superuser`）可绕过冻结检查
- 普通用户遇到冻结状态时需查看最新的冻结原因
- 通过 `freeze_records.filter(unfrozen_at__isnull=True).first()` 获取活跃冻结记录

## 与其他模块的关系

### 1. 交付物实例模块（instance）
- **关联方式：** `DeliverableFreeze.deliverable` → `DeliverableInstance`
- **反向查询：** `deliverable_instance.freeze_records.all()`
- **状态联动：** 冻结记录创建时需同步更新 `DeliverableInstance.state`

### 2. 异步任务模块（tasks）
**自动冻结场景：**
```python
# apps/PM/deliverable/instance/tasks.py:134-146
# 异步上传失败时的处理
if MaxRetriesExceededError:
    deliverable.state = DeliverableState.FROZEN.value
    deliverable.save()

    # 创建冻结记录
    from apps.PM.deliverable.freeze.models import DeliverableFreeze
    DeliverableFreeze.objects.create(
        deliverable=deliverable,
        reason='异步上传失败，请手动重试'
    )
```

### 3. 权限验证模块（authority）
- 冻结模块不直接调用权限验证
- 由上层业务逻辑（如序列化器）负责权限检查
- 权限代码定义在 `apps/PM/authority/enums.py`

### 4. 交付物文件模块（file）
- 冻结模块不直接操作文件记录
- 文件状态变化由实例模块协调
- 文件删除受冻结状态保护（通过实例模块的删除序列化器）

## 常见业务场景

### 场景1：新上传交付物的初始冻结
**触发条件：** 用户上传新交付物
**处理流程：**
1. 创建 `DeliverableInstance` 时设置状态为 `INITIAL_FROZEN`
2. 异步任务处理完成后更新状态为 `NORMAL`
3. 若异步任务失败，创建 `DeliverableFreeze` 记录并设置状态为 `FROZEN`

**代码位置：** `apps/PM/deliverable/instance/services.py:184-194`

### 场景2：异步任务失败自动冻结
**触发条件：** Celery 任务重试次数耗尽
**处理流程：**
1. 捕获 `MaxRetriesExceededError` 异常
2. 更新交付物状态为 `FROZEN`
3. 创建冻结记录，原因包含失败信息
4. 记录日志供运维排查

**代码位置：** `apps/PM/deliverable/instance/tasks.py:130-146`

### 场景3：用户访问被冻结的交付物
**触发条件：** 用户请求获取或修改已冻结的交付物
**处理流程：**
1. 序列化器检查 `deliverable.state == DeliverableState.FROZEN.value`
2. 查询最新的活跃冻结记录
3. 提取冻结原因并附加到错误信息
4. 抛出 `ValidationError` 阻止操作

**代码位置：** `apps/PM/deliverable/instance/serializers.py:88-97`

### 场景4：冻结/解冻切换操作
**触发条件：** 用户调用冻结/解冻接口
**处理流程：**
1. 验证用户权限（权限码2300）
2. 检查当前交付物状态
3. 若为 NORMAL 状态，执行冻结：
   - 更新 `DeliverableInstance.state` 为 `FROZEN`
   - 创建新的 `DeliverableFreeze` 记录
   - 记录操作日志
4. 若为 FROZEN 状态，执行解冻：
   - 更新 `DeliverableInstance.state` 为 `NORMAL`
   - 更新对应 `DeliverableFreeze` 记录的 `unfrozen_at` 和 `unfrozen_by`
   - 记录操作日志

**代码位置：** `apps/PM/deliverable/freeze/serializers.py:18-118`

## 技术实现建议（Django）

### 查询活跃冻结记录
```python
# 获取当前处于冻结状态的记录
active_freeze = deliverable.freeze_records.filter(unfrozen_at__isnull=True).first()

# 判断是否有活跃冻结
is_frozen = deliverable.freeze_records.filter(unfrozen_at__isnull=True).exists()
```

### 创建冻结记录
```python
from apps.PM.deliverable.freeze.models import DeliverableFreeze

freeze_record = DeliverableFreeze.objects.create(
    deliverable=deliverable_instance,
    reason='项目设计变更中，暂停交付物修改',
    frozen_by=request.user
)

# 同步更新交付物状态
from apps.PM.deliverable.instance.enums import DeliverableState
deliverable_instance.state = DeliverableState.FROZEN.value
deliverable_instance.save()
```

### 批量冻结（项目变更场景）
```python
from apps.PM.deliverable.freeze.models import DeliverableFreeze

# 获取项目下所有节点的交付物
deliverables = DeliverableInstance.objects.filter(
    project_node__list_id=project_id
)

# 批量创建冻结记录
freeze_records = [
    DeliverableFreeze(
        deliverable=d,
        reason='项目进入设计变更流程',
        frozen_by=request.user
    )
    for d in deliverables
]

DeliverableFreeze.objects.bulk_create(freeze_records)

# 批量更新状态
deliverables.update(state=DeliverableState.FROZEN.value)
```

## 扩展设计策略

### 1. 冻结策略枚举
**当前限制：** 冻结原因仅为字符串，缺乏结构化

**改进方案：**
```python
class FreezeReason(models.TextChoices):
    MANUAL = 'manual', '手动冻结'
    ASYNC_FAILED = 'async_failed', '异步处理失败'
    PROJECT_CHANGE = 'project_change', '项目设计变更'
    PROJECT_PAUSE = 'project_pause', '项目暂停'
    QUALITY_ISSUE = 'quality_issue', '质量问题'

class DeliverableFreeze(models.Model):
    reason_type = models.CharField(
        max_length=20,
        choices=FreezeReason.choices,
        default=FreezeReason.MANUAL,
        verbose_name='冻结原因类型'
    )
    reason = models.CharField(max_length=255, null=True, verbose_name='冻结详情')
```

### 2. 冻结权限控制
**当前状态：** 权限逻辑分散在各序列化器中

**改进方案：**
```python
# apps/PM/deliverable/freeze/services.py
class FreezePermissionService:
    @staticmethod
    def can_freeze(user, deliverable):
        """检查是否可以冻结交付物"""
        from apps.PM.authority.utils import AuthorityVerifier

        auth = AuthorityVerifier(
            target_id=deliverable.node_id,
            userinfo=user,
            type='project_node'
        )
        return auth.verify(2009) or user.is_superuser

    @staticmethod
    def can_unfreeze(user, deliverable):
        """检查是否可以解冻交付物"""
        # 更严格的权限控制
        return user.is_superuser or user.id == deliverable.project_node.list.owner_id
```

### 3. 冻结审计日志
**当前限制：** 只有冻结记录，无审计日志

**改进方案：**
```python
class DeliverableFreezeAudit(models.Model):
    """交付物冻结操作审计"""
    freeze_record = models.ForeignKey(DeliverableFreeze, on_delete=models.CASCADE)
    action = models.CharField(max_length=10)  # freeze/unfreeze
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    operated_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
```

## 演进方向

### 短期优化（3-6个月）
1. ✅ **补全解冻接口：** 已实现冻结/解冻切换功能的 REST API（2024年完成）
2. **冻结原因结构化：** 使用枚举替代纯字符串
3. **批量操作支持：** 支持项目级别的批量冻结/解冻
4. **冻结通知集成：** 通过飞书推送冻结状态变更通知

### 中期规划（6-12个月）
1. **权限系统整合：** 与 `authority` 模块深度集成
2. **审计日志完善：** 建立完整的操作审计链
3. **冻结工作流：** 支持冻结申请审批流程
4. **状态机增强：** 引入 Django-FSM 管理交付物状态

### 长期愿景（12个月以上）
1. **智能冻结策略：** 基于项目状态自动冻结相关交付物
2. **冻结影响分析：** 分析冻结对项目进度的影响
3. **多级冻结：** 支持只读、可下载、完全锁定等多级冻结
4. **跨模块联动：** 与项目变更、暂停流程深度整合

## 特有名词解释

| 名词 | 定位 | 相关文件 |
|------|------|----------|
| **DeliverableFreeze** | 冻结记录模型 | `apps/PM/deliverable/freeze/models.py` |
| **freeze_records** | 反向关联名称 | `DeliverableInstance.freeze_records` |
| **unfrozen_at** | 解冻时间戳 | `DeliverableFreeze.unfrozen_at` |
| **DeliverableState** | 交付物状态枚举 | `apps/PM/deliverable/instance/enums.py` |
| **async_upload_deliverable_task** | 异步上传任务 | `apps/PM/deliverable/instance/tasks.py:20-148` |
| **INITIAL_FROZEN** | 初始冻结状态 | 新上传交付物等待异步处理 |
| **FROZEN** | 冻结状态 | 交付物被锁定，不可访问 |
| **AuthorityVerifier** | 权限验证器 | `apps/PM/authority/utils.py` |
| **FreezeDeliverableSerializer** | 冻结/解冻序列化器 | `apps/PM/deliverable/freeze/serializers.py` |
| **DeliverableFreezeView** | 冻结/解冻视图 | `apps/PM/deliverable/freeze/views.py` |

## 关键代码片段索引

| 功能 | 文件路径 | 行号 |
|------|----------|------|
| 模型定义 | `apps/PM/deliverable/freeze/models.py` | 9-42 |
| 冻结/解冻序列化器 | `apps/PM/deliverable/freeze/serializers.py` | 18-118 |
| 冻结/解冻视图 | `apps/PM/deliverable/freeze/views.py` | 18-47 |
| 冻结检查逻辑 | `apps/PM/deliverable/instance/serializers.py` | 88-97 |
| 反向关联查询 | `apps/PM/deliverable/instance/serializers.py` | 93 |
| 异步任务冻结 | `apps/PM/deliverable/instance/tasks.py` | 140-144 |
| 异步任务冻结（file模块） | `apps/PM/deliverable/file/tasks.py` | 140-144 |
| 状态枚举定义 | `apps/PM/deliverable/instance/enums.py` | 7-15 |
| 权限验证工具 | `apps/PM/authority/utils.py` | 21-212 |

## 常见问题排查

### Q1: 为什么交付物无法解冻？
**排查步骤：**
1. 检查 `DeliverableInstance.state` 是否为 `frozen`
2. 查询是否存在 `unfrozen_at=NULL` 的冻结记录
3. 确认当前用户权限（是否超级管理员或项目负责人）
4. 查看是否有解冻接口实现

### Q2: 异步任务失败后如何恢复？
**处理方案：**
1. 查看 `DeliverableFreeze` 记录的冻结原因
2. 检查 Celery 日志确认失败原因
3. 修复问题后手动触发异步任务或重新上传
4. 解冻交付物并清理冻结记录

### Q3: 如何批量冻结项目交付物？
**实现方式：**
```python
# 获取项目所有交付物
deliverables = DeliverableInstance.objects.filter(
    project_node__list_id=project_id
)

# 创建冻结记录
DeliverableFreeze.objects.bulk_create([
    DeliverableFreeze(
        deliverable=d,
        reason='项目暂停',
        frozen_by=request.user
    )
    for d in deliverables
])

# 更新状态
deliverables.update(state=DeliverableState.FROZEN.value)
```
