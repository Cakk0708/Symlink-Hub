---
paths:
  - "**/models/**/*.py"
  - "**/models.py"
---

## 模型构造要求

### Meta 要求

- 必须包含 Meta.verbose_name
- 必须包含 Meta.db_table
- 必须包含 Meta.default_permissions = () 定义空权限
- class Meta 顺序必须在模型最后，必须包含两行空格

### 字段要求

- 不得使用 models.ManyToManyField 定义字段，多对多只能使用 models.ForeignKey 形式

## 示例

### 标准模型示例
```
class DeliverableInstance(models.Model):


    class Meta:
        verbose_name = '模型中文名'
        db_table = 'PM_deliverable_instance'
        default_permissions = ()
```
