# PM Authority 权限验证模块

## 模块定位

PM Authority 是项目权限验证的核心模块，负责项目/节点级别的操作权限检查。重构后从"硬编码 identity-permission 映射"改为"基于 Django Permission 的角色权限查询"。

**核心职责：**
- 项目操作权限验证（43 条语义化权限）
- 节点操作权限验证
- Identity → BUILTIN Role 映射
- 权限码映射（code → codename）

**关键变更：**
- 权限数据源：硬编码 → Django Permission
- 权限检查：identity 匹配 → 角色权限查询
- 权限标识：数字 code (1001) → 语义化 codename (pm.edit_project_name)

## 模块位置

```
pms_backend/apps/PM/authority/
├── __init__.py          # 模块导出层
├── models.py            # ProjectPermission 模型
├── enums.py             # Choices 类：权限代码和身份类型枚举
├── utils.py             # AuthorityVerifier 类：权限验证核心逻辑
└── views.py             # viewsAuthority 类：权限管理 API 视图
```

## 核心组件

### 1. ProjectPermission 模型

位置：`apps/PM/authority/models.py`

```python
class ProjectPermission(models.Model):
    """项目操作权限定义"""
    code = models.IntegerField(unique=True, verbose_name='权限代码')
    codename = models.CharField(max_length=100, unique=True, verbose_name='权限标识')
    name = models.CharField(max_length=100, verbose_name='权限名称')
    category = models.CharField(max_length=50, verbose_name='分类')
    sort = models.IntegerField(default=0, verbose_name='排序')

    class Meta:
        db_table = 'PM_project_permission'
        ordering = ['category', 'sort']
```

**权限定义：**
- 共 43 条权限（项目管理 10 + 节点管理 12 + 基本信息 15 + 项目结算 6）
- 语义化 codename：`pm.{action}_{resource}`
- 兼容旧系统的数字 code（1001-3002）

### 2. Choices（枚举类）

位置：`apps/PM/authority/enums.py`

```python
class Choices:
    class IdentityType(models.TextChoices):
        """Django TextChoices 枚举"""
        SUPERUSER = 'SUPERUSER', '超级用户'
        MANAGER = 'MANAGER', '管理者'
        CREATOR = 'CREATOR', '项目创建者'
        OWNER = 'OWNER', '项目负责人'
        FOLLOWER = 'FOLLOWER', '项目关注者'
        OWNER_NODE = 'OWNER_NODE', '节点负责人'
        ASSISTOR = 'ASSISTOR', '节点协助者'
        # ... 其他身份类型

    permission = [
        # 项目详情权限 (1001-1300)
        (1001, '项目名称', ('CREATOR', 'OWNER', 'SUPERUSER')),
        (1002, '项目描述', ('CREATOR', 'OWNER', 'SUPERUSER')),
        # ... 共 43 个权限点
    ]
```

**用途：**
- 权限定义初始化数据源
- Identity 类型枚举
- 向后兼容的权限码映射

### 3. AuthorityVerifier（权限验证类）

位置：`apps/PM/authority/utils.py`

**重构说明：**
- **旧逻辑**: 根据 identity 查询硬编码的 permission 列表
- **新逻辑**: 根据 identity 获取 BUILTIN 角色，查询角色的 Django Permission

```python
class AuthorityVerifier:
    def __init__(self, target_id: int, userinfo: UserInfo, type: str = 'project_detail'):
        """
        初始化权限验证器

        Args:
            target_id: 项目ID或节点ID
            userinfo: 用户信息字典
            type: 'project_detail' 或 'project_node'
        """

    def verify(self, code: int) -> bool:
        """验证特定权限代码（兼容旧接口）"""

    def list(self) -> Dict[int, bool]:
        """返回所有权限验证结果（兼容 H5 前端）"""

    def get_identities(self) -> List[str]:
        """获取用户当前具有的所有身份"""
```

## 重构前后对比

### 旧逻辑（硬编码）

```python
def verify(self, code: int) -> bool:
    # 1. 获取权限定义
    perm_def = self._get_permission_def(code)  # 从 Choices.permission 获取

    # 2. 检查用户 identity 是否在允许列表中
    allowed_identities = perm_def[2]  # ('CREATOR', 'OWNER', 'SUPERUSER')

    # 3. 检查用户是否具有允许的 identity
    for identity in allowed_identities:
        if self.has_identity(identity):
            return True

    return False
```

### 新逻辑（角色权限查询）

```python
def verify(self, code: int) -> bool:
    # 1. 超级用户直接通过
    if self._is_superuser:
        return True

    # 2. 将 code 映射到语义化 codename
    codename = self._code_to_codename.get(code)
    if not codename:
        # Fallback: 使用旧逻辑
        return self._verify_fallback(code)

    # 3. 获取用户的 BUILTIN 角色（基于 identity）
    builtin_roles = self._get_builtin_roles_for_identity()
    custom_roles = self._get_custom_roles()  # 全局分配的角色

    # 4. 检查任一角色是否拥有该权限
    all_roles = builtin_roles + custom_roles
    for role in all_roles:
        if role.permissions.filter(codename=codename).exists():
            return True

    return False
```

