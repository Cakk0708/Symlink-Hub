---
name: utils-feishu-auth_manager
description: 飞书认证管理器模块专家，负责飞书 OAuth 认证流程、授权码换取 Token、刷新用户访问令牌等核心认证功能。封装了 exchange_code（授权码换访问令牌）、refresh_access_token（刷新令牌）等飞书开放平台认证相关 API。当用户提到"飞书认证"、"FeishuAuthManager"、"exchange_code"、"refresh_access_token"、"授权码换 token"、"飞书登录"、"飞书 OAuth"、"access_token 刷新"或相关术语时激活此技能。
---

# 飞书认证管理器 (FeishuAuthManager) 模块文档

## 模块定位

`FeishuAuthManager` 是飞书开放平台认证流程的核心封装模块，位于 `utils/openapi/feishu/auth_manager.py`。它负责处理飞书 OAuth 2.0 认证流程中的关键步骤，包括授权码换取访问令牌、刷新过期令牌等操作。

该模块是飞书集成认证层的基础组件，与 `FeishuTokenManager`（Token 管理）和 `FeishuUserManager`（用户信息）协同工作，共同构成完整的飞书认证体系。

## 模块职责边界

**核心职责：**
- 封装飞书 OAuth 认证流程的 API 调用
- 处理授权码（authorization code）换取访问令牌
- 处理访问令牌（access_token）刷新逻辑
- 提供统一的认证相关错误处理和日志记录

**边界划分：**
- **FeishuAuthManager**：认证流程的 API 调用（授权、换取 token、刷新 token）
- **FeishuTokenManager**：Token 的缓存管理、有效期判断、自动刷新
- **FeishuUserManager**：获取用户信息、批量获取用户、获取用户部门信息

## 核心数据模型

### API 端点常量

```python
_ENDPOINT_EXCHANGE_CODE = 'https://open.feishu.cn/open-apis/authen/v1/oidc/access_token'
_ENDPOINT_REFRESH_TOKEN = 'https://open.feishu.cn/open-apis/authen/v1/oidc/refresh_access_token'
```

### 返回数据结构

**exchange_code 返回：**
```python
{
    'access_token': 'xxx',      # 用户访问令牌
    'refresh_token': 'yyy',     # 刷新令牌
    'token_type': 'Bearer'      # 令牌类型
}
```

**refresh_access_token 返回：**
```python
{
    'access_token': 'new_xxx',  # 新的访问令牌
    'refresh_token': 'new_yyy', # 新的刷新令牌
    'token_type': 'Bearer'      # 令牌类型
}
```

## 认证流程说明

### 完整 OAuth 认证流程

```
┌─────────┐                ┌──────────────┐                ┌─────────────┐
│ 前端应用 │                │ Django 后端  │                │  飞书平台   │
└────┬────┘                └──────┬───────┘                └──────┬──────┘
     │                            │                               │
     │ 1. 点击登录                  │                               │
     ├───────────────────────────>│                               │
     │                            │ 2. 重定向到飞书授权页           │
     ├──────────────────────────────────────────────────────────>│
     │                            │                               │
     │ 3. 用户授权                 │                               │
     │                            │                               │
     │ 4. 回调 + code + state      │                               │
     ├──────────────────────────────────────────────────────────>│
     │                            │                               │
     │                            │ 5. exchange_code(code)       │
     │                            ├──────────────────────────────>│
     │                            │                               │
     │                            │ 6. 返回 access_token          │
     │                            │<──────────────────────────────┤
     │                            │                               │
     │                            │ 7. 获取用户信息                │
     │                            ├──────────────────────────────>│
     │                            │                               │
     │                            │ 8. 返回用户信息                │
     │                            │<──────────────────────────────┤
     │                            │                               │
     │ 9. 返回 JWT Token           │                               │
     │<───────────────────────────┤                               │
     │                            │                               │
```

### 核心方法详解

#### 1. exchange_code(cls, code: str) -> Optional[Dict]

**功能**：通过飞书 OAuth 授权码换取访问令牌

**参数**：
- `code`: 飞书授权回调返回的授权码

**返回**：
- 成功：`{'access_token': str, 'refresh_token': str, 'token_type': str}`
- 失败：`None`

**使用示例**：
```python
from utils.openapi.feishu import FeishuAuthManager

# OAuth 回调中
token_data = FeishuAuthManager.exchange_code('auth_code_from_callback')
if token_data:
    access_token = token_data['access_token']
    refresh_token = token_data['refresh_token']
```

**错误处理**：
- 网络异常：记录 `logger.error`，返回 `None`
- API 错误（code != 0）：记录错误响应，返回 `None`

#### 2. refresh_access_token(cls, refresh_token: str) -> Optional[Dict]

**功能**：使用刷新令牌获取新的访问令牌

**参数**：
- `refresh_token`: 刷新令牌

**返回**：
- 成功：包含新 token 的字典
- 失败：`None`

**使用示例**：
```python
# Token 过期时刷新
new_tokens = FeishuAuthManager.refresh_access_token(old_refresh_token)
if new_tokens:
    # 更新存储的 token
    access_token = new_tokens['access_token']
    refresh_token = new_tokens['refresh_token']
```

#### 3. format_token(cls, token_type: str, access_token: str) -> str

**功能**：格式化 token 为 HTTP Authorization header 格式

**参数**：
- `token_type`: 令牌类型（如 "Bearer"）
- `access_token`: 访问令牌

**返回**：格式化后的字符串（如 "Bearer xxx"）

## 权限验证说明

本模块不涉及业务权限验证，仅处理飞书平台的 API 认证。

### 认证与授权的区别

