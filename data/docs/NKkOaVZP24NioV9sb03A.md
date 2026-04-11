# PSC 节点定义模块 (PSC Node Definition)

## 模块定位

PSC (Project Setting Configuration) 节点定义模块是项目管理系统中的核心配置模块，负责管理项目节点的模板定义。该模块采用版本化设计，支持节点定义的演进历史追溯，并通过多对多关联实现评审项和交付物的灵活配置。

**模块路径**: `apps/PSC/node/definition/`

## 触发条件 (When to use)

当用户提到以下关键词或场景时，应激活此技能：

- **关键词**：`节点定义`、`NodeDefinition`、`节点模板`、`节点规则`、`节点版本`
- **场景**：
  - 创建/修改项目节点模板
  - 配置节点的评审项
  - 配置节点的交付物要求
  - 管理节点层级关系（父子节点）
  - 处理节点定义版本变更
  - 查询节点树形结构
  - 批量启用/禁用节点定义

## 模块职责边界

### 核心职责

| 职责 | 说明 | 文件位置 |
|------|------|----------|
| 节点定义管理 | 节点模板的 CRUD，支持版本控制 | `apps/PSC/node/definition/` |
| 评审项定义管理 | 独立的评审项模板库 | `apps/PSC/review_definition/` |
| 节点-评审关联 | 节点定义版本与评审项定义的多对多关联 | `apps/PSC/node/review/` |
| 节点-交付物关联 | 节点定义版本与交付物定义版本的多对多关联 | `apps/PSC/node/deliverable/` |
| 功能配置管理 | 节点功能配置（枚举值存储） | `apps/PSC/node/definition/enums.py` |

### 边界说明

- **负责**：节点模板定义、版本控制、关联关系配置
- **不负责**：
  - 具体项目节点的实例化（由 PM 模块负责）
  - 节点的实际执行状态（由 PM/nodelist 负责）
  - 评审流程执行（由 SM/evaluation 负责）

## 模块架构

```
apps/PSC/
├── node/                              # 节点定义主模块
│   ├── definition/                     # 节点定义核心
│   │   ├── models.py                  # NodeDefinition, NodeDefinitionVersion, NodeDefinitionFeatureMapping
│   │   ├── serializers.py             # 序列化器（含版本处理逻辑）
│   │   ├── views.py                   # 视图（ListView, DetailView, SimpleListView）
│   │   ├── enums.py                   # 枚举定义（Category, FeatureConfig）
│   │   └── utils.py                   # 工具函数（含 currentName 注解）
│   ├── review/                        # 节点-评审关联（仅中间表）
│   │   └── models.py                  # NodeDefinitionReviewMapping
│   └── deliverable/                   # 节点-交付物关联（仅中间表）
│       └── models.py                  # NodeDefinitionDeliverableMapping
│
└── review_definition/                 # 独立评审项定义模块
    └── models.py                      # ReviewDefinition（原 Review 模型）
```

## 核心架构

### 版本化设计模式

节点定义采用**主模型 + 版本模型**的分离设计：

```
NodeDefinition (主模型)
├── code, is_active            # 仅创建时可编辑
├── created_at                 # 创建时间
└── versions (1:N)             # 版本关联

NodeDefinitionVersion (版本模型)
├── name                       # 🆕 节点名称（版本迭代时可修改）
├── category                   # 节点类型
├── default_owner              # 默认负责人
├── project_role               # 项目角色
├── evaluate_on_complete       # 节点完成时评价
├── default_workhours          # 节点默认工时
├── remark                     # 版本备注
├── version_number             # 版本号（自增）
├── is_current                 # 是否当前版本（⚠️ 唯一标识版本有效性）
├── created_by                 # 创建人
├── created_at                 # 创建时间
└── feature_mappings (1:N)     # 功能配置关联
```

**设计原则**：
- 主模型字段（code）仅在 POST 创建时可设置，PUT/PATCH 不能修改
- **name 字段存储在版本模型中，允许在版本迭代时修改**（🆕 Since 2026-03-09）
- `is_active` 仅可通过 PATCH 批量更新（控制节点定义是否启用）
- **版本有效性由 `is_current` 字段唯一标识**（⚠️ Since 2026-03-10）
- 所有业务变更通过版本迭代实现（PUT 请求创建新版本）
- `updatedAt` 取自最新版本的 `created_at`（主模型无 `updated_at` 字段）

