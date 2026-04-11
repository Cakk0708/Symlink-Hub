# PM 节点评审项模块 (PM-NodeList-Review)

## 模块定位

节点评审项模块 (`apps/PM/review/`) 是 PM 项目管理系统中负责**项目节点评审过程记录**的核心模块。它承接 PSC 模块定义的评审项规则，在项目执行过程中记录每个节点上评审项的处理结果（通过/拒绝），为项目质量控制提供数据支撑。

**模块性质**：业务记录层 + 接口适配层
**依赖方向**：PM → PSC（评审项定义来自 PSC，评审记录产生在 PM）


## 模块职责边界

### 核心职责（应做）

1. **评审项列表输出**
   - 从节点定义关联链路获取评审项列表
   - 链路：`node_definition → node_definition_version → review_mappings → review_definition_version`
   - 区分评审项类型：`fixed`（关联交付物定义） vs `custom`（自定义评审项）
   - 🆕 **Since 2025-03-05**：为每个评审项添加评审状态（`state`）和备注（`remark`）字段

2. **评审记录创建**
   - 接收评审操作（通过/拒绝）
   - 记录处理人、处理时间、备注信息
   - 防止重复评审（同一节点同一评审项版本只能有一条记录）

3. **评审记录查询**
   - 按节点+评审项维度查询评审历史
   - 支持评审记录详情输出

### 职责边界（不应做）

| 不属于本模块 | 正确归属 |
|------------|---------|
| 评审项定义管理 | PSC/review_definition |
| 评审项与节点关联规则配置 | PSC/node/review（NodeDefinitionReviewMapping） |
| 评审结果触发节点状态流转 | PM/nodelist/signals.py（信号处理） |
| 评审项权限验证（谁能评审） | PM/authority（权限验证模块） |


## 核心数据模型

### NodeReview（节点评审项模型）

**表名**：`PM_node_review`

**核心字段**：

| 字段 | 类型 | 说明 |
|-----|------|-----|
| `node` | ForeignKey | 关联项目节点（`PM.Project_Node`） |
| `review_definition_version` | ForeignKey | 关联评审项版本（`PSC.ReviewDefinitionVersion`） |
| `process_status` | CharField | 处理状态：`APPROVED`（通过）/ `REJECTED`（拒绝） |
| `processed_by` | ForeignKey | 处理人（`SM.User`） |
| `remark` | TextField | 备注（拒绝原因等） |
| `created_at` | DateTimeField | 创建时间（评审时间） |

**索引设计**：
- 复合索引：`['node', 'review_definition_version']`（防止重复评审）
- 单列索引：`['process_status']`、`['created_at']`（支持按状态和时间查询）

**关键属性**：
- `is_approved`：是否通过
- `is_rejected`：是否拒绝

### ReviewProcessStatus（枚举）

🆕 **Since 2025-03-05**：新增 `PENDING` 状态用于表示待评审状态

```python
class ReviewProcessStatus(models.TextChoices):
    PENDING = 'PENDING', '待评审'      # 🆕 新增
    APPROVED = 'APPROVED', '通过'
    REJECTED = 'REJECTED', '拒绝'
```

**状态说明**：
- `PENDING`：评审项尚未评审（序列化器中用于标识无评审记录状态）
- `APPROVED`：评审通过
- `REJECTED`：评审拒绝


## 序列化器架构

### 1. NodeReviewSerializer（评审项列表序列化器）

**用途**：将节点实例转换为评审项列表，包含评审状态信息

**关联链路**：
```
Project_Node
  └─→ node_definition (PSC.ProjectTemplateNodeMapping)
       └─→ node_definition_version (PSC.NodeDefinitionVersion)
            └─→ review_mappings (PSC.NodeDefinitionReviewMapping)
                 └─→ review_definition_version (PSC.ReviewDefinitionVersion)
                      └─→ review_definition (PSC.ReviewDefinition)
```

**🆕 Since 2025-03-05 输出结构**：
```python
{
    "list": [
        {
            "id": review_definition_version.id,
            "name": review_definition.name,
            "required": True,           # 固定为 True
            "type": "fixed" | "custom", # 有关联交付物定义版本为 fixed，否则为 custom
            "state": "PENDING" | "APPROVED" | "REJECTED",  # 🆕 评审状态
            "remark": str | None        # 🆕 评审备注
        }
    ]
}
```

**状态查询逻辑**（`serializers.py:36-66`）：
```python
# 1. 预取节点的所有评审记录，按创建时间倒序
node_reviews_queryset = instance.node_reviews.all().order_by('-created_at')

# 2. 构建 review_definition_version -> 最新评审记录 的映射字典
latest_reviews_map = {}
for review in node_reviews_queryset:
    rdv_id = review.review_definition_version_id
    if rdv_id not in latest_reviews_map:
        latest_reviews_map[rdv_id] = review

# 3. 遍历评审项列表，获取最新评审记录
latest_review = latest_reviews_map.get(review_def_version.id)

# 4. 确定评审状态
if latest_review:
    state = latest_review.process_status  # APPROVED 或 REJECTED
    remark = latest_review.remark
else:
    state = 'PENDING'                     # 无评审记录时返回待评审
    remark = None
```

