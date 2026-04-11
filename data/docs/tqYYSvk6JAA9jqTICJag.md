# BDM Staff 模块技能

## 模块位置

```
pms_backend/apps/BDM/staff/
├── models.py           # Staff、StaffDepartment 模型
├── serializers.py      # 员工序列化器
├── views.py            # 员工视图（CRUD + 枚举）
├── enums.py            # 枚举和权限定义
├── urls.py             # 子模块路由配置
├── utils.py            # 工具函数
└── __init__.py
```

## 数据模型

### Staff 模型

```python
class Staff(models.Model):
    id              # 主键（自增）
    code            # 员工编码（唯一，格式：STAFFXXXX）
    name            # 员工名称（唯一）
    disable_flag    # 禁用状态
    remark          # 备注

    # 关联字段
    created_by      # 创建人（外键到 SM.User）
    updated_by      # 最后修改人（外键到 SM.User）
    created_at      # 创建时间
    updated_at      # 最后修改日期
```

### StaffDepartment 模型（中间表）

```python
class StaffDepartment(models.Model):
    staff           # 员工（外键到 Staff，related_name='related_staff_dept'）
    department      # 部门（外键到 BDM.Department，related_name='related_dept_staff'）
    is_leader       # 是否为部门负责人
    created_by      # 创建人
    updated_by      # 最后修改人
    created_at      # 创建时间
    updated_at      # 最后修改日期
```

**说明**：`StaffDepartment` 是员工与部门的多对多中间表，支持一个员工属于多个部门。

## 序列化器

### ReadSerializer（详情序列化器）
用于员工详情查询：

```python
class ReadSerializer(serializers.ModelSerializer):
    document        # 员工主数据
        ├─ code         # 员工编码
        ├─ name         # 员工名称
        ├─ remark       # 备注
        ├─ disableFlag  # 禁用状态
        └─ departments  # 部门列表（数组）
            ├─ departmentId   # 部门ID
            ├─ departmentName # 部门名称
            └─ isLeader      # 是否为负责人
    others          # 其他数据
        ├─ createdAt    # 创建时间
        ├─ updatedAt   # 最后修改时间
        ├─ createdBy   # 创建人（{id, username}）
        └─ updatedBy   # 最后修改人（{id, username}）
```

### ListSerializer（列表序列化器）
用于列表展示：

```python
class ListSerializer(serializers.ModelSerializer):
    index           # 序号
    primaryId       # ID（source='id'）
    code            # 员工编码
    name            # 员工名称
    disableFlag     # 禁用状态（source='disable_flag'）
    createdByName   # 创建人（source='created_by.username'）
```

### ParamsSerializer（参数序列化器）
统一处理列表查询参数、筛选、分页、排序：

```python
class ParamsSerializer(serializers.Serializer):
    query            # 搜索关键词（name 或 code）
    pageNum          # 页码（默认 1）
    pageSize         # 每页数量（默认 10）
    sortField        # 排序字段（默认 id）
    sortOrder        # 排序方式（asc/desc，默认 desc）

    # 方法
    get_paginated_queryset(queryset)  # 返回（分页后queryset, pagination_info）
```

### DepartmentItemSerializer（部门项序列化器）
用于员工与部门关联：

```python
class DepartmentItemSerializer(serializers.Serializer):
    departmentId    # 部门ID
    isLeader        # 是否为负责人（默认 false）
```

### WriteSerializer（写入序列化器）
用于创建和更新员工：

```python
class WriteSerializer(serializers.ModelSerializer):
    # 字段
    code            # 员工编码（自动生成，可选）
    name            # 员工名称（必填，唯一）
    remark          # 备注（可选）
    disable_flag    # 禁用状态（可选）
    departments     # 部门列表（可选，数组）

    # 验证
    validate_code()      # 编码唯一性验证
    validate_name()      # 名称唯一性验证
    create()             # 创建时自动设置 created_by、updated_by，并创建部门关联
    update()             # 更新时自动设置 updated_by，并替换部门关联
```

** departments 字段格式**：
```python
[
    {"departmentId": 1, "isLeader": true},
    {"departmentId": 2, "isLeader": false}
]
```

### PatchSerializer（批量更新序列化器）
```python
class PatchSerializer(serializers.Serializer):
    ids             # 员工 ID 列表
    disableFlag     # 禁用状态（source='disable_flag'）

    # 验证
    validate()        # 验证状态是否发生变化
    execute_update()  # 执行批量更新
```

