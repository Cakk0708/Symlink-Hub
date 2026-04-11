# PM 项目列表模块 (PM Project List)

## 模块定位

本模块是 PMS 项目管理系统的核心模块，负责项目的**全生命周期管理**，包括项目创建、状态流转、查询过滤、详情展示等功能。

**关键特性**：
- 项目基于**模板版本锁定**创建，模板升级不影响已创建的项目
- 支持多维度查询过滤（状态、参与者、负责人、客户等）
- 完整的权限验证体系（基于 authority 模块）
- 集成审批流、节点管理、变更管理等子模块

**目录位置**：`apps/PM/project/`

## 核心数据模型

### Project_List 模型

**文件**：`apps/PM/project/models.py`

```python
class Project_List(models.Model):
    # 基础信息
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)                    # 项目名称
    content = models.CharField(max_length=255)                  # 项目描述
    state = models.IntegerField(default=5, choices=Choices.state)  # 项目状态

    # 业务分类（含积分计算）
    business = models.CharField(choices=Choices.business.choices, default='B1')
    difficulty = models.CharField(choices=Choices.difficulty.choices, default='EASY')
    workload = models.CharField(choices=Choices.workload.choices, default='W1')

    # 关联关系
    customer = models.ForeignKey('BDM.Customer', on_delete=models.CASCADE)
    model = models.ForeignKey('BDM.CustomerModel', on_delete=models.CASCADE)
    template = models.ForeignKey('PSC.ProjectTemplateVersion', null=True, on_delete=models.SET_NULL)
    creator = models.ForeignKey('SM.User', on_delete=models.SET_NULL, null=True, related_name='created_project_lists')
    owner = models.ForeignKey('SM.User', on_delete=models.SET_NULL, null=True, related_name='owned_project_lists')

    # 参与者
    followers = models.JSONField()                             # 关注者ID列表

    # 时间管理
    create_time = models.DateTimeField(auto_now_add=True)
    deadline_time = models.DateTimeField(null=True, blank=True)  # 截止时间（交付日期）
    complete_time = models.DateTimeField(null=True, blank=True)  # 完成时间

    # 订单管理
    place_order_date = models.DateTimeField(null=True, blank=True)
    place_order_flag = models.BooleanField(default=False)

    # 审批流关联
    approvals = GenericRelation('SM.Approval')
```

### 项目状态枚举

**文件**：`apps/PM/project/enums.py`

| 状态码 | 名称 | 说明 |
|--------|------|------|
| 0 | 删除 | 已删除 |
| 1 | 进行中 | 项目正在执行 |
| 2 | 已完成 | 项目已完成 |
| 3 | 变更中 | 项目变更审批中 |
| 4 | 已暂停 | 项目已暂停 |
| 5 | 申请中 | 项目立项申请中 |
| 6 | 取消立项 | 项目已取消 |

### 业务分类枚举

**难度等级**（积分系数）：
- `LOW` (0.5分) - 简单
- `EASY` (1.0分) - 一般
- `MEDIUM` (2.0分) - 中等
- `HARD` (3.0分) - 挑战

**工作量**（积分系数）：
- `W1` (1.0分) - ≤2天
- `W2` (2.0分) - >3天
- `W3` (3.0分) - >7天
- `W4` (4.0分) - >30天
- `W5` (5.0分) - >3个月

**业务类型**（积分系数）：
- `B1` (1.0分) - 经营业务类
- `B2` (2.0分) - 拓展业务类
- `B3` (3.0分) - 战略业务类

**积分计算公式**：`项目积分 = 难度系数 × 工作量系数 × 业务类型系数`

## API 接口清单

### 项目列表

**端点**：`GET /pm/projects/`

