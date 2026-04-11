# PM交付物评价模块 (DeliverableEvaluate)

## 模块定位

`apps/PM/deliverable/evaluate/` 是 PM 项目管理系统中**交付物评价**功能的独立模块，负责记录和管理项目交付物的质量评价信息。

### 业务背景
在项目执行过程中，交付物（如设计文档、代码、测试报告等）完成后需要由项目负责人、节点负责人或协作者进行质量评价，以：
- 确保交付物符合项目要求
- 记录交付物质量情况
- 为绩效考核提供依据
- 积累项目经验知识

### 与其他评价模块的区别
| 模块 | 评价对象 | 存储位置 | 主要用途 |
|------|---------|---------|---------|
| **deliverable/evaluate** | 单个交付物 | `PM_deliverable_evaluate` | 交付物质量评价 |
| **evaluation/v2** | 项目整体 | `PM_evaluate_v2_*` | 项目绩效2.0 |
| **evaluation/v3** | 项目角色 | `PM_evaluate_v3_*` | 项目角色评价3.0 |


## 核心数据模型

### DeliverableEvaluate（交付物评价记录）

**位置**: `apps/PM/deliverable/evaluate/models.py`

**数据库表**: `PM_deliverable_evaluate`

```python
class DeliverableEvaluate(models.Model):
    # 关联交付物实例
    deliverable = models.ForeignKey(
        'PM.DeliverableInstance',
        on_delete=models.CASCADE,
        related_name='evaluate_records'
    )

    # 评价内容（JSON格式存储）
    content = models.JSONField(null=True)

    # 评价人
    evaluated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='evaluated_deliverables'
    )

    # 评价时间
    evaluated_at = models.DateTimeField(auto_now_add=True)
```

### 关联关系
```
DeliverableInstance (交付物实例)
    ↓ 1:N
DeliverableEvaluate (评价记录)
    ↑ N:1
User (评价人)
```


## 模块职责边界

### 负责的功能
- ✅ 创建交付物评价记录
- ✅ 存储评价内容（JSON格式，支持灵活的评价维度）
- ✅ 记录评价人和评价时间
- ✅ 关联到具体的交付物实例

### 不负责的功能
- ❌ 交付物上传管理（由 `deliverable/file` 负责）
- ❌ 交付物冻结/解冻（由 `deliverable/freeze` 负责）
- ❌ 交付物权限验证（由 `deliverable/instance` 负责）
- ❌ 项目整体绩效评价（由 `evaluation/v2`, `evaluation/v3` 负责）
- ❌ 评价权限验证（通过 `apps/PM/authority` 模块）


## 权限验证流程

### 评价权限代码
根据 `apps/PM/authority/enums.py:81`，交付物评分权限代码为 **2007**：

```python
(2007, '交付物评分', ('OWNER', 'SUPERUSER', 'OWNER_NODE', 'ASSISTOR')),
```

### 允许评价的身份
- **OWNER**: 项目负责人
- **SUPERUSER**: 超级管理员
- **OWNER_NODE**: 节点负责人
- **ASSISTOR**: 节点协作者

### 权限验证流程
1. 用户发起评价请求
2. 系统检查用户身份（通过 `apps/PM/authority/utils.py`）
3. 验证用户是否具有该交付物的评价权限
4. 验证交付物状态（非冻结、非删除）
5. 创建评价记录


## 与其他模块关系

### 1. 交付物模块内部关系
```
PM/deliverable/
├── instance/       # 交付物实例主模块（被评价对象）
├── evaluate/       # 本模块（评价记录）
├── file/          # 交付物文件存储
├── freeze/        # 交付物冻结管理
└── folder/        # 交付物文件夹管理
```

### 2. 与评价体系的关系
```
PM 评价体系
├── deliverable/evaluate/    # 交付物评价（颗粒度最小）
├── evaluation/v2/           # 项目绩效2.0（项目级）
└── evaluation/v3/           # 项目角色评价3.0（角色级）
```

### 3. 外部依赖
- **PM.models**: 项目、节点等核心模型
- **PSC.models**: 交付物定义配置
- **SM.User**: 用户模型（评价人）


## 常见业务场景

### 场景1: 节点负责人评价交付物
```python
# 节点负责人对完成的设计文档进行评价
deliverable = DeliverableInstance.objects.get(id=123)
evaluation = DeliverableEvaluate.objects.create(
    deliverable=deliverable,
    content={
        "quality_score": 5,
        "completeness": 4,
        "timeliness": 5,
        "comments": "设计规范，符合项目要求"
    },
    evaluated_by=request.user
)
```

### 场景2: 项目负责人批量评价
```python
# 项目负责人对某节点的所有交付物进行评价
node = Project_Node.objects.get(id=456)
deliverables = node.deliverables.all()

for deliverable in deliverables:
    DeliverableEvaluate.objects.create(
        deliverable=deliverable,
        content={
            "overall_score": 4,
            "notes": "整体质量良好，建议改进细节"
        },
        evaluated_by=project_owner
    )
```

