# JSON Schema 到 Django 字段映射表

## 基础类型映射

| JSON Schema 类型 | Django 字段类型 | 示例 |
|-----------------|-----------------|------|
| `string` | `CharField(max_length=255)` | 短文本 |
| `string` (长文本) | `TextField()` | 长文本、备注 |
| `integer` | `IntegerField()` | 整数 |
| `number` | `FloatField()` | 浮点数 |
| `number` (精度) | `DecimalField(max_digits=10, decimal_places=2)` | 金额 |
| `boolean` | `BooleanField()` | 布尔值 |
| `array` | `JSONField()` | JSON 数组 |
| `object` | `JSONField()` | JSON 对象 |

## 字段选项映射

| JSON Schema 属性 | Django 选项 | 说明 |
|-----------------|-------------|------|
| `required: true` | `blank=False` | 必填 |
| `required: false` | `blank=True, null=True` | 可选 |
| `default: "value"` | `default="value"` | 默认值 |
| `description` | `help_text="..."` | 帮助文本 |

## 特殊字段处理

### 1. 外键字段

```json
"customerId": { "type": "integer" }
```

```python
customer = models.ForeignKey('BDM.Customer', on_delete=models.CASCADE)
```

### 2. 枚举字段

```json
"status": { "type": "string", "enum": ["active", "inactive"] }
```

```python
# 创建 enums.py
class Status(models.TextChoices):
    ACTIVE = "active", "启用"
    INACTIVE = "inactive", "停用"

# 模型中使用
status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
```

### 3. 时间字段

```json
"createdAt": { "type": "string", "format": "date-time" }
```

```python
created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)
```

### 4. 代码/编号字段

```json
"code": { "type": "string" }
```

```python
code = models.CharField(max_length=50, unique=True)
```
