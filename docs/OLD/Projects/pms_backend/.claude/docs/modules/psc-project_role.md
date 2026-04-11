# PSC 项目角色模块 (ProjectRole)

## 模块定位

**ProjectRole** 是 PSC（项目设置配置）模块中的核心子模块，负责定义项目管理中的角色体系。它作为 PM（项目管理）模块的基础配置，为项目节点分配负责人、项目评价配置、权限控制等提供角色维度。

**所属层级**: `apps/PSC/project_role/`

## 核心职责

1. **角色定义管理**: 维护项目角色的基础信息（名称、编码、描述）
2. **评价权限配置**: 控制角色是否可参与评价（is_evaluatable）和是否被评价（is_evaluated）
3. **预设角色保护**: 管理系统预置角色，防止误删除
4. **批量操作支持**: 支持批量禁用/启用、批量删除（软删除）
5. **特殊分数标记**: 标记需要特殊分数处理的角色

## 数据模型

### ProjectRole 主模型

```python
class ProjectRole(models.Model):
    code                # 唯一编码（自动生成，前缀PROJROLE）
    name                # 角色名称
    disable_flag        # 禁用状态
    is_evaluatable      # 是否参与评价（作为评价人）
    is_evaluated        # 是否被评价（作为被评价对象）
    is_preset           # 是否预设数据（受保护）
    is_special_score    # 分数是否特殊处理
    creator             # 创建人
    update_by           # 最后修改人
    is_active           # 是否有效（软删除标记）
```

### 核心字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `is_evaluatable` | Boolean | 该角色是否可以评价其他角色 |
| `is_evaluated` | Boolean | 该角色是否可以被其他角色评价 |
| `is_preset` | Boolean | 预设角色，不可删除 |
| `is_special_score` | Boolean | 特殊分数处理标记 |

### 关联关系

```
ProjectRole (项目角色)
    ├─ evaluation_config (反向) → EvaluationConfig # 项目评价配置
    ├─ evaluation_item_role (反向) → EvaluationConfigItemRole # 评价项角色关联
    ├─ node_definition_versions (反向) → NodeDefinitionVersion # 节点定义版本
    └─ created_project_role (反向) → User # 创建人
```

## 权限验证流程

### 权限枚举 (apps/PSC/project_role/enums.py)

```python
class Permissions:
    class OperationTypes(models.TextChoices):
        CREATE = 'CREATE', '创建'
        VIEW = 'VIEW', '查看'
        CHANGE = 'CHANGE', '修改'
        DELETE = 'DELETE', '删除'
        DISABLE = 'DISABLE', '禁用'

    DJANGO_CODENAME_MAP = {
        'CREATE': 'add_projectrole',
        'VIEW': 'view_projectrole',
        'CHANGE': 'change_projectrole',
        'DELETE': 'delete_projectrole',
        'DISABLE': 'disable_projectrole'
    }
```

### 权限验证代码示例

```python
from .enums import Permissions as enumPermissions

# 在序列化器中验证权限
def validate(self, attrs):
    permission_key = 'CHANGE' if self.instance else 'CREATE'
    if not self.current_user.has_perm(
        enumPermissions.get_permission_verify_codename(permission_key)
    ):
        raise CustomPermissionDenied()
    return attrs
```

### 权限验证位置

1. **创建**: `ProjectRoleSerialzer.validate()` - 检查 `PM.add_projectrole`
2. **修改**: `ProjectRoleSerialzer.validate()` - 检查 `PM.change_projectrole`
3. **删除**: `DeleteBatchSerializer.validate()` - 检查 `PM.delete_projectrole`
4. **禁用**: `PatchBatchUpdateSerializer.validate()` - 检查 `PM.disable_projectrole`

## API 端点

### 基础路由

```
/psc/role                    # 项目角色列表/创建
/psc/role/simple             # 简单列表（仅返回未禁用）
/psc/role/<action>           # 详情/修改/删除/批量操作
```

### 请求方法

| 方法 | 端点 | 说明 | 权限 |
|------|------|------|------|
| GET | `/psc/role` | 列表查询（支持分页、排序、筛选） | VIEW |
| GET | `/psc/role/{id}` | 获取单个角色详情 | VIEW |
| POST | `/psc/role` | 创建新角色 | CREATE |
| PUT | `/psc/role/{id}` | 更新角色信息 | CHANGE |
| PATCH | `/psc/role/{id1,id2,...}` | 批量更新（禁用/启用） | DISABLE |
| DELETE | `/psc/role/{id1,id2,...}` | 批量删除（软删除） | DELETE |
| GET | `/psc/role/simple` | 简单列表（不含分页） | VIEW |

### 查询参数 (GET /psc/role)

