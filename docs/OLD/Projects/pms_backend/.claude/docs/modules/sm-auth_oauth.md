# SM 认证模块 OAuth 2.0 专家

## 模块定位

`apps/SM/auth/` 是 PMS 项目的统一认证模块，负责处理所有用户登录相关的业务逻辑。该模块支持多种登录方式：

- **飞书容器内登录**：通过 `requestAccess` 方式（已实现）
- **浏览器 OAuth 登录**：通过标准 OAuth 2.0 流程（已实现）
- **账号密码登录**：通过 Django AbstractUser 认证（已实现）

核心设计原则：
1. 不直接信任第三方 token，后端统一签发 JWT
2. 所有登录方式统一到同一用户模型（User + UserFeishu）
3. 使用票据机制安全传递认证结果


## 模块职责边界

### 负责范围
- 用户登录验证（飞书 OAuth、requestAccess、账号密码）
- JWT token 签发与刷新
- OAuth state 生成与验证（防 CSRF）
- 登录票据（ticket）生成与兑换
- 用户状态检查（disable_flag、is_in_service、is_active）
- 用户信息同步与创建

### 不负责范围
- 用户信息管理（由 `apps/SM/user/` 负责）
- 权限验证（由 Django RBAC 系统负责）
- 飞书 API 封装（由 `utils/openapi/feishu/` 负责）


## 核心数据模型

### User 模型（`apps/SM/user/models.py`）
继承 `AbstractUser`，统一用户模型：

```python
class User(AbstractUser):
    # Django 内置字段：username, password, email, is_active, is_staff...
    avatar          # 头像 URL
    nickname         # 昵称
    mobile           # 手机号（可用于登录）
    is_in_service    # 是否在职
    disable_flag     # 禁用标志
    uses             # 使用次数
```

### UserFeishu 模型（`apps/SM/user/models.py`）
存储飞书 OAuth 认证信息：

```python
class UserFeishu(models.Model):
    user            # OneToOneField -> User
    open_id         # 飞书用户唯一标识
    token_type      # Token 类型
    access_token    # 飞书访问令牌
    refresh_token   # 飞书刷新令牌
    expires_at      # 过期时间
```


## 权限验证流程

### 用户状态检查顺序
在 `LoginSerializer.validate()` 和 `OAuthCallbackSerializer.validate()` 中：

1. **disable_flag** 检查 → 用户已被禁用
2. **is_in_service** 检查 → 用户已离职
3. **is_active** 检查 → 用户已被停用（Django 内置）

### 认证流程图

```
┌─────────────────────────────────────────────────────────────────┐
│                     前端发起登录请求                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────┴─────────────────────┐
        │                                           │
  飞书容器内登录                                 浏览器访问
        │                                           │
        ▼                                           ▼
 POST /auth/login                          GET /auth/oauth/feishu/login
 provider=FEISHU                            ?redirect_uri=<前端地址>
 loginType=REQUEST_ACCESS
 code=<飞书授权码>                                    │
        │                                           │
        ▼                                           ▼
 LoginSerializer                           FeishuOAuthLoginView
 ._validate_feishu_request_access()        生成 state 并存入 Redis
        │                                           │
        ▼                                           ▼
 FeishuAuthManager                         重定向到飞书授权页面
 .exchange_code(code)                              │
        │                                           │
        ▼                                           ▼
 FeishuUserManager                        用户在飞书授权后
 .get_user_info()                               │
        │                                           ▼
        ▼                            GET /auth/oauth/feishu/callback
 _process_feishu_userinfo()                   ?code=<授权码>&state=<state>
        │                                           │
        ▼                                           ▼
 检查用户状态                           OAuthCallbackSerializer
 (disable_flag,                                .validate()
 is_in_service,                                      │
 is_active)                                          ▼
        │                                   validate_oauth_state(state)
        ▼                                           │
 创建 JWT token                                        │
        │                                           ▼
        ▼                            FeishuAuthManager.exchange_code()
 返回 userinfo + token                               │
        │                                           ▼
        │                            FeishuUserManager.get_user_info()
        │                                           │
        ▼                                           ▼
└───────────────────────────────────────────────────────┘
        │                                           │
        ▼                                           ▼
   前端获取 token                           创建 login_ticket
   存储到 localStorage                            存入 Redis
        │                                           │
        ▼                                           ▼
   后续请求携带                            重定向到前端
   Authorization: Bearer               ?ticket=<ticket>&state=<state>
        │                                           │
        ▼                                           ▼
   POST /auth/oauth/exchange-ticket          前端调用
   {"ticket": "<ticket>"}                     票据兑换接口
        │                                           │
        ▼                                           ▼
   返回 userinfo + token                  返回 userinfo + token
        │                                           │
        └───────────────────┬───────────────────────┘
                            │
                            ▼
                    前端存储 JWT token
                    后续请求携带认证
```


