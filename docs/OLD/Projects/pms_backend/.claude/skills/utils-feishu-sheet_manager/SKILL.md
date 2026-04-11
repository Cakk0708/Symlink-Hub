---
name: utils-feishu-sheet_manager
description: 飞书电子表格（Sheets）API 统一管理器，负责表格创建、数据读写、样式设置等操作。当用户提到"表格"、"Sheet"、"电子表格"、"飞书表格"、"spreadsheet"、"sheet_manager"、"表格数据"、"表格样式"、"报表生成"时激活此技能。
---

# FeishuSheetManager 模块技能文档

## 模块定位

`FeishuSheetManager` 是飞书电子表格（Sheets）API 的统一管理器，位于 `utils/openapi/feishu/sheet_manager.py`，作为 PMS 系统与飞书表格操作的中间层。

**核心定位：**
- 飞书表格操作的专用工具类
- 提供表格创建、读取、写入、样式设置等完整功能
- 支持多工作表（Sheet）的批量操作
- 为项目交付物模板、报表生成等业务提供底层支持

## 模块职责边界

### 核心职责

1. **表格元信息管理**
   - 获取表格基础信息（标题、所有者、URL 等）
   - 查询工作表列表
   - 获取单个工作表属性

2. **数据读写操作**
   - 读取单元格/范围数据
   - 批量写入多个范围数据
   - 支持单范围和批量范围查询

3. **表格结构操作**
   - 创建新表格（指定文件夹）
   - 新增/删除/复制工作表
   - 更新工作表属性（标题、索引、隐藏、冻结行列等）
   - 删除行/列
   - 合并单元格

4. **样式与格式**
   - 批量设置单元格样式（字体、颜色、边框、对齐等）
   - 设置数据验证（如下拉列表）

5. **表格保护**
   - 设置工作表保护（锁定、指定可编辑用户）

### 职责边界

**包含：**
- 飞书 Sheets API v2/v3 的封装
- 表格结构操作
- 单元格数据读写
- 样式格式设置

**不包含：**
- 飞书文件操作（由 `FeishuFileManager` 负责）
- 飞书 Token 管理（由 `FeishuTokenManager` 负责）
- 飞书认证（由 `FeishuAuthManager` 负责）
- 业务逻辑（应由业务层调用此模块）

## 核心数据模型

### 1. Spreadsheet（电子表格）

```python
{
    "spreadsheet_token": "表格唯一标识",
    "title": "表格标题",
    "url": "表格访问链接"
}
```

### 2. Sheet（工作表）

```python
{
    "sheet_id": "工作表ID",
    "title": "工作表标题",
    "index": 0,  # 索引位置
    "hidden": False  # 是否隐藏
}
```

### 3. ValueRange（值范围）

```python
{
    "range": "sheet_id!A1:C3",  # 范围表示法
    "values": [
        ["行1列1", "行1列2", "行1列3"],
        ["行2列1", "行2列2", "行2列3"]
    ]
}
```

### 4. Style（单元格样式）

```python
{
    "font": {
        "bold": True,
        "italic": False,
        "fontSize": "10pt/1.5"
    },
    "foreColor": "#000000",
    "backColor": "#ffffff",
    "borderType": "FULL_BORDER",
    "borderColor": "#ff0000",
    "hAlign": 0,  # 水平对齐
    "vAlign": 0   # 垂直对齐
}
```

## 权限验证流程

### Token 管理

`FeishuSheetManager` 不直接管理 Token，而是依赖注入：

```python
# 推荐用法：配合 FeishuTokenManager
from utils.openapi.feishu.token_manager import FeishuTokenManager
from utils.openapi.feishu.sheet_manager import FeishuSheetManager

token_manager = FeishuTokenManager()
sheet_manager = FeishuSheetManager(
    access_token=token_manager.get_tenant_token()
)
```

### 权限要求

飞书表格操作需要以下应用权限：
- `sheets:spreadsheet` - 查看、评论和导出电子表格
- `sheets:spreadsheet.write` - 编辑电子表格

### 错误处理

所有方法在失败时返回 `False`，并打印错误信息：

```python
result = sheet_manager.sheet_values_batch_update(token, data)
if result is False:
    # 处理失败情况
    pass
```

## 与其他模块关系

### 依赖关系

