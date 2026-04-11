# FeishuSheetManager 演进路线图

## 当前状态（v1.0）

### 已实现功能

#### 核心功能
- ✅ 表格元信息获取
- ✅ 工作表查询与管理
- ✅ 单元格数据读写
- ✅ 批量数据操作
- ✅ 单元格样式设置
- ✅ 合并单元格
- ✅ 数据验证（下拉列表）
- ✅ 行列操作

#### API 覆盖
- ✅ Sheets API v2（数据操作）
- ✅ Sheets API v3（元数据操作）

### 当前限制

1. **返回值不一致**
   - 使用 `False` 表示错误
   - 缺少详细错误信息
   - 难以区分错误类型

2. **缺少日志**
   - 仅打印到控制台
   - 无结构化日志
   - 难以追踪问题

3. **无重试机制**
   - 网络失败直接返回
   - 无自动重试
   - 无超时控制

4. **同步阻塞**
   - 所有操作同步执行
   - 大数据量处理慢
   - 无并发支持

5. **类型安全弱**
   - 无类型注解
   - 无参数校验
   - IDE 支持差

## 短期优化（v1.1 - 1~2个月）

### 1. 错误处理改进

**目标：** 统一错误处理机制

**实施方案：**

```python
# 新增异常类
class SheetError(Exception):
    """表格操作基础异常"""
    pass

class SheetAuthError(SheetError):
    """权限错误"""
    pass

class SheetNotFoundError(SheetError):
    """表格不存在"""
    pass

class SheetValidationError(SheetError):
    """参数验证错误"""
    pass

class SheetNetworkError(SheetError):
    """网络错误"""
    pass

# 修改方法返回
def sheet_values_batch_update(self, sheet_token: str, value_ranges: dict) -> bool:
    """更新前：失败返回 False"""
    try:
        # ... 执行操作
        return True
    except requests.RequestException as e:
        raise SheetNetworkError(f"网络请求失败: {e}")
    except json.JSONDecodeError as e:
        raise SheetError(f"JSON 解析失败: {e}")
```

### 2. 日志系统

**目标：** 结构化日志记录

**实施方案：**

```python
import logging
from datetime import datetime

class FeishuSheetManagerWithLogging:
    """带日志的表格管理器"""

    def __init__(self, access_token: str = ''):
        super().__init__(access_token)
        self.logger = logging.getLogger(__name__)

    def sheet_values_batch_update(self, sheet_token: str, value_ranges: dict) -> bool:
        """写入数据（带日志）"""
        operation_id = f"{sheet_token}_{datetime.now().timestamp()}"

        self.logger.info({
            "event": "sheet_write_start",
            "operation_id": operation_id,
            "sheet_token": sheet_token,
            "ranges_count": len(value_ranges.get('valueRanges', []))
        })

        try:
            result = super().sheet_values_batch_update(sheet_token, value_ranges)

            if result:
                self.logger.info({
                    "event": "sheet_write_success",
                    "operation_id": operation_id
                })
            else:
                self.logger.error({
                    "event": "sheet_write_failed",
                    "operation_id": operation_id,
                    "reason": "api_return_false"
                })

            return result

        except Exception as e:
            self.logger.error({
                "event": "sheet_write_error",
                "operation_id": operation_id,
                "error": str(e)
            })
            raise
```

### 3. 参数校验

**目标：** 增强类型安全

**实施方案：**

```python
from typing import List, Dict, Optional
from pydantic import BaseModel, validator

class ValueRangeModel(BaseModel):
    """值范围模型"""
    range: str
    values: List[List[str]]

    @validator('range')
    def validate_range(cls, v):
        """校验范围格式"""
        if not re.match(r'^\w+!\w+:\w+$', v):
            raise ValueError(f"无效的范围格式: {v}")
        return v

class SheetManagerV2:
    """V2 版本管理器"""

    def sheet_values_batch_update(
        self,
        sheet_token: str,
        value_ranges: Dict[str, List[ValueRangeModel]]
    ) -> bool:
        """批量更新（带类型校验）"""
        # Pydantic 自动校验
        pass
```

