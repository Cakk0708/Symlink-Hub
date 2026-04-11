# Django 模型模板：支持 generate_code

## 标准模型定义

```python
from django.db import models

class YourModel(models.Model):
    """模型描述

    此模型使用 utils/code_generator.py 的 generate_code 函数
    自动生成唯一编码。
    """
    # 编码字段（必须）
    code = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        verbose_name='编码',
        help_text='系统自动生成，格式：前缀+日期+序号'
    )

    # 业务字段
    name = models.CharField(max_length=100, verbose_name='名称')
    # ... 其他字段

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'your_table'
        verbose_name = '您的模型'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.code} - {self.name}'
```

## 使用 Signal 自动生成编码

```python
from django.db.models.signals import pre_save
from django.dispatch import receiver
from utils.code_generator import generate_code

@receiver(pre_save, sender=YourModel)
def auto_generate_code(sender, instance, **kwargs):
    """保存前自动生成编码"""
    if not instance.code:
        instance.code = generate_code(
            sender,
            prefix='Y',  # 根据业务调整前缀
            date_format='%Y%m%d',
            sequence_length=3
        )
```

## 重写 save 方法

```python
class YourModel(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name='编码')
    name = models.CharField(max_length=100, verbose_name='名称')
    # ...

    def save(self, *args, **kwargs):
        if not self.code:
            from utils.code_generator import generate_code
            self.code = generate_code(
                self.__class__,
                prefix='Y'
            )
        super().save(*args, **kwargs)
```

## DRF Serializer 集成模板

```python
from rest_framework import serializers
from .models import YourModel
from utils.code_generator import generate_code

class YourModelSerializer(serializers.ModelSerializer):
    """序列化器：自动生成编码"""

    class Meta:
        model = YourModel
        fields = ['id', 'code', 'name', 'created_at']
        read_only_fields = ['code', 'created_at']

    def create(self, validated_data):
        """创建时自动生成编码"""
        validated_data['code'] = generate_code(
            YourModel,
            prefix='Y'
        )
        return super().create(validated_data)
```

## Admin 集成模板

```python
from django.contrib import admin
from .models import YourModel

@admin.register(YourModel)
class YourModelAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'created_at']
    list_filter = ['created_at']
    search_fields = ['code', 'name']
    readonly_fields = ['code']

    def save_model(self, request, obj, form, change):
        """保存时自动生成编码"""
        if not change and not obj.code:
            from utils.code_generator import generate_code
            obj.code = generate_code(YourModel, prefix='Y')
        super().save_model(request, obj, form, change)
```

## 完整示例：Customer 模型

```python
from django.db import models

class Customer(models.Model):
    """客户模型：使用编码生成器"""

    # 编码字段
    code = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        verbose_name='客户编码',
        help_text='格式：C + YYYYMMDD + 3位序号'
    )

    # 业务字段
    name = models.CharField(max_length=100, verbose_name='客户名称')
    category = models.CharField(
        max_length=20,
        choices=[('normal', '普通'), ('vip', 'VIP')],
        default='normal',
        verbose_name='客户类别'
    )

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'bdm_customer'
        verbose_name = '客户'
        verbose_name_plural = '客户'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.code} - {self.name}'

    def save(self, *args, **kwargs):
        if not self.code:
            from utils.code_generator import generate_code
            prefix = 'V' if self.category == 'vip' else 'C'
            self.code = generate_code(
                self.__class__,
                prefix=prefix,
                date_format='%Y%m%d',
                sequence_length=3
            )
        super().save(*args, **kwargs)
```