## API 路由

### 节点定义路由 (RESTful 设计)

| 路由 | 方法 | 说明 | 权限 |
|------|------|------|------|
| `/psc/node/definitions/list` | GET | 列表查询（分页） | IsAuthenticated |
| `/psc/node/definitions/list` | POST | 创建节点定义 | IsAuthenticated |
| `/psc/node/definitions/list` | PATCH | 批量更新（仅 isActive） | IsAuthenticated |
| `/psc/node/definitions/list` | DELETE | 批量删除 | IsAuthenticated |
| `/psc/node/definitions/<id>` | GET | 获取单个节点定义详情 | IsAuthenticated |
| `/psc/node/definitions/<id>` | PUT | 版本迭代（创建新版本，name可修改） | IsAuthenticated |
| `/psc/node/definitions/simple` | GET | 简单列表（下拉选择） | IsAuthenticated |
| `/psc/node/definitions/enums` | GET | 枚举数据 | IsAuthenticated |

### 评审项路由

| 路由 | 方法 | 说明 |
|------|------|------|
| `/psc/review_definitions` | GET/POST/PUT | 评审项定义 CRUD（独立模块） |
| `/psc/review_definitions/simple` | GET | 评审项定义简单列表 |

**注意**：评审项模块从 `review/` 重构为 `review_definition/`，模型从 `Review` 重命名为 `ReviewDefinition`

## 字段权限说明

### 字段修改权限矩阵

| 字段 | POST | PUT | PATCH | 说明 |
|------|------|-----|-------|------|
| `code` | ✅ 必填 | ❌ 不可修改 | ❌ 不可修改 | 仅创建时设置 |
| `name` | ✅ 必填 | ✅ 可修改 | ❌ 不可修改 | 🆕 版本迭代时可修改 |
| `isActive` | ✅ 默认 true | ❌ 不可修改 | ✅ 可修改 | 仅 PATCH 可修改 |
| 版本相关字段 | ✅ 创建初始版本 | ✅ 创建新版本 | ❌ 不可修改 | 版本迭代 |

### 操作说明

- **POST**：创建节点定义 + 第一个版本（`code`, `name` 必填，`isActive` 默认 true）
- **PUT**：版本迭代（创建新版本，name 可修改，不更新 `code`, `isActive`）
- **PATCH**：批量更新 `isActive` 字段（需要 `ids` 列表和 `isActive` 值）
- **DELETE**：批量删除（需要 `ids` 列表，会检查是否被项目模板使用）

## name 字段唯一性验证

**验证层级**：序列化器（Serializer），模型层无唯一约束

### POST（创建节点定义）

检查其他节点定义的**当前版本**（`is_current=True`）是否已有相同 name：

```python
NodeDefinitionVersion.objects.filter(
    name=name,
    is_current=True
).exists()
```

### PUT（版本迭代）

排除本节点定义的所有版本，检查其他节点定义的**所有版本**是否有相同 name：

```python
NodeDefinitionVersion.objects \
    .exclude(id__in=[v.id for v in self.instance.versions.all()]) \
    .filter(name=name).exists()
```

**验证逻辑**：
- POST: 只检查当前版本，因为旧版本已被标记为非当前
- PUT: 检查所有版本，排除本节点定义的所有版本（防止跨节点定义重复）

## 列表查询优化

使用 `get_list_queryset()` 预加载当前版本数据，避免 N+1 查询：

```python
# utils.py
current_version = NodeDefinitionVersion.objects.filter(
    node_definition=OuterRef('pk'),
    is_current=True
)[:1]

latest_version = NodeDefinitionVersion.objects.filter(
    node_definition=OuterRef('pk')
).order_by('-created_at')[:1]

queryset = NodeDefinition.objects.annotate(
    currentVersionId=Subquery(current_version.values('id')),
    currentName=Subquery(current_version.values('name')),  # 🆕 当前版本名称
    currentCategory=Subquery(current_version.values('category')),
    currentDefaultOwnerNickname=Subquery(...),
    currentProjectRoleName=Subquery(...),
    currentEvaluateOnComplete=Subquery(current_version.values('evaluate_on_complete')),
    # ⚠️ Since 2026-03-10: 移除 currentIsActive（版本有效性由 is_current 标识）
    # ... 其他当前版本字段
    updatedAt=Subquery(latest_version.values('created_at')),  # 最新版本时间
)
```