### 4. 单元测试

**目标：** 提升代码质量

**测试覆盖：**

```python
# tests/sheet_manager/test_sheet_manager.py
import pytest
from utils.openapi.feishu.sheet_manager import FeishuSheetManager

class TestFeishuSheetManager:
    """表格管理器测试"""

    def setup_method(self):
        self.manager = FeishuSheetManager("test_token")

    def test_get_spreadsheet_information_success(self, mocker):
        """测试获取表格信息 - 成功"""
        # Mock API 响应
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'code': 0,
            'data': {
                'spreadsheet': {
                    'spreadsheet_token': 'test_token',
                    'title': 'Test Sheet'
                }
            }
        }

        mocker.patch('requests.request', return_value=mock_response)

        result = self.manager.get_spreadsheet_information('test_token')

        assert result['spreadsheet_token'] == 'test_token'
        assert result['title'] == 'Test Sheet'

    def test_get_spreadsheet_information_api_error(self, mocker):
        """测试获取表格信息 - API 错误"""
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'code': -1, 'msg': 'Error'}

        mocker.patch('requests.request', return_value=mock_response)

        result = self.manager.get_spreadsheet_information('test_token')

        assert result is False
```

## 中期规划（v1.5 - 3~6个月）

### 1. 异步支持

**目标：** 支持 async/await

**实施方案：**

```python
import aiohttp
import asyncio

class AsyncFeishuSheetManager:
    """异步表格管理器"""

    def __init__(self, access_token: str = ''):
        self.access_token = access_token
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get_spreadsheet_information(
        self,
        spreadsheet_token: str
    ) -> Optional[dict]:
        """异步获取表格信息"""
        url = f'https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{spreadsheet_token}'

        async with self.session.get(
            url,
            headers={'Authorization': self.access_token}
        ) as response:
            data = await response.json()

            if data.get('code') == 0:
                return data['data']['spreadsheet']
            return None

# 使用示例
async def main():
    async with AsyncFeishuSheetManager(token) as manager:
        info = await manager.get_spreadsheet_information('token')
        print(info)

asyncio.run(main())
```

### 2. 重试机制

**目标：** 自动重试失败操作

**实施方案：**

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

class FeishuSheetManagerWithRetry(FeishuSheetManager):
    """带重试的表格管理器"""

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(SheetNetworkError)
    )
    def sheet_values_batch_update(
        self,
        sheet_token: str,
        value_ranges: dict
    ) -> bool:
        """批量更新（带重试）"""
        try:
            return super().sheet_values_batch_update(sheet_token, value_ranges)
        except requests.RequestException as e:
            raise SheetNetworkError(f"网络请求失败: {e}")
```

### 3. 批量优化

**目标：** 智能分批处理

**实施方案：**

```python
class BatchOperationHelper:
    """批量操作助手"""

    def __init__(self, manager: FeishuSheetManager, batch_size: int = 1000):
        self.manager = manager
        self.batch_size = batch_size

    def batch_write(
        self,
        sheet_token: str,
        sheet_id: str,
        data: List[List[str]],
        start_cell: str = "A1"
    ) -> bool:
        """分批写入大量数据"""

        total_rows = len(data)
        batches = (total_rows + self.batch_size - 1) // self.batch_size

        for i in range(batches):
            start = i * self.batch_size
            end = min((i + 1) * self.batch_size, total_rows)
            batch_data = data[start:end]

            # 计算范围
            range_str = self._calculate_range(sheet_id, start, len(batch_data[0]), start_cell)

            value_ranges = {
                'valueRanges': [{
                    'range': range_str,
                    'values': batch_data
                }]
            }

            if not self.manager.sheet_values_batch_update(sheet_token, value_ranges):
                return False

        return True
