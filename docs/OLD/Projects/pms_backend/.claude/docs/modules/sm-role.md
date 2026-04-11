# SM 角色管理模块 (sm-role)

## 模块定位

sm-role 是系统管理 (SM) 模块的核心子模块，负责基于 Django RBAC 的角色管理。它继承自 Django 的 `Group` 模型，是连接用户与权限的桥梁，支持细粒度的访问控制。

## 关键术语速查

| 术语 | 定位 | 快速定位 |
|------|------|----------|
| `Role` | 核心模型，继承自 `django.contrib.auth.models.Group` | `apps/SM/role/models.py:9` |
| `role_type` | 角色类型：BUILTIN（内置）/ CUSTOM（自定义） | `apps/SM/role/models.py:18` |
| `code` | 角色编码，自动生成 (ROL + 数字) | `apps/SM/role/models.py:11` |
| `name` | 角色名称，继承自 Group.name，必须唯一 | `apps/SM/role/models.py:Group` |
| `disable_flag` | 禁用状态，软删除机制 | `apps/SM/role/models.py:13` |
| `permissions` | 多对多关联，Django Permission 系统 | `apps/SM/role/models.py:Group.permissions` |
| `user_set` | 反向关联，拥有该角色的用户集合 | `apps/SM/role/models.py:Group.user_set` |

## 模块职责边界

### 核心职责

1. **角色生命周期管理**
   - 角色创建 (自动生成编码)
   - 角色更新 (完整/部分)
   - 角色删除 (软删除 + 关联检查)
   - 角色查询 (详情/列表/simple)

2. **权限管理集成**
   - 与 Django Permission 系统的 M2M 关联
   - 通过 `permissions` 字段管理权限集合
   - 配合 `SM.permission` 模块进行权限分配

3. **数据完整性保障**
   - `code` 全局唯一性校验
   - `name` (继承自 Group) 全局唯一性校验
   - 删除前检查用户关联 (`user_set.exists()`)

### 职责边界 (不负责)

- **不负责** 用户认证 (由 `SM.auth` 模块负责)
- **不负责** 用户管理 (由 `SM.user` 模块负责)
- **不负责** 权限定义 (由 `SM.permission` 模块负责)
- **不负责** 权限验证中间件 (由框架层处理)

## 核心数据模型

```python
# apps/SM/role/models.py:9
class Role(Group):
    """角色管理模型（继承 Django Group）"""
    code = models.CharField(max_length=255, default='', unique=True)
    role_type = models.CharField(
        max_length=10,
        choices=[('BUILTIN', '内置流程角色'), ('CUSTOM', '自定义角色')],
        default='CUSTOM',
        verbose_name='角色类型'
    )
    remark = models.CharField(max_length=255, default='')
    disable_flag = models.BooleanField(default=False)

    # 审计字段
    creator = models.ForeignKey('SM.User', ...)
    updated_by = models.ForeignKey('SM.User', ...)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### 继承的 Django Group 字段

- `id`: 主键 (继承)
- `name`: 角色名称，全局唯一 (继承)
- `permissions`: M2M 到 Django Permission (继承)

### 角色类型说明

**BUILTIN（内置流程角色）：**
- 系统预设的角色，由管理命令初始化
- 包含：项目负责人 (PROJECT_OWNER)、节点负责人 (NODE_OWNER)、节点协助者 (NODE_ASSISTOR)、管理者 (MANAGER)
- 约束：不可删除、不可修改名称、不允许修改后台管理权限
- 用途：项目/节点级别的权限控制

**CUSTOM（自定义角色）：**
- 用户创建的角色
- 约束：可删除（需先解除用户关联）
- 用途：全局权限分配

### 关键关系

```
Role (角色)
  ├── permissions (M2M) → Django Permission
  ├── user_set (反向 M2M) → User
  ├── creator (FK) → User
  └── updated_by (FK) → User