**查询参数**：
| 参数 | 类型 | 说明 |
|------|------|------|
| `type` | string | 项目类型：ALL/PRO/CHG/COM/SUS/INPROG/CANCEL/CHGS/RPB/FLW/IND |
| `participant` | string | 参与项目类型（逗号分隔） |
| `owner` | string | 负责人ID（逗号分隔） |
| `customer` | string | 客户ID（逗号分隔） |
| `order` | string | 下单状态：TRUE/FALSE |
| `time_type` | string | 时间类型：create_time/deadline_time |
| `start_time` | datetime | 开始时间 |
| `end_time` | datetime | 结束时间 |
| `limit` | int | 每页数量（默认10） |
| `skip` | int | 跳过数量（默认0） |
| `sort` | string | 排序：CT:DESC/GT:DESC/AT:DESC/CET:DESC/OWN:DESC |

**响应**：
```json
{
    "msg": "success",
    "data": [...],
    "total": 100
}
```

### 创建项目

**端点**：`POST /pm/projects/`

**请求体**：
```json
{
    "name": "项目名称",
    "model_name": "机型名称",
    "deadline_time": "2026-12-31",
    "customer_id": 1,
    "template_id": 1,
    "difficulty": "EASY",
    "workload": "W1",
    "business": "B1",
    "owner_id": 1
}
```

**响应**：
```json
{
    "msg": "success",
    "data": {"projectId": 123}
}
```

### 项目详情

**端点**：`GET /pm/projects/<int:pk>/`

**响应**：
```json
{
    "msg": "success",
    "data": {
        "id": 123,
        "name": "项目名称",
        "state": 1,
        "create_time": "2026-03-03 10:00:00",
        "deadline_time": "2026-12-31 00:00:00",
        "complete_time": false,
        "owner": {...},
        "creator": {...},
        "customer": {...},
        "nodes": {
            "list": [...]
        },
        "isProjectMember": true,
        "evaluationAvailable": true,
        "authority": [...]
    }
}
```

**🆕 Since 最新更新**：
- `authority` 字段已迁移到 `data` 内部，由 `DetailSerializer` 统一处理
- 视图层仅负责数据获取和响应返回
- 序列化器层负责数据构造、权限验证、数据转换

### 项目分类统计

**端点**：`GET /pm/projects/category`

**响应**：
```json
{
    "msg": "success",
    "data": [
        {"type": "ALL", "name": "全部", "total": 100, "overdue": 5},
        {"type": "PRO", "name": "进行中", "total": 50, "overdue": 3},
        ...
    ]
}
```

### 更新项目

**端点**：`PATCH /pm/projects/<int:pk>/`

**请求体**：
```json
{
    "name": "新项目名称",
    "deadlineTime": "2026-12-31",
    "ownerId": 123,
    "placeOrderFlag": true,
    "modelName": "新机型名称"
}
```

**⚠️ 注意**：
- 本接口不再支持更新项目状态（state 字段）
- 状态更新请使用专用接口：`PATCH /pm/projects/<int:pk>/status`

**🆕 Since 最新更新**：
- `modelName` 字段支持修改项目关联的机型名称
- 会自动验证新名称在同一客户下不重复
- 更新成功后记录项目操作日志

### 🆕 更新项目状态

**端点**：`PATCH /pm/projects/<int:pk>/status`

**请求体**：
```json
{
    "state": "6",
    "reason": "项目需求变更，不再需要实施"
}
```

**请求参数说明**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| state | string | ✅ | 目标状态，见下方状态值说明 |
| reason | string | 否 | 状态变更原因（用于取消、暂停等操作） |

**状态值说明**：

| 值 | 状态名称 | 说明 | 所需权限 |
|----|---------|------|----------|
| `1` | 进行中 | 恢复项目进行中（仅限已暂停的项目） | 1103 |
| `2` | 已完成 | 完成项目（需所有里程碑已完成） | 1100 |
| `4` | 已暂停 | 暂停项目（仅限进行中的项目） | 1101 |
| `6` | 取消立项 | 取消项目（仅限进行中或申请中的项目） | 1102 |