```

### 4. 缓存层

**目标：** 减少重复请求

**实施方案：**

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedFeishuSheetManager(FeishuSheetManager):
    """带缓存的表格管理器"""

    def __init__(self, access_token: str = '', cache_ttl: int = 3600):
        super().__init__(access_token)
        self.cache_ttl = cache_ttl
        self._cache = {}

    def get_spreadsheet_information(self, spreadsheet_token: str) -> Optional[dict]:
        """获取表格信息（带缓存）"""

        # 检查缓存
        cached = self._cache.get(spreadsheet_token)
        if cached:
            data, timestamp = cached
            if datetime.now() - timestamp < timedelta(seconds=self.cache_ttl):
                return data

        # 调用 API
        result = super().get_spreadsheet_information(spreadsheet_token)

        if result:
            self._cache[spreadsheet_token] = (result, datetime.now())

        return result
```

## 长期演进（v2.0 - 6~12个月）

### 1. 事件驱动架构

**目标：** 与业务层解耦

**设计方案：**

```python
# events/sheet_events.py
from enum import Enum
from dataclasses import dataclass
from typing import Any

class SheetEventType(Enum):
    """表格事件类型"""
    SHEET_CREATED = "sheet_created"
    SHEET_UPDATED = "sheet_updated"
    SHEET_DELETED = "sheet_deleted"
    DATA_WRITTEN = "data_written"
    DATA_READ = "data_read"

@dataclass
class SheetEvent:
    """表格事件"""
    type: SheetEventType
    sheet_token: str
    data: Any
    timestamp: datetime

# 管理器集成
class EventDrivenSheetManager(FeishuSheetManager):
    """事件驱动表格管理器"""

    def __init__(self, access_token: str = ''):
        super().__init__(access_token)
        self._event_handlers = []

    def on(self, event_type: SheetEventType):
        """注册事件处理器"""
        def decorator(func):
            self._event_handlers.append((event_type, func))
            return func
        return decorator

    def _emit(self, event: SheetEvent):
        """触发事件"""
        for event_type, handler in self._event_handlers:
            if event_type == event.type:
                handler(event)

    def sheet_values_batch_update(self, sheet_token: str, value_ranges: dict) -> bool:
        """写入数据（触发事件）"""
        result = super().sheet_values_batch_update(sheet_token, value_ranges)

        self._emit(SheetEvent(
            type=SheetEventType.DATA_WRITTEN,
            sheet_token=sheet_token,
            data={'ranges': len(value_ranges.get('valueRanges', []))},
            timestamp=datetime.now()
        ))

        return result
```

### 2. 多租户支持

**目标：** 支持多个飞书应用

**设计方案：**

```python
class TenantConfig:
    """租户配置"""
    app_id: str
    app_secret: str
    folder_token: str

class MultiTenantSheetManager:
    """多租户表格管理器"""

    def __init__(self):
        self._tenants = {}
        self._managers = {}

    def register_tenant(self, tenant_id: str, config: TenantConfig):
        """注册租户"""
        self._tenants[tenant_id] = config

    def get_manager(self, tenant_id: str) -> FeishuSheetManager:
        """获取租户管理器"""

        if tenant_id not in self._managers:
            config = self._tenants[tenant_id]
            token = self._get_tenant_token(config)
            self._managers[tenant_id] = FeishuSheetManager(token)

        return self._managers[tenant_id]

    def _get_tenant_token(self, config: TenantConfig) -> str:
        """获取租户 Token"""
        # 实现租户 Token 获取逻辑
        pass
```

### 3. 监控与告警

**目标：** 可观测性

**实施方案：**