```

## 路由设计

```
GET    /sm/roles/perm-tree   角色树（权限配置页专用）
GET    /sm/role/enums        枚举数据
GET    /sm/role/simple       简化列表 (id, code, name, roleType)
GET    /sm/role/list         列表查询 (分页)
POST   /sm/role/list         创建角色
PATCH  /sm/role/list         批量部分更新
DELETE /sm/role/list         批量删除
GET    /sm/role/<id>         详情查询
PUT    /sm/role/<id>         完整更新
```

### Simple 列表接口

**端点**: `GET /sm/role/simple`

**用途**: 下拉选择框等场景，返回全部角色

**返回格式**:
```json
{
    "msg": "success",
    "data": {
        "items": [
            {"id": 1, "code": "ROL001", "name": "管理员", "roleType": "CUSTOM"}
        ],
        "total": 1
    }
}
```

### 权限配置页角色树接口

**端点**: `GET /sm/roles/perm-tree`

**用途**: 权限配置页左侧角色树，返回按类型分组的角色列表（排除系统管理员）

**返回格式**:
```json
{
    "msg": "success",
    "data": {
        "builtin": [
            {"id": 1, "code": "PROJECT_OWNER", "name": "项目负责人", "roleType": "BUILTIN"},
            {"id": 2, "code": "NODE_OWNER", "name": "节点负责人", "roleType": "BUILTIN"},
            {"id": 3, "code": "NODE_ASSISTOR", "name": "节点协助者", "roleType": "BUILTIN"},
            {"id": 4, "code": "MANAGER", "name": "管理者", "roleType": "BUILTIN"}
        ],
        "custom": [
            {"id": 5, "code": "ROL00005", "name": "软件组", "roleType": "CUSTOM"}
        ]
    }
}
```

**说明：**
- `builtin`: 内置流程角色（BUILTIN 类型）
- `custom`: 自定义角色（CUSTOM 类型）
- 系统管理员角色 (SUPER_ADMIN) 不在列表中返回

## 权限验证流程

### 自定义权限定义

```python
# apps/SM/role/enums.py:19-34
class Permissions:
    class OperationTypes(models.TextChoices):
        CREATE = 'CREATE', '创建'
        VIEW = 'VIEW', '查看'
        CHANGE = 'CHANGE', '修改'
        DELETE = 'DELETE', '删除'
        DISABLE = 'DISABLE', '禁用'

    DJANGO_CODENAME_MAP = {
        'CREATE': 'add_role',
        'VIEW': 'view_role',
        'CHANGE': 'change_role',
        'DELETE': 'delete_role',
        'DISABLE': 'disable_role'  # 自定义权限
    }
```

### 权限验证方法

```python
# 获取权限 codename 用于验证
codename = Permissions.get_permission_verify_codename('VIEW')
# 返回: 'SM.view_role'

# 在视图中验证
request.user.has_perm(codename)
```

## 与其他模块关系

### 依赖模块

| 模块 | 关系类型 | 说明 |
|------|----------|------|
| `SM.user` | M2M 反向 | 通过 `Role.user_set` 访问拥有该角色的用户 |
| `SM.permission` | M2M | 通过 `Role.permissions` 管理 Django Permission |
| `SM.code` | 工具 | 使用 `get_unique_code('ROL', Role)` 生成编码 |

### 被依赖模块

| 模块 | 关系类型 | 说明 |
|------|----------|------|
| `SM.user` | FK/M2M | 用户模型中的 `roles` 字段关联角色 |
| `SM.permission` | 操作目标 | 权限分配接口 `/permissions/role/<id>` |
| `PM.*` / `PSC.*` / `BDM.*` | RBAC 基础 | 各业务模块通过角色控制访问 |

## 常见业务场景

### 场景 1: 创建角色并分配权限

```python
# 1. 创建角色
role = Role.objects.create(
    code='ROL001',
    name='项目经理',
    role_type='CUSTOM',  # 强制设置为 CUSTOM
    creator=request.user
)

# 2. 分配权限
from django.contrib.auth.models import Permission
permissions = Permission.objects.filter(codename__in=['add_project', 'change_project'])
role.permissions.set(permissions)
```

### 场景 2: 获取角色的所有用户

```python
role = Role.objects.get(code='ROL001')
users = role.user_set.all()  # 反向查询
user_count = role.user_set.count()  # 统计用户数量
```

### 场景 3: 删除前检查关联

```python
# 删除前必须检查是否有用户使用该角色
if role.user_set.exists():
    raise ValidationError('角色被用户使用，请先解除关联')

# BUILTIN 角色不允许删除
if role.role_type == 'BUILTIN':
    raise ValidationError('内置角色不允许删除')
