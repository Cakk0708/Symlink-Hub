# SM Version Control 模块技能

## 模块位置

```
pms_backend/apps/SM/version_control/
├── models.py              # VersionControl、VersionControlItem 模型
├── serializers.py         # 版本序列化器
├── views.py              # 版本视图（CRUD + 枚举 + 当前版本）
├── enums.py              # 枚举和权限定义
├── urls.py               # 子模块路由配置
├── utils.py              # 工具函数
└── __init__.py
```

## 数据模型

### VersionControl 模型（版本控制主模型）

```python
class VersionControl(models.Model):
    code            # 版本编码（自动生成，格式：VERSIONXXXX）
    version         # 版本号（必填，唯一，max_length=50）
    is_current      # 是否为当前版本（默认False）
    remark          # 备注（可选，max_length=500）

    # 关联字段
    creator         # 创建人（外键到 SM.User）
    update_by       # 最后修改人（外键到 SM.User）
    create_time     # 创建时间
    update_time     # 最后修改日期

    # 自动管理逻辑
    - 设置 is_current=True 时，自动将其他版本设为 False
    - code 自动生成，使用 get_unique_code('VERSION', VersionControl)

    # 数据库表名
    db_table = "SM_version_control"
```

### VersionControlItem 模型（版本内容项）

```python
class VersionControlItem(models.Model):
    version_control    # 关联版本（外键到 VersionControl）
    content           # 更新内容（必填，TextField）
    sort              # 排序（默认0，IntegerField）
    create_time       # 创建时间
    update_time       # 最后修改日期

    # 关系
    - 通过 version_control.version_control_items 反向访问

    # 数据库表名
    db_table = "SM_version_control_item"
```

## 序列化器

### VersionControlWriteSerializer（写序列化器）
用于创建和更新操作：

```python
class VersionControlWriteSerializer(serializers.Serializer):
    """版本控制写序列化器（创建/更新）"""
    version         # 版本号（必填，max_length=50）
    isCurrent       # 是否为当前版本（source='is_current', 默认False）
    remark          # 备注（可选）
    itemData        # 更新内容列表（只写，创建时必填）

    # 验证规则
    - 版本号唯一性验证
    - 取消当前版本时检查是否还有其他当前版本
    - 创建时必须提供 itemData
    - 更新时 itemData 可选
    - 权限验证（CREATE/CHANGE）
```

### VersionControlDetailSerializer（详情序列化器）
用于详情展示（只读）：

```python
class VersionControlDetailSerializer(serializers.Serializer):
    """版本控制详情序列化器（只读）"""
    id              # 版本ID
    document        # 版本文档信息（SerializerMethodField）
    items           # 版本内容项列表（SerializerMethodField）
    others          # 其他信息（SerializerMethodField）

    # document 结构
    {
        'code': 'VERSION0001',
        'version': '1.0.0',
        'isCurrent': True,
        'remark': '备注'
    }

    # others 结构
    {
        'createdBy': {'id': 1, 'nickname': '管理员'},
        'createdAt': '2024-01-01 10:00:00',
        'updatedBy': {'id': 1, 'nickname': '管理员'},
        'updatedAt': '2024-01-01 10:00:00'
    }
```

### GetListParamsSerializer（列表参数序列化器）
```python
class GetListParamsSerializer(serializers.Serializer):
    version         # 版本号（模糊搜索）
    isCurrent       # 是否为当前版本（精确匹配）
    pageNum         # 页码（默认1）
    pageSize        # 每页数量（默认10）
    pageSort        # 排序（如：CREATE_TIME:DESC）

    # 方法
    get_queryset(base_queryset)  # 返回（分页后queryset, total）
```

### ListSerializer（列表序列化器）
```python
class ListSerializer(serializers.ModelSerializer):
    id              # 版本ID
    code            # 版本编码
    version         # 版本号
    isCurrent       # 是否为当前版本
    remark          # 备注
    creatorName     # 创建人
    createdAt       # 创建时间（source='create_time'）
    updatedAt       # 最后修改时间（source='update_time'）
    itemCount       # 更新内容项数量
    content         # 更新内容拼接（逗号分隔）
```

### VersionControlItemSerializer（版本内容项序列化器）
```python
class VersionControlItemSerializer(serializers.ModelSerializer):
    id              # 内容项ID（更新时必填）
    content         # 更新内容（必填）
    sort            # 排序
    addVersionControl  # 关联版本（写专用，source='version_control'）
    createdAt       # 创建时间（source='create_time'）
    updatedAt       # 最后修改时间（source='update_time'）
```

### DeleteBatchSerializer（批量删除序列化器）
```python
class DeleteBatchSerializer(serializers.Serializer):
    ids             # 版本 ID 列表（1-100个）

    # 验证
    - 权限验证（DELETE权限）

    # 方法
    batch_delete()  # 执行批量删除
```

