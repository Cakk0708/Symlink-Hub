# SM Auth 模块技能

## 模块位置

```
pms_backend/apps/SM/auth/
├── views.py            # 登录、Token刷新、枚举视图
├── serializers.py      # 登录数据验证序列化器
├── utils.py            # 认证工具函数
├── enums.py            # 认证枚举定义
└── __init__.py
```

## 关联模块

```
pms_backend/apps/API/auth/           # OAuth 2.0 认证包
├── __init__.py                      # 包导出
├── urls.py                          # OAuth 路由
├── views.py                         # OAuth 视图
├── utils.py                         # OAuth 工具函数
└── services/                        # OAuth 服务提供商
    ├── __init__.py
    └── feishu.py                    # 飞书服务类
```

## 认证架构

### 双层认证架构

```
┌─────────────────────────────────────────────────────────────┐
│                        前端应用                              │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
                ▼                           ▼
    ┌──────────────────┐         ┌──────────────────┐
    │  OAuth 2.0 流程   │         │  直接登录流程     │
    │  /api/auth/      │         │  /sm/auth/login  │
    └──────────────────┘         └──────────────────┘
                │                           │
                ▼                           ▼
    ┌──────────────────┐         ┌──────────────────┐
    │  飞书授权跳转    │         │  LoginSerializer │
    │  回调处理        │         │  验证用户信息     │
    └──────────────────┘         └──────────────────┘
                │                           │
                └─────────────┬─────────────┘
                              ▼
                    ┌──────────────────┐
                    │  统一用户模型     │
                    │  SM.User         │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  JWT Token       │
                    │  返回前端        │
                    └──────────────────┘
```

## 数据模型

### 认证流程涉及模型

```python
# SM.User - 统一用户模型
class User(AbstractUser):
    username        # 用户名（用于密码登录）
    password        # 密码哈希
    disable_flag    # 禁用标志
    is_in_service   # 🆕 是否在职（重命名，原 in_service，Since 2026-03-03）
    is_active       # Django 激活状态
    # ... 其他字段

# SM.UserFeishu - 飞书 Token 扩展
class UserFeishu(models.Model):
    user            # 关联用户
    open_id         # 飞书唯一标识
    access_token    # 访问令牌
    refresh_token   # 刷新令牌
    expires_at      # 过期时间
```

## 序列化器

### LoginSerializer（登录序列化器）

```python
class LoginSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(choices=['FEISHU', 'OTHER'])
    loginType = serializers.ChoiceField(choices=['OAUTH', 'REQUEST_ACCESS', 'PASSWORD'])
    code = serializers.CharField(required=False, allow_blank=True)
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=False)

    # 验证方法
    validate(attrs)                    # 主验证入口
    _validate_feishu_request_access()  # 飞书请求码登录
    _validate_other_password()         # 账号密码登录

    # 用户状态检查
    - disable_flag   # 用户是否被禁用
    - is_in_service  # 🆕 用户是否在职（Since 2026-03-03）
    - is_active      # Django 激活状态

    # 返回数据（to_representation）
    - userinfo      # 用户信息
    - tokenData     # JWT Token（access + refresh）
    - authority     # 用户权限列表
```

## 视图

### LoginView（登录视图）

路由：`/sm/auth/login`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/sm/auth/login` | 统一登录接口 |

**请求格式**：
```json
// 飞书请求码登录
{
    "provider": "FEISHU",
    "loginType": "REQUEST_ACCESS",
    "code": "xxxxx"
}

// 账号密码登录
{
    "provider": "OTHER",
    "loginType": "PASSWORD",
    "username": "zhangsan",
    "password": "password123"
}
```

**响应格式**：
```json
{
    "code": 0,
    "msg": "登录成功",
    "data": {
        "userinfo": {
            "id": 1,
            "username": "zhangsan",
            "nickname": "张三",
            "avatar": "https://...",
            "mobile": "13800138000",
            "email": "zhangsan@example.com",
            "roles": [...]
        },
        "tokenData": {
            "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
        },
        "authority": {
            "items": ["PM.view_project", "SM.add_user", ...],
            "total": 42
        }
    }
}
```

### RefreshTokenView（Token 刷新视图）

路由：`/sm/auth/refresh`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/sm/auth/refresh` | 刷新 JWT Token |