```

### 场景 4: Simple 列表用于下拉选择

```python
# 前端下拉选择框场景
GET /sm/role/simple
# 返回所有角色的 id, code, name, roleType，无分页
```

### 场景 5: 权限配置页角色树

```python
# 权限配置页左侧角色树
GET /sm/roles/perm-tree
# 返回按类型分组的角色列表（builtin/custom）
# 用于权限配置页面的角色选择
```

### 场景 6: BUILTIN 角色约束

```python
# BUILTIN 角色不允许修改后台管理权限
if role.role_type == 'BUILTIN' and tab_type == 'ADMIN':
    raise PermissionDenied('内置角色不允许修改后台管理权限')

# BUILTIN 角色不允许删除
if role.role_type == 'BUILTIN':
    raise PermissionDenied('内置角色不允许删除')
```

## 技术实现建议 (Django)

### 1. 模型继承

```python
# ✅ 正确：继承 Group
class Role(Group):
    code = models.CharField(max_length=255, default='', unique=True)

# ❌ 错误：直接继承 models.Model
class Role(models.Model):
    group = models.OneToOneField(Group, ...)  # 不要这样做
```

### 2. 唯一性验证

```python
# code 唯一性
queryset = Role.objects.filter(code=code)
if self.instance:
    queryset = queryset.exclude(id=self.instance.id)

# name 唯一性 (继承自 Group，需要特殊处理)
from django.contrib.auth.models import Group
queryset = Group.objects.filter(name=name)
if self.instance:
    queryset = queryset.exclude(pk=self.instance.group_ptr.pk)
```

### 3. 懒加载权限字段

```python
class LazyPermissionPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        return Permission.objects.all()

# 使用
permissions = LazyPermissionPrimaryKeyRelatedField(many=True, write_only=True)
```

### 4. 查询优化

```python
# ✅ 正确：使用 select_related 减少查询
roles = Role.objects.select_related('creator', 'updated_by').all()

# ✅ 正确：使用 prefetch_related 处理 M2M
roles = Role.objects.prefetch_related('permissions').all()
```

## 扩展设计策略

### 1. 角色层级 (未来扩展)

```python
class Role(Group):
    parent = models.ForeignKey('self', null=True, blank=True, ...)
    # 支持角色继承
```

### 2. 数据权限 (未来扩展)

```python
class RoleDataRule(models.Model):
    role = models.ForeignKey(Role, ...)
    model = models.CharField(...)  # 限制的模型
    scope = models.CharField(...)  # all/department/self
```

### 3. 角色模板 (未来扩展)

```python
class RoleTemplate(models.Model):
    name = models.CharField(...)
    permissions = models.ManyToManyField(Permission)
    # 从模板创建角色
```

## 演进方向 (Future Evolution)

### 短期 (1-3 个月)

1. **性能优化**
   - 添加 `simple` 接口缓存 (Redis)
   - 列表查询优化 (索引)

2. **功能增强**
   - 角色复制功能
   - 角色导出/导入

### 中期 (3-6 个月)

1. **权限增强**
   - 支持数据权限 (行级)
   - 支持字段权限 (列级)

2. **角色管理**
   - 角色层级/继承
   - 角色生命周期状态机

### 长期 (6-12 个月)

1. **动态权限**
   - 基于规则的权限 (ABAC)
   - 临时权限/时效权限

2. **权限可视化**
   - 角色权限关系图
   - 权限影响分析

## 开发检查清单

在修改角色模块时，请确认：

- [ ] 是否检查了 `name` (Group 字段) 的唯一性？
- [ ] 是否检查了 `code` 的唯一性？
- [ ] 是否正确设置了 `role_type`？
- [ ] 创建角色时是否强制 `role_type='CUSTOM'`？
- [ ] 删除前是否检查了 `user_set.exists()`？
- [ ] 删除前是否检查了 `role_type == 'BUILTIN'`？
- [ ] 是否正确处理了 `permissions` M2M 关系？
- [ ] 是否使用了 `get_unique_code('ROL', Role)` 生成编码？
- [ ] 是否更新了审计字段 (`creator`, `updated_by`)？
- [ ] 序列化器是否正确处理了继承自 Group 的字段？
- [ ] BUILTIN 角色修改时是否检查了 `tab_type`（不允许修改 ADMIN Tab）？

## 相关文档

- **Django RBAC 文档**: https://docs.djangoproject.com/en/5.1/topics/auth/default/#permissions
- **SM 模块架构**: `.claude/skills/sms-architecture`
- **SM 用户模块**: `.claude/skills/sm-user`
- **SM 权限模块**: `apps/SM/permission/`