### PatchBatchSerializer（批量修改序列化器）
```python
class PatchBatchSerializer(serializers.Serializer):
    ids             # 版本 ID 列表（1-100个）
    isCurrent       # 是否为当前版本（必填）

    # 验证
    - 权限验证（CHANGE权限）
    - 批量取消当前版本时的边界检查

    # 方法
    batch_update()  # 执行批量更新
```

## 视图

### VersionControlListView（列表/批量视图）
路由：`/sm/version-control/list`、`/sm/version-control/`、`/sm/version-control`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/sm/version-control/list` | 列表查询（支持筛选、分页、排序） |
| POST | `/sm/version-control/list` | 创建新版本 |
| PATCH | `/sm/version-control/list` | 批量修改（如批量设置当前版本） |
| DELETE | `/sm/version-control/list` | 批量删除 |

### VersionControlDetailView（详情视图）
路由：`/sm/version-control/{id}`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/sm/version-control/{id}` | 获取版本详情 |
| PUT | `/sm/version-control/{id}` | 完整更新版本 |

### VersionControlCurrentView（当前版本视图）
路由：`/sm/version-control/current`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/sm/version-control/current` | 获取当前激活的版本详情 |

### VersionControlEnumsView（枚举视图）
路由：`/sm/version-control/enums`

| 方法 | 路径 | 返回内容 |
|------|------|----------|
| GET | `/sm/version-control/enums` | permissions（权限枚举列表） |

## URL 路由配置

```python
# apps/SM/version_control/urls.py
app_name = 'version_control'
urlpatterns = [
    # 优先级：具体路由在前
    path('/enums', VersionControlEnumsView.as_view()),         # 枚举
    path('/current', VersionControlCurrentView.as_view()),     # 当前版本
    path('/list', VersionControlListView.as_view()),          # 列表/批量
    path('/', VersionControlListView.as_view()),              # 列表（带斜杠）
    path('', VersionControlListView.as_view()),               # 列表（不带斜杠）
    path('/<int:id>', VersionControlDetailView.as_view()),    # 详情/更新
]

# apps/SM/urls.py
urlpatterns = [
    path('version-control', include('apps.SM.version_control.urls')),
]
```

## 工具函数（utils.py）

```python
# 获取列表查询集（优化关联查询）
get_list_queryset()

# 获取详情查询集（包含版本内容项）
get_detail_queryset()

# 获取当前版本
get_current_version() -> VersionControl or None

# 设置指定版本为当前版本
set_current_version(version_id) -> VersionControl

# 根据版本号获取版本
get_version_by_version_number(version_number) -> VersionControl or None
```

## 枚举数据

### Permissions 类
```python
class Permissions:
    class OperationTypes:
        CREATE = 'CREATE', '创建'
        VIEW = 'VIEW', '查看'
        CHANGE = 'CHANGE', '修改'
        DELETE = 'DELETE', '删除'

    DJANGO_CODENAME_MAP = {
        'CREATE': 'add_versioncontrol',
        'VIEW': 'view_versioncontrol',
        'CHANGE': 'change_versioncontrol',
        'DELETE': 'delete_versioncontrol'
    }

    # 权限验证格式：'SM.add_versioncontrol'
    @classmethod
    def get_permission_verify_codename(cls, op_value: str) -> str
