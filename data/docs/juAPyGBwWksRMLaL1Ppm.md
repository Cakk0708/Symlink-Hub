# PSC 评审项定义模块 (PSC Review Definition)

## 模块定位

PSC/review_definition 模块是**项目设置配置（PSC）**子系统中的评审项定义管理模块。它提供了一套独立可复用的评审项模板系统，供项目节点定义配置时使用。

**核心价值**：将评审流程标准化、模板化，使不同项目节点可以快速复用相同的评审规范。


## 模块职责边界

### 负责范围
- 评审项模板的 CRUD（创建、读取、更新、删除）
- 评审项编码自动生成（前缀：`REVIEW_DEF`）
- 评审项启用/禁用状态管理
- **🆕 多版本管理（版本迭代）**

### 不负责范围
- 评审项与具体节点的绑定（由 `PSC/node/review` 模块负责）
- 评审执行流程（由 PM/PM 模块负责）
- 评审权限控制（由 PM/authority 模块负责）


## 核心数据模型

### 🆕 多版本架构（Since 2026-03-09）

**主模型**: `ReviewDefinition`
**版本模型**: `ReviewDefinitionVersion`

**设计原则**：
- 主模型只保留必要字段和唯一标识
- 可变业务数据（包括**name**）存储在版本模型中
- 主模型只有 `is_active` 字段可编辑

### ReviewDefinition 模型
**表名**: `PSC_review_definition`

```python
class ReviewDefinition(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=100, unique=True)      # 自动生成，前缀：REVIEW_DEF
    is_active = models.BooleanField(default=True)              # 是否启用
    created_at = models.DateTimeField(auto_now_add=True)       # 创建时间

    # 方法
    def create_new_version(self, **version_data):
        """创建新版本，自动将旧版本标记为非当前"""
```

**字段权限**：
- `code`: 仅 POST 创建时设置
- `is_active`: 仅 PATCH 修改，POST 默认 true
- ⚠️ **`name` 字段已移至版本模型**（Deprecated since 2026-03-09）

### ReviewDefinitionVersion 模型
**表名**: `PSC_review_definition_version`

```python
class ReviewDefinitionVersion(models.Model):
    id = models.AutoField(primary_key=True)
    version_number = models.IntegerField()                      # 内部版本号（自动递增）
    review_definition = models.ForeignKey(ReviewDefinition, related_name='versions')
    name = models.CharField(max_length=255)                     # 🆕 评审项名称（版本迭代时可修改）
    deliverable_definition_version = models.ForeignKey(...)    # 关联的交付物定义版本
    remark = models.TextField(blank=True, null=True)           # 备注
    is_current = models.BooleanField(default=True)              # 是否当前版本
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, ...)
    created_at = models.DateTimeField(auto_now_add=True)
```

**版本控制规则**：
- 创建新版本时，旧版本自动标记为 `is_current=False`
- `version_number` 自动递增（当前最大版本号 + 1）
- 每次编辑评审项内容（**name**、remark、交付物关联）创建新版本
- **name 唯一性在序列化器层验证，模型层无约束**（🆕 Since 2026-03-09）


## 序列化器架构

### 读写分离 + 版本管理

```python
# 只读序列化器
SimpleSerializer                              # id, code, name（下拉选择，name来自当前版本）
ListSerializer                               # 列表（扁平化，含当前版本数据）
ReviewDefinitionVersionSimpleSerializer      # 版本数据（含 name）
DetailSerializer                             # 详情（分块输出：document, versionData, others）

# 写入序列化器
WriteSerializer                              # 创建/版本迭代（name可修改）
PatchSerializer                              # 批量更新（仅 is_active）
DeleteSerializer                             # 批量删除
```

### ListSerializer（扁平化输出）
```python
# 主模型字段
id, code, isActive, createdAt

# 当前版本扁平化字段（通过 Subquery annotate）
name, currentRemark, currentCreatedAt, updatedByNickname
```

**变更说明**：`name` 字段来自 `currentName` 注解（🆕 Since 2026-03-09）

### DetailSerializer（分块输出）
```python
{
    "id": 1,
    "document": {
        "code": "REVIEW_DEF001",
        "name": "设计评审",          # 来自当前版本 🆕
        "isActive": true
    },
    "versionData": {
        "id": 5,
        "versionNumber": 2,
        "isCurrent": true,
        "name": "设计评审",          # 🆕
        "remark": "评审备注",
        "deliverableDefinitionVersion": {...}
    },
    "others": {
        "versionCount": 2,
        "createdAt": "2026-03-03T10:00:00+08:00",     # 主模型创建时间
        "createdBy": null,                            # 主模型创建人已移除 🆕
        "updatedAt": "2026-03-03T15:30:00+08:00",     # 当前版本创建时间
        "updatedBy": {"id": 2, "nickname": "李四"}     # 当前版本创建人
    }
}
```

