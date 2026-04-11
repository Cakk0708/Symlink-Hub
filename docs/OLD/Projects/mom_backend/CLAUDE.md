# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此代码库中工作时提供指导。

## 项目概览

Django 5.1.1 + DRF 后端，用于 MOM（制造运营管理）系统。模块化架构，使用 MySQL 8.0+ 和 Redis。支持 Celery 异步任务和 Django Channels（WebSocket）。

## 常用开发命令

### 环境设置
```bash
# 设置环境（dev, test, prod, dev_fkq, dev_djc, dev_stk, cust_ydl）
python home/set_env.py dev

# 或直接设置环境变量
DJANGO_ENVIRONMENT=dev python manage.py <command>
```

### 开发服务器
```bash
# 运行 HTTP API 服务器（端口 8110）
python manage.py runserver 0.0.0.0:8110

# 运行 WebSocket ASGI 服务器（端口 8101）
daphne -p 8101 home.asgi:application
```

### 数据库操作
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 系统初始化（首次部署）
```bash
python manage.py init_sm_org
python manage.py init_sm_org_user
python manage.py init_sm_content_type_route
python manage.py init_sm_permission
python manage.py init_sm_system_config
```

### Celery（异步任务）
```bash
# 开发环境：worker + beat 一起运行（--pool=solo 用于 macOS/Windows）
celery -A home worker -B -l info --pool=solo

# 生产环境：分离 worker 和 beat
celery -A home worker -l info
celery -A home beat -l info
```

### 测试
```bash
python manage.py test
python manage.py test apps.SM.tests.test_organization
python manage.py test apps.WMS
```

## 工作习惯与协作方式

**重要：执行修改前必须先展示完整计划**

在执行任何涉及多个文件或复杂逻辑的代码修改时，必须遵循以下流程：

1. **先分析问题，理解需求**
2. **制定完整的修改计划** - 列出所有需要修改的文件和具体修改内容
3. **向用户展示修改计划** - 用清晰的格式说明每一步要做什么
4. **等待用户确认** - 必须得到用户明确同意后再执行
5. **执行修改** - 按照计划一次性完成所有修改

**禁止的行为：**
- 逐步执行修改，中途才展示计划
- 在未获用户确认前就开始修改代码
- 修改部分文件后才说明后续步骤

**正确的交互示例：**
```
## 修改计划

针对"分页序号问题"，我计划进行以下修改：

### 1. 修改 apps/SMS/pmconfig/list/utils.py
- 移除第 36-40 行的 `item_index` Window 函数定义

### 2. 修改 apps/SMS/pmconfig/list/serializers.py
- 将 `index` 字段从 `IntegerField` 改为 `SerializerMethodField`
- 在 `__init__` 中添加分页参数获取逻辑
- 添加 `get_index` 方法动态计算序号

是否执行此计划？
```

## 高层架构

### 模块化应用结构

系统在 `apps/` 中按模块组织，每个模块处理特定领域：

| App  | 模块               | 核心职责                         |
|------|-------------------|----------------------------------|
| SM   | 系统管理           | 组织、用户、角色、权限           |
| BDM  | 基础数据管理       | 物料、BOM、供应商、客户          |
| WMS  | 仓库管理           | 即时库存、入库/出库、调拨/形态转换/盘点计划            |
| MES  | 生产执行           | 工单、生产报工                   |
| APS  | 计划与排程         | 需求预测、生产计划               |
| PMS  | 采购管理           | 采购订单、定价                   |
| SMS  | 销售管理           | 销售订单、定价                   |
| VMS  | 可视化             | 数据看板、数据可视化             |

### 配置模式

配置按环境拆分在 `home/settings/` 中：
- `base.py` - 核心配置
- `dev.py`, `test.py`, `prod.py` - 环境特定覆盖
- 通过 `DJANGO_ENVIRONMENT` 变量或 `home/set_env.py` 选择

### Redis 使用（多索引）

Redis 用于不同目的，使用独立索引：
- 索引 0：Django 缓存
- 索引 2：Celery broker（消息队列）
- 索引 3：Django Channels WebSocket 层

### Celery 任务路由

任务按应用路由到队列：
- 主队列：`mom_backend_queue`
- 应用特定：`mom_backend_sm_queue`, `mom_backend_wms_queue` 等

### 标准 API 响应格式

```python
# 成功
JsonResponse({'msg': 'success', 'data': {...}})

# 成功（带分页）
JsonResponse({'msg': 'success', 'data': {'items': [...], 'pagination': {...}}})

# 错误
JsonResponse({'msg': '错误描述', 'errors': {...}}, status=400)

# 未找到
JsonResponse({'msg': '查询目标不存在'}, status=404)
```

## 代码规范

### 导入顺序
```python
# 1. 标准库
import os, re
from datetime import datetime

# 2. Django
from django.db import models
from django.http import JsonResponse

# 3. 第三方库
from rest_framework import serializers
import pytz, pandas

# 4. 本地 - utils 和 assist
from utils.date import to_local_time
from assist import method as views_method, serializer as serializer_func

# 5. 本地 - apps
from apps.SM.models import User
from .models import Organization
from .enums import Choices
```

### 命名规范

| 类型                 | 规范             | 示例              |
|----------------------|------------------|-------------------|
| Models               | PascalCase       | `Organization`    |
| Model 字段           | snake_case       | `org_type`        |
| Serializer 类        | PascalCase       | `ListSerializer`  |
| Serializer 字段      | PascalCase       | `orgType`（前端用） |
| Views                | PascalCase       | `ListViews`       |
| Functions            | snake_case       | `get_list_queryset` |
| Constants            | UPPER_SNAKE_CASE | `REDIS`           |

### Model 模式

- 显式主键：`id = models.AutoField(primary_key=True)`
- 所有字段使用中文 `verbose_name`
- 时间戳：`create_time`, `update_time`
- 通过 `disable_flag` 软删除
- 外键使用 `related_name`

### Serializer 模式

- 字段名使用 PascalCase 供前端使用（如 `orgType` 映射到 `org_type`）
- 使用 `source` 参数进行模型字段映射

### View 模式

视图遵循以下模式：
1. 使用序列化器验证请求参数
2. 使用工具函数获取过滤后的查询集
3. 使用上下文感知的序列化器序列化数据
4. 返回标准化的 JSON 响应

## 时间处理

服务器时区为 `Asia/Shanghai`，`USE_TZ = True`。

```python
# 转换为本地时间用于前端输出（assist/serializer.py）
to_local_time(time_str)  # 返回 '2025-01-10 14:30:00'

# 转换为服务器时间用于存储
to_server_time(time_str)  # 返回时区感知的 datetime
```

## 关键依赖

- Django 5.1.1, DRF 3.15.2
- django-redis 5.4.0（Redis 缓存）
- celery 5.4.0（异步任务）
- channels 4.2.2（WebSocket）
- pymysql 1.1.1（MySQL 驱动）
- pandas 2.2.1（数据处理）