**注意**：
- `updatedAt` 取自**最新版本**的 `created_at`，而非主模型的 `updated_at`（主模型无此字段）
- `name` 字段来自 `currentName` 注解（🆕 Since 2026-03-09）

## 技术实现要点

### 1. 序列化器设计

#### 列表相关序列化器

```python
# 查询参数序列化器
class GetListParamsSerializer(serializers.Serializer):
    code = serializers.CharField(required=False)
    name = serializers.CharField(required=False)  # 过滤 currentName
    category = serializers.ChoiceField(required=False)
    pageNum = serializers.IntegerField(required=False, default=1)
    pageSize = serializers.IntegerField(required=False, default=10)
    pageSort = serializers.CharField(required=False, default='id:DESC')

# 列表数据序列化器
class ListSerializer(serializers.ModelSerializer):
    # 扁平化输出，包含当前版本信息
    isActive = serializers.BooleanField(source='is_active', read_only=True)  # 主模型的 is_active
    name = serializers.CharField(read_only=True)  # 🆕 来自 currentName 注解
    # ⚠️ Since 2026-03-10: 移除 currentIsActive（版本模型已无 is_active 字段）

# 简单列表序列化器（用于下拉选择）
class SimpleListSerializer(serializers.ModelSerializer):
    # 仅返回启用状态的节点定义
    name = serializers.CharField(read_only=True)  # 🆕 来自 currentName 注解
```

#### 详情相关序列化器

```python
# 详情序列化器（分块输出）
class DetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    document = serializers.SerializerMethodField()  # code, name(来自当前版本), isActive
    versionData = serializers.SerializerMethodField()  # 当前版本信息
    others = serializers.SerializerMethodField()  # createdAt, updatedAt(最新版本), versionCount

# 版本简略序列化器（用于详情的 items）
class NodeDefinitionVersionSimpleSerializer(serializers.ModelSerializer):
    # 🆕 name 直接从版本模型获取，不再从 node_definition.name 获取
    # ⚠️ Since 2026-03-10: 移除 isActive 字段
    # 包含评审项和交付物定义列表
```

#### 写入序列化器

```python
class WriteSerializer(serializers.Serializer):
    """
    创建/更新序列化器
    POST: 创建定义 + 第一个版本（code 必填）
    PUT: 版本迭代（code 非必填，name 可修改）
    """
    code = serializers.CharField(required=False)  # POST 必填
    name = serializers.CharField(required=False)  # POST 必填，PUT 可修改
    isActive = serializers.BooleanField(required=False, source='is_active')

    # 版本相关字段
    category = serializers.ChoiceField(choices=Choices.Category.choices)
    defaultOwnerId = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    projectRoleId = serializers.PrimaryKeyRelatedField(queryset=ProjectRole.objects.all())
    evaluateOnComplete = serializers.BooleanField(default=False)
    defaultWorkhours = serializers.IntegerField(default=0)
    remark = serializers.CharField(required=False, allow_blank=True)

    # 关联数据
    reviewItems = ReviewItemSerializer(many=True, required=False)
    deliverableDefinitions = DeliverableDefinitionItemSerializer(many=True, required=False)
    featureConfigs = serializers.ListField(required=False)  # 功能配置
```

**name 处理逻辑**（🆕 Since 2026-03-09）：
```python
# POST: name 必填，存储到版本中
instance = NodeDefinition.objects.create(
    code=validated_data.get('code', ''),
    is_active=True  # name 不在主模型中
)

version_data = {
    'name': validated_data['name'],  # 必填
    'category': validated_data.get('category'),
    # ... 其他版本字段
}

# PUT: name 可选，不传则使用上一个版本的 name
previous_version = instance.versions.filter(is_current=True).first()
previous_name = previous_version.name if previous_version else None

version_data = {
    'name': validated_data.get('name', previous_name),  # 可选，有默认值
    'category': validated_data.get('category'),
    # ... 其他版本字段
}
```

