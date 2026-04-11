# Code Generator 使用示例

## 基础用法

### Customer 模型编码生成
```python
from apps.BDM.customer.models import Customer
from utils.code_generator import generate_code

# 生成默认格式编码: C20250308001
code = generate_code(Customer)
customer = Customer.objects.create(
    code=code,
    name='测试客户'
)
```

### 自定义前缀
```python
# VIP 客户编码: VIP20250308001
code = generate_code(Customer, prefix='VIP')
```

### 订单编码 (月度序列)
```python
from apps.APS.order.models import Order

# 订单编码: O202503001 (按月统计)
code = generate_code(Order, prefix='O', date_format='%Y%m')
```

### 长序号编码
```python
# 支持更大数量级: C2025030800001
code = generate_code(Customer, sequence_length=6)
```

## 高级用法

### 事务安全创建
```python
from django.db import transaction
from utils.code_generator import generate_code

@transaction.atomic
def create_customer_safely(name, contact):
    """事务安全的客户创建"""
    code = generate_code(Customer, 'C')
    return Customer.objects.create(
        code=code,
        name=name,
        contact=contact
    )
```

### 批量创建
```python
def batch_create_customers(names):
    """批量创建客户"""
    customers = []
    for name in names:
        code = generate_code(Customer, 'C')
        customers.append(Customer(code=code, name=name))

    return Customer.objects.bulk_create(customers)
```

### Signal 集成
```python
from django.db.models.signals import pre_save
from django.dispatch import receiver
from utils.code_generator import generate_code

@receiver(pre_save, sender=Customer)
def generate_customer_code(sender, instance, **kwargs):
    """保存前自动生成编码"""
    if not instance.code:
        instance.code = generate_code(Customer, 'C')
```

## 错误处理

### 编码重复处理
```python
from django.db import IntegrityError
from utils.code_generator import generate_code

def create_customer_with_retry(name, max_retries=3):
    """带重试的客户创建"""
    for i in range(max_retries):
        try:
            code = generate_code(Customer, 'C')
            return Customer.objects.create(code=code, name=name)
        except IntegrityError:
            if i == max_retries - 1:
                raise
            continue
```

### 模型字段校验
```python
def safe_generate_code(model_class, prefix='C'):
    """安全的编码生成，包含字段校验"""
    if not hasattr(model_class, '_meta'):
        raise ValueError("Invalid model class")

    # 检查是否有 code 字段
    code_field = None
    for field in model_class._meta.get_fields():
        if field.name == 'code':
            code_field = field
            break

    if not code_field:
        raise ValueError(f"{model_class.__name__} has no 'code' field")

    return generate_code(model_class, prefix)
```

## 性能优化

### 批量预生成
```python
def pre_generate_codes(model_class, prefix='C', count=10):
    """预生成编码池"""
    return [generate_code(model_class, prefix) for _ in range(count)]

# 使用预生成池
code_pool = pre_generate_codes(Customer, 'C', 100)
for i, name in enumerate(customer_names):
    Customer.objects.create(code=code_pool[i], name=name)
```

### 并发场景
```python
from django.db import transaction
from django.db.models import F

@transaction.atomic
def generate_code_concurrent(model_class, prefix='C'):
    """并发场景的编码生成（需配合序列表）"""
    # 这种方式需要 CodeSequence 模型支持
    # 见 evolution.md Phase 3
    pass
```

## 集成示例

### DRF Serializer 集成
```python
from rest_framework import serializers
from utils.code_generator import generate_code

class CustomerSerializer(serializers.ModelSerializer):
    code = serializers.CharField(read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'code', 'name', 'contact']

    def create(self, validated_data):
        validated_data['code'] = generate_code(Customer, 'C')
        return super().create(validated_data)
```

### Admin 集成
```python
from django.contrib import admin
from utils.code_generator import generate_code

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not change and not obj.code:
            obj.code = generate_code(Customer, 'C')
        super().save_model(request, obj, form, change)
```

### Celery Task 集成
```python
from celery import shared_task
from utils.code_generator import generate_code

@shared_task
def async_create_customer(name):
    """异步创建客户"""
    code = generate_code(Customer, 'C')
    Customer.objects.create(code=code, name=name)
    return code
```

## 测试示例

```python
from django.test import TestCase
from utils.code_generator import generate_code
from apps.BDM.customer.models import Customer

class CodeGeneratorTest(TestCase):

    def test_basic_generation(self):
        """测试基础编码生成"""
        code = generate_code(Customer, 'TEST')
        self.assertTrue(code.startswith('TEST'))
        self.assertEqual(len(code), 11)  # TEST + 8位日期 + 3位序号

    def test_sequence_increment(self):
        """测试序号递增"""
        code1 = generate_code(Customer, 'SEQ')
        Customer.objects.create(code=code1)
        code2 = generate_code(Customer, 'SEQ')

        # 提取序号部分比较
        seq1 = int(code1[-3:])
        seq2 = int(code2[-3:])
        self.assertEqual(seq2, seq1 + 1)

    def test_custom_length(self):
        """测试自定义序号长度"""
        code = generate_code(Customer, 'L', sequence_length=5)
        self.assertEqual(len(code.split('L')[-1]), 13)  # 8位日期 + 5位序号
```
