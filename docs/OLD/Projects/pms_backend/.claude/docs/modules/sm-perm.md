# SM 权限管理模块 (sm-perm)

## 模块定位

sm-perm 是系统管理 (SM) 模块的权限管理子模块，负责三 Tab 权限配置和权限数据管理。基于 Django RBAC 模型，提供后台管理、项目管理、交付物管理三大类权限的统一管理。

**核心职责：**
- 项目权限映射（ProjectPermissionMapping）
- 交付物权限映射（DeliverablePermissionMapping）
- 后台管理权限（基于 SYSTEM_MODULE_CONFIG，无映射表）
- 统一角色权限视图 (RolePermView)

**架构说明：**
- 后台管理 Tab (ADMIN) — 直接从 SYSTEM_MODULE_CONFIG 定义的模块查询 Django Permission 表，无需映射表。角色通过 Django Group.permissions 多对多字段关联
- 项目管理 Tab (PROJECT) — 由 `init_pm_permissions` 命令初始化 ProjectPermission，通过 ProjectPermissionMapping 映射到角色
- 交付物管理 Tab (DELIVERABLE) — 每个交付物定义的查看/编辑权限，通过 DeliverablePermissionMapping 映射到角色

## 模块职责边界

### 核心功能范围

1. **项目权限映射**
   - ProjectPermissionMapping 模型（角色→项目权限的映射表）
   - 与 PM.ProjectPermission 的关联
   - 语义化权限码 (pm.edit_project_name)
   - 43 条项目权限定义

2. **交付物权限映射**
   - DeliverablePermissionMapping 模型（角色→交付物定义 + can_view/can_edit）
   - 每个交付物定义的查看/编辑权限
   - 与 PSC.DeliverableDefinition 的关联

3. **后台管理权限**
   - 直接从 SYSTEM_MODULE_CONFIG 查询 Django Permission 表
   - 通过 AdminPermSerializer 序列化
   - 按模块配置顺序排序

4. **统一角色权限查询**
   - 按 category + roleId 查询角色权限（含 granted 状态）
   - 按 category + roleId 更新角色权限
   - 自动注入 granted 状态字段

### 职责边界 (不负责)

- **不负责** 角色的增删改查（由 `sm-role` 模块负责）
- **不负责** 用户权限分配（由 `sm-user` 模块负责）
- **不负责** 权限验证逻辑（由 `PM.authority` 模块负责）
- **不负责** 路由权限控制（由框架层处理）

## 核心数据模型

### ProjectPermissionMapping 模型

项目权限映射表，角色与项目权限的多对多关系。

```python
# apps/SM/permission/models.py
class ProjectPermissionMapping(models.Model):
    """项目权限映射 -- 角色→项目权限"""
    role = models.ForeignKey(
        'SM.Role',
        on_delete=models.CASCADE,
        related_name='project_perms'
    )
    project_permission = models.ForeignKey(
        'PM.ProjectPermission',
        on_delete=models.CASCADE,
        related_name='project_permission_mappings'
    )

    class Meta:
        db_table = 'SM_permission_project_mapping'
```

### DeliverablePermissionMapping 模型

交付物权限映射表，角色对交付物定义的查看/编辑权限。

```python
# apps/SM/permission/models.py
class DeliverablePermissionMapping(models.Model):
    """交付物权限映射 -- 角色→交付物定义 + can_view/can_edit"""
    role = models.ForeignKey(
        'SM.Role',
        on_delete=models.CASCADE,
        related_name='deliverable_perms'
    )
    deliverable_definition = models.ForeignKey(
        'PSC.DeliverableDefinition',
        on_delete=models.CASCADE,
        related_name='role_deliverable_perms'
    )
    can_view = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)

    class Meta:
        db_table = 'SM_permission_deliverable_mapping'
        unique_together = [('role', 'deliverable_definition')]
```

### Perm 模型（保留）

权限通用模型，用于部分权限的辅助配置。

