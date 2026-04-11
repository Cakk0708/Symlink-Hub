---
name: interservice_api
description: 这个SKILL说明了本项目中与PMS实现数据交互的实现方案，当用户提出“微服务”、“PMS-admin”、“管理后台”时阅读本文档
---


# 微服务间 API 通信技能

## 技能概述

本项目的微服务间通信使用自定义安全协议，基于 JWT + AES 加密实现。包含两个方向：
1. **向外服务发起请求**（如向 PMS 请求数据）
2. **接收外部服务请求**（如 PMS 向我们请求数据）

---

## 目录结构

```
utils/api_security/
├── __init__.py           # 模块入口，导出所有接口
├── protocol.py           # APISecurityProtocol 协议类
├── utils.py              # 工具函数（construct_request）
└── base_views.py         # 视图基类（PMSAPIView 等）

utils/（保留，逐步迁移）
├── api_security_protocol.py  # 旧版协议类
└── api_utils.py               # 旧版工具函数
```

---

## 导入接口

```python
from utils.api_security import (
    # 协议类
    APISecurityProtocol,

    # 工具函数（新）
    request_service,    # 简化版请求函数
    ServiceClient,      # 服务客户端类

    # 工具函数（旧，保留兼容）
    construct_request,

    # 视图基类
    PMSAPIView,      # PMS 服务专用
    MOMAPIView,      # MOM 服务专用
    ServiceAPIView,  # 通用基类

    # 异常
    ServiceAPIException,
)
```

---

## 场景 1：向外服务发起请求（推荐新方式）

当需要从 PMS-Admin 向外部服务（如 PMS）请求数据时使用。

---

### 方式 1：使用 `request_service` 函数（推荐）

适合**简单的一次性请求**，自动处理安全协议、请求发送、响应解析，支持缓存。

```python
from utils.api_security import request_service

# 简单调用
result = request_service(
    url='https://pms-admin-backend.com/bdm/sys/version/current',
    service_name='PMS-ADMIN'
)
if result['success']:
    version_data = result['data']
else:
    error = result['error']

# 带缓存的调用
result = request_service(
    url='/bdm/sys/version/current',
    service_name='PMS-ADMIN',
    cache_key='version:current',
    cache_timeout=600  # 10分钟
)
if result['success']:
    if result.get('from_cache'):
        print('来自缓存')
    version_data = result['data']

# 传递数据
result = request_service(
    url='/bdm/sys/hardware/update',
    data={'project_ids': [1, 2, 3], 'version_id': 5},
    service_name='PMS-ADMIN',
    method='POST'
)
```

**返回格式**：
```python
# 成功
{'success': True, 'data': {...}, 'from_cache': False}

# 失败
{'success': False, 'error': '错误信息'}
```

---

### 方式 2：使用 `ServiceClient` 类（频繁调用时推荐）

适合**需要频繁调用同一服务**的场景，可复用客户端实例，自动管理 base_url。

```python
from django.conf import settings
from utils.api_security import ServiceClient

# 创建客户端（可复用）
pms_admin_client = ServiceClient(
    base_url=settings.PMS_ADMIN_BASE_URL,
    service_name='PMS-ADMIN'
)

# GET 请求
result = pms_admin_client.get('/bdm/sys/version/current')
if result['success']:
    version_data = result['data']

# POST 请求
result = pms_admin_client.post(
    '/bdm/sys/hardware/update',
    data={'project_ids': [1, 2, 3]}
)

# 带缓存的请求
result = pms_admin_client.get(
    '/bdm/sys/version/current',
    cache_key='version:current',
    cache_timeout=600
)

# PATCH 请求
result = pms_admin_client.patch(
    '/bdm/sys/hardware/1',
    data={'status': 'active'}
)
```

**ServiceClient 方法**：
- `get(path, data=None, **kwargs)` - GET 请求
- `post(path, data=None, **kwargs)` - POST 请求
- `patch(path, data=None, **kwargs)` - PATCH 请求
- `put(path, data=None, **kwargs)` - PUT 请求
- `delete(path, **kwargs)` - DELETE 请求

**支持的参数**：
- `cache_key` - 缓存键
- `cache_timeout` - 缓存超时时间（秒）
- `timeout` - 请求超时时间（秒）

---

### 方式 3：使用 `construct_request`（旧方式，保留兼容）

```python
from utils.api_security import APISecurityProtocol, construct_request

security_protocol = APISecurityProtocol()
request_data = security_protocol.generate_request(
    data={},
    service_name='PMS'
)
return construct_request(
    url=url,
    request_data=request_data,
    method='GET'
)
```

---

### 完整示例：获取版本信息