#### 批量操作序列化器

```python
# 批量更新序列化器（PATCH）
class PatchSerializer(serializers.Serializer):
    """
    批量更新序列化器（PATCH）
    只能更新 is_active 字段（主模型的字段）
    """
    ids = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=NodeDefinition.objects.all()),
        required=True
    )
    isActive = serializers.BooleanField(required=False, source='is_active')

    def execute_update(self):
        """执行批量更新"""
        instances = self.validated_data['ids']
        is_active = self.validated_data.get('is_active')
        if is_active is not None:
            for instance in instances:
                instance.is_active = is_active
                instance.save()
        return len(instances)

# 批量删除序列化器（DELETE）
class DeleteSerializer(serializers.Serializer):
    """
    批量删除序列化器（DELETE）
    """
    ids = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=NodeDefinition.objects.all()),
        required=True
    )

    def validate(self, attrs):
        """验证是否可以删除"""
        from apps.PSC.project.node.models import ProjectTemplateNodeMapping
        instances = attrs['ids']
        errors = []
        for instance in instances:
            # 检查是否被项目模板引用
            if ProjectTemplateNodeMapping.objects.filter(
                node_definition_version__node_definition=instance
            ).exists():
                errors.append(f'"{instance.code}" 已被项目模板引用，无法删除')
        if errors:
            raise serializers.ValidationError({'ids': errors})
        return attrs

    def execute_delete(self):
        """执行批量删除"""
        for instance in self.validated_data['ids']:
            instance.delete()
        return True
```

### 2. 视图设计

#### ListView（列表视图）

```python
class ListView(APIView):
    """
    节点定义列表视图
    - GET    列表查询（分页）
    - POST   创建节点定义（含第一个版本，isActive 默认 true）
    - PATCH  批量更新（仅 isActive）
    - DELETE 批量删除
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """获取节点定义列表（分页）"""
        # 使用 GetListParamsSerializer 验证查询参数
        # 返回 ListSerializer 序列化的数据和分页信息

    def post(self, request):
        """创建节点定义（同时创建第一个版本，isActive 默认 true）"""
        # 使用 WriteSerializer 验证并创建
        # 返回 201 状态码

    def patch(self, request):
        """批量更新节点定义（仅 isActive）"""
        # 使用 PatchSerializer 验证并更新
        # 返回更新记录数

    def delete(self, request):
        """批量删除节点定义"""
        # 使用 DeleteSerializer 验证并删除
        # 检查是否被项目模板使用
```

#### DetailView（详情视图）

```python
class DetailView(APIView):
    """
    节点定义详情视图
    - GET    详情查询
    - PUT    版本迭代（创建新版本，name 可修改）
    """
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        """分发请求，设置 instance 参数"""
        try:
            self.definition_instance = NodeDefinition.objects.get(id=kwargs.get('id'))
        except NodeDefinition.DoesNotExist:
            return JsonResponse({'msg': '节点定义不存在'}, status=404)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """获取节点定义详情（分块输出）"""
        # 返回 DetailSerializer 序列化的数据

    def put(self, request, *args, **kwargs):
        """版本迭代：创建新版本（name 可修改）"""
        # 使用 WriteSerializer 验证并创建新版本
```

#### SimpleListView（简单列表视图）

```python
class SimpleListView(APIView):
    """简单列表视图（用于下拉选择等场景）"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """只返回启用的节点定义，按 code 排序"""
        queryset = get_list_queryset()
        params_serializer = GetSimpleListParamsSerializer(data=request.query_params)
        params_serializer.is_valid(raise_exception=True)
        serializer = SimpleSerializer(
            params_serializer.get_queryset(queryset), many=True
        )
        return JsonResponse({'msg': 'success', 'data': serializer.data})
```

### 3. 版本控制模式