### WriteSerializer（创建/版本迭代）
```python
# POST: 创建主模型 + 第一个版本
{
    "code": "REVIEW_DEF001",       # 可选，为空自动生成
    "name": "设计评审",             # 必填，存储到版本中 🆕
    "remark": "评审备注",
    "deliverableDefinitionVersionId": 10  # 可选
}

# PUT: 版本迭代（创建新版本，name可修改）🆕
{
    "name": "设计评审（更新）",     # 必填，可修改，创建新版本
    "remark": "更新后的备注",
    "deliverableDefinitionVersionId": 10
}
```

**验证规则**：
- `validate_code()`: 编码唯一性验证
- `validate_name()`: **名称唯一性验证**（🆕 Since 2026-03-09）
  - POST: 检查所有当前版本的 name 是否重复
  - PUT: 如果 name 与当前版本相同则跳过验证，否则检查其他评审项的当前版本


## API 路由设计

**基础路径**: `/psc/review_definition`

```
GET    /psc/review_definition/list           # 列表（分页、筛选）
POST   /psc/review_definition/list           # 创建主模型+第一个版本（name必填）🆕
PATCH  /psc/review_definition/list           # 批量更新（仅 isActive）
DELETE /psc/review_definition/list           # 批量删除
GET    /psc/review_definition/<id>           # 详情
PUT    /psc/review_definition/<id>           # 版本迭代（创建新版本，name可修改）🆕
GET    /psc/review_definition/simple         # 简单列表（下拉选择）
```

### 列表参数 (GetListParamsSerializer)
```python
name        # 模糊搜索（过滤 currentName）🆕
code        # 编码搜索（可选）
isActive    # 启用状态筛选（可选）
pageNum     # 页码，默认 1
pageSize    # 每页数量，默认 10
pageSort    # 排序，格式：FIELD:ASC/DESC，默认 id:DESC
```

**变更说明**：`name` 过滤条件更新为 `currentName`（🆕 Since 2026-03-09）


## 字段权限矩阵

| 字段 | POST | PATCH | PUT |
|-----|------|-------|-----|
| code | ✅创建 | ❌ | ❌ |
| name | ✅必填 | ❌ | ✅可修改 🆕 |
| is_active | ✅默认true | ✅ | ❌ |
| remark | ✅ | ❌ | ✅ |
| deliverableDefinitionVersionId | ✅ | ❌ | ✅ |

**变更说明**：PUT 时 name 可修改，会创建新版本（🆕 Since 2026-03-09）


## 版本迭代流程

### POST 创建流程 🆕
```
1. 创建 ReviewDefinition（code, is_active=True）
2. 自动创建第一个 ReviewDefinitionVersion（is_current=True, name必填）
```

### PUT 版本迭代流程 🆕
```
1. 读取现有 ReviewDefinition
2. 将当前版本标记为 is_current=False
3. 创建新 ReviewDefinitionVersion（is_current=True, version_number自动+1, name可修改）
4. 不修改 ReviewDefinition 的 code, is_active
```

### PATCH 更新流程
```
仅修改 ReviewDefinition.is_active
不创建新版本
```


## 查询集优化（utils.py）

### get_list_queryset() 🆕
```python
# 预加载当前版本数据（扁平化）
current_version = ReviewDefinitionVersion.objects.filter(
    review_definition=OuterRef('pk'),
    is_current=True
)[:1]

queryset = ReviewDefinition.objects.select_related('created_by').annotate(
    currentName=Subquery(current_version.values('name')),      # 🆕
    currentRemark=Subquery(current_version.values('remark')),
    currentCreatedAt=Subquery(current_version.values('created_at')),
    updatedByNickname=Subquery(current_created_by_nickname),
)
```

### get_detail_queryset()
```python
# 预加载版本数据和关联的交付物定义
queryset = queryset.prefetch_related(
    'versions__created_by',
    'versions__deliverable_definition_version__deliverable_definition',
)
```


## 与其他模块关系

### 1. PSC/node/definition（节点定义）
```python
# 节点定义配置时引用评审项
class ReviewItemSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=ReviewDefinition.objects.all())
    sortOrder = serializers.IntegerField(required=False, default=0)

# NodeDefinitionVersion 配置
reviewItems = ReviewItemSerializer(many=True, required=False)
```

### 2. PSC/deliverable/definition（交付物定义）
```python
# 评审项版本可关联交付物定义版本
class ReviewDefinitionVersion(models.Model):
    deliverable_definition_version = models.ForeignKey(
        'PSC.DeliverableDefinitionVersion',
        null=True, blank=True
    )
```