```
FeishuSheetManager
    ├── 依赖 ──> FeishuTokenManager (Token 管理)
    └── 依赖 ──> settings (飞书应用配置)
```

### 被依赖模块

1. **PSC/deliverable/template** - 交付物定义模板
   - 验证飞书表格模板有效性
   - 获取表格标题信息

2. **PM/report** - 项目报表
   - 生成项目统计报表
   - 写入报表数据到表格

3. **PM/tasks** - 项目任务
   - 创建项目报表表格
   - 更新表格数据

### 协作模块

- **FeishuFileManager** - 文件管理器（文件上传、移动、复制、删除）
- **FeishuAuthManager** - 认证管理器（OAuth 登录）

## 常见业务场景

### 场景 1：创建项目报表表格

```python
# 在指定文件夹创建新表格
sheet_token = sheet_manager.sheet_create(
    name="项目统计报表",
    folder_token=folder_token
)
```

### 场景 2：批量写入报表数据

```python
# 准备数据
value_ranges = {
    'valueRanges': [
        {
            'range': f'{sheet_id}!A1:C1',
            'values': [['项目', '状态', '负责人']]
        },
        {
            'range': f'{sheet_id}!A2:C2',
            'values': [['项目A', '进行中', '张三']]
        }
    ]
}

# 批量写入
sheet_manager.sheet_values_batch_update(sheet_token, value_ranges)
```

### 场景 3：设置报表样式

```python
# 设置表头样式
style_data = [{
    'ranges': [f'{sheet_id}!A1:C1'],
    'style': {
        'font': {'bold': True, 'fontSize': '12pt'},
        'backColor': '#f0f0f0',
        'hAlign': 1  # 居中
    }
}]

sheet_manager.sheet_styles_batch_update(sheet_token, style_data)
```

### 场景 4：验证表格模板

```python
# 验证飞书表格是否有效
sheet_info = sheet_manager.get_spreadsheet_information(spreadsheet_token)
if sheet_info:
    title = sheet_info.get('title', '')
    # 表格有效，可以使用
```

### 场景 5：读取表格数据

```python
# 读取单个范围
data = sheet_manager.sheet_get_range(
    spreadsheet_token=token,
    ranges='sheet1!A1:C10'
)

# 批量读取多个范围
data = sheet_manager.sheet_get_range(
    spreadsheet_token=token,
    ranges='sheet1!A1:C10,sheet1!E1:E10'
)
```

## 技术实现建议（Django）

### 1. 初始化管理器

```python
# services/feishu_sheet_service.py
from utils.openapi.feishu.token_manager import FeishuTokenManager
from utils.openapi.feishu.sheet_manager import FeishuSheetManager

class FeishuSheetService:
    """飞书表格服务类"""

    def __init__(self):
        self.token_manager = FeishuTokenManager()
        self.sheet_manager = FeishuSheetManager(
            self.token_manager.get_tenant_token()
        )

    def create_report_sheet(self, title, folder_token):
        """创建报表表格"""
        return self.sheet_manager.sheet_create(title, folder_token)
```

### 2. 异步操作

对于耗时的表格操作，使用 Celery 异步处理：

```python
# tasks/feishu_sheet_tasks.py
@shared_task
def generate_project_report(project_id):
    """异步生成项目报表"""
    service = FeishuSheetService()
    # 执行报表生成逻辑
    pass
```

### 3. 错误处理

```python
def safe_sheet_operation(func):
    """表格操作装饰器"""
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if result is False:
            logger.error(f"表格操作失败: {func.__name__}")
            raise SheetOperationError("表格操作失败")
        return result
    return wrapper
```

### 4. 缓存策略

对于频繁读取的表格元信息，建议使用缓存：

```python
from django.core.cache import cache

def get_sheet_info_cached(spreadsheet_token):
    cache_key = f'sheet:info:{spreadsheet_token}'
    info = cache.get(cache_key)

    if not info:
        sheet_manager = FeishuSheetManager(
            FeishuTokenManager.get_tenant_token()
        )
        info = sheet_manager.get_spreadsheet_information(spreadsheet_token)
        cache.set(cache_key, info, timeout=3600)  # 1小时

    return info
```

## 扩展设计策略

### 1. 操作日志

建议添加操作日志记录：