```
?name=xxx            # 按名称模糊搜索
&code=xxx            # 按编码模糊搜索
&disableFlag=true    # 按禁用状态筛选
&pageNum=1           # 页码
&pageSize=10         # 每页数量
&pageSort=ID:DESC    # 排序（格式: 字段:ASC/DESC）
```

### PATCH 批量更新请求体

```json
{
  "disableFlag": true  // true=禁用, false=启用
}
```

## 业务规则

### 创建/修改规则

1. **编码唯一性**: `code` 字段全局唯一（自动生成或手动指定）
2. **名称唯一性**: `name` 字段在 `is_active=True` 范围内唯一
3. **评价配置**: `is_evaluatable` 和 `is_evaluated` 可独立配置

### 删除规则

1. **预设保护**: `is_preset=True` 的角色不可删除
2. **评价配置检查**: 存在活跃评价配置的角色不可删除
3. **软删除**: 实际操作是设置 `is_active=False`

### 批量操作规则

1. **批量数量限制**: 单次最多操作 100 条
2. **原子性**: 使用 `transaction.atomic()` 保证数据一致性
3. **部分成功**: 返回成功和失败的详细信息

## 与其他模块的关系

### 依赖关系图

```
┌─────────────────────────────────────────────────────────┐
│                    PM (项目管理模块)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  NodeList    │  │  Evaluation  │  │   Project    │  │
│  │  (节点列表)   │  │   (评价)     │  │   (项目)     │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                 │           │
└─────────┼─────────────────┼─────────────────┼───────────┘
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────┐
│              PSC (项目设置配置模块)                       │
│  ┌──────────────────────────────────────────────────┐  │
│  │            ProjectRole (项目角色)                 │  │
│  │  • is_evaluatable  • is_evaluated  • is_preset   │  │
│  └──────────────────────────────────────────────────┘  │
│          │                    │                         │
│          ▼                    ▼                         │
│  ┌──────────────┐  ┌──────────────────────────┐        │
│  │NodeDefinition│  │EvaluationConfig (评价配置) │        │
│  │  (节点定义)   │  │  • 关联角色参与评价        │        │
│  └──────────────┘  └──────────────────────────┘        │
└─────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────┐
│               SM (系统管理模块)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │    User      │  │    Role      │  │  Authority   │  │
│  │   (用户)      │  │   (角色)      │  │   (权限)     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 关联模块说明

1. **PM/NodeList**: 节点列表通过 `project_role` 字段关联角色，用于设置节点负责人
2. **PM/Evaluation**: 评价模块使用角色的 `is_evaluatable` 和 `is_evaluated` 属性
3. **PSC/NodeDefinition**: 节点定义模板中的 `project_role` 字段
4. **PSC/EvaluationConfig**: 评价配置通过 `project_role` 字段关联角色

### 数据流向

```
1. ProjectRole 创建/更新
   ↓
2. PM/NodeList 创建节点时引用 ProjectRole
   ↓
3. PM/Evaluation 进行评价时检查角色权限
   ↓
4. 评价结果基于角色的 is_special_score 属性处理
```

## 序列化器结构

### ProjectRoleSerialzer

- **用途**: 单个角色的创建、更新、详情输出
- **特殊字段映射**:
  - `disableFlag` ← `disable_flag`
  - `isEvaluatable` ← `is_evaluatable`
  - `isEvaluated` ← `is_evaluated`
- **验证**: 名称唯一性、编码唯一性、权限检查

### DeleteBatchSerializer

- **用途**: 批量删除（软删除）
- **验证**: 预设角色保护、评价配置检查
- **返回**: 删除数量和 ID 列表

### PatchBatchUpdateSerializer

- **用途**: 批量禁用/启用
- **验证**: 权限检查
- **返回**: 更新数量和 ID 列表

### SimpleListSerializer

- **用途**: 简单列表（下拉选择等场景）
- **字段**: id, name, isEvaluatable, isEvaluated, hasEvaluationConfig

### BlukUpdateToPMSSerializer

- **用途**: 同步到 PMS 系统的序列化器
- **方法**: `construct_request_data()` 构建角色数据

## 工具函数

### get_list_queryset() (apps/PSC/project_role/utils.py)

```python
def get_list_queryset(disableFlag=None):
    """
    获取项目角色列表查询集
    自动注解 has_evaluation_config 字段（检查是否存在活跃评价配置）
    """
    queryset = ProjectRole.objects.filter(is_active=True).annotate(
        has_evaluation_config=Exists(
            EvaluationConfig.objects.filter(
                project_role=OuterRef('id'),
                is_active=True
            )
        )
    )

    if disableFlag is not None:
        queryset = queryset.filter(disable_flag=disableFlag)

    return queryset
