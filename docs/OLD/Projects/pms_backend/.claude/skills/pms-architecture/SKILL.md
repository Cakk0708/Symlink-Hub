---
name: pms-architecture
description: PMS与PMS-Admin双系统架构说明，包括两个项目的职责划分、数据流向、微服务通信机制（JWT+AES安全协议）。当用户询问"管理后台"、"PMS-Admin"、"微服务"、"配置中心"或涉及跨项目数据交互时触发此技能。
---

# PMS 双系统架构技能

## 简介

本系统由两个独立的 Django 项目组成，通过微服务架构协同工作：

- **PMS-Admin (管理后台)**：配置中心，负责管理所有可配置的业务规则
- **PMS (主系统)**：执行系统，使用 PMS-Admin 提供的配置数据运行实际业务

## 项目对比

| 特性 | PMS (主系统) | PMS-Admin (管理后台) |
|------|-------------|---------------------|
| **项目路径** | `/Users/ly/Code/pms_backend` | `/Users/ly/Code/pms-admin_backend` |
| **端口** | 8001 (Django), 8000 (WebSocket) | 8050 |
| **数据库** | PMS | PMS_ADMIN |
| **核心定位** | 项目执行系统 | 配置管理中心 |
| **用户识别** | 飞书 open_id | 自定义 User 模型 + JWT |
| **环境配置** | `dev`, `test`, `prod`, `dev_fkq` | `dev`, `test`, `prod`, `dev_fkq` |

## 职责划分

### PMS-Admin 负责配置的内容

1. **节点规则配置** (`PM/node_rule/`)
   - 项目流程节点规则定义
   - 节点类型、状态流转规则
   - 节点评审规则

2. **评价项配置** (`PM/evaluate/`)
   - 评估模板
   - 评估项定义
   - 评分规则

3. **硬件规格配置** (`PM/hardware_spec/`)
   - 硬件分类
   - 硬件规格版本管理

4. **项目角色配置** (`PM/project_role/`)
   - 项目角色定义
   - 角色权限分配

5. **版本管理** (`BDM/version_control/`)
   - 系统版本发布记录
   - 版本内容更新管理

### PMS 负责执行的功能

1. **项目全生命周期管理**
   - 项目列表、详情
   - 项目启动、执行、完成

2. **节点执行**
   - 应用 PMS-Admin 配置的节点规则
   - 节点状态流转
   - 节点催办、通知

3. **评估执行**
   - 应用 PMS-Admin 配置的评价项
   - 绩效评价

4. **硬件管理**
   - 使用 PMS-Admin 配置的硬件规格
   - 硬件信息管理

5. **飞书集成**
   - 用户认证（open_id）
   - 消息推送
   - 审批流程

## 微服务通信机制

### 安全协议

两个项目之间通过自定义 **API 安全协议** 通信，基于 **JWT + AES 加密**：

```
PMS ←→ PMS-Admin
  ↓
生成请求: JWT Token + AES加密业务数据
  ↓
传输: POST /api/endpoint
  ↓
验证: 验证JWT签名 + AES解密数据
  ↓
返回: JSON Response
```

### 通信方向

#### 方向 1：PMS → PMS-Admin（获取配置）

**场景**：PMS 需要获取节点规则、评价项、硬件规格等配置数据

**推荐方式**：使用 `request_service()` 函数或 `ServiceClient` 类

```python
from utils.api_security import request_service

# 简单调用
result = request_service(
    url='http://127.0.0.1:8050/pm/node_rule/list',
    service_name='PMS-ADMIN'
)

# 带缓存调用
result = request_service(
    url='/pm/node_rule/list',
    service_name='PMS-ADMIN',
    cache_key='node_rule:all',
    cache_timeout=600
)

# POST 请求
result = request_service(
    url='/pm/hardware/update',
    data={'project_ids': [1, 2, 3]},
    service_name='PMS-ADMIN',
    method='POST'
)
```

**使用 ServiceClient（频繁调用时推荐）**：

```python
from utils.api_security import ServiceClient
from django.conf import settings

# 创建客户端（可复用）
admin_client = ServiceClient(
    base_url=settings.PMS_ADMIN_BASE_URL,
    service_name='PMS-ADMIN'
)

# GET 请求
result = admin_client.get('/pm/node_rule/list')

# POST 请求
result = admin_client.post('/pm/hardware/update', data={...})
```

#### 方向 2：PMS-Admin → PMS（回调/通知）

**场景**：PMS-Admin 需要通知 PMS 配置已更新

**使用基类**：`PMSAPIView`

