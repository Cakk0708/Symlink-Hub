---
paths:
  - "**/serializers/**/*.py"
  - "**/serializers.py"
---

# 写入序列化器（WriteSerializer）规范

## 字段规范

- 所有向外暴露的字段**必须**使用 camelCase 命名
- 每个 camelCase 字段**必须**通过 `source` 参数映射到 snake_case 的模型字段
- 涉及外键或关联模型的 ID 字段**必须**使用 `PrimaryKeyRelatedField` 类型，禁止使用 `IntegerField` 代替

## 正确示例

```python
class DeliverableWriteSerializer(serializers.Serializer):
    """创建交付物序列化器"""
    projectNodeId = serializers.PrimaryKeyRelatedField(
        source='project_node',
        queryset=ProjectNode.objects.all(),
        error_messages=serializer_func.error_data
    )
    assignedUserId = serializers.PrimaryKeyRelatedField(
        source='assigned_user',
        queryset=User.objects.all(),
        error_messages=serializer_func.error_data
    )
```

## 错误示例

```python
# ❌ 字段名未使用 camelCase
project_node_id = serializers.PrimaryKeyRelatedField(...)

# ❌ 缺少 source 参数
projectNodeId = serializers.PrimaryKeyRelatedField(
    queryset=ProjectNode.objects.all()
)

# ❌ ID 字段不应使用 IntegerField
projectNodeId = serializers.IntegerField()
```
