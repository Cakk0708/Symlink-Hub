# Code Generator 演进路线图

## 当前状态 (v1.0)

**实现方式**: 数据库计数查询
**适用场景**: 低并发、单服务器部署
**核心限制**: 无并发保护、性能依赖数据库查询

---

## Phase 1: 并发安全增强 (v1.5)

### 目标
解决高并发场景下的编码重复问题

### 实现方案
```python
from django.db import transaction

@transaction.atomic
def generate_code_safe(
    model_class,
    prefix='C',
    date_format='%Y%m%d',
    sequence_length=3
):
    """并发安全的编码生成"""
    today = datetime.now().strftime(date_format)
    code_prefix = f'{prefix}{today}'

    # 使用 select_for_update 锁定查询
    today_count = model_class.objects.filter(
        code__startswith=code_prefix
    ).select_for_update().count()

    sequence = str(today_count + 1).zfill(sequence_length)
    return f'{code_prefix}{sequence}'
```

### 风险
- 数据库锁可能导致性能下降
- 长事务风险

---

## Phase 2: 缓存优化 (v2.0)

### 目标
减少数据库查询次数，提升性能

### 实现方案
```python
from django.core.cache import cache

def generate_code_cached(
    model_class,
    prefix='C',
    date_format='%Y%m%d',
    sequence_length=3,
    cache_timeout=3600
):
    """带缓存的编码生成"""
    today = datetime.now().strftime(date_format)
    cache_key = f'code_seq_{prefix}_{today}'

    # 原子递增缓存值
    count = cache.incr(cache_key)

    if count is None:
        # 缓存未初始化，从数据库加载
        db_count = model_class.objects.filter(
            code__startswith=f'{prefix}{today}'
        ).count()
        count = cache.set(cache_key, db_count + 1, timeout=cache_timeout)

    sequence = str(count).zfill(sequence_length)
    return f'{prefix}{today}{sequence}'
```

### 风险
- 缓存失效可能导致序号不连续
- 多服务器部署时缓存不同步

---

## Phase 3: 序列表模型 (v2.5)

### 目标
引入独立的序列管理模型，实现更好的可控性

### 实现方案
```python
from django.db import models

class CodeSequence(models.Model):
    """编码序列管理表"""
    prefix = models.CharField(max_length=10, verbose_name='前缀')
    date = models.DateField(verbose_name='日期')
    count = models.IntegerField(default=0, verbose_name='当前序号')

    class Meta:
        unique_together = [['prefix', 'date']]
        verbose_name = '编码序列'

    @classmethod
    def get_next_sequence(cls, prefix, date):
        """获取下一个序列号"""
        obj, created = cls.objects.get_or_create(
            prefix=prefix,
            date=date,
            defaults={'count': 1}
        )
        if not created:
            obj.count += 1
            obj.save()
        return obj.count

def generate_code_with_model(
    model_class,
    prefix='C',
    date_format='%Y%m%d',
    sequence_length=3
):
    """基于序列表的编码生成"""
    from datetime import date

    today_str = datetime.now().strftime(date_format)
    today = datetime.now().date()

    if date_format == '%Y%m%d':
        seq_date = today
    else:
        # 处理其他日期格式
        seq_date = today

    sequence = CodeSequence.get_next_sequence(prefix, seq_date)
    return f'{prefix}{today_str}{str(sequence).zfill(sequence_length)}'
```

### 优势
- 序列状态可追溯
- 支持手动调整序列
- 便于监控和调试

---

## Phase 4: 分布式方案 (v3.0)

### 目标
支持多服务器部署，使用分布式锁保证一致性

### 实现方案 (Redis)
```python
from django_redis import get_redis_connection

def generate_code_distributed(
    model_class,
    prefix='C',
    date_format='%Y%m%d',
    sequence_length=3
):
    """分布式环境下的编码生成"""
    redis = get_redis_connection('default')
    today = datetime.now().strftime(date_format)
    key = f'code_seq:{prefix}:{today}'

    # Redis INCR 原子操作
    sequence = redis.incr(key)

    # 设置过期时间（可选）
    if sequence == 1:
        redis.expire(key, 86400 * 7)  # 7天过期

    return f'{prefix}{today}{str(sequence).zfill(sequence_length)}'
```

### 优势
- 天然分布式支持
- 高性能
- 原子操作保证一致性

### 风险
- 依赖 Redis 可用性
- 序列可能不连续（Redis重启）

---

## Phase 5: 高级特性 (v3.5)

### 5.1 自定义序列范围
```python
def generate_code_with_range(
    model_class,
    prefix='C',
    start=100,
    end=999,
    ...
):
    """支持自定义序列范围的编码生成"""
    pass
```

### 5.2 业务规则嵌入
```python
def generate_code_with_rules(
    model_class,
    prefix='C',
    rules=None,  # {'exclude_weekend': True, 'skip_numbers': [4, 13]}
    ...
):
    """支持业务规则的编码生成"""
    pass
```

### 5.3 批量生成
```python
def generate_code_batch(
    model_class,
    prefix='C',
    batch_size=10,
    ...
):
    """批量生成编码，用于批量创建场景"""
    pass
```

---

## 迁移建议

### 当前 -> Phase 1
- 在现有函数外添加 `generate_code_safe`
- 保持向后兼容
- 在高并发场景使用新函数

### Phase 1 -> Phase 2
- 评估缓存方案可行性
- 监控缓存命中率
- 准备缓存降级方案

### Phase 2 -> Phase 3
- 创建 CodeSequence 模型及迁移
- 数据迁移脚本：初始化历史序列
- 逐步替换调用点

### Phase 3 -> Phase 4
- 引入 Redis 依赖
- 灰度切换
- 保留序列表作为备份
