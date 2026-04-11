# BDM 部门管理模块 (bdm-department)

## 模块定位

BDM（Business Data Management）部门管理模块位于 `apps/BDM/department/`，负责系统中部门信息的管理以及用户与部门的关联关系。

### 在 BDM 模块中的位置

```
BDM 模块架构
├── customer/          # 客户管理
├── customer_model/    # 客户机型管理
├── department/        # 部门管理 ← 当前模块
│   ├── models.py      # Department, UserDepartment 模型
│   ├── serializers.py # 部门序列化器
│   ├── views.py       # 部门视图
│   └── urls.py        # 部门路由
├── staff/             # 员工管理
└── version_control/   # 版本控制
```


## 模块职责边界

### 核心职责

1. **部门信息管理**：部门的 CRUD 操作
2. **用户部门关联** 🆕：用户与部门的多对多关系管理（Since 2026-03-07）
3. **飞书部门同步** 🆕：自动从飞书同步部门信息（Since 2026-03-07）
4. **部门层级管理**：支持上级部门关系

### 不负责的内容

- ❌ 部门详情的数据验证由业务层处理
- ❌ 用户信息的直接管理由 SM 模块负责
- ❌ 飞书 API 调用由 `FeishuUserManager` 负责


## 核心数据模型

### 1. Department 模型

部门基础信息表，存储部门的基本属性和层级关系。

```python
class Department(models.Model):
    code = models.CharField(max_length=255, unique=True)    # 部门编码（存储飞书 open_department_id）
    name = models.CharField(max_length=255, unique=True)    # 部门名称
    disable_flag = models.BooleanField(default=False)       # 禁用状态
    remark = models.CharField(max_length=255)               # 备注

    # 层级关系
    parent = models.ForeignKey('self', ...)                 # 上级部门
    owner = models.ForeignKey('BDM.Staff', ...)             # 部门负责人

    # 审计字段
    creator = models.ForeignKey('SM.User', ...)             # 创建人
    updated_by = models.ForeignKey('SM.User', ...)          # 最后修改人
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**字段说明**：

| 字段 | 类型 | 说明 |
|-----|------|------|
| `code` | CharField | 部门编码，用于存储飞书的 `open_department_id`，全局唯一 |
| `name` | CharField | 部门名称，全局唯一 |
| `parent` | ForeignKey | 上级部门，支持部门层级结构 |
| `owner` | ForeignKey | 部门负责人，关联到 Staff 模型 |

### 2. UserDepartment 模型 🆕

用户与部门的多对多关系表，用于关联 User 和 Department。

```python
class UserDepartment(models.Model):
    user = models.ForeignKey('SM.User', ...)               # 用户
    department = models.ForeignKey('BDM.Department', ...)   # 部门
    feishu_department_id = models.CharField(...)            # 飞书部门ID
    is_leader = models.BooleanField(default=False)          # 是否为部门负责人
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'BDM_user_department'
        unique_together = [['user', 'department']]         # 联合唯一约束
```

**字段说明**：

| 字段 | 类型 | 说明 |
|-----|------|------|
| `user` | ForeignKey | 关联到 SM.User |
| `department` | ForeignKey | 关联到 BDM.Department |
| `feishu_department_id` | CharField | 存储飞书的 `open_department_id`，用于快速查询 |
| `is_leader` | BooleanField | 标识用户是否为该部门的负责人 |

**关系说明**：

- 通过 `user.user_departments` 可以获取用户的所有部门关联
- 通过 `department.department_users` 可以获取部门的所有用户关联
- `unique_together` 约束确保同一用户与同一部门只有一条关联记录


## 飞书部门同步机制 🆕

### 触发时机

```
飞书用户登录
    ↓
UserFeishu 模型创建/更新
    ↓
post_save 信号触发
    ↓
sync_user_departments 异步任务
    ↓
FeishuUserManager.get_user_departments()
    ↓
创建/更新 Department 记录
    ↓
创建 UserDepartment 关联
```

### 同步逻辑

```python
# apps/SM/user/tasks.py