**状态转换规则**：

| 当前状态 | 可转换至 | 说明 |
|---------|---------|------|
| 进行中 (1) | 已暂停 (4)、已完成 (2)、取消立项 (6) | |
| 已暂停 (4) | 进行中 (1) | |
| 申请中 (5) | 取消立项 (6) | |

**响应**：
```json
{
    "msg": "success",
    "data": {
        "projectId": 123,
        "state": 6
    }
}
```

**🆕 Since 2026-03-17**：
- 新增专用状态更新接口，参考 nodelist 模块验证器模式
- 状态验证逻辑抽取到 `validators.py` 模块
- 新增权限码 1102（可取消项目）和 1103（可恢复项目）

### 删除项目

**端点**：`DELETE /pm/projects/<int:pk>/`

**注意**：需要权限验证，同时删除关联的机型和飞书文件夹

## 序列化器架构

### 序列化器职责划分

**文件**：`apps/PM/project/serializers.py`

遵循**职责分离原则**，将序列化器按功能划分：

| 序列化器 | 职责 |
|---------|------|
| `ListSerializer` | 项目列表数据序列化 |
| `DetailSerializer` | 🆕 项目详情数据序列化（含权限验证） |
| `CreateSerializer` | 项目创建数据验证 |
| `PatchSerializer` | 项目更新数据验证（不含状态） |
| `PatchStatusSerializer` | 🆕 项目状态更新专用序列化器 |

### DetailSerializer 设计（🆕 最新重构）

**职责**：项目详情数据交互层逻辑

**字段划分**：
```python
class DetailSerializer(serializers.ModelSerializer):
    # 时间字段（格式化）
    create_time = serializers.SerializerMethodField()
    deadline_time = serializers.SerializerMethodField()
    complete_time = serializers.SerializerMethodField()
    last_change_time = serializers.SerializerMethodField()

    # 关联对象
    creator = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()

    # 节点信息
    nodes = serializers.SerializerMethodField()

    # 计算字段
    is_overdue = serializers.SerializerMethodField()

    # 评价相关
    evaluationAvailable = serializers.SerializerMethodField()
    evaluationVisible = serializers.SerializerMethodField()
    evaluationStatus = serializers.SerializerMethodField()

    # 权限信息
    authority = serializers.SerializerMethodField()
```

**关键方法**：
```python
def get_authority(self, obj):
    """获取用户权限信息"""
    pn = authority_project.permission(obj.id, self.userinfo, 'project_detail')
    return pn.list()
```

### 视图层重构（🆕 最新重构）

**重构前**（视图层处理权限验证）：
```python
def get(self, request, *args, **kwargs):
    instance = Project_List.objects.select_related(...).get(pk=kwargs.get('pk'))

    # ⚠️ 视图层处理权限验证
    pn = authority_project.permission(kwargs.get('pk'), userinfo, 'project_detail')

    serializer = DetailSerializer(instance, context={'request': request})

    return JsonResponse({
        'msg': 'success',
        'data': serializer.data,
        'authority': pn.list()  # ⚠️ authority 单独返回
    })
```

**重构后**（视图层只负责基础服务层业务）：
```python
def get(self, request, *args, **kwargs):
    instance = Project_List.objects.select_related(...).get(pk=kwargs.get('pk'))

    # 使用序列化器处理数据交互层逻辑（包括权限验证）
    userinfo = UserHelper.setup_request_userinfo(request)
    serializer = DetailSerializer(instance, context={'request': request, 'userinfo': userinfo})

    return JsonResponse({
        'msg': 'success',
        'data': serializer.data  # ✅ authority 已包含在 data 内
    })
```

### 架构优势

| 层级 | 职责 | 示例 |
|------|------|------|
| **视图层** | 数据获取、响应返回 | `Project_List.objects.select_related(...).get()` |
| **序列化器层** | 数据构造、权限验证、数据转换 | `get_authority()`、`get_nodes()`、`get_is_overdue()` |

