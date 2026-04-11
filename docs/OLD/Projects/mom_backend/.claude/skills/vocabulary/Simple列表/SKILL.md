---
name: vocab-simple-list
description: 当用户提到"Simple列表"、"SimpleSerializer"、"精简列表"、"基础字段列表"、"首页下拉选项"、"快速查询接口"或要求修改"用户自定义排序"、"别名规则"时，必须调用此技能以获取正确的物理路径和功能定义。
---

# 术语：Simple列表 (Simple List)

## 触发关键词
- Simple列表、SimpleSerializer
- 精简列表、基础字段列表、核心字段接口
- 首页下拉选项、选择器接口、快速查询接口
- 用户自定义排序、别名规则、字段配置


## 1. 物理指向 (Physical Mapping)
- **目标文件**：指代各功能模块 `serializers/` 目录下的 `SimpleSerializer` 类。
- **关联视图**：该序列化器通常被对应模块 `views.py` 中以 `Simple` 命名的 Action 或接口调用。

## 2. 功能逻辑与职责 (Core Responsibilities)
当处理“Simple列表”相关的代码时，必须遵循以下业务准则：
- **精简输出**：仅包含最核心的基础字段（如 ID, Name, Code），严禁包含复杂的嵌套数据，以确保极速响应。
- **快速过滤**：应配合后端 FilterSet 实现高频字段的精确或模糊查询。
- **系统配置适配 (MOM/PMS 特有)**：
    - **用户 DIY 排序**：代码中必须体现对系统配置项中自定义排序规则（Ordering）的支持。
    - **别名规则 (Alias)**：支持通过系统配置动态重命名输出字段（如将 `name` 输出为 `display_title`）。

## 3. 开发规范 (Implementation Rules)
1. **序列化器继承**：`SimpleSerializer` 应继承自项目的基础简易类（如 `BaseSimpleSerializer`），避免冗余逻辑。
2. **字段定义**：在 `Meta` 类中明确指定 `fields`，而非使用 `__all__`。
3. **性能要求**：禁止在 Simple 列表中触发 `SerializerMethodField` 中的复杂数据库查询。

## 4. 交互示例 (Usage Examples)
- **用户**：“帮我把 BDM 模块的 Simple 列表增加一个‘状态’字段。”
- **助手**：(查阅 CSV 确认 BDM 路径) “好的，我将修改 `/apps/BDM/serializers/` 下的 `SimpleSerializer` 类，并确保它能响应别名规则。”

## 5. 关联知识
- 如果涉及路径查找，请结合 `module-resolver` 技能使用。