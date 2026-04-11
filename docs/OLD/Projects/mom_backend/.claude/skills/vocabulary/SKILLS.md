---
name: vocabulary
description: 当用户提到项目术语（如"Simple列表"、"扁平化列表"、"扁平化序列化器"、"枚举"、"跟踪检查"、"上查下查"、"单据追溯"）或询问模块物理路径、序列化器定义、枚举定义时，必须调用此技能。
---

# MOM 系统术语词汇表 (Vocabulary)

## 核心原则
在处理任何与以下内容相关的任务时，必须参考对应的术语定义：
- 序列化器
- 枚举定义
- 单据追溯关系
- 模块物理路径

## 术语索引

| 术语 | 别名关键词 | 物理指向 | 子技能 |
|------|-----------|---------|--------|
| **Simple列表** | SimpleSerializer、精简列表、基础字段列表、首页下拉选项、快速查询接口 | `serializers/SimpleSerializer` | `Simple列表/SKILL.md` |
| **扁平化列表** | 扁平化序列化器、ListSerializer、模块首页列表、GET List接口 | `serializers/ListSerializer` | `扁平化列表/SKILL.md` |
| **枚举** | enums.py、枚举接口、Choices、Permissions、Metadata、EntryTrace、字段枚举 | 模块根目录 `enums.py` | `枚举/SKILL.md` |
| **跟踪检查** | 上查、下查、单据追溯、来源单据、下游单据、EntryTrace | `apps/SM/entry_trace/models.py` | `跟踪检查/SKILLS.md` |

## 使用场景

当用户出现以下任一表述时，请调用对应的子技能：

### Simple列表 相关
- "修改Simple列表"
- "调整下拉选项"
- "优化快速查询接口"
- "配置用户自定义排序"
- "设置别名规则"

### 扁平化列表 相关
- "修改扁平化序列化器"
- "调整模块首页列表"
- "优化GET List接口"
- "处理index序号问题"
- "设置默认排序规则"

### 枚举 相关
- "添加枚举选项"
- "修改字段枚举"
- "查看权限枚举"
- "配置元数据枚举"
- "处理EntryTrace"

### 跟踪检查 相关
- "实现上查功能"
- "实现下查功能"
- "追溯单据关系"
- "查询来源单据"
- "查询下游单据"

## 注意事项
1. **物理路径优先**：在定位文件时，优先使用 `module-resolver` 技能获取模块物理路径
2. **术语一致性**：确保代码中使用统一的术语命名，避免混用
3. **标准类遵循**：枚举功能必须包含 Choices/Permissions/Metadata/EntryTrace 四个标准类