### 3. PSC/evaluation_config（评价配置）
- **关系类型**: 平行模块
- **区别**:
  - `ReviewDefinition`: 节点级别的评审项（如"设计评审"、"测试评审"）
  - `EvaluationConfig`: 项目级别的绩效评价（如"贡献度评价"、"能力评价"）


## 常见业务场景

### 场景 1: 创建评审项 🆕
```python
POST /psc/review_definition/list
{
    "name": "设计评审",          # 必填，存储到版本中
    "remark": "对设计方案进行全面评审"
}
# 响应
{
    "msg": "success",
    "data": {"insertId": 1}
}
```

### 场景 2: 版本迭代（修改 name）🆕
```python
PUT /psc/review_definition/1
{
    "name": "设计评审（更新版）", # 可修改 name，创建新版本
    "remark": "更新后的评审要求",
    "deliverableDefinitionVersionId": 10
}
# 创建新版本，version_number 自动 +1，新版本的 name 为"设计评审（更新版）"
```

### 场景 3: 批量启用/禁用
```python
PATCH /psc/review_definition/list
{
    "ids": [1, 2, 3],
    "isActive": false
}
```

### 场景 4: 获取详情（分块输出）
```python
GET /psc/review_definition/1
# 返回 document, versionData, others 三块数据
# document.name 来自当前版本 🆕
```


## 模块特有名词索引

| 名词 | 说明 | 关联 |
|------|------|------|
| 评审项定义 | ReviewDefinition 模型核心概念 | 本模块 |
| ReviewDefinition | 评审项定义英文名 | 本模块 |
| 评审配置 | 评审项定义管理功能 | 本模块 |
| REVIEW_DEF | 评审项编码前缀 | 本模块 |
| 版本迭代 | PUT 创建新版本，name可修改 🆕 | 本模块 |
| 评审项关联 | NodeDefinitionReviewMapping | PSC/node/review |
| 节点评审 | 节点定义配置评审项 | PSC/node/definition |
| name 可修改 | PUT 时可修改评审项名称 🆕 | 本模块 |


## 开发注意事项

### 1. 版本数据查询
```python
# 获取当前版本
current_version = definition.versions.filter(is_current=True).first()

# 获取当前版本的 name
name = current_version.name if current_version else None  # 🆕

# 获取所有版本（倒序）
all_versions = definition.versions.all().order_by('-version_number')
```

### 2. 迁移文件
```bash
# 0024_move_review_definition_name.py 🆕
# 数据迁移：将主模型的 name 复制到版本模型
python manage.py migrate PSC
```

### 3. ⚠️ 已废弃设计
- ~~`ReviewDefinition.name`~~: 已移至版本模型（Deprecated since 2026-03-09）
- ~~`ReviewDefinition.created_by`~~: 已移除（Deprecated since 2026-03-09）
- ~~`ReviewDefinition.updated_at`~~: 已移除，使用 `ReviewDefinitionVersion.created_at` 作为更新时间
- ~~单模型方案~~: 已废弃，改用多版本架构

### 4. 🆕 新增能力（Since 2026-03-09）
- **name 字段存储在版本模型中**：允许在版本迭代时修改评审项名称
- **name 唯一性验证**：在序列化器层验证，检查当前版本的 name 唯一性
- **PUT 时 name 可修改**：创建新版本时可以传入新的 name
- **currentName 注解**：列表查询时通过 Subquery 获取当前版本的 name


## 演进方向 (Future Evolution)

### Phase 1: 权限集成
- [ ] 集成 PM/authority 权限验证
- [ ] 区分"系统评审项"（只读）和"自定义评审项"（可编辑）

### Phase 2: 关联检查
- [ ] 删除前检查节点定义引用
- [ ] 提供引用查看 API

### Phase 3: 版本管理增强
- [ ] 版本历史查看
- [ ] 版本对比功能（含 name 变更历史）🆕
- [ ] 版本回滚功能

### Phase 4: 智能推荐
- [ ] 基于节点类型推荐评审项
- [ ] 基于历史数据生成评审模板


## 相关文件清单

### 核心文件

| 文件 | 说明 |
|-----|------|
| `apps/PSC/review_definition/models.py` | 数据模型定义（name 在版本模型中）🆕 |
| `apps/PSC/review_definition/serializers.py` | 序列化器（含 name 唯一性验证）🆕 |
| `apps/PSC/review_definition/views.py` | API 视图 |
| `apps/PSC/review_definition/utils.py` | 查询集优化（currentName 注解）🆕 |
| `apps/PSC/review_definition/urls.py` | 路由配置 |
| `apps/PSC/migrations/0024_move_review_definition_name.py` | 数据迁移文件 🆕 |