## Identity → BUILTIN Role 映射

### 映射关系

| Identity | BUILTIN Role | Role Code |
|----------|--------------|-----------|
| OWNER | 项目负责人 | PROJECT_OWNER |
| OWNER_NODE | 节点负责人 | NODE_OWNER |
| ASSISTOR | 节点协助者 | NODE_ASSISTOR |
| MANAGER | 管理者 | MANAGER |
| SUPERUSER | 系统管理员 | SUPER_ADMIN |

### 获取 BUILTIN 角色

```python
def _get_builtin_roles_for_identity(self) -> List[Role]:
    """根据用户的 identity 获取对应的 BUILTIN 角色"""
    roles = []

    if self._is_superuser:
        # 超级用户拥有所有权限，不需要查询角色
        return []

    if self._is_owner:
        roles.append(Role.objects.get(code='PROJECT_OWNER'))

    if self._is_node_owner:
        roles.append(Role.objects.get(code='NODE_OWNER'))

    if self._is_assistor:
        roles.append(Role.objects.get(code='NODE_ASSISTOR'))

    if self._is_manager:
        roles.append(Role.objects.get(code='MANAGER'))

    return roles
```

### 获取 CUSTOM 角色

```python
def _get_custom_roles(self) -> List[Role]:
    """获取用户全局分配的 CUSTOM 角色"""
    user = User.objects.get(id=self._userinfo['id'])
    return user.roles.filter(role_type='CUSTOM')
```

## 权限码映射

### Code → Codename 映射

| 旧 code | 新 codename | name | category |
|---------|-------------|------|----------|
| 1001 | `pm.edit_project_name` | 项目名称 | 基本信息 |
| 1002 | `pm.edit_project_desc` | 项目描述 | 基本信息 |
| 1006 | `pm.manage_followers` | 项目关注者 | 项目管理 |
| 1007 | `pm.add_node` | 添加节点 | 项目管理 |
| 1100 | `pm.complete_project` | 完成项目 | 项目管理 |
| 1102 | `pm.delete_project` | 删除项目 | 项目管理 |
| 2200 | `pm.complete_node` | 完成节点 | 节点管理 |
| 2201 | `pm.rollback_node` | 回滚节点 | 节点管理 |

**完整映射表：** 参见 `apps/PM/management/commands/init_pm_permissions.py`

### 映射加载机制

```python
def _load_code_mappings(self):
    """从 ProjectPermission 表动态加载映射"""
    self._code_to_codename = dict(
        ProjectPermission.objects.values_list('code', 'codename')
    )
```

## 向后兼容性

### H5 前端零改动

**兼容点：**
1. **接口签名不变**: `verify(code)` 和 `list()` 方法签名不变
2. **返回格式不变**: `list()` 仍返回 `{1001: true, 1002: false, ...}`
3. **权限码不变**: 仍使用数字 code（1001-3002）
4. **调用方式不变**: 120+ 处模板调用无需修改

**示例：**

```python
# H5 代码（无需修改）
auth = AuthorityVerifier(project_id=123, userinfo=userinfo, type='project_detail')

# 检查权限
if auth.verify(1001):  # 项目名称编辑权限
    # 显示编辑按钮
    pass

# 获取所有权限
authority = auth.list()  # {1001: True, 1002: True, 1003: False, ...}
```

### 后端代码兼容

**24 个文件中的 ~60 处 `verify()` 调用 — 无需修改**

```python
# 后端代码（无需修改）
from apps.PM.authority import permission

auth = permission(project_id=123, userinfo=userinfo, type='project_detail')
if auth.verify(1001):
    # 执行操作
    pass
```

## 权限验证流程

### project_detail 类型流程

```
1. 接收参数: target_id (项目ID), userinfo
2. 查询项目信息（Django ORM）
   - Project_List.objects.filter(id=target_id).values(...)
3. 设置身份:
   - SUPERUSER: userinfo['is_superuser'] == 1
   - CREATOR: project['creator_id'] == userinfo['id']
   - OWNER: project['owner_id'] == userinfo['id']
   - FOLLOWER: userinfo['id'] in project['followers']
4. 获取 BUILTIN 角色（基于 identity）
5. 获取 CUSTOM 角色（全局分配）
6. 验证权限: 检查角色是否拥有对应 codename
```

### project_node 类型流程

```
1. 接收参数: target_id (节点ID), userinfo
2. 查询节点信息
   - Project_Node.objects.get(pk=target_id)
3. 查询节点负责人关系
   - node_owners.filter(user_id=userinfo['id'])
4. 设置身份:
   - OWNER_NODE: is_major=True
   - ASSISTOR: is_major=False
5. 获取 BUILTIN 角色（基于 identity）
6. 获取 CUSTOM 角色（全局分配）
7. 验证权限: 检查角色是否拥有对应 codename
```

## 管理命令