```python
# 创建新版本的正确方式
node_definition.create_new_version(
    name="节点名称",  # 🆕 name 在版本中
    category="main_node",
    default_owner=user,
    project_role=role,
    evaluate_on_complete=True,
    default_workhours=8,
    remark="备注信息",
    created_by=user,
)

# 系统自动：
# 1. 将旧版本的 is_current 设为 False
# 2. 创建新版本并自动递增 version_number
# 3. 设置新版本的 is_current = True
```

### 4. 多对多关联处理

在创建/更新节点定义时，评审项和交付物通过数组传递：

```json
{
  "name": "需求评审",
  "reviewItems": [
    {"versionId": 1, "sortOrder": 1},
    {"versionId": 2, "sortOrder": 2}
  ],
  "deliverableDefinitions": [
    {"versionId": 1, "sortOrder": 1, "isRequired": true}
  ]
}
```

系统会自动：
1. 删除旧的关联记录
2. 批量创建新的关联记录

### 5. 枚举使用

```python
from apps.PSC.node.definition.enums import Choices

# 获取枚举值
Choices.Category.MILESTONE        # 'MILESTONE'
Choices.Category.MILESTONE.label  # '里程碑节点'

# 获取所有枚举
Choices.get_choices_enum()
```

## 数据模型

### NodeDefinitionDeliverableMapping

节点定义版本与交付物定义版本的多对多关联表。

| 字段 | 类型 | 说明 |
|------|------|------|
| node_definition_version | ForeignKey | 节点定义版本 |
| deliverable_definition_version | ForeignKey | 交付物定义版本 |
| function_restriction | CharField | 功能限制 |
| sort_order | IntegerField | 排序 |
| is_required | BooleanField | default=False | 是否必填 |

## 核心数据模型

详见 `models.md`

## 信号驱动版本升级 (🆕 Since 2026-03-10)

### 设计概述

节点定义模块支持**关联定义变化自动触发节点定义版本升级**机制，通过信号处理器实现：

- **评审项定义变化** → 触发节点定义版本升级
- **交付物定义变化** → 触发节点定义版本升级

### 评审项定义变化处理

**信号源**：`apps/PSC/review_definition/signals.py`

**处理函数**：`upgrade_node_definition_version_when_review_changes()`

**触发条件**：
1. 新创建的评审项定义版本（`created=True`）
2. 是当前版本（`is_current=True`）
3. 不是首次创建（第一个版本不需要触发升级）

**处理流程**：
```python
# 1. 查找所有引用旧评审项版本的节点定义版本
affected_mappings = NodeDefinitionReviewMapping.objects.filter(
    review_definition_version=old_review_version
)

# 2. 为每个节点定义创建新版本
for node_definition in affected_node_definitions:
    # 创建新版本（复制所有数据）
    new_version = node_definition.create_new_version(**version_data)

    # 3. 复制评审项映射（替换被修改的评审项）
    for old_mapping in old_review_mappings:
        review_version = new_review_version if old_mapping.review_definition_version == old_review_version else old_mapping.review_definition_version
        NodeDefinitionReviewMapping.objects.create(
            node_definition_version=new_version,
            review_definition_version=review_version,
            sort_order=old_mapping.sort_order
        )

    # 4. 复制交付物定义映射
    # 5. 复制功能配置映射
```

### 交付物定义变化处理

**信号源**：`apps/PSC/deliverable/definition/signals.py` 🆕

**处理函数**：`upgrade_node_definition_version_when_deliverable_changes()` 🆕

**触发条件**：
1. 新创建的交付物定义版本（`created=True`）
2. 是当前版本（`is_current=True`）
3. 不是首次创建（第一个版本不需要触发升级）

**处理流程**：
```python
# 1. 查找所有引用旧交付物版本的节点定义版本
affected_mappings = NodeDefinitionDeliverableMapping.objects.filter(
    deliverable_definition_version=old_deliverable_version
)

# 2. 为每个节点定义创建新版本
for node_definition in affected_node_definitions:
    # 创建新版本（复制所有数据）
    new_version = node_definition.create_new_version(**version_data)

    # 3. 复制交付物定义映射（替换被修改的交付物）
    for old_mapping in old_deliverable_mappings:
        deliverable_version = new_deliverable_version if old_mapping.deliverable_definition_version == old_deliverable_version else old_mapping.deliverable_definition_version
        NodeDefinitionDeliverableMapping.objects.create(
            node_definition_version=new_version,
            deliverable_definition_version=deliverable_version,
            function_restriction=old_mapping.function_restriction,
            sort_order=old_mapping.sort_order,
            is_required=old_mapping.is_required
        )

    # 4. 复制评审项映射
    # 5. 复制功能配置映射
```

