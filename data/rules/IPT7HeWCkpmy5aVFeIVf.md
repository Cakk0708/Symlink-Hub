---
paths:
  - "**/serializers/**/*.py"
  - "**/serializers.py"
---

# 序列化器命名规范

所有序列化器必须严格遵循以下命名约定：

| 用途     | 命名后缀             | 示例                          |
|--------|------------------|------------------------------|
| 写入     | `Write`  | `WriteSerializer`  |
| 读取     | `Read`   | `ReadSerializer`   |
| 列表     | `List`   | `ListSerializer`   |
| 详情     | `Detail` | `DetailSerializer` |
| 删除     | `Delete` | `DeleteSerializer` |
| 列表参数处理     | `ListParams` | `ListParamsSerializer` |

命名格式：`{模型名}{用途后缀}`，模型名使用 PascalCase。