**认证**：
- 验证用户身份（Who are you?）
- 由 FeishuAuthManager 处理
- 涉及：登录、Token 获取、Token 刷新

**授权**：
- 验证用户权限（What can you do?）
- 由 SM/authority 模块处理
- 涉及：角色、权限、资源访问控制

## 与其他模块关系

### 依赖模块

```
utils/openapi/feishu/
├── auth_manager.py    (本模块) - 认证流程 API
├── token_manager.py   - Token 缓存和管理
├── user_manager.py    - 用户信息获取
└── file_manager.py    - 文件操作
```

### 调用关系

**被调用方**：
- `apps/API/auth/views.py` - OAuth 登录视图
- `assists/feishu.py` - 旧版飞书接口（兼容层）

**协作方**：
- `FeishuTokenManager`：提供 tenant token 用于认证请求
- `FeishuUserManager`：使用 access token 获取用户信息

## 常见业务场景

### 场景 1：飞书 OAuth 登录

**流程**：
1. 前端重定向到飞书授权页
2. 用户授权后回调，携带 `code` 和 `state`
3. 后端使用 `FeishuAuthManager.exchange_code(code)` 换取 token
4. 使用 token 调用 `FeishuUserManager.get_user_info()` 获取用户信息
5. 创建/更新本地用户记录
6. 返回 JWT token 给前端

**代码位置**：`apps/API/auth/views.py:FeishuOAuthCallbackView`

### 场景 2：用户 Token 自动刷新

**触发条件**：
- 用户 access_token 即将过期（提前 5 分钟）
- API 调用返回 401 未授权

**处理方式**：
- `FeishuTokenManager` 检测到 token 即将过期
- 调用 `FeishuAuthManager.refresh_access_token()` 刷新
- 更新数据库中的 token 记录

### 场景 3：多租户 Token 管理

**需求**：
- tenant_access_token（应用级）
- app_access_token（应用级，用于刷新用户 token）
- user_access_token（用户级）

**职责划分**：
- `FeishuTokenManager`：管理 tenant 和 app token
- `FeishuAuthManager`：处理用户 token 认证流程
- `UserFeishu` 模型：存储用户 token

## 技术实现建议

### 错误处理

```python
try:
    token_data = FeishuAuthManager.exchange_code(code)
    if not token_data:
        # 处理换取失败
        return error_response("授权码无效或已过期")
except Exception as e:
    # 处理异常
    logger.error(f"认证异常: {e}")
    return error_response("认证服务异常")
```

### Token 存储建议

```python
# UserFeishu 模型存储
class UserFeishu(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=512)
    refresh_token = models.CharField(max_length=512)
    token_type = models.CharField(max_length=32, default='Bearer')
    expires_at = models.DateTimeField()  # Token 过期时间
```

### 日志记录

```python
import logging

logger = logging.getLogger(__name__)

# 记录认证操作
logger.info(f"用户 {open_id} Token 刷新成功")
logger.error(f"Token 刷新失败: {response}")
```

## 扩展设计策略

### 支持多平台认证

当前设计支持扩展到其他 OAuth 平台：

```python
# 未来可以抽象为统一接口
class BaseOAuthManager:
    @classmethod
    def exchange_code(cls, code: str) -> Optional[Dict]:
        raise NotImplementedError

    @classmethod
    def refresh_access_token(cls, refresh_token: str) -> Optional[Dict]:
        raise NotImplementedError

class FeishuAuthManager(BaseOAuthManager):
    # 飞书实现
    pass

class WechatAuthManager(BaseOAuthManager):
    # 企业微信实现（未来）
    pass
```

### Token 失效处理

```python
# 建议添加 token 撤销方法
@classmethod
def revoke_token(cls, access_token: str) -> bool:
    """撤销用户 token（登出时调用）"""
    # 调用飞书撤销 API
    pass
```

## 演进方向

### 短期优化

1. **增强错误处理**：
   - 区分不同错误类型（网络、API、业务）
   - 提供更详细的错误信息

2. **添加重试机制**：
   - 对于网络错误自动重试
   - 指数退避策略

3. **性能优化**：
   - 连接池复用
   - 请求超时优化

### 中期规划

1. **监控告警**：
   - Token 刷新成功率监控
   - 认证耗时监控
   - 失败告警

2. **安全加固**：
   - Token 加密存储
   - 敏感信息脱敏日志

3. **多实例支持**：
   - 支持多个飞书应用
   - 租户隔离

### 长期愿景

1. **统一认证中心**：
   - 抽象统一认证接口
   - 支持多种认证方式
   - 认证即服务（Authentication as a Service）

2. **分布式认证**：
   - Token 分布式缓存
   - 认证状态同步

## 模块特有名词索引

当出现以下术语时，应关联到此技能：

| 术语 | 说明 |
|------|------|
| `FeishuAuthManager` | 飞书认证管理器类 |
| `exchange_code` | 授权码换取访问令牌 |
| `refresh_access_token` | 刷新访问令牌 |
| `authorization_code` | OAuth 授权码 |
| `access_token` | 访问令牌 |
| `refresh_token` | 刷新令牌 |
| `token_type` | 令牌类型（通常为 Bearer） |
| 飞书 OAuth | 飞书开放平台认证流程 |
| 飞书登录 | 使用飞书账号登录系统 |
| OIDC | OpenID Connect 协议 |

## 代码位置索引

- **模块定义**：`utils/openapi/feishu/auth_manager.py`
- **统一导入**：`utils/openapi/feishu/__init__.py`
- **使用示例**：`apps/API/auth/views.py`
- **兼容层**：`assists/feishu.py` (basic 类)
- **Token 管理**：`utils/openapi/feishu/token_manager.py`