### 防并发处理

两个函数都使用**缓存标记**防止并发问题：

```python
cache_key = f'node_upgrade_{node_definition.id}_{old_version.id}'
if cache.get(cache_key):
    continue  # 正在升级中，跳过
cache.set(cache_key, True, 300)  # 有效期 5 分钟
```

### 关键文件

| 文件 | 说明 |
|------|------|
| `apps/PSC/node/definition/utils.py` | 包含两个版本升级函数 |
| `apps/PSC/review_definition/signals.py` | 评审项定义信号处理器 |
| `apps/PSC/deliverable/definition/signals.py` | 🆕 交付物定义信号处理器 |
| `apps/PSC/signals.py` | 信号注册入口 |

## 权限验证

该模块的权限验证遵循 PSC 模块的统一规范，详见 `permission-flow.md`

## 常见业务场景

### 场景1：创建新的节点模板

```python
# 1. 创建评审项定义（如果需要）
POST /psc/review_definitions
{
  "name": "技术评审",
  "description": "技术方案评审"
}

# 2. 创建节点定义
POST /psc/node/definitions/list
{
  "code": "TECH_REVIEW",
  "name": "技术评审",  # 🆕 name 必填
  "category": "SUB_NODE",
  "projectRoleId": 5,
  "reviewItems": [
    {"versionId": 1, "sortOrder": 1}
  ],
  "featureConfigs": [
    "TIMELINE_PRESET",
    "CHECKLIST_EDIT"
  ]
}
```

### 场景2：修改节点定义（自动创建新版本，name 可修改）

```python
PUT /psc/node/definitions/123
{
  "name": "技术评审v2",  # 🆕 name 可以修改
  "category": "MILESTONE",
  "reviewItems": [...]   # 更新关联的评审项
}
```

### 场景3：批量启用/禁用节点定义

```python
PATCH /psc/node/definitions/list
{
  "ids": [1, 2, 3],
  "isActive": false
}
```

### 场景4：批量删除节点定义

```python
DELETE /psc/node/definitions/list
{
  "ids": [1, 2, 3]
}
# 注意：如果节点定义已被项目模板使用，将返回错误
```

### 场景5：获取节点定义详情

```python
GET /psc/node/definitions/123

# 返回：
{
  "msg": "success",
  "data": {
    "id": 123,
    "document": {
      "code": "TECH_REVIEW",
      "name": "技术评审",  # 🆕 来自当前版本
      "isActive": true
    },
    "versionData": {
      "id": 456,
      "versionNumber": 2,
      "name": "技术评审",  # 🆕 直接来自版本模型
      "category": "milestone",
      # ⚠️ Since 2026-03-10: 移除 isActive 字段
      # ... 其他版本字段
      "reviewItems": [...],
      "deliverableDefinitions": [...]
    },
    "others": {
      "createdAt": "2024-01-01T00:00:00+08:00",
      "updatedAt": "2024-01-02T00:00:00+08:00",  # 🆕 来自最新版本
      "versionCount": 2
    }
  }
}
```

## 演进方向

详见 `evolution.md`

## 关联模块

- **PSC/project/template**：使用节点定义创建项目模板节点映射
- **PSC/review_definition**：评审项定义模块（独立模块）
- **PSC/deliverable/definition**：交付物定义模块

## 特有名词索引