### 关键关系

```
ProjectPermissionMapping (项目权限映射)
  |-- role (FK) -> SM.Role
  +-- project_permission (FK) -> PM.ProjectPermission

DeliverablePermissionMapping (交付物权限映射)
  |-- role (FK) -> SM.Role
  |-- deliverable_definition (FK) -> PSC.DeliverableDefinition
  |-- can_view -> 是否可查看
  +-- can_edit -> 是否可编辑

ADMIN 权限 (无映射表)
  |-- 直接从 SYSTEM_MODULE_CONFIG 定义的全部模块查询 Django Permission 表
  +-- 角色通过 Django Group.permissions 多对多字段关联
```

## 路由设计

### 新版统一接口 (RolePermView)

```
GET    /sm/permissions/<category>/roles/<roleId>   获取角色权限（含 granted 状态）
PUT    /sm/permissions/<category>/roles/<roleId>   更新角色权限（按 category 隔离）
```

**URL 模式**: `path('/<str:category>/roles/<int:roleId>', RolePermView.as_view())`

**category 映射**:
- `PROJECT` -> 项目管理权限
- `DELIVERABLE` -> 交付物管理权限
- `ADMIN` -> 后台管理权限

### 旧版兼容接口 (PermView / DeliverablePermView)

```
GET    /sm/perm                                  获取权限列表（支持 tab_type 参数）
GET    /sm/perm_role/<int:roleId>                获取角色权限（ADMIN Tab）
PUT    /sm/perm_role/<int:roleId>                更新角色权限（支持 tab_type 参数）
GET    /sm/permissions/project                   获取项目权限列表（纯数据）
GET    /sm/permissions/deliverable               获取交付物权限列表（纯数据）
GET    /sm/permissions/admin                     获取后台管理权限列表（纯数据）
GET    /sm/permissions/enums                     获取权限枚举值
```

> 旧版接口保留用于向后兼容，新开发应优先使用 RolePermView 统一接口。

## 权限分类体系

### 后台管理 (ADMIN)

**数据源**: `SYSTEM_MODULE_CONFIG` (home/settings/module.py)，直接查询 Django Permission 表

**查询方式**: `get_admin_permissions()` 遍历 SYSTEM_MODULE_CONFIG，按 app_label + model 过滤 Permission 表

**权限分组**:
- 查询 (view_): 查看类权限
- 编辑 (add_/change_/delete_): 增删改类权限
- 业务操作 (approval_/disable_): 审核等业务操作
- 其他 (print_/can_/other_): 打印等其他权限

**数据结构**:
```
{appName: {modelName: [{group, groupLabel, list: [{..., granted}]}]}}
```

**排序**: 通过 `_get_module_sort_map()` 按 SYSTEM_MODULE_CONFIG 中模块定义的顺序排序

### 项目管理 (PROJECT)

**数据源**: `PM.ProjectPermission` 表，通过 `ProjectPermissionMapping` 映射到角色

**权限分类**:
- 项目管理 (10): 项目级操作（暂停、完成、删除、变更等）
- 节点管理 (12): 节点级操作（完成、回滚、负责人等）
- 基本信息 (15): 项目基本信息编辑（名称、描述、机型等）
- 项目结算 (6): 交付物、工时、评分等

**权限命名规范**: `pm.{action}_{resource}`

示例：
- `pm.pause_project` -- 暂停项目
- `pm.complete_node` -- 完成节点
- `pm.edit_project_name` -- 编辑项目名称

**数据结构**:
```
[{categoryId, categoryName, items: [{id, name, codename, granted}]}]
```

### 交付物管理 (DELIVERABLE)

**数据源**: `PSC.DeliverableDefinition` + `SM.DeliverablePermissionMapping`

**权限命名规范**: `psc_view_deliv_{def_id}` / `psc_edit_deliv_{def_id}`