## 认证与授权区别说明

### 认证（Authentication）
- **位置**：`apps/SM/auth/`
- **目的**：验证用户身份，签发 JWT token
- **方式**：飞书 OAuth、requestAccess、账号密码
- **输出**：JWT access_token + refresh_token

### 授权（Authorization）
- **位置**：Django REST Framework + RBAC
- **目的**：验证用户权限，控制资源访问
- **方式**：基于 JWT token 的权限验证
- **配置**：`home/settings/base.py` 中的 `REST_FRAMEWORK`

**关键配置**：
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}
AUTH_USER_MODEL = 'SM.User'
```


## 与其他模块关系

### 依赖模块
| 模块 | 用途 |
|------|------|
| `apps/SM/user/` | 用户模型（User、UserFeishu） |
| `utils/openapi/feishu/` | 飞书 API 封装（FeishuAuthManager、FeishuUserManager） |
| `config/info.py` | 系统配置（飞书应用凭证） |
| `home/settings/` | 环境配置（OAUTH_CONFIG） |

### 被依赖模块
所有需要认证的 API 端点都依赖本模块签发的 JWT token。


## 常见业务场景

### 场景 1：飞书容器内登录
```json
POST /auth/login
{
  "provider": "FEISHU",
  "loginType": "REQUEST_ACCESS",
  "code": "<飞书授权码>"
}

响应:
{
  "code": 0,
  "msg": "登录成功",
  "data": {
    "userinfo": {...},
    "tokenData": {
      "access": "<JWT access token>",
      "refresh": "<JWT refresh token>"
    },
    "authority": {...}
  }
}
```

### 场景 2：浏览器 OAuth 登录
```
1. 前端跳转到: GET /auth/oauth/feishu/login?redirect_uri=<前端回调地址>
2. 用户在飞书完成授权
3. 飞书回调到: GET /auth/oauth/feishu/callback?code=<授权码>&state=<state>
4. 后端重定向到: {前端回调地址}?ticket=<ticket>&state=<state>
5. 前端调用: POST /auth/oauth/exchange-ticket
   请求体: {"ticket": "<ticket>"}
   响应: {userinfo, token, config}
```

### 场景 3：JWT Token 刷新
```json
POST /auth/refresh
{
  "token": "<refresh_token>"
}

响应:
{
  "msg": "success",
  "data": {
    "access_token": "<新的 access token>",
    "refresh_token": "<新的 refresh token>"
  }
}
```

### 场景 4：账号密码登录
```json
POST /auth/login
{
  "provider": "OTHER",
  "loginType": "PASSWORD",
  "username": "<用户名或手机号>",
  "password": "<密码>"
}
```


## 技术实现建议（Django）

### 1. 添加新的 OAuth 提供商
在 `apps/SM/auth/enums.py` 中添加新的 Provider：
```python
class Provider(models.TextChoices):
    FEISHU = "FEISHU", "飞书"
    WECHAT = "WECHAT", "企业微信"  # 新增