### DeleteSerializer（批量删除序列化器）
```python
class DeleteSerializer(serializers.Serializer):
    ids             # 员工 ID 列表

    # 方法
    execute_delete()   # 执行批量删除
```

## 视图

### StaffViews（主视图）
路由：`/bdm/staff/<id>`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/bdm/staff/<id>` | 获取员工详情 |
| PUT | `/bdm/staff/<id>` | 完整更新员工 |

### StaffListView（列表/批量视图）
路由：`/bdm/staff/list`、`/bdm/staff/`、`/bdm/staff`

| 方法 | 路径 | Body 参数 | 说明 |
|------|------|-----------|------|
| GET | `/bdm/staff` | query参数 | 列表查询 |
| GET | `/bdm/staff/list` | query参数 | 列表查询（分页格式） |
| POST | `/bdm/staff/list` | 员工数据 | 创建员工 |
| PATCH | `/bdm/staff/list` | `{"ids": [1,2,3], ...}` | 批量部分更新 |
| DELETE | `/bdm/staff/list` | `{"ids": [1,2,3]}` | 批量删除 |

### StaffEnumView（枚举视图）
路由：`/bdm/staff/enums`

| 方法 | 路径 | 返回内容 |
|------|------|----------|
| GET | `/bdm/staff/enums` | choices, permissions |

## URL 路由配置

```python
# apps/BDM/staff/urls.py
app_name = 'staff'
urlpatterns = [
    # 优先级：具体路由在前
    path('/enums', StaffEnumView.as_view()),         # 枚举
    path('/list', StaffListView.as_view()),          # 列表/批量
    path('/', StaffListView.as_view()),              # 列表（带斜杠）
    path('', StaffListView.as_view()),               # 列表（不带斜杠）
    path('/<int:id>', StaffViews.as_view()),         # 详情/更新
]

# apps/BDM/urls.py
urlpatterns = [
    path('staff', include('apps.BDM.staff.urls')),
]
```

## 枚举数据

### Choices 类
```python
class Choices:
    disable_flag = [
        (True, '禁用'),
        (False, '启用')
    ]
```

### Permissions 类
```python
class Permissions:
    class OperationTypes:
        CREATE = 'CREATE', '创建'
        VIEW = 'VIEW', '查看'
        CHANGE = 'CHANGE', '修改'
        DELETE = 'DELETE', '删除'
        DISABLE = 'DISABLE', '禁用'

    DJANGO_CODENAME_MAP = {
        'CREATE': 'add_staff',
        'VIEW': 'view_staff',
        'CHANGE': 'change_staff',
        'DELETE': 'delete_staff',
        'DISABLE': 'disable_staff'
    }
```

## 关联模块

| 模块 | 关联方式 | 说明 |
|------|----------|------|
| SM.User | ForeignKey | 创建人（created_by）、最后修改人（updated_by） |
| BDM.Department | ManyToMany | 通过 StaffDepartment 中间表关联 |

## 业务规则

### 员工编码
- 创建时自动生成，格式：`STAFFXXXX`
- 通过 `get_unique_code('STAFF', Staff)` 生成
- 编码唯一，不可重复

### 员工名称
- 必须唯一
- 创建/更新时验证唯一性

### 员工与部门关系
- **多对多关系**：一个员工可以属于多个部门
- **中间表**：`StaffDepartment` 模型
- **部门负责人**：通过 `is_leader` 字段标识

**创建/更新员工时的部门处理**：
```python
# 创建时：同步创建 StaffDepartment 记录
StaffDepartment.objects.create(
    staff=staff,
    department_id=dept_data['departmentId'],
    is_leader=dept_data.get('isLeader', False)
)

# 更新时：先删除旧的关联，再创建新的
StaffDepartment.objects.filter(staff=instance).delete()
# 然后重新创建...
```

### 部门关联查询
```python
# 预加载部门关联（避免 N+1 查询）
queryset = queryset.prefetch_related('related_staff_dept__department')

# 获取员工的所有部门
for sd in staff.related_staff_dept.all():
    print(sd.department.name, sd.is_leader)