```python
from django.conf import settings
from django.core.cache import cache
from utils.api_security import request_service

# 定义缓存配置
VERSION_CACHE_KEY = 'version:current'
VERSION_CACHE_TIMEOUT = 600  # 10分钟

def get_current_version():
    """获取当前版本信息（带缓存）"""
    result = request_service(
        url=f"{settings.PMS_ADMIN_BASE_URL}/bdm/sys/version/current",
        service_name='PMS-ADMIN',
        cache_key=VERSION_CACHE_KEY,
        cache_timeout=VERSION_CACHE_TIMEOUT
    )

    if result['success']:
        return result['data']
    return None
```

---

### 对比：新旧方式

#### 旧方式（繁琐）

```python
import json
from utils.api_security import APISecurityProtocol, construct_request

url = f"{settings.PMS_ADMIN_BASE_URL}/bdm/sys/version/current"

try:
    security_protocol = APISecurityProtocol()
    request_data = security_protocol.generate_request(
        data={},
        service_name='PMS-ADMIN'
    )

    response = construct_request(url=url, request_data=request_data, method='GET')

    if response.status_code == 200:
        response_data = json.loads(response.content.decode('utf-8'))
        if response_data.get('msg') == 'success' and 'data' in response_data:
            version_data = response_data['data']
            cache.set(VERSION_CACHE_KEY, version_data, VERSION_CACHE_TIMEOUT)
            return version_data
    return None
except Exception:
    return None
```

#### 新方式（简洁）

```python
from utils.api_security import request_service

result = request_service(
    url=f"{settings.PMS_ADMIN_BASE_URL}/bdm/sys/version/current",
    service_name='PMS-ADMIN',
    cache_key='version:current',
    cache_timeout=600
)

return result['data'] if result['success'] else None
```

---

### 配置要求

确保 `settings/<env>.py` 中配置了：
```python
PMS_BASE_URL = 'http://127.0.0.1:8001'  # 或其他环境的 URL
API_SECURITY_PROTOCOL = {
    'PMS': {
        'JWT_SECRET': 'xxx',
        'AES_KEY': 'xxx',
        'AES_IV': 'xxx',
    }
}
```

---

## 场景 2：接收外部服务请求（PMSAPIView 模式）

当 PMS 服务需要向 PMS-Admin 请求数据时使用。

### 文件位置
```
apps/<module>/views.py  # 直接在模块 views.py 中添加
```

### 标准模板

```python
from rest_framework.views import APIView
from django.http import JsonResponse

from utils.api_security import PMSAPIView
from .models import VersionControl
from .serializers import VersionControlToPMSSerializer

class VersionControlPMSView(PMSAPIView):
    """PMS 服务专用版本视图"""

    def get(self, request, *args, **kwargs):
        '''获取当前版本信息'''
        try:
            # 直接使用 request.service_data（已自动解密）
            instance = VersionControl.objects.get(is_current=True)

            return JsonResponse({
                'msg': 'success',
                'data': VersionControlToPMSSerializer(instance).data
            })

        except VersionControl.DoesNotExist:
            return JsonResponse({
                'msg': '当前版本不存在',
                'data': None
            }, status=400)

    def post(self, request, *args, **kwargs):
        '''根据条件查询版本'''
        try:
            # 获取 PMS 传递的参数
            version = request.service_data.get('version')

            queryset = VersionControl.objects.filter(version__icontains=version)
            return JsonResponse({
                'msg': 'success',
                'data': VersionControlToPMSSerializer(queryset, many=True).data
            })
        except Exception as e:
            return JsonResponse({'msg': '查询失败', 'error': str(e)}, status=400)
```

### URL 配置

```python
# apps/<module>/urls.py
from .views import VersionControlPMSView

urlpatterns = [
    # ... 其他路由

    # PMS 专用接口 - 使用 sys 前缀区分
    path('sys/version/current', VersionControlPMSView.as_view()),
]
```

---

## PMS 专用序列化器（可选）

如果返回给 PMS 的数据格式与内部不同，建议创建专用序列化器：

```python
# serializers.py
class VersionControlToPMSSerializer(serializers.ModelSerializer):
    """PMS 专用版本序列化器 - 返回简化数据"""
    version = serializers.CharField()
    isCurrent = serializers.BooleanField(source='is_current')
    remark = serializers.CharField()
    items = serializers.SerializerMethodField()

    class Meta:
        model = VersionControl
        fields = ['id', 'code', 'version', 'isCurrent', 'remark', 'items']

    def get_items(self, obj):
        """获取版本内容项列表"""
        items = obj.get_active_items.order_by('sort').values('content', 'sort')
        return list(items)
```