### init_pm_permissions

```bash
python manage.py init_pm_permissions
```

**功能：**
- 创建 43 条 ProjectPermission 记录
- 为每条创建对应的 Django Permission
- 创建 PermissionConfig 记录（tab_type='PROJECT'）
- 为 BUILTIN 角色分配默认权限

**初始化数据：**
- 项目管理: 10 条权限
- 节点管理: 12 条权限
- 基本信息: 15 条权限
- 项目结算: 6 条权限

### init_builtin_roles

```bash
python manage.py init_builtin_roles
```

**功能：**
- 创建 4 个 BUILTIN 角色（项目负责人、节点负责人、节点协助者、管理者）
- 根据 identity-permission 映射设置默认权限
- 系统管理员角色（手动创建，拥有所有权限）

**默认权限映射：**
- 项目负责人：所有 identity 包含 `OWNER` 的权限
- 节点负责人：所有 identity 包含 `OWNER_NODE` 的权限
- 节点协助者：所有 identity 包含 `ASSISTOR` 的权限
- 管理者：所有 identity 包含 `MANAGER` 的权限

## 与其他模块关系

### 依赖模块

| 模块 | 关系类型 | 说明 |
|------|----------|------|
| `PM.Project_List` | FK | 项目列表（查询项目信息） |
| `PM.Project_Node` | FK | 项目节点（查询节点信息） |
| `SM.Role` | Query | 角色权限查询 |
| `SM.User` | FK | 用户信息 |
| `auth.Permission` | M2M | Django 权限系统 |

### 被依赖模块

| 模块 | 关系类型 | 说明 |
|------|----------|------|
| `PM.*` (24 个文件) | 调用 | 权限验证 |
| `H5 前端` | API | 项目/节点详情 authority 字段 |

## 性能优化

### 查询优化

```python
# ✅ 正确：使用 select_related 减少查询
project = Project_List.objects.select_related('creator', 'owner').get(pk=target_id)

# ✅ 正确：使用 prefetch_related 处理 M2M
roles = user.roles.prefetch_related('permissions').all()

# ✅ 正确：缓存权限映射
self._code_to_codename = self._load_code_mappings()  # 只加载一次
```

### 缓存策略

```python
# 权限映射缓存（类级别）
_code_to_codename_cache = None

def _load_code_mappings(self):
    if AuthorityVerifier._code_to_codename_cache is None:
        AuthorityVerifier._code_to_codename_cache = dict(
            ProjectPermission.objects.values_list('code', 'codename')
        )
    return AuthorityVerifier._code_to_codename_cache
```

## 开发注意事项

1. **权限检查位置**：在视图或序列化器中进行权限检查，不要在前端依赖
2. **用户信息获取**：使用 `UserHelper.setup_request_userinfo(request)` 获取用户信息
3. **错误处理**：项目或节点不存在时会抛出 `ValueError`
4. **向后兼容**：保持 `verify(code)` 和 `list()` 接口签名不变
5. **权限初始化**：新建环境必须运行 `init_pm_permissions` 和 `init_builtin_roles`

## 关键文件索引

| 文件路径 | 说明 |
|---------|------|
| `apps/PM/authority/models.py` | ProjectPermission 模型 |
| `apps/PM/authority/enums.py` | Choices 枚举类 |
| `apps/PM/authority/utils.py` | AuthorityVerifier 类 |
| `apps/PM/authority/views.py` | viewsAuthority 类 |
| `apps/PM/management/commands/init_pm_permissions.py` | 初始化项目权限 |
| `apps/SM/management/commands/init_builtin_roles.py` | 初始化内置角色 |

## 常见问题

### Q: 为什么要重构 AuthorityVerifier？
A: 旧系统使用硬编码的 identity-permission 映射，难以维护。新系统使用 Django Permission + 角色，统一了权限管理，更灵活易维护。

### Q: H5 前端需要修改吗？
A: 不需要。AuthorityVerifier 的接口签名和返回格式保持不变，H5 代码零改动。

### Q: 如何添加新的项目权限？
A: 在 `apps/PM/management/commands/init_pm_permissions.py` 中添加新的权限定义，然后运行 `python manage.py init_pm_permissions`。

### Q: code 和 codename 的关系？
A: code 是旧系统的数字标识（1001-3002），codename 是新系统的语义化标识（pm.edit_project_name）。两者通过 ProjectPermission 表映射。

### Q: 如何调试权限问题？
A: 使用 `auth.get_identities()` 查看用户当前具有的所有身份，使用 `auth.list()` 查看所有权限验证结果。

## 更新日志

- 2025-04-03：重大重构
  - 权限数据源：硬编码 → Django Permission
  - 权限检查：identity 匹配 → 角色权限查询
  - 新增 ProjectPermission 模型（43 条语义化权限）
  - 新增 code → codename 映射机制
  - 新增 Identity → BUILTIN Role 映射
  - 向后兼容：H5 零改动
- 2024-XX-XX：初始版本，硬编码 identity-permission 映射
