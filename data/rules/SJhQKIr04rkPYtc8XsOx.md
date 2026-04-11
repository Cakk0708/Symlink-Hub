---
paths:
  - "**/enums/**/*.py"
  - "**/enums.py"
---

## 枚举文件构造要求

### 类型要求

- 必须使用 Django 的 models 方案枚举
- 必须包含 必须作为 Choices 内的子类

### 方法要求

- 必须有输出到列表字段函数供视图向外抛出

## 示例

### 标准枚举示例
```
### 正确示例

```python
class Choices:
    class OperationTypes(models.TextChoices):
        CREATE = 'CREATE', '创建'
        VIEW = 'VIEW', '查看'
        CHANGE = 'CHANGE', '修改'
        DELETE = 'DELETE', '删除'
        DISABLE = 'DISABLE', '禁用'

        @classmethod
        def to_array(cls):
            return [{"value": item.value, "label": item.label} for item in cls]

    @staticmethod
    def output():
        return {
            'operationTypes': Choices.OperationTypes.to_array(),
        }
```