### 场景3: 查询交付物评价记录
```python
# 获取某个交付物的所有评价记录
deliverable = DeliverableInstance.objects.get(id=123)
evaluations = deliverable.evaluate_records.all().order_by('-evaluated_at')

# 获取某个用户参与评价的所有交付物
user_evaluations = request.user.evaluated_deliverables.all()
```


## 技术实现建议

### 1. JSON字段设计
`content` 字段使用 JSONField 存储评价内容，建议结构：

```python
{
    "scores": {
        "quality": 5,      # 质量评分
        "completeness": 4, # 完整性评分
        "timeliness": 5    # 及时性评分
    },
    "overall_score": 4.7,  # 综合评分
    "comments": "评价文本内容",
    "tags": ["优秀", "规范"],  # 标签
    "improvements": ["建议1", "建议2"]  # 改进建议
}
```

### 2. 序列化器设计
```python
class DeliverableEvaluateSerializer(serializers.ModelSerializer):
    evaluated_by_name = serializers.CharField(source='evaluated_by.nickname', read_only=True)

    class Meta:
        model = DeliverableEvaluate
        fields = ['id', 'deliverable', 'content', 'evaluated_by',
                  'evaluated_by_name', 'evaluated_at']

    def validate_content(self, value):
        """验证评价内容格式"""
        if not isinstance(value, dict):
            raise ValidationError("评价内容必须为JSON对象")
        return value
```

### 3. 视图设计
```python
class DeliverableEvaluateViewSet(viewsets.ModelViewSet):
    queryset = DeliverableEvaluate.objects.all()
    serializer_class = DeliverableEvaluateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """创建时自动设置评价人"""
        serializer.save(evaluated_by=self.request.user)

    def get_queryset(self):
        """过滤查询结果"""
        queryset = super().get_queryset()
        deliverable_id = self.request.query_params.get('deliverable_id')
        if deliverable_id:
            queryset = queryset.filter(deliverable_id=deliverable_id)
        return queryset
```


## 扩展设计策略

### 1. 评价模板化
未来可以支持评价模板，实现：
- 预定义评价维度
- 标准化评分规则
- 自动计算综合评分

### 2. 评价统计
```python
# 添加统计方法到 DeliverableInstance
@property
def average_score(self):
    evaluations = self.evaluate_records.all()
    if not evaluations:
        return None
    # 计算平均综合评分
    scores = [e.content.get('overall_score', 0) for e in evaluations]
    return sum(scores) / len(scores)
```

### 3. 评价与绩效考核联动
将交付物评价结果与 `evaluation/v3` 项目角色评价模块联动：
- 自动汇总项目内所有交付物评价
- 作为角色评价的参考依据


## 演进方向 (Future Evolution)

### 短期计划
1. **完善评价内容结构**: 定义标准的评价维度和评分规则
2. **添加评价统计功能**: 提供交付物质量统计报表
3. **集成权限验证**: 完善评价权限检查逻辑

### 中期计划
1. **评价模板化**: 支持按交付物类型配置不同的评价模板
2. **评价流程化**: 支持评价审批流程（如需要多人评价）
3. **评价结果可视化**: 提供评价结果图表展示

### 长期规划
1. **智能评价建议**: 基于历史数据提供评价建议
2. **评价与AI集成**: 使用AI辅助分析交付物质量
3. **跨项目评价对比**: 支持不同项目间的交付物质量对比


## 模块特有名词索引

当提到以下名词时，应关联到此模块：

| 名词 | 说明 |
|------|------|
| **交付物评价** | 本模块核心功能 |
| **DeliverableEvaluate** | 评价记录模型 |
| **交付物评分** | 评价的具体操作 |
| **evaluate_records** | 交付物实例的反向关联字段 |
| **evaluated_deliverables** | 评价人的反向关联字段 |
| **2007权限码** | 交付物评分权限代码 |


## 开发注意事项

1. **JSON字段验证**: 创建评价时需验证 `content` 字段格式
2. **权限检查**: 评价前必须检查用户是否具有 2007 权限码
3. **级联删除**: 交付物删除时，评价记录会自动删除（CASCADE）
4. **评价人保留**: 评价人删除时，评价记录保留但 `evaluated_by` 设为 NULL（SET_NULL）
5. **时间戳**: `evaluated_at` 使用 `auto_now_add`，创建后不可修改


## 相关文件路径

- **模型定义**: `apps/PM/deliverable/evaluate/models.py`
- **关联模块**: `apps/PM/deliverable/instance/models.py`
- **权限定义**: `apps/PM/authority/enums.py`
- **评价体系v2**: `apps/PM/evaluation/v2/models.py`
- **评价体系v3**: `apps/PM/evaluation/v3/record/models.py`
