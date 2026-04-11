---
name: utils-code_generator
description: 通用编码生成工具模块，负责为Django模型生成唯一编码序列。当用户提到"编码生成"、"code生成"、"generate_code"、"唯一编码"、"序列号"、"Customer编码"、"前缀编码"、"日期编码"、"流水号"、"编码规则"或相关术语时激活此技能。
---

# 通用编码生成器 (utils/code_generator)

## 模块定位

`utils/code_generator.py` 是一个独立于业务逻辑的通用工具模块，为 Django 模型提供基于时间与序列的唯一编码生成能力。该模块不依赖任何业务模型，可被任何需要自动生成编码的场景复用。

## 核心职责

1. **编码格式生成**：按照 `前缀 + 日期 + 序号` 的格式生成唯一编码
2. **序列计数**：自动统计当日已有编码数量并生成下一序号
3. **格式化控制**：支持自定义前缀、日期格式、序号位数

## 核心数据模型

无独立数据模型，依赖调用方传入的 Django Model 类。

## 函数签名

```python
def generate_code(
   model_class,
   prefix='C',
   date_format='%Y%m%d',
   sequence_length=3
) -> str
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `model_class` | Django Model | 必填 | 需要生成编码的模型类，必须包含 `code` 字段 |
| `prefix` | str | 'C' | 编码前缀，用于区分不同业务对象 |
| `date_format` | str | '%Y%m%d' | 日期格式，默认为 YYYYMMDD |
| `sequence_length` | int | 3 | 序号位数，不足补零 |

### 返回值

- **类型**: `str`
- **格式**: `{prefix}{date}{sequence}`
- **示例**: `C20250308001`

## 编码生成逻辑

### 1. 日期部分生成
```python
today = datetime.now().strftime(date_format)
code_prefix = f'{prefix}{today}'
```

### 2. 序列计数
```python
today_count = model_class.objects.filter(
   code__startswith=code_prefix
).count()
```

### 3. 序号格式化
```python
sequence = str(today_count + 1).zfill(sequence_length)
return f'{code_prefix}{sequence}'
```

## 与其他模块关系

### 依赖关系
- **Django ORM**: 通过 `model_class.objects.filter()` 查询已有编码
- **datetime**: 用于生成日期部分

### 被依赖模块
- `apps.BDM.customer.models`: Customer 模型使用此函数生成 `C20250308001` 格式编码
- 未来可扩展至 Account、Order、Product 等任何需要编码的模型

## 常见业务场景

### 场景1: 客户编码生成
```python
from apps.BDM.customer.models import Customer
from utils.code_generator import generate_code

customer_code = generate_code(Customer, prefix='C')
# 返回: 'C20250308001'
```

### 场景2: 订单编码生成
```python
from apps.APS.order.models import Order
from utils.code_generator import generate_code

order_code = generate_code(Order, prefix='O', date_format='%Y%m')
# 返回: 'O202503001'
```

### 场景3: 自定义序号位数
```python
# 生成 4 位序号，支持更大数量级
code = generate_code(Customer, prefix='VIP', sequence_length=4)
# 返回: 'VIP202503080001'
```

## 技术实现建议 (Django)

### 1. 模型字段要求
调用此函数的模型必须包含：
```python
class Customer(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name='编码')
```

### 2. 事务安全
在高并发场景下，建议配合 `transaction.atomic` 使用：
```python
from django.db import transaction

@transaction.atomic
def create_customer():
    code = generate_code(Customer, 'C')
    customer = Customer.objects.create(code=code, ...)
```

### 3. 性能优化
对于大量编码查询，可考虑：
- 在 `code` 字段上添加数据库索引
- 使用 `select_for_update()` 防止并发冲突

## 扩展设计策略

### 当前限制
1. **并发安全**: 无锁机制，高并发可能产生重复编码
2. **性能**: 每次生成需查询数据库统计数量
3. **灵活性**: 序列必须从 1 开始，不支持自定义起始值

### 未来演进方向 (Future Evolution)

#### Phase 1: 并发安全增强
```python
from django.db import transaction

@transaction.atomic
def generate_code_safe(model_class, prefix='C', ...):
    # 使用 select_for_update 锁定查询
    today_count = model_class.objects.filter(
        code__startswith=code_prefix
    ).select_for_update().count()
```

#### Phase 2: 缓存优化
```python
from django.core.cache import cache

def generate_code_cached(model_class, prefix='C', ...):
    cache_key = f'code_count_{prefix}_{today}'
    count = cache.get(cache_key)
    if count is None:
        count = model_class.objects.filter(...)
        cache.set(cache_key, count, timeout=3600)
```

#### Phase 3: 序列表方案
创建独立的 `CodeSequence` 模型管理序列：
```python
class CodeSequence(models.Model):
    prefix = models.CharField(max_length=10)
    date = models.DateField()
    count = models.IntegerField(default=0)

    class Meta:
        unique_together = [['prefix', 'date']]
```

#### Phase 4: 分布式支持
- 引入 Redis 分布式锁
- 支持多服务器部署场景
- 使用 Redis INCR 原子操作

## 模块特有名词索引

| 名词 | 定位 | 说明 |
|------|------|------|
| `generate_code` | 核心函数 | 主函数，生成唯一编码 |
| `model_class` | 参数 | Django 模型类，需有 code 字段 |
| `prefix` | 参数 | 编码前缀，区分业务类型 |
| `date_format` | 参数 | 日期格式化字符串 |
| `sequence_length` | 参数 | 序号位数，默认 3 |
| `code_prefix` | 内部变量 | 前缀+日期的组合 |
| `today_count` | 内部变量 | 当日已有编码数量 |
| `sequence` | 内部变量 | 格式化后的序号 |
| `code` | 模型字段 | 目标模型的编码字段名 |
| `zfill` | 方法 | Python 字符串方法，左侧补零 |

## 触发关键词

当用户使用以下术语时，应激活此技能：
- "编码生成"
- "code生成"
- "generate_code"
- "唯一编码"
- "序列号"
- "Customer编码"
- "前缀编码"
- "日期编码"
- "流水号"
- "编码规则"
- "utils/code_generator"
