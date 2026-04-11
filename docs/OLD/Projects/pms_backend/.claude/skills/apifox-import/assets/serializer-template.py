# Django REST Framework 序列化器代码模板

from rest_framework import serializers
from .models import {{ModelName}}


class {{ModelName}}Serializer(serializers.ModelSerializer):
    """
    {{模型名称}}序列化器
    """

    # ===== 外键序列化 =====
    {{foreign_key}}_name = serializers.SerializerMethodField()

    class Meta:
        model = {{ModelName}}
        fields = '__all__'
        # 或指定字段：
        # fields = ['id', 'name', 'code', ...]

    def get_{{foreign_key}}_name(self, obj):
        """获取外键关联对象的名称"""
        if obj.{{foreign_key}}:
            return obj.{{foreign_key}}.name
        return None


class {{ModelName}}ListSerializer(serializers.ModelSerializer):
    """
    {{模型名称}}列表序列化器（简化版）
    """
    class Meta:
        model = {{ModelName}}
        fields = ['id', 'name', 'code']  # 列表页只显示核心字段


class {{ModelName}}BatchSerializer(serializers.Serializer):
    """
    批量操作序列化器
    处理 { "models": [...] } 格式的请求
    """
    models = {{ModelName}}Serializer(many=True)

    def create(self, validated_data):
        """批量创建"""
        models_data = validated_data.get('models', [])
        created_objects = []

        for model_data in models_data:
            instance = {{ModelName}}.objects.create(**model_data)
            created_objects.append(instance)

        return {'models': created_objects}