```python
class FeishuSheetManagerWithLogging(FeishuSheetManager):
    """带日志的表格管理器"""

    def sheet_values_batch_update(self, sheet_token, value_ranges):
        logger.info(f"写入表格数据: {sheet_token}")
        result = super().sheet_values_batch_update(sheet_token, value_ranges)
        if result:
            logger.info(f"写入成功: {sheet_token}")
        else:
            logger.error(f"写入失败: {sheet_token}")
        return result
```

### 2. 重试机制

对网络操作添加自动重试：

```python
from tenacity import retry, stop_after_attempt, wait_fixed

class FeishuSheetManagerWithRetry(FeishuSheetManager):

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    def sheet_values_batch_update(self, sheet_token, value_ranges):
        return super().sheet_values_batch_update(sheet_token, value_ranges)
```

### 3. 批量操作优化

对于大量数据，分批处理：

```python
def batch_write_data(sheet_manager, sheet_token, data, batch_size=100):
    """分批写入数据"""
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        # 执行批量写入
        pass
```

### 4. 类型安全

使用 TypedDict 增强类型安全：

```python
from typing import TypedDict

class SpreadsheetInfo(TypedDict):
    spreadsheet_token: str
    title: str
    url: str

def get_spreadsheet_information(self, spreadsheet_token: str) -> SpreadsheetInfo:
    # 实现逻辑
    pass
```

## 演进方向（Future Evolution）

### 短期优化

1. **统一返回值**
   - 当前使用 `False` 表示失败，建议改用异常机制
   - 提供 `SheetOperationError` 异常类

2. **完善错误信息**
   - 记录详细的错误上下文
   - 区分不同类型的错误（权限、网络、数据格式等）

3. **添加单元测试**
   - 覆盖核心方法
   - Mock API 响应

### 中期规划

1. **异步支持**
   - 支持 `async/await` 调用方式
   - 与 Celery 任务更好集成

2. **批量操作优化**
   - 实现智能分批
   - 并发处理独立操作

3. **数据校验**
   - 添加参数校验
   - 数据格式校验

### 长期演进

1. **事件驱动**
   - 表格变更事件通知
   - 与业务层解耦

2. **多租户支持**
   - 支持多个飞书应用
   - 租户隔离

3. **监控与告警**
   - 操作成功率监控
   - 异常告警机制

## 模块特有名词索引

| 名词 | 定位 | 说明 |
|------|------|------|
| `spreadsheet_token` | 表格标识 | 飞书电子表格的唯一标识符 |
| `sheet_id` | 工作表ID | 表格内单个工作表的标识 |
| `valueRanges` | 值范围 | 批量写入时的数据结构 |
| `styleData` | 样式数据 | 单元格样式配置 |
| `range` | 范围 | 单元格范围表示法（如 `A1:C3`） |
| `frozen` | 冻结 | 冻结行列配置 |
| `dataValidation` | 数据验证 | 下拉列表等数据验证规则 |

## 快速上手

```python
# 1. 导入模块
from utils.openapi.feishu.token_manager import FeishuTokenManager
from utils.openapi.feishu.sheet_manager import FeishuSheetManager

# 2. 初始化
token_manager = FeishuTokenManager()
sheet_manager = FeishuSheetManager(token_manager.get_tenant_token())

# 3. 创建表格
sheet_token = sheet_manager.sheet_create("新表格", folder_token)

# 4. 写入数据
value_ranges = {
    'valueRanges': [{
        'range': f'{sheet_id}!A1',
        'values': [['Hello', 'World']]
    }]
}
sheet_manager.sheet_values_batch_update(sheet_token, value_ranges)

# 5. 设置样式
style_data = [{
    'ranges': [f'{sheet_id}!A1:B1'],
    'style': {'font': {'bold': True}}
}]
sheet_manager.sheet_styles_batch_update(sheet_token, style_data)
```

## 注意事项

1. **API 版本**
   - 模块同时使用 Sheets API v2 和 v3
   - 注意不同版本的接口差异

2. **权限范围**
   - 确保飞书应用已开通表格相关权限
   - Token 需要有足够的操作权限

3. **性能优化**
   - 批量操作优于单个操作
   - 大数据量考虑分批处理

4. **错误处理**
   - 所有方法失败返回 `False`
   - 注意检查返回值

5. **线程安全**
   - 实例方法非线程安全
   - 多线程环境需创建独立实例