**类型判断逻辑**（`serializers.py:69-70`）：
```python
review_type = "fixed" if review_def_version.deliverable_definition_version else "custom"
```

### 2. NodeReviewWriteSerializer（评审记录写入序列化器）

**用途**：创建评审记录

**验证规则**：
- 防止重复评审：同一节点同一评审项版本只能有一条记录（`serializers.py:98-106`）
- 自动注入处理人：从请求上下文获取当前用户 ID

### 3. NodeReviewReadSerializer（评审记录读取序列化器）

**用途**：评审记录详情输出

**关联字段**：
- `node_id`、`node_name`：节点信息
- `review_definition_version_id`、`review_name`：评审项信息
- `process_status_display`：状态显示名称
- `processed_by`：处理人信息（嵌套对象：id/name/avatar）


## 权限验证流程

### 当前实现（views.py:26）

```python
permission_classes = [IsAuthenticated]
```

**现状**：仅验证用户登录状态

### 权限验证缺口

本模块**未实现**以下权限验证（需调用 PM/authority 模块）：

1. **评审权限**：谁能评审该节点？
   - 节点负责人？
   - 项目管理员？
   - 被指定的评审人？

2. **状态约束**：节点在什么状态下允许评审？
   - 仅当节点状态为"进行中"时可评审？
   - 已完成/暂停节点是否允许评审？

3. **业务规则**：
   - 是否必须所有评审项都通过才能完成节点？
   - 评审被拒绝是否自动回退节点状态？


## 认证与授权区别说明

### 认证（Authentication）

**本模块实现**：通过 `IsAuthenticated` 权限类
- 验证请求是否来自已登录用户
- 从请求中提取用户信息（`UserHelper.setup_request_userinfo(request)`）
- 自动注入 `processed_by_id`

### 授权（Authorization）

**本模块未实现**：需要对接 PM/authority 模块

**建议授权逻辑**：
```python
# 建议的权限验证伪代码
def has_review_permission(user, node):
    # 1. 节点负责人可以评审
    if user in node.node_owners:
        return True

    # 2. 项目管理员可以评审
    if has_project_admin_permission(user, node.list):
        return True

    # 3. 被指定的评审人可以评审
    if is_designated_reviewer(user, node):
        return True

    return False
```


## 与其他模块关系

### 依赖关系图

```
PM/nodelist/review (本模块)
    ├─→ PM/nodelist (父模块)
    │   ├─→ Project_Node：节点实体
    │   └─→ signals：节点状态变更信号
    ├─→ PSC/review_definition (评审项定义)
    │   ├─→ ReviewDefinition：评审项主模型
    │   └─→ ReviewDefinitionVersion：评审项版本
    ├─→ PSC/node/review (评审项关联)
    │   └─→ NodeDefinitionReviewMapping：节点-评审项映射
    └─→ SM/user (用户模块)
        └─→ User：处理人信息
```

### 数据流向

1. **配置阶段**（PSC 模块）
   - 在节点定义版本中关联评审项
   - 创建评审项版本并关联交付物定义（可选）

2. **执行阶段**（PM 模块）
   - 创建项目节点时自动继承节点定义的评审项配置
   - 用户调用评审接口创建评审记录
   - 触发信号处理节点状态流转

3. **查询阶段**
   - 获取节点评审项列表（从节点定义关联链路获取）
   - 🆕 查询每个评审项的最新评审记录（从 NodeReview 表查询）
   - 查询评审记录历史（从 NodeReview 表查询）


## 常见业务场景

### 场景0：🆕 评审拒绝处理流程（Since 2026-03-18）

**触发条件**：当评审项创建且状态为 `REJECTED`（拒绝）时

**业务流程**：

```
评审项创建（process_status = REJECTED）
    ↓
信号处理器触发（handle_node_review_created）
    ↓
检查是否有关联交付物定义版本
    ↓
在项目所有节点中查找包含该交付物定义的交付物实例
    ├─ 查询条件：project_node__list=project, definition=deliverable_definition_version
    └─ 注意：一个交付物定义可能对应多个交付物实例，分布在不同的节点上
    ↓
对所有找到的交付物实例执行：
    ├─ 更新交付物状态为 REVIEW_REJECTED
    └─ 记录该交付物所在的节点
    ↓
回滚所有相关节点到 IN_PROGRESS 状态
    ├─ 更新节点状态为 IN_PROGRESS
    └─ 重置节点评审规则历史（review_rule.history）
    ↓
异步发送通知消息给节点负责人
    └─ 使用 SerializerMessage 创建飞书消息
```