```python
from prometheus_client import Counter, Histogram, Gauge

# 指标定义
sheet_operations_total = Counter(
    'sheet_operations_total',
    '表格操作总数',
    ['operation', 'status']
)

sheet_operation_duration = Histogram(
    'sheet_operation_duration_seconds',
    '表格操作耗时',
    ['operation']
)

sheet_active_operations = Gauge(
    'sheet_active_operations',
    '当前进行中的操作数'
)

class MonitoredSheetManager(FeishuSheetManager):
    """可监控表格管理器"""

    def sheet_values_batch_update(self, sheet_token: str, value_ranges: dict) -> bool:
        """批量更新（带监控）"""

        sheet_active_operations.inc()
        operation_duration = sheet_operation_duration.labels('batch_update').time()

        try:
            result = super().sheet_values_batch_update(sheet_token, value_ranges)

            if result:
                sheet_operations_total.labels('batch_update', 'success').inc()
            else:
                sheet_operations_total.labels('batch_update', 'failed').inc()

            return result

        finally:
            operation_duration.__exit__(None, None, None)
            sheet_active_operations.dec()
```

### 4. 智能限流

**目标：** API 限流保护

**设计方案：**

```python
from asyncio import Semaphore
from datetime import datetime, timedelta

class RateLimitedSheetManager(FeishuSheetManager):
    """限流表格管理器"""

    def __init__(self, access_token: str = '', max_requests: int = 100, window: int = 60):
        super().__init__(access_token)
        self.max_requests = max_requests
        self.window = window
        self._requests = []
        self._semaphore = Semaphore(max_requests)

    async def _acquire_permission(self):
        """获取请求许可"""
        now = datetime.now()

        # 清理过期记录
        self._requests = [
            req_time for req_time in self._requests
            if now - req_time < timedelta(seconds=self.window)
        ]

        # 检查是否超限
        if len(self._requests) >= self.max_requests:
            sleep_time = self.window - (now - self._requests[0]).total_seconds()
            await asyncio.sleep(sleep_time)

        self._requests.append(now)
        await self._semaphore.acquire()

    async def sheet_values_batch_update_async(
        self,
        sheet_token: str,
        value_ranges: dict
    ) -> bool:
        """异步批量更新（带限流）"""
        await self._acquire_permission()

        try:
            # 执行操作
            pass
        finally:
            self._semaphore.release()
```

## 迁移指南

### 从 v1.0 迁移到 v1.1

**步骤 1：** 更新异常处理

```python
# 旧代码
result = manager.sheet_values_batch_update(token, data)
if result is False:
    print("操作失败")

# 新代码
try:
    manager.sheet_values_batch_update(token, data)
except SheetNetworkError as e:
    print(f"网络错误: {e}")
except SheetError as e:
    print(f"操作失败: {e}")
```

**步骤 2：** 启用日志

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 使用带日志的管理器
manager = FeishuSheetManagerWithLogging(token)
```

### 从 v1.1 迁移到 v1.5

**步骤 1：** 使用异步接口

```python
# 旧代码（同步）
def process_sheet():
    manager = FeishuSheetManager(token)
    info = manager.get_spreadsheet_information(sheet_token)
    return info

# 新代码（异步）
async def process_sheet():
    async with AsyncFeishuSheetManager(token) as manager:
        info = await manager.get_spreadsheet_information(sheet_token)
        return info
```

**步骤 2：** 启用重试

```python
# 使用带重试的管理器
manager = FeishuSheetManagerWithRetry(token)
# 自动重试，无需额外代码
```

## 版本兼容性

| 版本 | Python | Django | 飞书 API |
|------|--------|--------|----------|
| v1.0 | 3.10+ | 5.1+ | v2/v3 |
| v1.1 | 3.10+ | 5.1+ | v2/v3 |
| v1.5 | 3.10+ | 5.1+ | v2/v3 |
| v2.0 | 3.11+ | 5.2+ | v2/v3/v4 |

## 废弃计划

### v1.0 功能废弃时间表

| 功能 | 废弃版本 | 替代方案 |
|------|----------|----------|
| 返回 `False` 错误处理 | v1.1 | 异常机制 |
| `print` 日志 | v1.1 | 结构化日志 |
| 同步接口 | v2.0 | 异步接口 |
| 无重试 | v1.5 | 自动重试 |

## 反馈与贡献

欢迎提交反馈和改进建议：

- 问题反馈：GitHub Issues
- 功能建议：GitHub Discussions
- 代码贡献：Pull Requests