---

## 完整工作流程示例

### 1. 创建 PMS 专用视图

```python
# apps/BDM/version_control/views.py
from utils.api_security import PMSAPIView
from django.http import JsonResponse
from .models import VersionControl
from .serializers import VersionControlToPMSSerializer

class VersionControlPMSView(PMSAPIView):
    """PMS 获取当前版本信息"""
    def get(self, request, *args, **kwargs):
        instance = VersionControl.objects.get(is_current=True)
        return JsonResponse({
            'msg': 'success',
            'data': VersionControlToPMSSerializer(instance).data
        })
```

### 2. 配置 URL

```python
# apps/BDM/urls.py
from .version_control.views import VersionControlPMSView

urlpatterns = [
    # ... 其他路由
    path('sys/version/current', VersionControlPMSView.as_view()),
]
```

### 3. PMS 服务调用

```python
# PMS 服务端代码
from utils.api_security import APISecurityProtocol
import requests

# 生成安全请求
security_protocol = APISecurityProtocol()
request_data = security_protocol.generate_request(
    data={},  # 传递的数据
    service_name='PMS'
)

# 发送请求
response = requests.post(
    'https://pms-admin-backend.com/bdm/sys/version/current',
    json=request_data
)
```

---

## 最佳实践

### 1. 路由命名规范

```python
# 内部 API：正常命名
path('version/current', VersionControlCurrentView.as_view())

# PMS 专用：使用 sys 前缀区分
path('sys/version/current', VersionControlPMSView.as_view())
```

### 2. 序列化器分离

- 内部 API：`VersionControlSerializer`（完整数据，包含用户信息等）
- PMS API：`VersionControlToPMSSerializer`（简化数据，仅必要字段）

### 3. 错误处理

```python
class VersionControlPMSView(PMSAPIView):
    def get(self, request, *args, **kwargs):
        try:
            instance = VersionControl.objects.get(is_current=True)
            return JsonResponse({'msg': 'success', 'data': ...})
        except VersionControl.DoesNotExist:
            return JsonResponse({'msg': '当前版本不存在'}, status=400)
        except Exception as e:
            return JsonResponse({'msg': '获取失败', 'error': str(e)}, status=400)
```

### 4. 使用 request.service_data

在 PMSAPIView 中，直接使用 `request.service_data` 获取解密后的数据：

```python
def post(self, request, *args, **kwargs):
    # PMS 传递的参数已自动解密到 service_data
    user_id = request.service_data.get('user_id')
    filters = request.service_data.get('filters', {})
```

---

## 与旧代码对比

### 旧方式（手动验证）

```python
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from utils.api_utils import validate_request_from_pms

class GetHardwareSpecView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        # 每次都要手动验证
        decrypted_data = validate_request_from_pms(request)
        ids = decrypted_data.get('ids', [])
        # ... 业务逻辑
```

### 新方式（推荐）

```python
from utils.api_security import PMSAPIView

class GetHardwareSpecView(PMSAPIView):
    def get(self, request, *args, **kwargs):
        # 直接使用 request.service_data，无需手动验证
        ids = request.service_data.get('ids', [])
        # ... 业务逻辑
```

---

## 迁移指南

1. **新接口**：直接使用 `PMSAPIView` 基类
2. **旧接口**：保持不变，逐步按需迁移
3. **原有文件**：`utils/api_security_protocol.py` 和 `utils/api_utils.py` 保留不删除

---

## 常见问题

### Q: request.service_data 和 request.data 有什么区别？

- `request.data`：原始请求数据（加密的：token + encrypted_data）
- `request.service_data`：解密后的业务数据

### Q: 如何调试 PMSAPIView？

在 PMSAPIView 的 `initialize_request` 方法中会自动验证安全协议。如果验证失败，会抛出 `ServiceAPIException`。可以通过查看异常信息定位问题。

### Q: 支持 GET 请求吗？

当前安全协议使用 POST 方法传递加密数据。如果需要 GET，可以：
1. PMS 先调用一个 POST 接口获取数据
2. 或将 GET 参数放到 encrypted_data 中

---

## 扩展：其他服务

### MOM 服务

```python
from utils.api_security import MOMAPIView

class MOMDataCallbackView(MOMAPIView):
    def post(self, request, *args, **kwargs):
        order_id = request.service_data.get('order_id')
        # ... 处理 MOM 回调
```

### 通用服务

```python
from utils.api_security import ServiceAPIView

class CustomServiceView(ServiceAPIView):
    service_name = 'CUSTOM_SERVICE'

    def post(self, request, *args, **kwargs):
        data = request.service_data
        # ... 业务逻辑
```
