# BDM Customer 模块技能

## 模块位置

```
pms_backend/apps/BDM/customer/
├── models.py           # Customer 模型
├── serializers.py       # 客户序列化器
├── views.py            # 客户视图（CRUD + 枚举）
├── signals.py          # 信号处理器（拼音自动生成）
├── enums.py            # 枚举和权限定义
├── urls.py             # 子模块路由配置
├── utils.py            # 工具函数
└── __init__.py
```

## 数据模型

### Customer 模型

```python
class Customer(models.Model):
    code           # 客户编码（自动生成，格式：CUSTXXXX）
    name           # 客户名称（唯一）
    name_pinyin    # 客户名称拼音数组（JSONField，自动生成）
    region         # 客户分组（枚举：中国各省份/直辖市/自治区）
    disable_flag    # 禁用状态
    remark         # 备注

    # 关联字段
    creator        # 创建人（外键到 SM.User）
    updated_by     # 最后修改人（外键到 SM.User）
    create_at      # 创建时间
    updated_at     # 最后修改日期
```

## 序列化器

### ReadSerializer（详情序列化器）
用于客户详情查询：

```python
class ReadSerializer(serializers.ModelSerializer):
    # 只读字段（输出）
    document        # 客户主数据
        ├─ code         # 客户编码
        ├─ name         # 客户名称
        ├─ namePinyin   # 客户名称拼音数组
        ├─ region       # 客户分组（{value, label}）
        ├─ remark       # 备注
        └─ disableFlag  # 禁用状态
    others          # 其他数据
        ├─ createAt    # 创建时间
        ├─ updatedAt   # 最后修改时间
        ├─ creator     # 创建人（{id, username}）
        └─ updatedBy   # 最后修改人（{id, username}）
```

### ListSerializer（列表序列化器）
用于列表展示：

```python
class ListSerializer(serializers.ModelSerializer):
    index           # 序号
    primaryId       # ID（source='id'）
    code            # 客户编码
    name            # 客户名称
    namePinyin      # 客户名称拼音数组（source='name_pinyin'）
    region          # 客户分组（{value, label}）
    disableFlag     # 禁用状态（source='disable_flag'）
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

### WriteSerializer（写入序列化器）
用于创建和更新客户：

```python
class WriteSerializer(serializers.ModelSerializer):
    # 字段
    code            # 客户编码（自动生成，创建时可选）
    name            # 客户名称（必填，唯一）
    region          # 客户分组（可选）
    remark          # 备注（可选）
    disable_flag    # 禁用状态（可选）

    # 验证
    validate_code()      # 编码唯一性验证
    validate_name()      # 名称唯一性验证
    create()             # 创建时自动设置 creator、updated_by
    update()             # 更新时自动设置 updated_by
```

### PatchSerializer（批量更新序列化器）
```python
class PatchSerializer(serializers.Serializer):
    ids             # 客户 ID 列表
    disableFlag      # 禁用状态（source='disable_flag'）

    # 验证
    validate()        # 验证状态是否发生变化
    execute_update()   # 执行批量更新
```

### DeleteSerializer（批量删除序列化器）
```python
class DeleteSerializer(serializers.Serializer):
    ids             # 客户 ID 列表

    # 方法
    execute_delete()   # 执行批量删除
```

## 视图

### CustomerViews（主视图）
路由：`/bdm/customer/<id>`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/bdm/customer/<id>` | 获取客户详情 |
| PUT | `/bdm/customer/<id>` | 完整更新客户 |

### CustomerListView（列表/批量视图）
路由：`/bdm/customer/list`、`/bdm/customer/`、`/bdm/customer`

| 方法 | 路径 | Body 参数 | 说明 |
|------|------|-----------|------|
| GET | `/bdm/customer` | query参数 | 列表查询 |
| GET | `/bdm/customer/list` | query参数 | 列表查询（分页格式） |
| POST | `/bdm/customer/list` | 客户数据 | 创建客户 |
| PATCH | `/bdm/customer/list` | `{"ids": [1,2,3], ...}` | 批量部分更新 |
| DELETE | `/bdm/customer/list` | `{"ids": [1,2,3]}` | 批量删除 |

### CustomerEnumView（枚举视图）
路由：`/bdm/customer/enum`

| 方法 | 路径 | 返回内容 |
|------|------|----------|
| GET | `/bdm/customer/enum` | choices, permissions |

## URL 路由配置

```python
# apps/BDM/customer/urls.py
app_name = 'customer'
urlpatterns = [
    # 优先级：具体路由在前
    path('/enums', CustomerEnumView.as_view()),       # 枚举
    path('/list', CustomerListView.as_view(),        # 列表/批量
    path('/', CustomerListView.as_view()),            # 列表（带斜杠）
    path('', CustomerListView.as_view()),             # 列表（不带斜杠）
    path('/<int:id>', CustomerViews.as_view()),      # 详情/更新
]

# apps/BDM/urls.py
urlpatterns = [
    path('customers', include('apps.BDM.customer.urls')),
]
```