**关键代码位置**：

1. **信号处理器**：`apps/PM/review/signals.py:22`
   ```python
   @receiver(post_save, sender=NodeReview)
   def handle_node_review_created(sender, instance, created, **kwargs):
       if not created:
           return
       if instance.process_status != Choices.ReviewProcessStatus.REJECTED:
           return
       NodeReviewService.handle_review_rejection(instance)
   ```

2. **服务层**：`apps/PM/review/services.py:19`
   ```python
   class NodeReviewService:
       @staticmethod
       def handle_review_rejection(node_review):
           # 获取评审项关联的交付物定义版本
           # 在项目所有节点中查找包含该交付物定义的交付物实例
           # 更新交付物状态为 REVIEW_REJECTED
           # 回滚相关节点
           # 发送通知消息
   ```

3. **异步通知任务**：`apps/PM/review/tasks.py:20`
   ```python
   @shared_task
   def async_send_review_rejection_notice(node_review_id, node_id):
       # 获取节点负责人列表
       # 使用 SerializerMessage 创建飞书消息
       # 消息内容：项目名称、节点名称、评审项名称、拒绝原因
   ```

**交付物状态变更**：`apps/PM/deliverable/instance/enums.py:16`
- 新增状态：`REVIEW_REJECTED = 'REVIEW_REJECTED', '评审拒绝'`

**节点状态变更**：无需新增状态，评审拒绝时将节点回滚到 `IN_PROGRESS`（进行中）状态

**通知消息模板**：使用 `settings.API_FEISHU['message']['template']['general_notice']['id']`
- 标题颜色：`red`
- 标题主题：`评审拒绝通知`
- 消息内容包含：项目名称、节点名称、评审项名称、拒绝原因
- 跳转链接：项目详情页

### 场景1：获取节点评审项列表（🆕 含状态）

**接口**：`GET pm/node/{node_id}/review`（未实现，建议新增）

**返回示例**：
```json
{
    "msg": "success",
    "data": {
        "list": [
            {
                "id": 1,
                "name": "技术方案评审",
                "required": true,
                "type": "fixed",
                "state": "APPROVED",    // 🆕 已评审通过
                "remark": "方案符合要求" // 🆕 评审备注
            },
            {
                "id": 2,
                "name": "风险评估",
                "required": true,
                "type": "custom",
                "state": "PENDING",     // 🆕 待评审
                "remark": null          // 🆕 无备注
            }
        ]
    }
}
```

### 场景2：提交评审（通过）

**接口**：`POST pm/node/{node_id}/review/{review_id}`

**请求体**：
```json
{
    "process_status": "APPROVED",
    "remark": "方案符合要求，通过评审"
}
```

### 场景3：提交评审（拒绝）

**请求体**：
```json
{
    "process_status": "REJECTED",
    "remark": "需补充性能测试报告"
}
```

### 场景4：查询评审历史

**接口**：`GET pm/node/{node_id}/review/{review_id}`

**返回示例**：
```json
{
    "msg": "success",
    "data": [
        {
            "id": 1,
            "node_id": 100,
            "node_name": "需求评审",
            "review_definition_version_id": 5,
            "review_name": "技术方案评审",
            "process_status": "APPROVED",
            "process_status_display": "通过",
            "processed_by": {
                "id": 10,
                "name": "张三",
                "avatar": "https://..."
            },
            "remark": "通过",
            "created_at": "2025-03-05T10:30:00Z"
        }
    ]
}
```


## 技术实现建议（Django）

### 1. 评审项列表接口（建议新增）

**views.py 新增视图**：
```python
class NodeReviewListView(views.APIView):
    """节点评审项列表视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request, node_id):
        """获取节点的评审项列表（含状态）"""
        node = get_object_or_404(Project_Node, id=node_id)
        serializer = NodeReviewSerializer(node)
        return JsonResponse({'msg': 'success', 'data': serializer.data})
```

### 2. 权限验证装饰器（建议）

```python
# utils/permission.py
def check_review_permission(user, node):
    """检查评审权限"""
    # 1. 节点负责人
    if node.node_owners.filter(user=user).exists():
        return True
    # 2. 项目管理员
    if check_project_admin(user, node.list_id):
        return True
    return False
```

### 3. 信号处理（建议集成到 PM/nodelist/signals.py）

```python
# 当评审被拒绝时，自动回退节点状态
@receiver(post_save, sender=NodeReview)
def handle_review_rejected(sender, instance, created, **kwargs):
    if instance.is_rejected:
        # 回退节点状态到进行中
        if instance.node.state == 2:  # 已完成
            instance.node.state = 1  # 进行中
            instance.node.save(update_fields=['state'])
```