| 名词 | 说明 |
|------|------|
| NodeDefinition | 节点定义主模型，管理节点模板的元数据（无 name 字段） |
| NodeDefinitionVersion | 节点定义版本模型，存储节点的具体配置（含 name 字段）🆕 |
| ReviewDefinition | 评审项定义，独立的评审模板（原 Review 模型） |
| NodeDefinitionReviewMapping | 节点-评审项定义版本关联表 |
| NodeDefinitionDeliverableMapping | 节点-交付物定义版本关联表 |
| NodeDefinitionFeatureMapping | 节点-功能配置关联表（枚举值存储） |
| category | 节点类型：MILESTONE(里程碑)、MAIN_NODE(主节点)、SUB_NODE(子节点) |
| FeatureConfig | 功能配置枚举：TIMELINE_PRESET、CHECKLIST_EDIT、CHECKLIST_UPLOAD、CHECKLIST_REVIEW |
| is_current | 标识当前有效版本（⚠️ 唯一标识版本有效性，Since 2026-03-10） |
| version_number | 内部版本号（自增） |
| currentName | 当前版本的 name 注解（🆕） |
| updatedAt | 最新版本的 created_at（🆕） |

## 版本历史
### vX.X.X - is_required 迁移 (2026-03-27)

- [x] `NodeDefinitionDeliverableMapping` 新增 `is_required` 字段（default=False）
- [x] 节点定义创建/编辑接口 `deliverableDefinitions` 支持 `isRequired` 参数
- [x] 节点定义详情返回 `deliverableDefinitionIsRequired`（来源改为 mapping.is_required）
- [x] 节点定义版本升级时复制 `is_required` 字段
- [x] 评审跳过逻辑改为基于 `NodeDefinitionDeliverableMapping.is_required`

### v1.7 (2026-03-10) 🆕

**新增交付物定义变化触发节点定义版本升级**：
- 🆕 新增 `upgrade_node_definition_version_when_deliverable_changes()` 函数
- 🔧 与评审项定义变化处理逻辑保持一致
- 🔧 支持交付物定义版本变化自动升级引用它的节点定义
- 🔧 复制所有关联数据（评审项、交付物、功能配置）
- 🔧 防并发处理（缓存标记）

**关联模块**：
- `apps/PSC/deliverable/definition/signals.py` 新增信号处理器

### v1.6 (2026-03-10)

**删除冗余 is_active 字段**：
- ⚠️ 删除 `NodeDefinitionVersion.is_active` 字段（版本模型）
- 🔧 版本有效性现由 `is_current` 字段唯一标识
- 🔧 删除 `ListSerializer` 中的 `currentIsActive` 字段
- 🔧 删除 `NodeDefinitionVersionSimpleSerializer` 中的 `isActive` 字段
- 🔧 删除 `utils.py` 中的 `currentIsActive` Subquery 注解
- 🔧 删除 `upgrade_node_definition_version_when_review_changes` 中的 `is_active` 复制

**设计原则更新**：
- 主模型 `is_active`：控制节点定义是否启用
- 版本模型 `is_current`：标识当前有效版本（唯一标识版本有效性）

**数据库迁移**：
- 迁移文件：`0027_remove_nodedefinitionversion_is_active.py`

### v1.5 (2026-03-09)

**name 字段重构**：
- 🆕 将 `NodeDefinition` 主模型的 `name` 字段移至 `NodeDefinitionVersion` 子模型
- 🆕 移除 `NodeDefinition` 主模型的 `updated_at` 字段
- 🔧 `updatedAt` 现在取自最新版本的 `created_at`
- 🔧 列表查询添加 `currentName` 注解
- 🔧 序列化器更新 `name` 字段处理逻辑
- 🔧 `name` 字段唯一性验证调整（检查当前版本/所有版本）
- 🔧 `name` 字段现在可以在版本迭代时修改

**设计原则更新**：
- 主模型只保留必要字段和唯一标识
- 可变业务数据（包括 name）存储在版本模型中
- 主模型只有 `is_active` 字段可编辑
- `updatedAt` 取自最新版本的 `created_at`（主模型无 `updated_at` 字段）

**模型变更**：
```python
# 修改前
class NodeDefinition(models.Model):
    code = CharField(unique=True)
    name = CharField(unique=True)  # ⚠️ 在主模型中
    is_active = BooleanField()
    created_at = DateTimeField()
    updated_at = DateTimeField()  # ⚠️ 在主模型中

# 修改后
class NodeDefinition(models.Model):
    code = CharField(unique=True)
    # ⚠️ name 字段已移除
    is_active = BooleanField()
    created_at = DateTimeField()
    # ⚠️ updated_at 字段已移除

class NodeDefinitionVersion(models.Model):
    # ...
    name = CharField()  # 🆕 name 在版本模型中
```

