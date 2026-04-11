# 权限管理命令文档

## 概述

本文档记录了 PMS 系统中与权限管理相关的 Django 管理命令，用于初始化、同步和重置权限数据。

---

## 命令列表

### 1. init_pm_permissions

**路径：** `apps/PM/management/commands/init_pm_permissions.py`

**功能：** 初始化项目管理权限

**说明：**
- 创建 43 条 ProjectPermission 记录
- 为每条创建对应的 Django Permission
- 创建 PermissionConfig 记录（tab_type='PROJECT'）
- 为 BUILTIN 角色分配默认权限

**权限分类：**
- 项目管理（10 条）：暂停项目、完成项目、删除项目、变更项目等
- 节点管理（12 条）：完成节点、回滚节点、负责人编辑、工时编辑等
- 基本信息（15 条）：项目名称、项目描述、机型信息、优先级等
- 项目结算（6 条）：交付物创建、交付物删除、工时编辑、评分等

**权限命名规范：** `pm.{action}_{resource}`

**使用方法：**
```bash
python manage.py init_pm_permissions
```

**输出示例：**
```
完成: 新建 43 条 PM 权限
- 项目管理: 10 条
- 节点管理: 12 条
- 基本信息: 15 条
- 项目结算: 6 条
```

**注意事项：**
- 重复运行会跳过已存在的权限（使用 `get_or_create`）
- 如需强制重新创建，需先手动删除 ProjectPermission 表中的数据
- 初始化后建议运行 `init_builtin_roles` 为 BUILTIN 角色分配权限

---

### 2. sync_deliverable_perms

**路径：** `apps/SM/management/commands/sync_deliverable_perms.py`

**功能：** 同步交付物权限

**说明：**
- 遍历所有 PSC.DeliverableDefinition（交付物定义）
- 为每个交付物定义创建/更新 DeliverablePermission
- 创建对应的查看/编辑 Django Permission
- 创建对应的 PermissionConfig 记录（tab_type='DELIVERABLE'）

**权限命名规范：** `psc_view_deliv_{def_id}` / `psc_edit_deliv_{def_id}`

**使用方法：**
```bash
python manage.py sync_deliverable_perms
```

**输出示例：**
```
完成: 新建 5 条, 跳过 3 条（已存在）
```

**注意事项：**
- 重复运行会跳过已存在的权限（使用 `get_or_create`）
- 如需强制重新创建，使用 `--force` 参数：`python manage.py sync_deliverable_perms --force`
- 交付物定义被删除时，通过 CASCADE 自动清理对应的权限

---

### 3. init_builtin_roles

**路径：** `apps/SM/management/commands/init_builtin_roles.py`

**功能：** 初始化内置角色

**说明：**
- 创建 4 个 BUILTIN 角色（项目负责人、节点负责人、节点协助者、管理者）
- 根据 identity-permission 映射设置默认权限
- 系统管理员角色需手动创建（拥有所有权限）

**内置角色列表：**
| 编码 | 名称 | roleType | 说明 |
|------|------|----------|------|
| PROJECT_OWNER | 项目负责人 | BUILTIN | 项目所有者 |
| NODE_OWNER | 节点负责人 | BUILTIN | 节点主要负责人 |
| NODE_ASSISTOR | 节点协助者 | BUILTIN | 节点协助负责人 |
| MANAGER | 管理者 | BUILTIN | 部门管理者 |
| SUPER_ADMIN | 系统管理员 | BUILTIN | 系统管理员（手动创建） |

**默认权限映射：**
- 项目负责人：所有 identity 包含 `OWNER` 的权限
- 节点负责人：所有 identity 包含 `OWNER_NODE` 的权限
- 节点协助者：所有 identity 包含 `ASSISTOR` 的权限
- 管理者：所有 identity 包含 `MANAGER` 的权限

**使用方法：**
```bash
python manage.py init_builtin_roles
```

**输出示例：**
```
完成: 创建 4 个 BUILTIN 角色
- 项目负责人: 18 条权限
- 节点负责人: 12 条权限
- 节点协助者: 8 条权限
- 管理者: 5 条权限
```

**注意事项：**
- 重复运行会跳过已存在的角色（使用 `get_or_create`）
- 角色权限会重新分配（清除后重新添加）
- 系统管理员角色需要手动创建并分配所有权限

---

### 4. reset_permission_config

**路径：** `apps/SM/management/commands/reset_permission_config.py`

**功能：** 重置权限配置（后台管理 Tab）

**说明：**
- 遍历 SYSTEM_MODULE_CONFIG（home/settings/module.py）
- 为每个模块的 Django Permission 创建 PermissionConfig（tab_type='ADMIN'）
- 根据 codename 前缀自动设置 group（查询/编辑/业务操作/其他）