```

## 信号处理

当前信号处理器为空（signals.py），原微服务同步逻辑已移除。

```python
@receiver(post_save, sender=ProjectRole)
def project_role_post_save(sender, instance, created, **kwargs):
    """
    项目角色保存后的处理
    当前为空，预留扩展点
    """
    pass
```

## 常见业务场景

### 场景1: 创建新的项目角色

```python
# 通过 API 创建
POST /psc/role
{
  "name": "硬件工程师",
  "isEvaluatable": true,
  "isEvaluated": true
}

# 通过代码创建
from apps.PSC.project_role.models import ProjectRole

role = ProjectRole.objects.create(
    name='硬件工程师',
    is_evaluatable=True,
    is_evaluated=True,
    creator=request.user
)
```

### 场景2: 批量禁用角色

```python
# 通过 API 禁用
PATCH /psc/role/1,2,3
{
  "disableFlag": true
}

# 返回结果
{
  "msg": "success",
  "data": {
    "updated": {
      "count": 3,
      "ids": [1, 2, 3]
    }
  }
}
```

### 场景3: 获取简单列表（下拉选择）

```python
GET /psc/role/simple

# 返回
{
  "msg": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "name": "项目经理",
        "isEvaluatable": true,
        "isEvaluated": true,
        "hasEvaluationConfig": true
      }
    ],
    "total": 1
  }
}
```

### 场景4: 检查角色是否可删除

```python
from apps.PSC.project_role.models import ProjectRole

role = ProjectRole.objects.get(id=1)

# 检查是否为预设角色
if role.is_preset:
    return "该角色为预置角色，无法删除"

# 检查是否存在评价配置
if role.get_active_evaluation_config().exists():
    return "该角色存在评价配置，无法删除"
```

## 初始化命令

系统提供管理命令初始化预设角色：

```bash
python manage.py init_pm_project_role
```

**初始化内容**: 创建"项目经理"预设角色
- is_preset: True
- is_special_score: True
- is_evaluatable: True
- is_evaluated: True

## 扩展设计策略

### 当前架构优势

1. **职责单一**: 仅负责角色基础信息管理
2. **评价配置解耦**: 评价配置在独立的 EvaluationConfig 模块
3. **软删除机制**: 通过 `is_active` 字段实现软删除
4. **批量操作支持**: 支持高效的批量禁用/删除

### 未来扩展方向

1. **角色层级**: 支持角色之间的层级关系（如上级角色）
2. **角色继承**: 支持角色权限继承
3. **动态角色**: 支持项目级别的自定义角色
4. **角色模板**: 支持角色模板配置

## 演进方向 (Future Evolution)

### 短期优化

1. **缓存机制**: 对常用角色添加缓存支持
2. **操作日志**: 完善角色变更的审计日志
3. **批量操作优化**: 使用 bulk_update 提升性能

### 中期规划

1. **角色组**: 引入角色组概念，便于批量管理
2. **动态权限**: 基于角色的动态权限配置
3. **角色分析**: 角色使用情况分析报表

### 长期愿景

1. **智能推荐**: 基于项目类型智能推荐角色配置
2. **跨项目同步**: 支持角色配置在项目间同步
3. **角色生态**: 构建完整的角色权限生态体系

## 技术实现建议

### Django 最佳实践

1. **查询优化**: 使用 `select_related()` 减少 SQL 查询
2. **事务管理**: 批量操作使用 `transaction.atomic()`
3. **权限验证**: 在序列化器层进行权限验证
4. **软删除**: 使用 `is_active` 字段而非物理删除

### 性能优化

```python
# 推荐做法
queryset = ProjectRole.objects.filter(is_active=True).select_related(
    'creator', 'update_by'
)

# 避免 N+1 查询
queryset = queryset.prefetch_related('evaluation_config')
```

### 错误处理

```python
from utils.serializer.error_utils import CustomPermissionDenied

# 权限错误
if not user.has_perm(...):
    raise CustomPermissionDenied()

# 唯一性错误
if queryset.exists():
    raise serializers.ValidationError({
        'name': '该名称已被使用'
    })
```

## 模块特有名词速查

| 名词 | 说明 | 相关字段 |
|------|------|----------|
| **项目角色** | 项目管理中的角色定义 | `ProjectRole` |
| **评价权限** | 角色参与评价的权限配置 | `is_evaluatable`, `is_evaluated` |
| **预设角色** | 系统预置的受保护角色 | `is_preset` |
| **特殊分数** | 需要特殊分数处理的角色 | `is_special_score` |
| **软删除** | 通过标记删除而非物理删除 | `is_active` |
| **批量操作** | 同时操作多个角色的功能 | PATCH/DELETE 批量接口 |
| **评价配置** | 关联到角色的评价配置 | `evaluation_config` 反向关联 |
| **禁用状态** | 角色的启用/禁用状态 | `disable_flag` |