```

在 `apps/SM/user/models.py` 中添加对应的 Token 模型：
```python
class UserWechat(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    open_id = models.CharField(max_length=255, unique=True)
    # ... 其他字段
```

### 2. 修改 JWT Token 有效期
在 `home/settings/base.py` 中修改：
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),   # 建议缩短到 2 小时
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),   # 建议缩短到 7 天
}
```

### 3. 添加 OAuth 配置
在各环境配置文件（如 `dev.py`）中添加：
```python
OAUTH_CONFIG = {
    'feishu': {
        'app_id': '<飞书应用 ID>',
        'app_secret': '<飞书应用密钥>',
        'redirect_uri': 'http://<域名>/auth/oauth/feishu/callback/',
    }
}
```


## 扩展设计策略

### 1. 支持多租户
在 `UserFeishu` 模型中添加 `tenant_id` 字段：
```python
class UserFeishu(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tenant_id = models.CharField(max_length=64)  # 租户 ID
    open_id = models.CharField(max_length=255)
```

### 2. 添加登录日志
创建 `LoginLog` 模型记录用户登录行为：
```python
class LoginLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_type = models.CharField(max_length=32)  # OAUTH, REQUEST_ACCESS, PASSWORD
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    login_time = models.DateTimeField(auto_now_add=True)
```

### 3. 实现单点登录（SSO）
使用 Redis 存储用户的活跃 session，登录时清除旧 session：
```python
def clear_old_sessions(user_id):
    cache_key = f'user:sessions:{user_id}'
    old_sessions = cache.get(cache_key, [])
    for session_id in old_sessions:
        cache.delete(f'session:{session_id}')
```


## 演进方向（Future Evolution）

### 短期优化
1. **添加 PKCE 支持**：增强 OAuth 2.0 安全性
2. **实现 Token 黑名单**：用户主动登出时使 token 失效
3. **添加登录限流**：防止暴力破解

### 中期扩展
1. **支持多因素认证（MFA）**：TOTP、短信验证码
2. **实现单点登录（SSO）**：跨应用统一认证
3. **添加 OAuth 2.0 客户端模式**：服务间调用认证

### 长期规划
1. **接入统一认证中心**：支持多种身份提供商
2. **实现动态权限系统**：基于资源的细粒度权限控制
3. **添加审计日志**：记录所有认证和授权行为


## 核心文件索引

| 文件 | 作用 |
|------|------|
| `apps/SM/auth/views.py` | 认证视图（LoginView、OAuth 视图、RefreshTokenView） |
| `apps/SM/auth/serializers.py` | 数据验证（LoginSerializer、OAuthCallbackSerializer） |
| `apps/SM/auth/utils.py` | 工具函数（用户处理、JWT 生成、OAuth state/ticket） |
| `apps/SM/auth/enums.py` | 枚举定义（Provider、LoginType） |
| `apps/SM/auth/urls.py` | OAuth 路由配置 |
| `apps/SM/user/models.py` | 用户模型（User、UserFeishu） |
| `utils/openapi/feishu/auth_manager.py` | 飞书认证管理器 |
| `utils/openapi/feishu/user_manager.py` | 飞书用户管理器 |


## 特有名词索引

- **OAuth**：开放授权，一种安全的授权协议
- **requestAccess**：飞书容器内的登录方式
- **state**：OAuth 状态参数，用于防 CSRF 攻击
- **ticket**：登录票据，用于安全传递认证结果
- **JWT**：JSON Web Token，用于用户认证
- **open_id**：飞书用户唯一标识符
- **FeishuAuthManager**：飞书认证管理器，封装 exchange_code 等方法
- **exchange_code**：用授权码换取访问令牌
- **callback**：OAuth 回调处理
- **refresh_token**：刷新令牌，用于获取新的访问令牌