## 权限验证流程

### 权限代码体系

**文件**：`apps/PM/authority/authority.py`

| 权限代码 | 说明 |
|----------|------|
| 1001 | 项目名称编辑 |
| 1002 | 项目内容编辑 |
| 1003 | 项目删除 |
| 1100 | 项目完成 |
| 1101 | 项目暂停 |
| 1102 | 项目取消（🆕 新增） |
| 1103 | 项目恢复（🆕 新增） |

### 身份类型

| 类型 | 说明 |
|------|------|
| SUPERUSER | 超级用户 |
| MANAGER | 管理者 |
| CREATOR | 项目创建者 |
| OWNER | 项目负责人 |
| FOLLOWER | 项目关注者 |
| OWNER_NODE | 节点负责人 |
| ASSISTOR | 节点协助者 |

### 权限验证示例

```python
from apps.PM.authority import authority as authority_project

# 创建权限验证器
auth = authority_project.permission(project_id, userinfo, 'project_detail')

# 验证具体权限
if auth.verify(1001):  # 检查项目名称编辑权限
    # 执行操作
```

## 与其他模块关系

### 与 PSC 模块

| 关联 | 说明 |
|------|------|
| `PSC.ProjectTemplateVersion` | 项目模板版本（项目锁定到创建时的版本） |
| `PSC.ProjectTemplateNodeMapping` | 🆕 节点模板映射（项目节点通过 ForeignKey 关联） |
| `PSC.NodeDefinition` | 节点定义 |
| `PSC.NodeDefinitionVersion` | 节点定义版本 |

### 与 PM 子模块

| 模块 | 关系 |
|------|------|
| `PM.nodelist` | 项目节点管理 |
| `PM.change` | 项目变更流程 |
| `PM.pause` | 项目暂停流程 |
| `PM.deliverable` | 交付物管理 |
| `PM.performance` | 绩效管理 |
| `PM.authority` | 权限验证 |

### 与 BDM 模块

| 关联 | 说明 |
|------|------|
| `BDM.Customer` | 项目客户 |
| `BDM.CustomerModel` | 项目机型 |

### 与 SM 模块

| 关联 | 说明 |
|------|------|
| `SM.User` | 用户信息（创建者、负责人） |
| `SM.Approval` | 审批流 |

## 常见业务场景

### 1. 项目创建流程

```
1. 前端传递 template_id（ProjectTemplate ID）
2. 后端获取当前模板版本（is_current=True）
3. 创建项目时锁定到该版本
4. 根据模板版本创建项目节点
5. 设置默认负责人
6. 创建操作日志
```

### 2. 项目状态流转

```
申请中(5) → 进行中(1) → 变更中(3) → 进行中(1) → 已完成(2)
                ↓              ↓
              已暂停(4) → 进行中(1)    取消立项(6)
```

### 3. 项目查询过滤

- **按类型**：type 参数（ALL/PRO/CHG/COM 等）
- **按参与者**：participant 参数（项目类型）
- **按负责人**：owner 参数
- **按客户**：customer 参数
- **按时间范围**：time_type + start_time + end_time
- **按下单状态**：order 参数

### 4. 项目删除流程

1. 验证删除权限
2. 删除关联的 CustomerModel
3. 删除飞书文件夹结构
4. 删除项目记录

## 技术实现建议

### 1. 模板版本锁定

```python
# 创建项目时锁定模板版本
template_instance = validated_data.pop('template_id')
template_version_instance = template_instance.versions.filter(is_current=True).first()

project_instance = Project_List.objects.create(
    ...
    template=template_version_instance,  # 锁定版本
    ...
)
```

### 2. 节点树形结构

```python
from apps.PM.project.utils import get_project_node_tree

# 获取项目节点树
nodes_tree = get_project_node_tree(project_id)
```

### 3. 分页查询

