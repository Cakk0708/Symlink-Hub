---
paths:
  - "**/serializers/**/*.py"
  - "**/serializers.py"
---

# 列表序列化器（ListSerializer）规范

## 字段顺序规范

字段声明**必须**按以下顺序排列，不得随意混排：

1. **基础类型字段**（IntegerField、CharField、BooleanField、DateTimeField 等）
2. **对象/嵌套字段**（SerializerMethodField、嵌套 Serializer）

这样做的目的是让阅读者先掌握标量数据，再理解复杂结构，降低认知负担。

## 正确示例

```python
class DeliverableListSerializer(serializers.ModelSerializer):
    """交付物列表序列化器"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    isCompleted = serializers.BooleanField(source='is_completed')
    createdAt = serializers.DateTimeField(source='created_at')

    class Meta:
        model = Deliverable
        fields = ['id', 'name', 'isCompleted', 'createdAt']
```

## 错误示例

```python
# ❌ 对象字段混在基础字段之前
class DeliverableDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    data = serializers.SerializerMethodField()   # ❌ 必须由查询集直接获取不得构造
    name = serializers.CharField()
    isCompleted = serializers.BooleanField(source='is_completed')
    created_at = serializers.DateTimeField()   # ❌ 必须遵循CamelCase命名规范
```
