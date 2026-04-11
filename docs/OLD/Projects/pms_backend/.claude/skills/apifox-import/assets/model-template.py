# Django 模型代码模板

from django.db import models


class {{ModelName}}(models.Model):
    """
    {{模型描述}}
    """

    # ===== 字段定义 =====
    # 从 JSON Schema properties 解析生成
    # string -> CharField / TextField
    # integer -> IntegerField
    # number -> FloatField / DecimalField
    # boolean -> BooleanField

    {{field_name}} = models.{{FieldType}}(
        {{options}}  # blank=True, null=True, default=...
    )

    # ===== 外键关联 =====
    # customerId -> customer
    {{related_name}} = models.ForeignKey(
        '{{AppLabel}}.{{RelatedModel}}',
        on_delete=models.CASCADE,
        related_name='{{reverse_relation}}',
        null=True,
        blank=True
    )

    # ===== 标准时间戳 =====
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    # ===== Meta 配置 =====
    class Meta:
        db_table = '{{app_label}}_{{table_name}}'  # 如: bdm_customer
        verbose_name = '{{verbose_name}}'
        verbose_name_plural = '{{verbose_name_plural}}'
        ordering = ['-created_at']

    # ===== 字符串表示 =====
    def __str__(self):
        return self.{{display_field}}
