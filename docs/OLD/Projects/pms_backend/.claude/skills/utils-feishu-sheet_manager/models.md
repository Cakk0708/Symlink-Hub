# FeishuSheetManager 数据模型详解

## 概述

本文档详细说明 `FeishuSheetManager` 中使用的各种数据结构和模型定义。

## 核心数据结构

### 1. Spreadsheet（电子表格）

飞书电子表格的顶级容器，包含多个工作表（Sheet）。

#### 属性说明

| 属性 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `spreadsheet_token` | `str` | 表格唯一标识符 | `"L0uBsnjdIh4ORstP6OgcBXXVnvc"` |
| `title` | `str` | 表格标题 | `"项目统计报表"` |
| `url` | `str` | 表格访问链接 | `"https://xxx.feishu.cn/sheets/xxx"` |

#### 获取方式

```python
sheet_manager.get_spreadsheet_information(spreadsheet_token)
```

#### 返回结构

```python
{
    "spreadsheet_token": "表格token",
    "title": "表格标题",
    "url": "表格URL链接"
}
```

### 2. Sheet（工作表）

电子表格中的单个工作表（类似于 Excel 的工作表）。

#### 属性说明

| 属性 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `sheet_id` | `str` | 工作表唯一标识 | `"6e5ed3"` |
| `title` | `str` | 工作表标题 | `"销售数据"` |
| `index` | `int` | 工作表索引位置 | `0` |
| `hidden` | `bool` | 是否隐藏 | `false` |
| `frozen_row_count` | `int` | 冻结行数 | `1` |
| `frozen_col_count` | `int` | 冻结列数 | `0` |

#### 获取方式

```python
# 获取所有工作表
sheets = sheet_manager.sheet_get_detail(spreadsheet_token)

# 获取单个工作表信息
sheet_info = sheet_manager.sheet_get_info(spreadsheet_token, sheet_id)
```

#### 返回结构（列表）

```python
[
    {
        "sheet_id": "6e5ed3",
        "title": "Sheet1",
        "index": 0,
        "hidden": false
    },
    {
        "sheet_id": "Q7PlXT",
        "title": "Sheet2",
        "index": 1,
        "hidden": false
    }
]
```

### 3. ValueRange（值范围）

表示表格中一个连续的单元格范围及其数据。

#### 属性说明

| 属性 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `range` | `str` | 单元格范围 | `"sheet_id!A1:C3"` |
| `values` | `list[list]` | 二维数组数据 | `[["A1", "B1"], ["A2", "B2"]]` |

#### 范围表示法

飞书使用以下格式表示单元格范围：

```
{sheet_id}!{start_col}{start_row}:{end_col}{end_row}
```

示例：
- `sheet1!A1` - 单个单元格
- `sheet1!A1:C3` - 矩形范围
- `sheet1!A:A` - 整列
- `sheet1!1:1` - 整行

#### 写入数据结构

```python
{
    'valueRanges': [
        {
            'range': 'sheet1!A1:C1',
            'values': [
                ['标题1', '标题2', '标题3']
            ]
        },
        {
            'range': 'sheet1!A2:C2',
            'values': [
                ['数据1', '数据2', '数据3']
            ]
        }
    ]
}
```

#### 读取数据结构

```python
# 单个范围
['A1', 'B1', 'C1']

# 多个范围
[
    ['A1', 'B1', 'C1'],
    ['A2', 'B2', 'C2']
]
```

### 4. CellStyle（单元格样式）

定义单个单元格或单元格范围的样式。

#### 完整样式结构

```python
{
    "font": {
        "bold": True,              # 加粗
        "italic": False,           # 斜体
        "fontSize": "12pt",        # 字号
        "foreColor": "#000000",    # 字体颜色
        "clean": False             # 清除格式
    },
    "textDecoration": 0,           # 文本装饰
    "formatter": "",              # 格式化公式
    "hAlign": 0,                  # 水平对齐 (0:左, 1:中, 2:右)
    "vAlign": 0,                  # 垂直对齐 (0:上, 1:中, 2:下)
    "foreColor": "#000000",       # 前景色
    "backColor": "#ffffff",       # 背景色
    "borderType": "FULL_BORDER",  # 边框类型
    "borderColor": "#ff0000",     # 边框颜色
    "clean": False                # 清除样式
}
```

