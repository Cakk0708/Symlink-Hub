---
paths:
  - "**/views/**/*.py"
  - "**/views.py"
---

## 视图使用规范

- **功能边界**: 所有的视图功能仅能用于沟通 `urls.py` 作为服务层传递数据信息，不直接在服务层设计业务逻辑

## 视图命名规范

所有视图必须严格遵循以下命名约定：

| 用途     | 命名后缀             | 示例                          |
|--------|------------------|------------------------------|
| 写入     | `WriteView`  | `WriteView`  |
| 读取     | `ReadView`   | `ReadView`   |
| 列表     | `ListView`   | `ListView`   |
| 简单列表 | `SimpleView`  | `SimpleView`   |
| 详情     | `DetailView` | `DetailView` |
| 枚举     | `EnumView` | `EnumView` |
| 删除     | `DeleteView` | `DeleteView` |

命名格式：`{模型名}{用途后缀}`，类名使用 PascalCase。

## 视图排序规范

视图类在文件中的顺序必须遵循以下规则：

3. **ListView** - 列表视图（如果存在）
5. **DetailView** - 详情视图（如果存在）
4. **SimpleView** - 简单列表视图（如果存在）
6. **EnumView** - 枚举视图（如果存在）
7. **DeleteView** - 删除视图（如果存在）

如果没有某种类型的视图，则跳过该类型。所有视图类必须按照上述顺序排列在文件中。