```python
# 使用 skip + limit 实现分页
start = skip
end = skip + limit
paginated_queryset = queryset[start:end]
```

### 4. 排序处理

```python
# 解析 sort 参数：CT:DESC → -create_time
def construct_order_by(sort_str):
    temp = sort_str.split(':')
    if temp[0] == 'CT':
        return f"{'-' if temp[1] == 'DESC' else ''}create_time"
```

## 关键名词索引

| 名词 | 定位 |
|------|------|
| Project_List | 项目列表主模型 |
| state | 项目状态（1-6） |
| template | 项目模板版本（已锁定） |
| authority | 权限验证模块 |
| validators | 🆕 项目状态验证器模块 |
| CategoryListView | 分类统计视图 |
| get_project_node_tree | 节点树形结构函数 |
| difficulty | 难度等级 |
| workload | 工作量 |
| business | 业务类型 |
| ListSerializer | 🆕 项目列表序列化器 |
| DetailSerializer | 🆕 项目详情序列化器（含权限验证） |
| PatchSerializer | 项目更新序列化器（不含状态） |
| PatchStatusSerializer | 🆕 项目状态更新专用序列化器 |
| PatchStatusView | 🆕 项目状态更新专用视图 |
| SerializerMethodField | 🆕 序列化器方法字段（用于复杂数据构造） |
| ProjectStatusPauseValidator | 🆕 项目暂停验证器 |
| ProjectStatusCompleteValidator | 🆕 项目完成验证器 |
| ProjectStatusCancelValidator | 🆕 项目取消验证器 |
| ProjectStatusInProgressValidator | 🆕 项目恢复验证器 |

## 扩展设计策略

### 1. 状态机扩展

如需添加新状态：
1. 在 `apps/PM/project/enums.py` 的 `Choices.state` 中添加
2. 更新状态流转逻辑
3. 更新权限验证规则

### 2. 过滤器扩展

如需添加新的过滤条件：
1. 在 `serializer_get_list` 中添加字段
2. 在 `get_params` 方法中添加查询逻辑
3. 更新 API 文档

### 3. 积分规则扩展

如需修改积分计算：
1. 在 `Choices` 中调整 `difficulty`、`workload`、`business` 的积分
2. 更新 `serializer_project.update` 中的积分计算逻辑

### 4. 序列化器扩展（🆕）

如需为 `DetailSerializer` 添加新字段：

1. 添加字段声明：
```python
class DetailSerializer(serializers.ModelSerializer):
    new_field = serializers.SerializerMethodField()
```

2. 实现 `get_` 方法：
```python
def get_new_field(self, obj):
    # 数据构造逻辑
    return computed_value
```

3. 在 `Meta.fields` 中注册：
```python
class Meta:
    model = Project_List
    fields = [..., 'new_field']
```

## 演进方向 (Future Evolution)

### 近期规划

1. **项目模板动态化**
   - 支持项目创建后更换模板
   - 支持部分节点复用其他模板

2. **查询性能优化**
   - 添加数据库索引
   - 使用 Redis 缓存热点数据

3. **权限细粒度化**
   - 支持字段级权限控制
   - 支持动态权限规则

### 长期规划

1. **项目版本管理**
   - 支持项目快照
   - 支持项目回滚

2. **智能推荐**
   - 根据历史数据推荐模板
   - 根据用户角色推荐项目

3. **多租户支持**
   - 支持项目分组
   - 支持跨组织协作

## 演进历史 (Evolution History)

### 2026-03-17 - 项目状态管理重构

**变更内容**：
1. 新增 `validators.py` 模块，参考 nodelist 模块验证器模式
2. 新增 `PatchStatusSerializer` 专用状态更新序列化器
3. 新增 `PatchStatusView` 专用状态更新视图
4. 从 `PatchSerializer` 中移除 state 字段及相关逻辑
5. 支持项目取消立项（CANCELLED）状态