#### 边框类型

| 值 | 说明 |
|------|------|
| `FULL_BORDER` | 全边框 |
| `BORDER_BOTTOM` | 底边框 |
| `BORDER_TOP` | 上边框 |
| `BORDER_LEFT` | 左边框 |
| `BORDER_RIGHT` | 右边框 |

#### 批量设置样式

```python
style_data = [
    {
        "ranges": ["sheet1!A1:C1", "sheet2!A2:B6"],
        "style": {
            "font": {"bold": True, "fontSize": "12pt"},
            "hAlign": 1,  # 居中
            "backColor": "#f0f0f0"
        }
    }
]

sheet_manager.sheet_styles_batch_update(sheet_token, style_data)
```

### 5. SheetProtection（工作表保护）

控制工作表的编辑权限。

#### 保护结构

```python
{
    "lock": "LOCK",           # 锁定类型
    "lockInfo": "说明信息",   # 锁定说明
    "userIDs": [              # 可编辑用户ID列表
        "ou_48d0958ee4b2ab3eaf0b5f6c968abcef"
    ]
}
```

#### 锁定类型

| 值 | 说明 |
|------|------|
| `LOCK` | 锁定工作表 |
| `UNLOCK` | 解锁工作表 |

### 6. DataValidation（数据验证）

为单元格设置数据验证规则，如下拉列表。

#### 下拉列表结构

```python
{
    "validation": {
        "sheetId": "sheet_id",
        "ranges": [{"startIndex": 0, "endIndex": 10}],  # 行范围
        "condition": {
            "type": "TEXT_IS_ONE_OF",
            "values": ["选项1", "选项2", "选项3"]
        }
    }
}
```

#### 验证类型

| 类型 | 说明 | 值示例 |
|------|------|--------|
| `TEXT_IS_ONE_OF` | 下拉列表 | `["A", "B", "C"]` |
| `NUMBER_BETWEEN` | 数值范围 | `[1, 100]` |
| `TEXT_CONTAINS` | 包含文本 | `"关键词"` |

### 7. Dimension（维度范围）

用于行/列操作的范围定义。

#### 结构说明

```python
{
    "dimension": {
        "sheetId": "sheet_id",
        "majorDimension": "ROWS",     # ROWS: 行, COLUMNS: 列
        "startIndex": 3,              # 起始索引（从0开始）
        "endIndex": 7                 # 结束索引（不包含）
    }
}
```

#### 使用示例

```python
# 删除第3-6行
sheet_manager.sheet_delete_rows_columns(
    sheet_token, sheet_id,
    major_dimension="ROWS",
    start_index=3,
    end_index=7
)
```

### 8. SheetOperation（工作表操作）

工作表的增删改查操作请求。

#### 新增工作表

```python
{
    "addSheet": {
        "properties": {
            "title": "新工作表",
            "index": 1
        }
    }
}
```

#### 更新工作表

```python
{
    "updateSheet": {
        "properties": {
            "sheetId": "sheet_id",
            "title": "新标题",
            "index": 2,
            "hidden": True,
            "frozenColCount": 2,
            "frozenRowCount": 1
        }
    }
}
```

#### 复制工作表

```python
{
    "copySheet": {
        "source": {
            "sheetId": "source_sheet_id"
        },
        "destination": {
            "title": "副本"
        }
    }
}
```

#### 删除工作表

```python
{
    "deleteSheet": {
        "sheetId": "sheet_id"
    }
}
```

#### 批量操作

```python
requests = [
    {"addSheet": {...}},
    {"updateSheet": {...}},
    {"deleteSheet": {...}}
]

sheet_manager.sheet_spreadsheets_update(sheet_token, requests)
```

### 9. MergeCells（合并单元格）