**交互规则**:
- 勾选"编辑"时自动勾选"查看"
- 取消"查看"时自动取消"编辑"

## 视图类说明

### RolePermView (新版统一视图)

统一角色权限查询/更新视图，支持按 category 和 roleId 查询权限列表（含 granted 状态）。

**核心方法**:
- `dispatch()` -- 解析 category 和 roleId，校验 category 合法性
- `_get_role()` -- 获取角色实例，不存在返回 None
- `_get_role_perm_ids(role)` -- 获取角色拥有的权限 ID 集合（用于 granted 判断）
- `get()` -- 根据 category 分发到对应处理方法
- `_get_project(role)` -- 查询 ProjectPermission，通过 mapping 检查 granted
- `_get_deliverable(role)` -- 查询 DeliverablePermissionMapping 的 can_view/can_edit
- `_get_admin(role)` -- 查询 SYSTEM_MODULE_CONFIG 对应的 Permission，通过 AdminPermSerializer 序列化
- `put()` -- 更新角色权限（category 隔离）

### PermView (旧版视图)

权限配置视图，处理旧版接口。支持按 tab_type 过滤和更新角色权限。

### DeliverablePermView (旧版视图)

交付物权限列表视图，返回所有交付物定义及其查看/编辑权限（不含 granted 状态）。

### EnumViews

权限枚举视图，返回权限相关的枚举值。

## 与其他模块关系

### 依赖模块

| 模块 | 关系类型 | 说明 |
|------|----------|------|
| `PM.ProjectPermission` | 数据源 | PROJECT Tab 的权限定义 |
| `PSC.DeliverableDefinition` | FK | 交付物定义（DeliverablePermissionMapping） |
| `auth.Permission` | 直接查询 | Django 内置权限模型（ADMIN Tab） |
| `home.settings.module` | 配置 | SYSTEM_MODULE_CONFIG（ADMIN Tab 数据源） |
| `SM.Role` | 查询目标 | RolePermView 查询角色权限 |

### 被依赖模块

| 模块 | 关系类型 | 说明 |
|------|----------|------|
| `sm-role` | 操作目标 | 角色权限配置 |
| `PM.authority` | 数据源 | 权限验证（通过角色查询权限） |

## 常见业务场景

### 场景 1: 查询角色项目权限（含 granted 状态）

```python
# GET /sm/permissions/PROJECT/roles/1
# 查询 PM.ProjectPermission，通过 mapping 检查 granted
role = Role.objects.get(group_ptr_id=1)
permissions = ProjectPermission.objects.all()

for perm in permissions:
    granted = perm.project_permission_mappings.filter(
        role=role
    ).exists()
```

### 场景 2: 初始化项目权限

```python
# 管理命令：python manage.py init_pm_permissions --force
# 创建 ProjectPermission 定义（43 条），并创建映射

from apps.PM.management.commands.init_pm_permissions import Command
Command().handle(force=True)
```

### 场景 3: 更新角色项目权限

```python
# PUT /sm/permissions/PROJECT/roles/1
# body: {"permission": [101, 102, 103]}

role = Role.objects.get(group_ptr_id=1)

# 清除旧映射
role.project_perms.all().delete()

# 创建新映射
mappings = [
    ProjectPermissionMapping(
        role=role,
        project_permission_id=perm_id
    )
    for perm_id in [101, 102, 103]
]
ProjectPermissionMapping.objects.bulk_create(mappings)
```

### 场景 4: 更新角色 ADMIN 权限

```python
# PUT /sm/permissions/ADMIN/roles/1
# body: {"permission": [10, 20, 30]}

from apps.SM.permission.utils import get_admin_perm_ids

role = Role.objects.get(group_ptr_id=1)
all_admin_ids = get_admin_perm_ids()

# 移除旧的 ADMIN 权限
role.permissions.remove(*role.permissions.filter(id__in=all_admin_ids))

# 添加新的 ADMIN 权限
role.permissions.add(*Permission.objects.filter(id__in=[10, 20, 30]))
```

