# BDM CustomerModel 模块技能

## 模块位置

```
pms_backend/apps/BDM/customer_model/
├── models.py           # CustomerModel 模型
├── serializers.py       # 客户机型序列化器
├── views.py            # 客户机型视图（CRUD + 枚举）
├── enums.py            # 枚举和权限定义
├── urls.py             # 子模块路由配置
├── utils.py            # 工具函数
└── __init__.py
```

## 数据模型

### CustomerModel 模型

```python
class CustomerModel(models.Model):
    code           # 机型编码（自动生成，格式：CMODXXXX）
    name           # 机型名称（唯一）
    disable_flag    # 禁用状态
    remark         # 备注

    # 关联字段
    customer       # 所属客户（外键到 BDM.Customer）
    creator        # 创建人（外键到 SM.User）
    updated_by     # 最后修改人（外键到 SM.User）
    create_at      # 创建时间
    updated_at     # 最后修改日期
```

## 序列化器

### ReadSerializer（详情序列化器）
用于客户机型详情查询：

```python
class ReadSerializer(serializers.ModelSerializer):
    # 只读字段（输出）
    document        # 机型主数据
        ├─ code         # 机型编码
        ├─ name         # 机型名称
        ├─ customer     # 所属客户（{id, code, name}）
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
    code            # 机型编码
    name            # 机型名称
    customerName    # 所属客户名称
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
用于创建和更新客户机型：

```python
class WriteSerializer(serializers.ModelSerializer):
    # 字段
    code            # 机型编码（自动生成，创建时可选）
    name            # 机型名称（必填，唯一）
    customerId      # 所属客户ID（write_only，可选）
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
    ids             # 机型ID列表
    disableFlag      # 禁用状态（source='disable_flag'）

    # 验证
    validate()        # 验证状态是否发生变化
    execute_update()   # 执行批量更新
```

### DeleteSerializer（批量删除序列化器）
```python
class DeleteSerializer(serializers.Serializer):
    ids             # 机型ID列表

    # 方法
    execute_delete()   # 执行批量删除
```

## 视图

### CustomerModelViews（主视图）
路由：`/bdm/customer-model/<id>`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/bdm/customer-model/<id>` | 获取机型详情 |
| PUT | `/bdm/customer-model/<id>` | 完整更新机型 |

### CustomerModelListView（列表/批量视图）
路由：`/bdm/customer-model/list`、`/bdm/customer-model/`

| 方法 | 路径 | Body 参数 | 说明 |
|------|------|-----------|------|
| GET | `/bdm/customer-model` | query参数 | 列表查询 |
| GET | `/bdm/customer-model/list` | query参数 | 列表查询（分页格式） |
| POST | `/bdm/customer-model/list` | 机型数据 | 创建机型 |
| PATCH | `/bdm/customer-model/list` | `{"ids": [1,2,3], ...}` | 批量部分更新 |
| DELETE | `/bdm/customer-model/list` | `{"ids": [1,2,3]}` | 批量删除 |

### CustomerModelEnumView（枚举视图）
路由：`/bdm/customer-model/enum`

| 方法 | 路径 | 返回内容 |
|------|------|----------|
| GET | `/bdm/customer-model/enum` | choices, permissions |

## URL 路由配置

```python
# apps/BDM/customer_model/urls.py
app_name = 'customer_model'
urlpatterns = [
    # 优先级：具体路由在前
    path('/enum', CustomerModelEnumView.as_view()),      # 枚举
    path('/list', CustomerModelListView.as_view(),       # 列表/批量
    path('/<int:id>', CustomerModelViews.as_view()),     # 详情/更新
    path('/', CustomerModelListView.as_view()),           # 列表（带斜杠）
    path('', CustomerModelListView.as_view()),             # 列表（不带斜杠）
]

# apps/BDM/urls.py
urlpatterns = [
    path('customer-models', include('apps.BDM.customer_model.urls')),
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
        'CREATE': 'add_customermodel',
        'VIEW': 'view_customermodel',
        'CHANGE': 'change_customermodel',
        'DELETE': 'delete_customermodel',
        'DISABLE': 'disable_customermodel'
    }
```