**序列化器变更**：
- `ListSerializer` 添加 `name` 注解字段（来自 currentName）
- `SimpleSerializer` 添加 `name` 注解字段（来自 currentName）
- `SimpleListSerializer` 添加 `name` 注解字段（来自 currentName）
- `DetailSerializer.get_document` 从当前版本获取 name
- `DetailSerializer.get_others` 从最新版本获取 updatedAt
- `WriteSerializer.validate_name` 更新验证逻辑
- `WriteSerializer.create` 将 name 放入版本数据
- `WriteSerializer.update` 支持版本迭代时修改 name

**查询优化变更**：
- `get_list_queryset` 添加 `currentName` 注解
- `get_list_queryset` 添加 `updatedAt` 注解（从最新版本）
- 过滤条件从 `name` 改为 `currentName`

**API 变更**：
- PUT 请求现在可以修改 `name` 字段（版本迭代时）
- `name` 不传时使用上一个版本的 name

**数据库迁移**：
- 迁移文件：`0025_move_name_to_deliverable_definition_version.py`
- 同时处理 NodeDefinition 和 DeliverableDefinition 的 name 字段调整

### v1.4 (2026-03-02)

**架构重构**：
- ⚠️ 评审项模块重构：`Review` 模型重命名为 `ReviewDefinition`
- ⚠️ 评审项模块迁移：从 `apps/PSC/review/` 迁移到 `apps/PSC/review_definition/`
- 🔧 `NodeDefinitionReviewMapping` 关联从 `Review` 更新为 `ReviewDefinition`
- 🆕 功能配置采用枚举值存储（`Choices.FeatureConfig`），而非独立模型

### v1.3 (2026-03-02)

**新增功能配置**：
- 🆕 新增 `FeatureConfig` 枚举定义，定义可选的功能配置项
- 🆕 新增 `NodeDefinitionFeatureMapping` 中间表，支持节点定义与功能配置的多对多关联
- 🆕 节点定义版本支持配置多个功能（时间线预设、配置清单编辑、配置清单上传、配置清单复核）
- 🆕 枚举接口新增 `featureConfigs` 字段，返回可选的功能配置列表

### v1.2 (2026-03-02)

**重要架构修复**：
- 🔧 修复交付物定义版本关联问题（`NodeDefinitionDeliverableMapping`）
- 🆕 关联表从关联 `DeliverableDefinition`（主模型）改为关联 `DeliverableDefinitionVersion`（版本模型）
- 🆕 创建节点定义时自动锁定交付物定义的当前版本（`is_current=True`）
- 🆕 API 响应新增 `deliverableDefinitionVersionId` 和 `deliverableDefinitionVersion` 字段

### v1.1 (2025-03-02)

**新增功能**：
- 🆕 新增 `PatchSerializer` 序列化器，支持批量更新 `is_active` 字段
- 🆕 `ListView` 新增 `patch()` 方法，处理批量更新请求
- 🆕 `ListView` 新增 `delete()` 方法，处理批量删除请求

**重构优化**：
- ⚠️ 重构 `DeleteSerializer`，添加业务验证（检查是否被项目节点使用）
- ⚠️ `DetailView` 移除 `delete()` 方法，删除操作统一由 `ListView` 处理
- ⚠️ 路由重构，参考交付物定义模块的 RESTful 设计
- ⚠️ 所有视图添加 `IsAuthenticated` 权限控制
- ⚠️ 统一错误处理，使用 `status.HTTP_*` 状态码

**字段权限规范**：
- `code`: 仅 POST 创建，PUT/PATCH 不能修改
- `name`: POST 创建，PUT/PATCH 不能修改（⚠️ v1.5 之前，v1.5 之后 PUT 可修改）
- `isActive`: 仅 PATCH 修改，POST 默认 true，PUT 不能修改
- 版本相关字段: POST 创建初始版本，PUT 创建新版本（版本迭代）