def _sync_departments_and_create_relations(user, departments):
    """
    将飞书部门同步到 BDM.Department 表并创建关联关系

    Args:
        user: User 实例
        departments: 部门信息列表 [{'id': 'od_xxx', 'name': '部门名称'}, ...]
    """
    # 获取用户现有的部门关联
    existing_relations = UserDepartment.objects.filter(user=user).values_list(
        'feishu_department_id', flat=True
    )

    for dept_info in departments:
        dept_id = dept_info['id']      # 飞书 open_department_id
        dept_name = dept_info['name']

        # 1. 检查部门是否存在（通过 code 字段匹配飞书部门 ID）
        department = Department.objects.filter(code=dept_id).first()

        if not department:
            # 2. 创建新部门
            department = Department.objects.create(
                code=dept_id,
                name=dept_name,
                disable_flag=False,
                remark=f'从飞书自动同步，飞书部门 ID: {dept_id}'
            )
        elif department.name != dept_name:
            # 3. 更新部门名称（如果飞书部门名称发生变化）
            department.name = dept_name
            department.save(update_fields=['name'])

        # 4. 创建用户与部门的关联（如果不存在）
        if dept_id not in existing_relations:
            UserDepartment.objects.create(
                user=user,
                department=department,
                feishu_department_id=dept_id,
                is_leader=False
            )
```

### 同步规则

| 场景 | 处理方式 |
|-----|---------|
| 部门不存在 | 自动创建部门，`code` 存储飞书 `open_department_id` |
| 部门名称变化 | 更新 `Department.name` 字段 |
| 用户部门关联不存在 | 创建 `UserDepartment` 记录 |
| 用户部门关联已存在 | 跳过，不做处理 |


## 数据库表结构

### BDM_department 表

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|------|------|
| `id` | INT | PK | 主键 |
| `code` | VARCHAR(255) | UNIQUE | 部门编码（飞书部门ID） |
| `name` | VARCHAR(255) | UNIQUE | 部门名称 |
| `disable_flag` | BOOLEAN | | 禁用状态 |
| `remark` | VARCHAR(255) | | 备注 |
| `parent_id` | INT | FK | 上级部门 |
| `owner_id` | INT | FK | 部门负责人 |
| `creator_id` | INT | FK | 创建人 |
| `updated_by_id` | INT | FK | 最后修改人 |
| `created_at` | DATETIME | | 创建时间 |
| `updated_at` | DATETIME | | 更新时间 |

### BDM_user_department 表 🆕

| 字段名 | 类型 | 约束 | 说明 |
|-------|------|------|------|
| `id` | INT | PK | 主键 |
| `user_id` | INT | FK | 用户ID |
| `department_id` | INT | FK | 部门ID |
| `feishu_department_id` | VARCHAR(255) | | 飞书部门ID |
| `is_leader` | BOOLEAN | | 是否为部门负责人 |
| `created_at` | DATETIME | | 创建时间 |
| `updated_at` | DATETIME | | 更新时间 |

**联合唯一约束**：(user_id, department_id)


## 模型关系图

```
SM.User
    │
    │ user_departments (related_name)
    ↓
BDM.UserDepartment ←───────────────┐
    │                              │
    │ department (FK)              │ user (FK)
    ↓                              │
BDM.Department                     │
    │                              │
    │ department_users (related_name)
    └──────────────────────────────┘

BDM.Staff
    │
    │ dept_owner (related_name)
    ↓
BDM.Department (owner)
```


## 使用示例

### 查询用户的所有部门

```python
user = User.objects.get(id=1)
user_depts = user.user_departments.all()  # QuerySet[UserDepartment]

for ud in user_depts:
    print(f"部门: {ud.department.name}, 是否负责人: {ud.is_leader}")
```

### 查询部门的所有用户

```python
dept = Department.objects.get(id=1)
dept_users = dept.department_users.all()  # QuerySet[UserDepartment]

for ud in dept_users:
    print(f"用户: {ud.user.nickname}, 飞书部门ID: {ud.feishu_department_id}")
```

### 检查用户是否在某个部门

```python
from apps.BDM.department.models import UserDepartment

exists = UserDepartment.objects.filter(
    user=user,
    department__code='od_xxx'
).exists()
```


## 特有名词索引

当以下名词出现时，应关联到此技能：

| 名词 | 说明 |
|------|------|
| **Department** | BDM 部门模型 |
| **UserDepartment** 🆕 | 用户部门关联模型 |
| **code** | 部门编码字段（存储飞书 open_department_id） |
| **feishu_department_id** 🆕 | 飞书部门ID字段 |
| **user_departments** 🆕 | User 模型的反向关联字段 |
| **department_users** 🆕 | Department 模型的反向关联字段 |
| **sync_user_departments** 🆕 | 异步同步用户部门的任务 |
| **部门同步** 🆕 | 飞书部门自动同步机制 |


## 相关技能

- **utils-feishu-user_manager**：飞书用户管理器（获取部门信息）
- **sm-user** 🆕：SM 用户模块（信号和异步任务）
- **bdm-staff**：BDM 员工管理模块（Staff 模型）
