---
paths:
  - "**/serializers/**/*.py"
  - "**/serializers.py"
---

# 详情序列化器（DetailSerializer）规范

## 字段顺序规范

字段声明**必须**按以下顺序排列，不得随意混排：

1. **基础类型字段**（IntegerField、CharField、BooleanField、DateTimeField 等）
2. **对象/嵌套字段**（SerializerMethodField、嵌套 Serializer）

这样做的目的是让阅读者先掌握标量数据，再理解复杂结构，降低认知负担。

## 正确示例

```python
class DeliverableDetailSerializer(serializers.Serializer):
    """交付物详情序列化器"""
    # 第一部分：基础类型字段
    id = serializers.IntegerField()
    name = serializers.CharField()
    isCompleted = serializers.BooleanField(source='is_completed')
    createdAt = serializers.DateTimeField(source='created_at')

    # 第二部分：对象/嵌套字段
    assignedUser = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    def get_assignedUser(self, obj):
        """获取负责人信息"""
        return {'id': obj.assigned_user_id, 'name': obj.assigned_user.name}

    def get_tags(self, obj):
        """获取标签列表"""
        return list(obj.tags.values('id', 'name'))
```

## 错误示例

```python
# ❌ 对象字段混在基础字段之前
class DeliverableDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    data = serializers.SerializerMethodField()   # ❌ 对象字段不能插在基础字段中间
    name = serializers.CharField()
    isCompleted = serializers.BooleanField(source='is_completed')
    created_at = serializers.DateTimeField()   # ❌ 必须遵循CamelCase命名规范
```
