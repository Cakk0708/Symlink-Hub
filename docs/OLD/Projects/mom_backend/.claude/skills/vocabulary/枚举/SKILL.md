---
name: vocab-enums-list
description: 当用户提到"枚举"、"enums.py"、"枚举接口"、"Choices"、"Permissions"、"Metadata"、"EntryTrace"、"字段枚举"、"列表元数据"、"筛选字段"、"可搜索字段"或要求修改模块权限、添加字段选项时，必须调用此技能以获取正确的物理路径和代码规范。
---

# 术语：枚举功能 (Enums System)

## 触发关键词
- 枚举、enums.py、枚举接口、枚举列表
- Choices（字段枚举）、Permissions（权限枚举）
- Metadata（列表元数据）、ListSerializerMetadata
- EntryTrace（分单/溯源枚举）
- 筛选字段、可搜索字段、可排序字段、DIY排序
- 模块权限、权限代码、RBAC权限


## 1. 物理指向 (Physical Mapping)
- **核心文件**：指代各功能模块根目录下的 `enums.py` 文件。
- **关联接口**：通常对应模块视图中名为 `EnumsView` 或 `/enums/` 的 Action 接口，用于向前端透传元数据。

## 2. 标准枚举类定义 (Standard Classes)
当你处理或生成 `enums.py` 时，必须包含或参考以下四个标准类：

### A. Choices (常用字段枚举)
- **职责**：定义模块内模型字段（如 Status, Type）的合法取值。
- **要求**：必须继承自 `django.db.models.TextChoices` 或 `IntegerChoices`。

### B. Permissions (权限枚举)
- **职责**：穷举该模块所有可用的权限代码（如 `BDM_STOCK_ADD`, `WMS_PURC_VIEW`）。
- **联动**：此处的定义必须与 Django 权限系统或 RBAC 模块的配置保持一致。

### C. ListSerializerMetadata (列表元数据枚举)
- **职责**：**核心术语**。定义“扁平化列表”的结构化行为。
- **属性要求**：每个成员需包含以下配置元组：
    - `display`: 是否在前端表格显示。
    - `filterable/searchable`: 是否允许用户在该字段进行筛选或全局搜索。
    - `sortable`: 是否支持 DIY 排序。
    - `fixed`: 字段是否在前端固定（不可拖动）。

### D. EntryTrace (分单/溯源枚举)
- **职责**：定义具备“下推（Push）”或“上下查（Trace）”能力的模块范围。
- **适用场景**：仅在富有业务流转逻辑的模块（如从“采购订单”下推到“采购入库”）中使用。

## 3. 执行指令 (Instructions)
1. **语义联想**：当用户提到“增加一个筛选字段”时，你应该首先检查 `enums.py` 中的 `ListSerializerMetadata`。
2. **一致性检查**：修改 `models.py` 的字段时，必须主动询问是否同步更新 `enums.py` 中的 `Choices`。
3. **术语对齐**：当用户说“枚举列表”或“枚举接口”时，统一指向 `enums.py` 的整体结构。

## 4. 交互示例
- **用户**：“给报工模块增加一个‘班组’筛选。”
- **助手**：(查阅 `apps/MES/reprec/enums.py`) “好的，我将在 `ListSerializerMetadata` 类中为 `team` 字段添加元数据，并设置 `filterable=True`。”