**请求格式**：
```json
{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**响应格式**：
```json
{
    "msg": "success",
    "data": {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
}
```

### EnumViews（认证枚举视图）

路由：`/sm/auth/enum`

| 方法 | 路径 | 返回内容 |
|------|------|----------|
| GET | `/sm/auth/enum` | provider, loginType 枚举 |

## URL 路由配置

```python
# apps/SM/auth/urls.py
urlpatterns = [
    path('auth/login', LoginView.as_view()),
    path('auth/refresh', RefreshTokenView.as_view(), name='auth_refresh'),
    path('auth/enum', EnumViews.as_view()),
]
```

## 枚举数据

### Choices 类

```python
class Choices:
    class Provider(models.TextChoices):
        FEISHU = "FEISHU", "飞书"
        OTHER = "OTHER", "其他"

    class LoginType(models.TextChoices):
        OAUTH = "OAUTH", "OAuth"
        REQUEST_ACCESS = "REQUEST_ACCESS", "请求"
        PASSWORD = "PASSWORD", "账号密码"
```

## 工具函数

### _process_feishu_userinfo()

```python
def _process_feishu_userinfo(token_data, userinfo):
    """
    处理飞书用户信息

    用户查找优先级：
    1. 检查 UserFeishu.open_id 是否存在（已有飞书关系的用户）
    2. 如果不存在，检查 User.mobile 是否相同（手机号关联的用户）
    3. 如果都不存在，创建新用户

    处理流程：
    - 存在：更新用户信息（avatar, nickname, mobile），uses 计数+1
    - 新建：使用 open_id 作为 username，INITIAL_PASSWORD 作为初始密码
    - 存储/更新 UserFeishu Token（access_token, refresh_token, expires_at）

    返回：(True, auth_user)
    """
```

**用户关联逻辑（防止重复用户创建）**：

```
飞书用户登录流程
│
├─ 步骤1：通过 open_id 查找 UserFeishu
│   └─ 找到 → 关联到已有 User，更新用户信息
│
├─ 步骤2：open_id 未找到，通过 mobile 查找 User
│   ├─ 找到 → 关联飞书关系到该 User，更新用户信息
│   └─ 未找到 → 继续下一步
│
└─ 步骤3：创建新 User
    └─ username=open_id, password=INITIAL_PASSWORD
```

**适用场景**：
- 用户先通过账号密码注册，后通过飞书登录 → 关联到同一账户
- 用户更换飞书账号（mobile 相同） → 复用已有账户

### _create_jwt_token()

```python
def _create_jwt_token(auth_user):
    """
    创建 JWT Token
    返回：{
        'access': str(refresh.access_token),
        'refresh': str(refresh)
    }
    """
```

## OAuth 2.0 认证流程

### 飞书 OAuth 流程（apps/API/auth）

```
┌──────────┐                ┌──────────┐                ┌──────────┐
│  前端    │                │  后端    │                │  飞书    │
└──────────┘                └──────────┘                └──────────┘
     │                           │                           │
     │  1. 访问登录页             │                           │
     ├─────────────────────────>│                           │
     │  GET /api/auth/feishu/login/?redirect_uri=...       │
     │                           │                           │
     │                           │  2. 重定向到飞书授权      │
     │                           ├─────────────────────────>│
     │                           │  3. 用户授权              │
     │                           │<─────────────────────────┤
     │  4. 飞书授权页             │                           │
     │                           │                           │
     │  5. 授权回调               │                           │
     │<─────────────────────────┤                           │
     │  飞书回调后端              │                           │
     │  GET /api/auth/feishu/callback/?code=...&state=...  │
     │                           │                           │
     │                           │  6. 换取 access_token    │
     │                           ├─────────────────────────>│
     │                           │<─────────────────────────┤
     │                           │  7. 返回 token 和用户信息  │
     │                           │                           │
     │                           │  8. 生成 login_ticket     │
     │                           ├─────────────────────────┐
     │                           │                         │
     │  9. 重定向到前端           │                         │
     │<─────────────────────────┤                         │
     │  前端回调 ?ticket=...&state=...                   │
     │                           │                         │
     │  10. 兑换 ticket           │                         │
     ├─────────────────────────>│                         │
     │  POST /api/auth/exchange-ticket/                   │
     │<─────────────────────────┤                         │
     │  返回 JWT Token           │                         │
     │                           │                         │
```

### OAuth 路由（apps/API/auth）

| 路由 | 说明 |
|------|------|
| `/api/auth/feishu/login/` | 飞书 OAuth 登录入口 |
| `/api/auth/feishu/callback/` | 飞书 OAuth 回调处理 |
| `/api/auth/exchange-ticket/` | login_ticket 兑换 JWT |

## 登录方式详解

### 1. 飞书请求码登录（REQUEST_ACCESS）

**适用场景**：飞书容器内应用，直接获取授权码

**流程**：
1. 前端从飞书容器获取 `code`
2. 调用 `/sm/auth/login` 传入 `code`
3. 后端调用飞书 API 换取 `access_token`
4. 获取飞书用户信息
5. 创建/更新用户和 Token
6. 返回 JWT Token

**请求示例**：
```json
{
    "provider": "FEISHU",
    "loginType": "REQUEST_ACCESS",
    "code": "xxxxx"
}
```

### 2. 飞书 OAuth 登录（OAUTH）

**适用场景**：浏览器端应用，需要用户授权

**流程**：
1. 前端访问 `/api/auth/feishu/login/?redirect_uri=...`
2. 后端生成 `state` 并重定向到飞书授权页
3. 用户在飞书页面授权
4. 飞书回调 `/api/auth/feishu/callback/?code=...&state=...`
5. 后端处理用户信息，生成 `login_ticket`
6. 重定向到前端，携带 `ticket` 和 `state`
7. 前端调用 `/api/auth/exchange-ticket/` 兑换 JWT Token

### 3. 账号密码登录（PASSWORD）

**适用场景**：非飞书用户，或测试环境

**流程**：
1. 前端收集用户名和密码
2. 调用 `/sm/auth/login`
3. 后端验证用户名和密码
4. 检查用户状态（禁用、离职、激活）
5. 返回 JWT Token

**请求示例**：
```json
{
    "provider": "OTHER",
    "loginType": "PASSWORD",
    "username": "zhangsan",
    "password": "password123"
}
```

## 用户状态检查

登录时按以下顺序检查用户状态：

| 状态 | 字段 | 错误提示 | 说明 |
|------|------|----------|------|
| 禁用 | `disable_flag=True` | 用户已被禁用 | 管理员手动禁用 |
| 离职 | `is_in_service=False` | 用户已离职 | HR 系统同步 |
| 停用 | `is_active=False` | 用户已被停用 | Django 层面禁止 |

## JWT Token 配置

### SimpleJWT 配置（settings/base.py）

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),  # 访问令牌有效期
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),     # 刷新令牌有效期
    'ROTATE_REFRESH_TOKENS': True,                   # 刷新时轮换 refresh token
    'BLACKLIST_AFTER_ROTATION': True,                # 轮换后加入黑名单
    'AUTH_HEADER_TYPES': ('Bearer',),                # 认证头类型
    'USER_ID_FIELD': 'id',                           # 用户ID字段
    'USER_ID_CLAIM': 'user_id',                      # Token 中的用户ID声明
}
```

### Token 使用方式

**请求头格式**：
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**刷新 Token**：
```json
POST /sm/auth/refresh
{
    "token": "refresh_token_value"
}
```

## 安全注意事项

1. **HTTPS**：生产环境必须使用 HTTPS 传输 Token
2. **Token 存储**：前端使用 localStorage 或 sessionStorage 存储
3. **Token 刷新**：在 access_token 过期前自动刷新
4. **密码加密**：使用 Django 的密码哈希，永远不存储明文密码
5. **State 验证**：OAuth 流程必须验证 state 防止 CSRF
6. **一次性 Ticket**：login_ticket 兑换后立即删除

## 关联模块

| 模块 | 关联方式 | 说明 |
|------|----------|------|
| SM.User | - | 统一用户模型 |
| SM.UserFeishu | OneToOneField | 飞书 Token 存储 |
| SM.Role | ManyToManyField | 用户角色权限 |
| API.auth | - | OAuth 2.0 认证包 |

## 使用场景

### 场景 1：飞书容器内登录

```javascript
// 飞书容器内获取授权码
tt.request({
    url: 'https://open.feishu.cn/open-apis/authen/v1/authorize',
    success: (res) => {
        const code = res.code;
        // 调用后端登录
        axios.post('/sm/auth/login', {
            provider: 'FEISHU',
            loginType: 'REQUEST_ACCESS',
            code: code
        });
    }
});
```

### 场景 2：浏览器 OAuth 登录

```javascript
// 1. 前端跳转到 OAuth 登录
window.location.href = '/api/auth/feishu/login/?redirect_uri=' + callbackUrl;

// 2. 回调处理
const urlParams = new URLSearchParams(window.location.search);
const ticket = urlParams.get('ticket');

// 3. 兑换 ticket
axios.post('/api/auth/exchange-ticket/', { ticket })
    .then(res => {
        // 保存 JWT Token
        localStorage.setItem('access', res.data.data.token.token);
        localStorage.setItem('refresh', res.data.data.token.refresh);
    });
```

### 场景 3：账号密码登录

```javascript
axios.post('/sm/auth/login', {
    provider: 'OTHER',
    loginType: 'PASSWORD',
    username: 'zhangsan',
    password: 'password123'
})
.then(res => {
    // 保存 JWT Token
    const { access, refresh } = res.data.data.tokenData;
    localStorage.setItem('access', access);
    localStorage.setItem('refresh', refresh);
});
```

### 场景 4：Token 刷新

```javascript
axios.post('/sm/auth/refresh', {
    token: localStorage.getItem('refresh')
})
.then(res => {
    const { access_token, refresh_token } = res.data.data;
    localStorage.setItem('access', access_token);
    localStorage.setItem('refresh', refresh_token);
});
```

## 常见问题

### Q: OAuth 和请求码登录有什么区别？

A:
- **OAuth**：浏览器端，需要用户在飞书页面授权，会重定向
- **请求码**：飞书容器内，直接获取授权码，无需重定向

### Q: Token 过期后怎么办？

A: 使用 `refresh_token` 调用 `/sm/auth/refresh` 刷新 Token。`refresh_token` 有效期为 7 天。

### Q: 如何判断用户需要修改密码？

A: 检查 `User.initial_password` 字段，为 `True` 表示需要修改。

### Q: 飞书用户首次登录的密码是什么？

A: 使用配置文件中的 `INITIAL_PASSWORD` 作为初始密码。

### Q: OAuth 回调的 state 有什么用？

A: 防止 CSRF 攻击，验证回调请求的合法性。

### Q: 用户先通过密码注册，后通过飞书登录会发生什么？

A: 系统会通过 `mobile` 字段找到已有用户，将飞书账号关联到该用户，而不是创建重复账户。这样可以确保同一用户在不同登录方式下使用同一个账户。

## 开发注意事项

1. **用户状态检查顺序**：disable_flag → is_in_service → is_active
2. **使用次数统计**：每次登录更新 `User.uses`
3. **错误提示中文化**：使用中文错误提示
4. **密码字段映射**：to_internal_value 中将 password 映射为 "用户密码"
5. **权限查询**：使用 `user.get_all_permissions()` 获取所有权限
6. **飞书用户关联逻辑**（`_process_feishu_userinfo`）：
   - 优先通过 `open_id` 查找已有飞书关系
   - 未找到时，通过 `mobile` 查找已存在的用户（防止重复创建）
   - 仅在两者都找不到时才创建新用户
   - 适用于用户先通过其他方式注册，后通过飞书登录的场景
7. **🆕 字段引用**：使用 `is_in_service` 替代 `in_service`（Since 2026-03-03）

## 字段变更历史

### 🆕 2026-03-03 字段重命名

| 旧字段 | 新字段 | 说明 |
|--------|--------|------|
| `in_service` | `is_in_service` | 统一命名风格（is_ 前缀） |

### ⚠️ 已废弃字段（Deprecated）

- `in_service`：使用 `is_in_service` 替代（Since 2026-03-03）
