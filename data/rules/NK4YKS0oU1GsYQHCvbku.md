---
paths:
  - "**/serializers/**/*.py"
  - "**/serializers.py"
---

# 删除序列化器（DeleteSerializer）规范

## 字段规范

- **必须**包含 `ids` 字段用于批量删除，禁止只接受单个 `id`
- `ids` **必须**是 `ListField` 类型
- `ids` 的 `child` **必须**是 `PrimaryKeyRelatedField`，并带有 `queryset` 参数，用于自动校验 ID 是否存在
- `ids` **必须**设置 `required=True` 及中文 `error_messages`

## 正确示例

```python
class UserDeleteSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(
            queryset=User.objects.all()
        ),
        required=True,
        error_messages={'required': 'ids 不能为空'}
    )

   def validate_ids(self, value):
      """验证ID列表及关联账户"""
        if not value:
            raise serializers.ValidationError('ids 不能为空')

        for customer in value:
            if customer.accounts.exists():
                raise serializers.ValidationError(
                    f'客户"{customer.name}"存在关联账户，无法删除'
                )

      return value
   
   def execute(self, data):
        """执行删除操作"""
        for instance in data.get('ids'):
            instance.delete()
   
```

## 错误示例

```python
# ❌ 使用单个 id 而非批量 ids
class UserDeleteSerializer(serializers.Serializer):
    id = serializers.IntegerField()

# ❌ child 未使用 PrimaryKeyRelatedField，无法校验记录是否存在
class UserDeleteSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.IntegerField()
    )

# ❌ 缺少 required 和 error_messages
class UserDeleteSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    )
```
