---
paths:
  - "**/views/**/*.py"
  - "**/views.py"
---

# 视图设计规范

## 核心要求

- 返回体使用 JsonResponse 构造

## 枚举视图

### 命名规范

- 枚举视图类名使用 `EnumView` 后缀
- 例如：`RuleEnumView`

### 正确示例

- enums.py
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
            return [{"value": member.value, "label": member.label} for member in cls]

    @staticmethod
    def output():
        return {
            'operationTypes': Choices.OperationTypes.to_array(),
        }

```

- views.py
```python
from .enums import Choices

class CustomerEnumView(APIView):
    """客户枚举数据视图"""

    def get(self, request):
        """获取枚举数据"""
        return Response({
            'msg': 'success',
            'data': {
                'choices': Choices.output(),
            }
        })
```

### 错误示例

- 没有统一放在 Choices 类中

```python
class OrderStatus(models.TextChoices):
    """订单状态枚举"""
    WAITING = 'waiting', '等待'
    IN_PROGRESS = 'doing', '进行中'


class OrderCategory(models.TextChoices):
    """订单分类枚举"""
    EXP = 'exp', '经验'
    GEMS = 'gems', '宝石'


class OrderBusiness(models.TextChoices):
    """订单业务类型枚举"""
    PAID = 'paid', '付费'
    FREE = 'free', '免费'
```
