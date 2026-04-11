# 模型命名规范

全局生效，适用于所有 Model、迁移文件、URL 配置。

## Django Model

- 类名使用**单数** PascalCase，禁止复数
- 表名使用 `{app_label}_{model_snake_case}` 格式

```python
# ✅
class DeliveryOrder(models.Model):
    class Meta:
        db_table = 'logistics_delivery_order'

# ❌ 类名复数
class DeliveryOrders(models.Model): ...

# ❌ 表名未带 app_label 前缀
class Meta:
    db_table = 'delivery_order'
```

## 通用字段命名

所有 Model 的时间与备注字段必须统一命名，禁止自创别名：

| 用途     | 字段名         |
|--------|-------------|
| 创建时间   | `created_at` |
| 更新时间   | `updated_at` |
| 备注／说明  | `remark`     |

```python
# ✅
created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)
remark = models.CharField(max_length=255, blank=True, default='')

# ❌ 自创别名
create_time = ...
update_time = ...
note = ...
desc = ...
```

## REST URL

- 使用 **kebab-case**，禁止 snake_case 或 camelCase
- 资源名使用复数

```python
# ✅
path('delivery-orders/', DeliveryOrderListView.as_view()),
path('delivery-orders/<int:id>/', DeliveryOrderDetailView.as_view()),

# ❌ snake_case
path('delivery_orders/', ...)

# ❌ 单数资源名
path('delivery-order/', ...)
```