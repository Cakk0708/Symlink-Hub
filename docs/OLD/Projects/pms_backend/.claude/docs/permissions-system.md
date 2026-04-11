# 权限系统重构说明

> 最后更新：2026-04-06

## 重构概述

本次重构将后端所有模型的 `default_permissions` 统一设置为空，并使用自定义权限枚举定义来管理权限，解决了权限 codename 无序的问题。

## 重构内容

### 1. 模型权限修改

所有模型的 Meta 类都进行了如下修改：

```python
# 修改前
default_permissions = ('view', 'change', 'delete', 'add')

# 修改后
default_permissions = ()
permissions = [
    enumPermissions.get_permission_key('CREATE'),
    enumPermissions.get_permission_key('VIEW'),
    enumPermissions.get_permission_key('CHANGE'),
    enumPermissions.get_permission_key('DELETE')
]
```

### 2. 权限枚举结构

每个模型模块的 `enums.py` 文件都包含统一的权限定义结构：

```python
class Permissions:
    """权限枚举"""

    class OperationTypes(models.TextChoices):
        """操作类型"""
        CREATE = 'CREATE', '创建'
        VIEW = 'VIEW', '查看'
        CHANGE = 'CHANGE', '修改'
        DELETE = 'DELETE', '删除'
        # 可根据业务需要添加其他操作类型

    DJANGO_CODENAME_MAP = {
        'CREATE': 'add_modelname',
        'VIEW': 'view_modelname',
        'CHANGE': 'change_modelname',
        'DELETE': 'delete_modelname',
    }

    @classmethod
    def get_permission_key(cls, op_value: str) -> tuple:
        """获取权限 key 与 label"""
        member = cls.OperationTypes[op_value]
        return cls.DJANGO_CODENAME_MAP.get(op_value), member.label

    @classmethod
    def get_permission_verify_codename(cls, op_value: str) -> str:
        """获取用于验证的权限 codename"""
        return f'{app_label}.{cls.DJANGO_CODENAME_MAP.get(op_value)}'

    @classmethod
    def get_choices_permissions(cls):
        """获取权限选项列表"""
        return [
            {
                'value': value,
                'label': label,
                'key': f'{app_label}.{cls.DJANGO_CODENAME_MAP[value]}'
            }
            for value, label in cls.OperationTypes.choices
        ]
```

### 3. 涉及的模型

#### SM 模块（系统管理）
- User - 用户管理
- Role - 角色管理
- VersionControl - 版本控制
- Perm - 权限管理
- PermissionConfig - 权限配置
- Route - 路由管理
- 各种审批流程和消息模板模型

#### PSC 模块（项目系统配置）
- ProjectTemplate - 项目模板
- NodeDefinition - 节点定义
- DeliverableDefinition - 交付物定义
- ReviewDefinition - 审核定义
- EventDefinition - 事件定义
- 各种配置和定义模型

#### BDM 模块（业务数据管理）
- Customer - 客户
- Department - 部门
- Staff - 员工

#### PM 模块（项目管理）
- 已使用空权限，无需修改

#### API 模块（API模型）
- APIToken - API令牌（已使用空权限）

### 4. 数据库迁移

生成了以下迁移文件：
- `BDM.0008_update_permissions_for_all_models.py`
- `PSC.0036_update_permissions_for_all_models.py`
- `SM.0013_update_permissions_for_all_models.py`

### 5. 权限验证使用示例

```python
# 在视图中使用权限验证
from apps.SM.user.enums import Permissions

# 检查用户是否有查看用户的权限
has_permission = user.has_perm(Permissions.get_permission_verify_codename('VIEW'))

# 获取所有权限选项
permission_choices = Permissions.get_choices_permissions()
```

## 重构优势

1. **统一性**：所有模型使用相同的权限定义模式
2. **可扩展性**：可以轻松添加新的操作类型
3. **可维护性**：权限定义集中管理，便于维护
4. **一致性**：权限 codename 格式统一，避免混乱

## 注意事项

1. 所有权限验证代码需要更新为使用新的权限枚举类
2. 权限 codename 格式为 `{app_label}.{action}_{modelname}`
3. 添加新的操作类型时，需要在 `OperationTypes` 和 `DJANGO_CODENAME_MAP` 中同时定义