```python
from utils.api_security import PMSAPIView
from django.http import JsonResponse

class ConfigUpdateNotifyView(PMSAPIView):
    """PMS 配置更新通知接口"""
    def post(self, request, *args, **kwargs):
        # 直接使用 request.service_data（已自动解密）
        config_type = request.service_data.get('config_type')
        config_id = request.service_data.get('config_id')

        # 处理配置更新通知...

        return JsonResponse({'msg': 'success', 'data': {...}})
```

## URL 命名规范

### PMS-Admin 对外接口（供 PMS 调用）

使用 `sys/` 前缀标识微服务接口：

```python
# apps/PM/urls.py (PMS-Admin)
urlpatterns = [
    # 内部管理接口
    path('node_rule/list', NodeRuleListView.as_view()),

    # PMS 专用接口 - 使用 sys 前缀
    path('sys/node_rule/active', NodeRulePMSView.as_view()),
    path('sys/evaluate/template/current', EvaluateTemplatePMSView.as_view()),
]
```

### PMS 接收 PMS-Admin 调用

```python
# apps/API/urls.py (PMS)
urlpatterns = [
    # PMS-Admin 回调接口
    path('callback/config/update', ConfigUpdateCallbackView.as_view()),
]
```

## 配置要求

两个项目的 `settings/<env>.py` 中都需要配置：

### PMS 配置

```python
# PMS-Admin 服务地址
PMS_ADMIN_BASE_URL = 'http://127.0.0.1:8050'

# API 安全协议
API_SECURITY_PROTOCOL = {
    'PMS-ADMIN': {
        'JWT_SECRET': 'xxx',
        'AES_KEY': 'xxx',
        'AES_IV': 'xxx',
    }
}
```

### PMS-Admin 配置

```python
# PMS 服务地址
PMS_BASE_URL = 'http://127.0.0.1:8001'

# API 安全协议
API_SECURITY_PROTOCOL = {
    'PMS': {
        'JWT_SECRET': 'xxx',
        'AES_KEY': 'xxx',
        'AES_IV': 'xxx',
    }
}
```

## 关键文件位置

### PMS (主系统)

```
pms_backend/
├── utils/api_security_protocol.py    # API安全协议（旧版，兼容保留）
└── utils/api_security/               # API安全协议（新版）
    ├── protocol.py                   # APISecurityProtocol 协议类
    ├── utils.py                      # request_service, ServiceClient
    └── base_views.py                 # PMSAPIView, ServiceAPIView
```

### PMS-Admin (管理后台)

```
pms-admin_backend/
├── utils/api_security_protocol.py    # API安全协议（旧版，兼容保留）
└── utils/api_security/               # API安全协议（新版，结构同PMS）
    ├── protocol.py
    ├── utils.py
    └── base_views.py
```

## 常见使用场景

### 场景 1：PMS 获取当前有效的节点规则

```python
# PMS 代码
from utils.api_security import request_service
from django.conf import settings

def get_active_node_rules():
    """获取PMS-Admin中当前有效的节点规则"""
    result = request_service(
        url=f"{settings.PMS_ADMIN_BASE_URL}/pm/sys/node_rule/active",
        service_name='PMS-ADMIN',
        cache_key='node_rule:active',
        cache_timeout=600  # 10分钟缓存
    )

    if result['success']:
        return result['data']
    return []
```

### 场景 2：PMS-Admin 通知 PMS 配置已更新

```python
# PMS-Admin 代码
from utils.api_security import APISecurityProtocol
import requests

def notify_pms_config_update(config_type, config_id):
    """通知PMS配置已更新"""
    security_protocol = APISecurityProtocol()
    request_data = security_protocol.generate_request(
        data={'config_type': config_type, 'config_id': config_id},
        service_name='PMS'
    )

    response = requests.post(
        f"{settings.PMS_BASE_URL}/api/callback/config/update",
        json=request_data
    )
```

## 开发注意事项

1. **环境一致性**：两个项目切换环境时保持同步（dev ↔ dev, test ↔ test）
2. **缓存策略**：配置类数据建议使用缓存，减少跨服务调用
3. **错误处理**：微服务调用失败时应有降级方案
4. **序列化器分离**：PMS-Admin 中为 PMS 调用创建专用序列化器（如 `ToPMSSerializer`）
5. **日志记录**：记录跨服务调用日志，便于调试

## 相关文档

- **微服务 API 通信详细文档**：`.claude/skills/interservice_api/SKILL.md`
- **PMS 项目说明**：`CLAUDE.md`
- **PMS-Admin 项目说明**：`/Users/ly/Code/pms-admin_backend/README.md`