## 枚举数据

### Choices 类
```python
class Choices:
    region = [
        (0, '北京市'), (1, '天津市'), (2, '河北省'),
        (3, '山西省'), (4, '内蒙古自治区'),
        # ... 中国所有省份/直辖市/自治区/特别行政区
    ]
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
        'CREATE': 'add_customer',
        'VIEW': 'view_customer',
        'CHANGE': 'change_customer',
        'DELETE': 'delete_customer',
        'DISABLE': 'disable_customer'
    }
```

## 关联模块

| 模块 | 关联方式 | 说明 |
|------|----------|------|
| SM.User | ForeignKey | 创建人（creator）、最后修改人（updated_by） |
| BDM.CustomerModel |反向关联 | 客户机型（related_name='customer_model_customer'） |

## 业务规则

### 客户编码
- 创建时自动生成，格式：`CUSTXXXX`
- 通过 `get_unique_code('CUST', Customer)` 生成
- 编码唯一，不可重复

### 客户名称
- 必须唯一
- 创建/更新时验证唯一性
- **自动生成拼音**：通过 `pre_save` 信号自动生成 `name_pinyin` 字段
- **拼音用途**：支持前端拼音搜索功能（如按首字母筛选）

### 客户名称拼音（name_pinyin）
- 字段类型：JSONField，存储拼音数组
- 自动生成：使用 `pypinyin.lazy_pinyin()` 函数
- 生成时机：新建客户或修改客户名称时
- 示例：`"北京科技"` → `["bei", "jing", "ke", "ji"]`
- 存储位置：`apps/BDM/customer/signals.py`

### 客户分组（region）
- 使用中国行政区划枚举
- 包含34个省级行政区划
- 可选字段，支持按地区筛选

### 禁用状态
- `disable_flag=True` 表示禁用
- 禁用后不再出现在默认列表中
- 可通过批量操作批量禁用/启用

## 使用场景

### 场景 1：获取客户列表（带搜索分页）
```python
GET /bdm/customers/list?query=科技&pageNum=1&pageSize=10&sortField=name&sortOrder=asc
```

### 场景 2：创建客户
```python
POST /bdm/customers/list
{
    "name": "北京科技股份有限公司",
    "region": 0,
    "remark": "华北地区重要客户"
}
```

### 场景 3：批量更新禁用状态
```python
PATCH /bdm/customers/list
{
    "ids": [1, 2, 3],
    "disableFlag": true
}
```

### 场景 4：获取客户详情
```python
GET /bdm/customers/1
```

### 场景 5：获取枚举数据
```python
GET /bdm/customers/enums
# 返回：choices（地区选项）、permissions（权限列表）
```

## 常见问题

### Q: 客户名称拼音是如何生成的？
A: 使用 `pypinyin.lazy_pinyin()` 函数自动生成，在客户创建或更新名称时通过 `pre_save` 信号自动填充 `name_pinyin` 字段。

### Q: 如何使用拼音搜索客户？
A: 前端可以使用 `namePinyin` 字段进行拼音搜索，例如筛选首字母为 "b" 的客户。

### Q: 客户分组（region）有多少选项？
A: 共34个选项，包含中国所有省级行政区划（省、自治区、直辖市、特别行政区）。

### Q: 客户编码可以自定义吗？
A: 创建时可以手动传入，如果不传则系统自动生成（CUSTXXXX格式）。但必须保证唯一性。

### Q: 如何按地区筛选客户？
A: 前端通过 region 字段筛选，后端可在 `get_list_queryset()` 中添加过滤逻辑。

### Q: 批量删除会检查关联数据吗？
A: 当前实现直接删除。未来如果有关联 CustomerModel 的业务，应先检查是否存在关联。

## 开发注意事项

1. **客户编码自动生成**：创建时无需手动传 code，系统自动生成
2. **创建人自动设置**：通过序列化器的 `create()` 方法自动设置
3. **修改人自动更新**：通过序列化器的 `update()` 方法自动设置
4. **参数验证统一处理**：使用 `ParamsSerializer` 统一处理查询参数
5. **视图保持简洁**：业务逻辑封装在序列化器中，视图只负责调用
6. **地区枚举**：region 使用完整的行政区划枚举，前端可展示中文标签

## 与 CustomerModel 的关系

Customer 模块与 CustomerModel（客户机型）模块存在一对多关联：
- 一个客户可以拥有多个机型
- CustomerModel 通过 `customer` 外键关联到 Customer
- Customer 通过 `customer_model_customer` 反向访问所有机型

关联查询示例：
```python
# 获取某客户的所有机型
customer_models = customer.customer_model_customer.all()

# 创建机型时关联客户
CustomerModel.objects.create(name="型号A", customer=customer_instance)
```