```

## 业务规则

### 版本编码（code）
- 创建时自动生成，格式：`VERSIONXXXX`
- 通过 `get_unique_code('VERSION', VersionControl)` 生成
- 编码唯一，不可重复

### 版本号（version）
- 必须唯一
- 创建/更新时验证唯一性
- 手动输入，格式如 "1.0.0"、"v2.1" 等

### 当前版本（is_current）
- 系统中可以有零个或多个当前版本
- 设置某个版本为 `is_current=True` 时，模型会自动将其他版本设为 `False`
- 批量取消当前版本时，可能导致系统没有当前版本（这是允许的）

### 版本内容项（itemData）
- 创建版本时必须提供至少一个更新内容项
- 更新版本时可以选择性修改内容项
- 内容项通过 `id` 字段识别，更新时需传入 `id` 表示修改现有项
- 不传入 `id` 表示创建新项
- 更新时未出现在 `itemData` 中的现有项会被删除

### 权限验证
- CREATE：创建版本（`SM.add_versioncontrol`）
- VIEW：查看版本（`SM.view_versioncontrol`）
- CHANGE：修改版本（`SM.change_versioncontrol`）
- DELETE：删除版本（`SM.delete_versioncontrol`）

## 使用场景

### 场景 1：获取版本列表（带筛选分页）
```python
GET /sm/version-control/list?version=1.0&isCurrent=true&pageNum=1&pageSize=10&pageSort=CREATE_TIME:DESC
```

### 场景 2：创建新版本
```python
POST /sm/version-control/list
{
    "version": "1.0.0",
    "isCurrent": true,
    "remark": "初始版本",
    "itemData": [
        {"content": "新增用户管理功能", "sort": 1},
        {"content": "修复登录Bug", "sort": 2}
    ]
}
```

### 场景 3：更新版本内容
```python
PUT /sm/version-control/1
{
    "remark": "修复了若干问题",
    "itemData": [
        {"id": 1, "content": "新增用户管理功能", "sort": 1},
        {"id": 2, "content": "修复登录Bug（已解决）", "sort": 2},
        {"content": "新增导出功能", "sort": 3}
    ]
}
```

### 场景 4：批量设置当前版本
```python
PATCH /sm/version-control/list
{
    "ids": [5],
    "isCurrent": true
}
```

### 场景 5：批量删除版本
```python
DELETE /sm/version-control/list
{
    "ids": [3, 4, 5]
}
```

### 场景 6：获取当前版本
```python
GET /sm/version-control/current
```

### 场景 7：获取枚举数据
```python
GET /sm/version-control/enums
# 返回：permissions（权限枚举列表）
```

## 响应数据结构

### 列表响应
```json
{
    "msg": "success",
    "data": {
        "items": [
            {
                "id": 1,
                "code": "VERSION0001",
                "version": "1.0.0",
                "isCurrent": true,
                "remark": "初始版本",
                "creatorName": "admin",
                "createdAt": "2024-01-01 10:00:00",
                "updatedAt": "2024-01-01 10:00:00",
                "itemCount": 2,
                "content": "新增用户管理功能, 修复登录Bug"
            }
        ],
        "total": 10
    }
}
```

### 详情响应
```json
{
    "msg": "success",
    "data": {
        "id": 1,
        "document": {
            "code": "VERSION0001",
            "version": "1.0.0",
            "isCurrent": true,
            "remark": "初始版本"
        },
        "items": [
            {
                "id": 1,
                "content": "新增用户管理功能",
                "sort": 1,
                "createdAt": "2024-01-01 10:00:00",
                "updatedAt": "2024-01-01 10:00:00"
            }
        ],
        "others": {
            "createdBy": {
                "id": 1,
                "nickname": "管理员"
            },
            "createdAt": "2024-01-01 10:00:00",
            "updatedBy": {
                "id": 1,
                "nickname": "管理员"
            },
            "updatedAt": "2024-01-01 10:00:00"
        }
    }
}
```

## 常见问题

### Q: 版本编码是如何生成的？
A: 使用 `get_unique_code('VERSION', VersionControl)` 自动生成，创建时无需手动传入。

### Q: 可以有多个当前版本吗？
A: 可以。模型的 `save()` 方法会将新设置为当前版本的版本设为 `True`，同时将其他版本设为 `False`。但可以通过批量操作取消所有当前版本。

### Q: 更新版本时如何处理内容项？
A: 通过 `itemData` 数组处理：
- 包含 `id` 的项表示更新现有项
- 不包含 `id` 的项表示创建新项
- 未出现在 `itemData` 中的现有项会被删除

### Q: 版本号有格式要求吗？
A: 没有强制格式要求，可以是任意字符串，如 "1.0.0"、"v2.1"、"2024-01" 等。

### Q: 如何获取系统最新的当前版本？
A: 调用 `GET /sm/version-control/current` 或使用工具函数 `get_current_version()`。

### Q: 删除版本会关联删除内容项吗？
A: 是的，由于 `VersionControlItem` 的外键使用 `on_delete=models.CASCADE`，删除版本会自动删除其关联的所有内容项。

## 开发注意事项

1. **版本编码自动生成**：创建时无需手动传 code，系统自动生成
2. **当前版本自动管理**：设置 `is_current=True` 时自动将其他版本设为 `False`
3. **创建人自动设置**：通过序列化器的 `create()` 方法自动设置
4. **修改人自动更新**：通过序列化器的 `update()` 方法自动设置
5. **内容项更新逻辑**：更新时需要完整传入所有要保留的项，未传入的会被删除
6. **权限验证**：所有写操作都需要相应的权限验证
7. **查询优化**：使用 `select_related` 和 `prefetch_related` 优化关联查询
8. **时间字段命名**：使用 `createdAt` 和 `updatedAt` 而非 `createTime` 和 `updateTime`

## 关联模块

| 模块 | 关联方式 | 说明 |
|------|----------|------|
| SM.User | ForeignKey | 创建人（creator）、最后修改人（update_by） |
| SM.code | utils | 编码生成工具 `get_unique_code()` |
| SM.system | utils | 版本获取工具 `get_version()` |

## 变更历史

### 2026-03-13
- 模块从 `BDM/version_control` 迁移到 `SM/version_control`
- 数据库表名从 `BDM_version_control` 改为 `SM_version_control`
- 数据库表名从 `BDM_version_control_item` 改为 `SM_version_control_item`
- 权限前缀从 `BDM.` 改为 `SM.`
- 路由从 `/bdm/version-control` 改为 `/sm/version-control`
- 序列化器拆分：`VersionControlSerializer` 拆分为 `VersionControlWriteSerializer`（写）和 `VersionControlDetailSerializer`（读）
- 详情响应结构优化：`others.createdBy` 和 `others.updatedBy` 从字符串改为对象（包含 id 和 nickname）

## 参考文档

- **接口文档**：`references/version_control.apifox.json` - 完整的 Apifox 接口定义