**新增验证器**：
- `BaseProjectStatusValidator` - 状态验证器基类
- `ProjectStatusPauseValidator` - 暂停验证（权限 1101）
- `ProjectStatusCompleteValidator` - 完成验证（权限 1100）
- `ProjectStatusCancelValidator` - 取消验证（权限 1102，新增）
- `ProjectStatusInProgressValidator` - 恢复验证（权限 1103，新增）

**新增接口**：
- `PATCH /pm/projects/<int:pk>/status` - 项目状态更新专用接口

**新增权限码**：
- 1102: 可取消项目
- 1103: 可恢复项目

**影响范围**：
- `apps/PM/project/validators.py`：新建
- `apps/PM/project/serializers.py`：新增 `PatchStatusSerializer`，修改 `PatchSerializer`
- `apps/PM/project/views.py`：新增 `PatchStatusView`
- `apps/PM/project/urls.py`：新增 `/<int:pk>/status` 路由

**设计优势**：
- 职责分离：状态管理逻辑与通用项目更新逻辑分离
- 可复用性：验证器可在其他场景复用（如权限判断、UI 状态控制）
- 可扩展性：新增状态只需添加验证器，无需修改现有代码
- 一致性：与 nodelist 模块保持一致的设计模式

### 2026-03-11 - PatchSerializer 功能扩展

**变更内容**：
1. 为 `PatchSerializer` 新增 `modelName` 字段支持修改项目机型名称
2. 新增 `validate_modelName()` 方法验证同一客户下机型名称不重复
3. 新增 `_update_model_name()` 私有方法处理机型名称更新逻辑
4. 删除冗余的 `field_mapping` 字典，DRF `source` 参数已自动处理映射

**影响范围**：
- `apps/PM/project/serializers.py`：`PatchSerializer` 更新

**功能说明**：
- 通过 `PATCH /pm/projects/{id}` 传递 `modelName` 字段可修改项目关联的机型名称
- 自动验证新名称在同一客户下不重复
- 更新成功后记录项目操作日志

### 2026-03-10 - 序列化器架构重构

**变更内容**：
1. 创建 `DetailSerializer` 用于项目详情数据序列化
2. 将视图层的数据交互逻辑迁移到序列化器层
3. `authority` 字段从响应外层迁移到 `data` 内部
4. 所有数据构造逻辑使用 `SerializerMethodField` 实现

**影响范围**：
- `apps/PM/project/serializers.py`：新增 `DetailSerializer`
- `apps/PM/project/views.py`：`DetailViews.get` 方法重构

**架构优势**：
- 视图层仅负责数据获取和响应返回
- 序列化器层负责数据构造、权限验证、数据转换
- 提高代码复用性和可维护性

### PatchStatusSerializer 设计（🆕 2026-03-17）

**职责**：项目状态更新的专用序列化器

**设计模式**：参考 nodelist 模块验证器模式

**字段定义**：
```python
class PatchStatusSerializer(serializers.Serializer):
    state = serializers.ChoiceField(
        choices=Choices.Status.choices,
        required=True,
        help_text='目标状态'
    )
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='状态变更原因（用于取消、暂停等操作）'
    )
```

**验证流程**：
1. 根据目标状态选择对应的验证器
2. 执行权限验证和业务规则验证
3. 验证通过后执行状态更新

**支持的状态转换**：
| 目标状态 | 验证器 | 权限码 | 业务规则 |
|---------|--------|--------|----------|
| 进行中 (1) | ProjectStatusInProgressValidator | 1103 | 仅限已暂停的项目 |
| 已完成 (2) | ProjectStatusCompleteValidator | 1100 | 需所有里程碑已完成 |
| 已暂停 (4) | ProjectStatusPauseValidator | 1101 | 仅限进行中的项目 |
| 取消立项 (6) | ProjectStatusCancelValidator | 1102 | 仅限进行中或申请中的项目 |