```

### 禁用状态
- `disable_flag=True` 表示禁用
- 禁用后不再出现在默认列表中
- 可通过批量操作批量禁用/启用

## 使用场景

### 场景 1：获取员工列表（带搜索分页）
```python
GET /bdm/staff/list?query=张三&pageNum=1&pageSize=10&sortField=name&sortOrder=asc
```

### 场景 2：创建员工（带部门关联）
```python
POST /bdm/staff/list
{
    "name": "张三",
    "remark": "研发工程师",
    "departments": [
        {"departmentId": 1, "isLeader": false},
        {"departmentId": 2, "isLeader": true}
    ]
}
```

### 场景 3：更新员工（替换部门关联）
```python
PUT /bdm/staff/1
{
    "name": "张三",
    "remark": "高级研发工程师",
    "departments": [
        {"departmentId": 1, "isLeader": true}
    ]
}
```

### 场景 4：批量更新禁用状态
```python
PATCH /bdm/staff/list
{
    "ids": [1, 2, 3],
    "disableFlag": true
}
```

### 场景 5：获取员工详情（含部门信息）
```python
GET /bdm/staff/1
# 返回：
{
    "document": {
        "code": "STAFF0001",
        "name": "张三",
        "remark": "研发工程师",
        "disableFlag": false,
        "departments": [
            {"departmentId": 1, "departmentName": "研发部", "isLeader": false},
            {"departmentId": 2, "departmentName": "技术部", "isLeader": true}
        ]
    },
    "others": {...}
}
```

### 场景 6：获取枚举数据
```python
GET /bdm/staff/enums
# 返回：choices（禁用状态选项）、permissions（权限列表）
```

## 常见问题

### Q: 员工与部门是多对多关系吗？
A: 是的，通过 `StaffDepartment` 中间表实现。一个员工可以属于多个部门，一个部门也可以有多个员工。

### Q: 如何标识某员工是部门负责人？
A: 在 `StaffDepartment` 中间表中，`is_leader=True` 表示该员工是该部门的负责人。

### Q: 更新员工时部门关联如何处理？
A: 更新时会先删除旧的 `StaffDepartment` 记录，然后创建新的关联记录。这是替换模式，不是增量更新。

### Q: 员工编码可以自定义吗？
A: 创建时可以手动传入，如果不传则系统自动生成（STAFFXXXX格式）。但必须保证唯一性。

### Q: 如何查询某部门下的所有员工？
A: 通过 `StaffDepartment` 中间表反向查询：
```python
# 获取部门ID为1的所有员工
staff_ids = StaffDepartment.objects.filter(department_id=1).values_list('staff_id', flat=True)
staffs = Staff.objects.filter(id__in=staff_ids)
```

### Q: 如何查询某员工负责的所有部门？
A:
```python
staff_depts = staff.related_staff_dept.filter(is_leader=True)
for sd in staff_depts:
    print(sd.department.name)
```

### Q: 批量删除员工会检查部门关联吗？
A: 当前实现直接删除员工和关联的 `StaffDepartment` 记录（CASCADE）。无需手动清理。

### Q: departments 字段是必填的吗？
A: 不是，`departments` 是可选字段。创建员工时可以不传部门信息。

## 开发注意事项

1. **驼峰命名**：请求和响应使用驼峰命名（`departmentId`、`isLeader`），模型字段使用下划线命名（`department_id`、`is_leader`）
2. **员工编码自动生成**：创建时无需手动传 code，系统自动生成
3. **创建人自动设置**：通过序列化器的 `create()` 方法自动设置
4. **修改人自动更新**：通过序列化器的 `update()` 方法自动设置
5. **部门关联处理**：在 `WriteSerializer` 的 `create()` 和 `update()` 方法中处理
6. **预加载优化**：详情查询时使用 `prefetch_related('related_staff_dept__department')` 避免N+1查询
7. **参数验证统一处理**：使用 `ParamsSerializer` 统一处理查询参数
8. **视图保持简洁**：业务逻辑封装在序列化器中，视图只负责调用

## 与 Department 的关系

Staff 模块与 Department（部门）模块存在多对多关联：
- 一个员工可以属于多个部门
- 一个部门可以有多个员工
- 通过 `StaffDepartment` 中间表关联
- 支持部门负责人标识（`is_leader` 字段）

关联查询示例：
```python
# 获取某员工的所有部门
staff_depts = staff.related_staff_dept.all()

# 获取某部门的所有员工
dept_staffs = department.related_dept_staff.all()

# 创建员工时关联部门
staff = Staff.objects.create(name="张三")
StaffDepartment.objects.create(staff=staff, department=dept, is_leader=False)
```