**权限分组规则：**
| 前缀 | 分组 | 说明 |
|------|------|------|
| view_ | 查询 | 查看类权限 |
| add_ | 编辑 | 新增权限 |
| delete_ | 编辑 | 删除权限 |
| change_ | 编辑 | 修改权限 |
| approval_ | 业务操作 | 审核权限 |
| disable_ | 业务操作 | 禁用权限 |
| print_ | 其他 | 打印权限 |
| can_ | 其他 | 允许权限 |
| other_ | 其他 | 其他权限 |

**使用方法：**
```bash
python manage.py reset_permission_config
```

**输出示例：**
```
完成: 新建 150 条 PermissionConfig
- 查询: 30 条
- 编辑: 80 条
- 业务操作: 25 条
- 其他: 15 条
```

**注意事项：**
- 重复运行会跳过已存在的配置（使用 `get_or_create`）
- 如需强制重新创建，使用 `--force` 参数：`python manage.py reset_permission_config --force`
- 此命令替换了旧版的 `reset_sm_permission` 命令

---

## CI/CD 集成

### 部署流程中的权限命令

**测试环境 (.gitea/workflows/deploy_test.yaml)：**
```yaml
- name: 初始化路由模块, 权限模块
  run: |
    cd /home/pms-test/backend/
    source .venv/bin/activate
    DJANGO_ENVIRONMENT=test python manage.py reset_sm_route
    DJANGO_ENVIRONMENT=test python manage.py reset_permission_config
```

**生产环境 (.gitea/workflows/deploy_prod.yaml)：**
```yaml
- name: 初始化路由模块, 权限模块
  run: |
    cd /home/pms/backend/
    source .venv/bin/activate
    python manage.py reset_sm_route
    python manage.py reset_permission_config
```

**开发环境 (.gitea/workflows/deploy_develop.yaml)：**
```yaml
- name: 初始化路由模块, 权限模块, 评审模板
  run: |
    cd /home/PMS/backend/
    source .venv/bin/activate
    python manage.py reset_sm_route
    python manage.py reset_permission_config
```

---

## 初始化顺序

**全新环境初始化时，请按以下顺序执行：**

```bash
# 1. 数据库迁移
python manage.py migrate

# 2. 初始化项目管理权限
python manage.py init_pm_permissions

# 3. 同步交付物权限
python manage.py sync_deliverable_perms

# 4. 初始化内置角色
python manage.py init_builtin_roles

# 5. 重置权限配置（后台管理 Tab）
python manage.py reset_permission_config

# 6. 创建系统管理员角色（手动）
python manage.py createsuperuser
# 或在后端管理界面创建 SUPER_ADMIN 角色并分配所有权限
```

---

## 常见问题

### Q: 如何强制重新创建所有权限？
A: 使用对应命令的 `--force` 参数（如果支持），或手动清空相关表后重新运行命令。

### Q: 权限初始化后需要重启服务吗？
A: 不需要。权限数据存储在数据库中，服务会实时读取。

### Q: 如何验证权限是否初始化成功？
A: 检查对应表的数据：
- `PM_project_permission`: 应有 43 条记录
- `SM_deliverable_permission`: 应与交付物定义数量一致
- `SM_permission_config`: 应包含所有权限配置
- `SM_role` (role_type='BUILTIN'): 应有 4 条记录

### Q: 交付物定义新增后如何同步权限？
A: 重新运行 `python manage.py sync_deliverable_perms`。

### Q: 如何查看 BUILTIN 角色的权限？
A: 在管理后台的权限配置页面，选择对应的 BUILTIN 角色，查看各 Tab 下的权限。

### Q: 系统管理员角色如何创建？
A: 系统管理员角色需要手动创建，创建时设置 role_type='BUILTIN'，code='SUPER_ADMIN'，并分配所有权限。

---

## 相关文档

- **SM 权限 API 文档**: `backend/.claude/docs/api/sm-permission.md`
- **SM 角色模块文档**: `backend/.claude/docs/modules/sm-role.md`
- **PM Authority 模块文档**: `backend/.claude/docs/modules/pm-authority.md`
- **权限配置页文档**: `frontend-admin/.claude/docs/modules/sm-perm.md`

---

## 更新日志

- 2025-04-03：初始版本
  - 新增 `init_pm_permissions` 命令
  - 新增 `sync_deliverable_perms` 命令
  - 新增 `init_builtin_roles` 命令
  - 新增 `reset_permission_config` 命令
  - 移除 `reset_sm_permission` 命令（替换为 reset_permission_config）