## 工具函数

### utils.py

```python
def get_admin_permissions():
    """从 SYSTEM_MODULE_CONFIG 定义的全部模块取 Permission 列表"""

def get_admin_perm_ids():
    """获取后台管理所有权限 ID 集合"""

def get_enum_group(codename):
    """根据 codename 前缀获取权限组"""
```

### AdminPermSerializer (serializers.py)

直接序列化 Django Permission 对象（非 ModelSerializer），从 codename 前缀推导 group/groupLabel，从 content_type 获取 appName/modelName。

## 管理命令

| 命令 | 说明 |
|------|------|
| `init_pm_permissions --force` | 初始化项目管理权限（ProjectPermission + ProjectPermissionMapping） |
| `init_builtin_roles --force` | 初始化内置角色，超级管理员自动获取 PROJECT + ADMIN 全部权限 |
| `sync_deliverable_perms` | 同步交付物权限（DeliverablePermission + DeliverablePermissionMapping） |

> **已删除**: `reset_permission_config` 命令已删除。ADMIN 权限不再需要预配置，直接从 SYSTEM_MODULE_CONFIG 查询。

## 开发检查清单

在修改权限模块时，请确认：

- [ ] PROJECT 权限变更是否更新了 `init_pm_permissions` 命令？
- [ ] ADMIN 权限变更是否更新了 `SYSTEM_MODULE_CONFIG` 配置？
- [ ] 是否正确处理了 ProjectPermissionMapping 的 CASCADE 删除？
- [ ] 是否正确处理了 DeliverablePermissionMapping 的 unique_together 约束？
- [ ] 是否使用了查询优化（select_related / prefetch_related）？
- [ ] RolePermView 中新增 category 时是否更新了 CATEGORY_MAP？
- [ ] 新增权限返回格式是否与前端 Tab 对齐？

## 相关文档

- **Django RBAC 文档**: https://docs.djangoproject.com/en/5.1/topics/auth/default/#permissions
- **SM 角色模块**: `modules/sm-role.md`
- **PM Authority 模块**: `modules/pm-authority.md`
- **API 文档**: `../api/sm-permission.md`

## 关键文件索引

| 文件路径 | 说明 |
|---------|------|
| `apps/SM/permission/models.py` | ProjectPermissionMapping / DeliverablePermissionMapping 模型 |
| `apps/SM/permission/views.py` | 权限 API 视图（PermView / DeliverablePermView / RolePermView / EnumViews） |
| `apps/SM/permission/serializers.py` | 权限序列化器（AdminPermSerializer / ProjectPermSerializer） |
| `apps/SM/permission/urls.py` | 路由配置（含新版 RolePermView 路由） |
| `apps/SM/permission/utils.py` | 权限查询工具函数（get_admin_permissions / get_admin_perm_ids） |
| `apps/SM/permission/enums.py` | 权限枚举定义（Choices） |
| `apps/PM/management/commands/init_pm_permissions.py` | 初始化项目权限命令 |
| `apps/SM/management/commands/init_builtin_roles.py` | 初始化内置角色命令 |
| `apps/SM/management/commands/sync_deliverable_perms.py` | 同步交付物权限命令 |
| `home/settings/module.py` | SYSTEM_MODULE_CONFIG 配置 |

## 变更记录

| 日期 | 变更内容 |
|------|----------|
| 2026-04-06 | 删除 PermissionConfig 模型，改用映射表架构；新增 ProjectPermissionMapping 和 DeliverablePermissionMapping；ADMIN 权限改为直接查询 Permission 表；删除 reset_permission_config 命令 |
| 2025-04-06 | 新增 RolePermView 统一角色权限视图，支持按 category/roleId 查询权限（含 granted 状态）和按 category 隔离更新权限；新增 URL 模式 `/<category>/roles/<roleId>`；旧版接口保留兼容 |