合并单元格的请求结构。

#### 结构说明

```python
{
    "mergeType": "MERGE_ALL",      # 合并类型
    "sheetId": "sheet_id",
    "dimension": {
        "majorDimension": "ROWS",
        "startIndex": 0,
        "endIndex": 2
    }
}
```

#### 合并类型

| 值 | 说明 |
|------|------|
| `MERGE_ALL` | 全部合并 |
| `MERGE_ROWS` | 按行合并 |
| `MERGE_COLUMNS` | 按列合并 |

### 10. CreateSheetRequest（创建表格）

创建新电子表格的请求结构。

#### 结构说明

```python
{
    "title": "表格标题",
    "folder_token": "文件夹token"
}
```

#### 返回结构

```python
{
    "spreadsheet": {
        "spreadsheet_token": "新表格token",
        "title": "表格标题",
        "url": "表格URL"
    }
}
```

## API 版本差异

### v2 vs v3

| 功能 | v2 | v3 |
|------|----|----|
| 获取表格信息 | - | ✓ |
| 查询工作表 | ✓ | ✓ |
| 读写数据 | ✓ | - |
| 样式设置 | ✓ | - |
| 工作表操作 | ✓ | ✓ |

### 版本选择建议

- **使用 v3**：获取表格元信息
- **使用 v2**：数据读写、样式设置

## 类型注解

### Python TypedDict 定义

```python
from typing import TypedDict, List

class SpreadsheetInfo(TypedDict):
    spreadsheet_token: str
    title: str
    url: str

class SheetInfo(TypedDict):
    sheet_id: str
    title: str
    index: int
    hidden: bool

class ValueRange(TypedDict):
    range: str
    values: List[List[str]]

class CellStyle(TypedDict):
    font: dict
    foreColor: str
    backColor: str
    hAlign: int
    vAlign: int
```

## 常见数据转换

### DataFrame 转换

```python
import pandas as pd

def dataframe_to_value_ranges(df: pd.DataFrame, sheet_id: str, start_cell: str = "A1") -> dict:
    """将 Pandas DataFrame 转换为 ValueRange 格式"""
    values = df.values.tolist()
    # 添加表头
    values.insert(0, df.columns.tolist())

    return {
        'valueRanges': [{
            'range': f'{sheet_id}!{start_cell}',
            'values': values
        }]
    }
```

### 列表转换

```python
def list_to_value_ranges(data: list, sheet_id: str, start_cell: str = "A1") -> dict:
    """将列表转换为 ValueRange 格式"""
    return {
        'valueRanges': [{
            'range': f'{sheet_id}!{start_cell}',
            'values': data if isinstance(data[0], list) else [data]
        }]
    }
```

## 最佳实践

### 1. 数据校验

```python
def validate_value_ranges(data: dict) -> bool:
    """校验 ValueRange 数据结构"""
    if 'valueRanges' not in data:
        return False

    for item in data['valueRanges']:
        if 'range' not in item or 'values' not in item:
            return False

    return True
```

### 2. 范围计算

```python
def calculate_range(sheet_id: str, rows: int, cols: int, start: str = "A1") -> str:
    """计算数据范围"""
    # 实现 Excel 列号转字母
    # A=1, B=2, ..., Z=26, AA=27, ...
    pass
```

### 3. 批量处理

```python
def chunk_value_ranges(data: list, chunk_size: 1000) -> list:
    """将大数据分块"""
    chunks = []
    for i in range(0, len(data), chunk_size):
        chunks.append(data[i:i + chunk_size])
    return chunks
```

## 错误处理

### 常见错误码

| 错误码 | 说明 | 处理方式 |
|--------|------|----------|
| `99991663` | 无权限 | 检查 Token 权限 |
| `99991401` | 表格不存在 | 检查 spreadsheet_token |
| `99991400` | 参数错误 | 检查请求参数格式 |
| `99991365` | 超出限制 | 分批处理数据 |

### 错误响应结构

```python
{
    "code": 错误码,
    "msg": "错误信息"
}
```