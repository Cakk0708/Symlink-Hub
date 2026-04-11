---
name: module-resolver
description: 通过检索 references/modules.csv 自动定位 MOM/PMS 系统模块的物理路径。
---

# MOM 模块路径解析专家 (CSV 驱动版)

## 核心任务
当你（Claude）遇到任何模块名称（缩写或中文）时，**必须首先读取** `references/modules.csv`。

## 执行逻辑
1. **读取数据**：使用 `read_file` 工具加载 `references/modules.csv`。
2. **匹配算法**：
   - 将用户输入的关键词与 `Code` 列（忽略大小写）或 `Name` 列进行匹配。
   - 找到匹配行后，提取 `Path` 列的值。
3. **路径补全**：
   - 所有路径均相对于项目根目录。
   - 默认假设核心逻辑（Views/Models）就在该 `Path` 下。

## 交互要求
- **禁止猜测**：如果 CSV 中不存在该模块，请直接询问我，不要编造路径。
- **上下文关联**：一旦确定了模块路径，后续的 `ls` 或 `read_file` 操作应优先在该路径及其子目录下进行。

## 示例
- **用户**：查看“生产报工”的视图。
- **助手**：(读取 CSV 发现 REPREC 对应 /apps/MES/reprec) “好的，正在打开 /apps/MES/reprec/v3/views.py...”