## 关联模块

| 模块 | 关联方式 | 说明 |
|------|----------|------|
| BDM.Customer | ForeignKey | 所属客户（customer） |
| SM.User | ForeignKey | 创建人（creator）、最后修改人（updated_by） |

## 业务规则

### 机型编码
- 创建时自动生成，格式：`CMODXXXX`
- 通过 `get_unique_code('CMOD', CustomerModel)` 生成
- 编码唯一，不可重复

### 机型名称
- 必须唯一
- 创建/更新时验证唯一性

### 所属客户
- 可选字段（可为空）
- 如果提供，必须是已存在的客户ID
- 通过 LazyCustomerPrimaryKeyRelatedField 实现懒加载避免循环导入

### 禁用状态
- `disable_flag=True` 表示禁用
- 禁用后不再出现在默认列表中
- 可通过批量操作批量禁用/启用

## 使用场景

### 场景 1：获取机型列表（带搜索分页）
```python
GET /bdm/customer-models/list?query=型号&pageNum=1&pageSize=10
```

### 场景 2：创建机型
```python
POST /bdm/customer-models/list
{
    "name": "旗舰版",
    "customerId": 5,
    "remark": "高端产品线"
}
```

### 场景 3：批量更新禁用状态
```python
PATCH /bdm/customer-models/list
{
    "ids": [1, 2, 3],
    "disableFlag": true
}
```

### 场景 4：获取机型详情
```python
GET /bdm/customer-models/1
```

### 场景 5：获取某客户的所有机型
```python
# 通过客户ID筛选
GET /bdm/customer-models/list?customerId=5

# 或通过客户模型的反向关联
customer.customer_model_customer.all()
```

## 常见问题

### Q: 机型必须关联客户吗？
A: 不是。customer 字段是可选的（null=True, blank=True），可以创建不关联任何客户的通用机型。

### Q: 如何避免与 Customer 模型的循环导入？
A: 使用 `LazyCustomerPrimaryKeyRelatedField`，通过 `apps.get_model('BDM', 'Customer')` 懒加载模型。

### Q: 如何按客户筛选机型？
A: 前端通过 customerId 参数筛选，后端在 `get_list_queryset()` 中添加：
```python
customerId = request.GET.get('customerId')
if customerId:
    queryset = queryset.filter(customer_id=customerId)
```

### Q: 批量删除会检查关联数据吗？
A: 当前实现直接删除。如果有其他模块（如项目、订单）关联机型，应先检查。

## 开发注意事项

1. **机型编码自动生成**：创建时无需手动传 code，系统自动生成
2. **创建人自动设置**：通过序列化器的 `create()` 方法自动设置
3. **修改人自动更新**：通过序列化器的 `update()` 方法自动设置
4. **参数验证统一处理**：使用 `ParamsSerializer` 统一处理查询参数
5. **视图保持简洁**：业务逻辑封装在序列化器中，视图只负责调用
6. **懒加载避免循环导入**：使用 LazyCustomerPrimaryKeyRelatedField

## 与 Customer 的关系

CustomerModel（客户机型）模块与 Customer 模块存在多对一关联：
- 多个机型可以属于同一个客户
- CustomerModel 通过 `customer` 外键关联到 Customer
- Customer 通过 `customer_model_customer` 反向访问所有机型

关联查询示例：
```python
# 获取某客户的所有机型
from apps.BDM.customer.models import Customer
customer = Customer.objects.get(id=1)
models = customer.customer_model_customer.all()

# 创建机型时关联客户
from apps.BDM.customer_model.models import CustomerModel
CustomerModel.objects.create(name="型号A", customer=customer)
```