### 4. 批量查询优化

```python
# 使用 select_related 优化查询
queryset = NodeReview.objects.select_related(
    'node',
    'review_definition_version__review_definition',
    'processed_by'
).filter(node_id=node_id)
```


## 扩展设计策略

### 短期扩展（当前可做）

1. **评审附件支持**
   - 添加 `attachment` 字段（JSON/ForeignKey）
   - 支持上传评审报告

2. **评审提醒**
   - 集成飞书消息通知
   - 待评审项提醒

3. **评审统计**
   - 节点评审通过率
   - 评审人工作统计

### 中期扩展（需要架构调整）

1. **多轮评审**
   - 支持同一评审项多次评审
   - 记录评审历史链

2. **评审会签**
   - 支持多人评审
   - 所有人通过才算通过

3. **评审模板**
   - 不同节点类型使用不同评审模板
   - 评审项动态加载

### 长期演进（需要跨模块协作）

1. **评审工作流引擎**
   - 定义评审流程
   - 条件分支（不同结果触发不同流程）

2. **AI 辅助评审**
   - 自动检查交付物完整性
   - AI 评分建议


## 演进方向（Future Evolution）

### 当前架构约束

1. **评审项类型判断逻辑硬编码**
   - `serializers.py:69-70` 的 fixed/custom 判断逻辑
   - 建议抽取为 `ReviewDefinitionVersion` 的方法或属性

2. **评审规则配置不灵活**
   - `Project_Node.review_rule` 字段未使用
   - 建议实现评审规则引擎

3. **缺少评审与交付物关联**
   - 虽然评审项可关联交付物定义
   - 但评审记录未记录实际交付物实例

### 建议演进路径

**阶段1：完善评审记录（当前）**
- ✅ 基础评审记录（通过/拒绝）
- ✅ 🆕 评审状态查询（PENDING/APPROVED/REJECTED）
- ✅ 🆕 评审备注展示（remark 字段）
- ⏳ 评审附件支持
- ⏳ 评审与交付物实例关联

**阶段2：灵活配置（中期）**
- ⏳ 评审规则引擎（基于 `review_rule` 字段）
- ⏳ 评审项动态加载（基于节点类型）
- ⏳ 权限配置化（谁可以评审）

**阶段3：工作流集成（长期）**
- ⏳ 评审工作流引擎
- ⏳ 与审批流集成（SM/approval）
- ⏳ 自动触发节点状态流转


## 模块特有名词索引

当用户提到以下名词时，应快速定位到本技能：

| 名词 | 定位 |
|-----|------|
| 节点评审、NodeReview | 本模块核心模型 |
| 评审项列表 | NodeReviewSerializer 序列化输出 |
| fixed/custom 评审项 | 类型判断逻辑（`serializers.py:69`） |
| 评审记录、评审历史 | NodeReview 模型实例 |
| review_mapping | PSC 模块的节点-评审项映射 |
| 评审项版本 | ReviewDefinitionVersion（PSC 模块） |
| process_status | 评审处理状态（PENDING/APPROVED/REJECTED）🆕 |
| state | 评审项列表中的状态字段（🆕 Since 2025-03-05） |
| remark | 评审备注字段（🆕 Since 2025-03-05） |


## 文件索引

**核心文件**：
- `apps/PM/review/models.py`：NodeReview 模型定义
- `apps/PM/review/enums.py`：ReviewProcessStatus 枚举（🆕 含 PENDING）
- `apps/PM/review/serializers.py`：序列化器（🆕 含状态查询逻辑）
- `apps/PM/review/views.py`：NodeReviewDetailView 视图
- `apps/PM/review/urls.py`：路由配置

**🆕 信号与服务（Since 2026-03-18）**：
- `apps/PM/review/signals.py`：信号处理器（监听评审项创建，触发拒绝处理）
- `apps/PM/review/services.py`：服务层（评审拒绝处理逻辑）
- `apps/PM/review/tasks.py`：Celery 异步任务（评审拒绝通知）
- `apps/PM/review/__init__.py`：信号注册入口

**依赖文件**：
- `apps/PSC/review_definition/models.py`：评审项定义模型
- `apps/PM/nodelist/models.py`：Project_Node 节点模型
- `apps/SM/models.py`：User 用户模型


## 快速导航

**当你需要**：
1. 理解评审项类型判断逻辑 → `serializers.py:69-70`
2. 查看评审记录模型 → `models.py:12-104`
3. 理解评审项列表输出结构 → `serializers.py:26-83`（🆕 含状态逻辑）
4. 查看评审接口实现 → `views.py:20-129`
5. 了解评审状态枚举 → `enums.py:10-18`（🆕 含 PENDING）
6. 了解评审项定义来源 → `apps/PSC/review_definition/models.py`