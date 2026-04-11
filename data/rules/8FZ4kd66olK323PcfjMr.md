---
paths:
  - "**/serializers/**/*.py"
  - "**/serializers.py"
---

# � 简单序列化器（SimpleSerializer）规范

## 字段顺序规范

字段声明**必须**按以下顺序排列，不得随意混排：

1. **基础类型字段**（IntegerField、CharField、BooleanField、DateTimeField 等）
2. **对象/嵌套字段**（SerializerMethodField、嵌套 Serializer）

这样做的目的是让阅读者先掌握标量数据，再理解复杂结构，降低认知负担。

## 正确示例

```python
class SimpleSerializer(serializers.ModelSerializer):
    """部门简化序列化器 - 只返回 id, code, name"""
    class Meta:
        model = Department
        fields = ['id', 'code', 'name']
```
