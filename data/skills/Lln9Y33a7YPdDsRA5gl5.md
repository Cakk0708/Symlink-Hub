---
name: user-token-management
description: PMS用户认证与飞书Token管理 - 处理JWT认证、OAuth登录流程、飞书Token获取(UserFeishuToken)、用户模型(User)关系、枚举视图
---

# PMS 用户认证与飞书Token管理

## 简介

本技能处理 PMS 系统中的用户认证相关逻辑，包括：

- **统一用户模型**：`User` 模型继承 Django `AbstractUser`，支持双登录模式
- **飞书 OAuth 登录**：通过 `UserFeishu.open_id` 关联飞书用户
- **用户名密码登录**：使用 `username` 和 `password`
- **JWT Token 认证**：基于 `django-rest-framework-simplejwt`
- **用户枚举视图**：`UserViews`、`EnumViews` 返回用户相关枚举选项
- **认证枚举视图**：`LoginView`、`EnumViews` 返回认证相关枚举选项
- **信号驱动拼音生成**：`User` 保存时自动生成 `nickname_pinyin`

## 模块结构

```
apps/SM/
├── user/                          # 用户模块
│   ├── models.py                   # User, UserFeishu 模型
│   ├── enums.py                     # UserChoices 枚举
│   ├── views.py                     # UserViews, EnumViews 视图
│   ├── serializers.py               # 序列化器
│   ├── signals.py                   # nickname_pinyin 自动生成信号
│   └── utils.py                     # 工具函数
└── auth/                          # 认证模块
    ├── enums.py                     # Choices 枚举
    ├── views.py                     # LoginView, RefreshTokenView, EnumViews
    ├── serializers.py               # LoginSerializer
    └── utils.py                     # OAuth 处理逻辑
```

## 触发条件 (When to use)

当用户涉及以下场景时，激活此技能：

- 提及"用户认证"、"登录"、"User"
- 提及"飞书登录"、"OAuth"、"feishu"
- 提及"open_id"、"UserFeishu"
- 提及"nickname_pinyin"、"拼音"
- 提及"枚举"、"enum"、"Choices"
- 提及"JWT"、"token"、"refresh"
- 需要在视图中获取当前用户信息
- 需要获取用户或认证相关的枚举选项

## 核心模型关系

```
┌─────────────────────────────────────────────────────────────────┐
│                     User (统一用户模型)                      │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Django AbstractUser 字段                                 │  │
│  │ ├── username: CharField (unique)                       │  │
│  │ ├── password: CharField (哈希)                          │  │
│  │ ├── is_staff: BooleanField                              │  │
│  │ ├── is_superuser: BooleanField                          │  │
│  │ ├── is_active: BooleanField                              │  │
│  │ └── ...                                                   │  │
│  └─────────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ 自定义字段                                              │  │
│  │ ├── avatar: CharField              (头像URL)        │  │
│  │ ├── nickname: CharField            (昵称)          │  │
│  │ ├── mobile: CharField              (手机号)         │  │
│  │ ├── nickname_pinyin: JSONField      (拼音,自动生成) │  │
│  │ ├── is_executive_core: BooleanField (🆕 是否核心决策者) │  │
│  │ ├── is_in_service: BooleanField     (🆕 是否在职)    │  │
│  │ ├── uses: IntegerField            (使用次数)       │  │
│  │ ├── initial_password: BooleanField  (是否初始密码)   │  │
│  │ └── disable_flag: BooleanField      (禁用标志)       │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ user_feishu: OneToOneField → UserFeishu             │──┼──→ UserFeishu
│  └─────────────────────────────────────────────────────────┘  │     │
└─────────────────────────────────────────────────────────────────┘     │
                                                               │
                                        ┌────────────────────────────────┴────────┐
                                        │ UserFeishu (飞书Token存储)            │
                                        │ ├── user: OneToOneField → User   │
                                        │ ├── open_id: CharField (unique)   │ ← 飞书用户唯一标识
                                        │ ├── token_type: CharField          │
                                        │ ├── access_token: CharField        │
                                        │ ├── refresh_token: CharField       │
                                        │ └── expires_at: DateTimeField       │
                                        └────────────────────────────────────────┘
```

## 架构设计要点

### 1. open_id 存储位置调整

**重要变更**：`open_id` 字段从 `User` 模型移至 `UserFeishu` 模型

| 方面 | 旧设计 | 新设计 |
|------|--------|--------|
| 存储位置 | `User.open_id` | `UserFeishu.open_id` |
| 查找用户 | `User.objects.get(open_id=xxx)` | `UserFeishu.objects.get(open_id=xxx)` |
| 访问方式 | `user.open_id` | `user.user_feishu.open_id` 或 `user.open_id`(属性) |

### 2. nickname_pinyin 自动生成机制

**信号驱动设计**：`User` 保存时自动生成拼音

```python
# apps/SM/user/signals.py
@receiver(pre_save, sender=User)
def handle_user_nickname_pinyin(sender, instance, **kwargs):
    """监听 User 保存前事件，自动补充 nickname_pinyin"""
    if instance.nickname:
        if (
            not instance.pk
            or instance.nickname_pinyin == list
            or not instance.nickname_pinyin
        ):
            instance.nickname_pinyin = lazy_pinyin(instance.nickname)
```

### 3. 用户枚举设计

**UserChoices 类**：定义用户相关枚举

```python
class UserChoices:
    class InService(models.IntegerChoices):        # 🆕 字段重命名（Since 2026-03-03）
        """在职状态"""
        IN_SERVICE = (1, '在职')
        RESIGNED = (0, '离职')

    class IsExecutiveCore(models.BooleanChoices):  # 🆕 替代 IsLeader（Since 2026-03-03）
        """核心决策者状态"""
        YES = (True, '是')
        NO = (False, '否')

    # ... 其他枚举
```

### 4. 认证枚举设计

**Choices 类**：定义认证相关枚举

```python
class Choices:
    class Provider(models.TextChoices):
        """认证提供方"""
        FEISHU = 'FEISHU', '飞书'
        OTHER = 'OTHER', '其他'

    class LoginType(models.TextChoices):
        """登录类型"""
        OAUTH = 'OAUTH', 'OAuth'
        REQUEST_ACCESS = 'REQUEST_ACCESS', '请求'
        PASSWORD = 'PASSWORD', '账号密码'
```

## 专业术语说明

### 用户相关术语

| 术语 | 说明 | 相关代码 |
|------|------|----------|
| `User` | 统一用户模型，继承 AbstractUser | `apps/SM/user/models.py` |
| `UserFeishu` | 飞书Token扩展模型 | `apps/SM/user/models.py` |
| `open_id` | 飞书用户唯一标识，存储在 UserFeishu | `UserFeishu.open_id` |
| `nickname_pinyin` | 昵称拼音，由信号自动生成 | `User.nickname_pinyin` |
| `is_in_service` | 🆕 是否在职 | `User.is_in_service` |
| `is_executive_core` | 🆕 是否为核心决策者 | `User.is_executive_core` |

### 认证相关术语

| 术语 | 说明 | 相关代码 |
|------|------|----------|
| `JWT` | JSON Web Token，用于API认证 | `rest_framework_simplejwt` |
| `access_token` | JWT访问令牌 | `LoginSerializer.data.token` |
| `refresh_token` | JWT刷新令牌 | `LoginSerializer.data.refresh` |
| `OAuth` | 开放授权协议 | 飞书登录流程 |
| `LoginView` | 登录视图 | `apps/SM/auth/views.py` |

## 详细指令 (Instructions)

### 1. 用户认证（在视图中）

**✅ 正确做法**：
```python
from rest_framework.views import APIView
from django.http import JsonResponse

class MyView(APIView):
    def get(self, request):
        # JWT 认证自动处理
        user = request.user
        open_id = user.user_feishu.open_id if user.user_feishu else None
        return JsonResponse({'open_id': open_id})
```

**❌ 禁止使用**：
```python
# 已废弃，不要使用
user = request.custom_user
```

### 2. 通过 open_id 查找用户

**✅ 正确做法**：
```python
from apps.SM.user.models import User, UserFeishu

# 通过 UserFeishu 查找
feishu = UserFeishu.objects.get(open_id=xxx)
user = feishu.user
```

**❌ 禁止使用**：
```python
# User.open_id 已移除，不存在此字段
user = User.objects.get(open_id=xxx)
```

### 3. 创建用户时的字段

**✅ 正确做法**：
```python
# apps/SM/auth/utils.py
user = User.objects.create_user(
    username=userinfo['open_id'],
    password=settings.INITIAL_PASSWORD,
    avatar=userinfo['avatar'],
    nickname=userinfo['nickname'],
    mobile=userinfo['mobile'],
    department=department,
    is_active=True,
    # 不需要设置 nickname_pinyin，由信号自动生成
)
```

**❌ 禁止使用**：
```python
# nickname_pinyin 由信号自动生成，不要手动设置
user = User.objects.create_user(
    ...,
    nickname_pinyin=lazy_pinyin(userinfo['nickname'])  # ❌
)
```

### 4. 获取枚举选项

**User 模块枚举**：
```python
# GET /sm/user/enum/
from apps.SM.user import EnumViews

urlpatterns = [
    path('sm/user/enum/', EnumViews.as_view()),
]

# 返回
{
  "msg": "success",
  "data": {
    "inService": [
      {"value": "1", "label": "在职"},
      {"value": "0", "label": "离职"}
    ],
    "isExecutiveCore": [...],  # 🆕 替代 isLeader（Since 2026-03-03）
    "initialPassword": [...],
    "disableFlag": [...],
    ...
  }
}
```

**Auth 模块枚举**：
```python
# GET /sm/auth/enum/
from apps.SM.auth import EnumViews

urlpatterns = [
    path('sm/auth/enum/', EnumViews.as_view()),
]

# 返回
{
  "msg": "success",
  "data": {
    "provider": [
      {"value": "FEISHU", "label": "飞书"},
      {"value": "OTHER", "label": "其他"}
    ],
    "loginType": [...]
  }
}
```

### 5. Token 刷新

```python
# POST /auth/refresh
{
  "token": "<refresh_token>"
}

# 返回
{
  "msg": "success",
  "data": {
    "access_token": "<new_access_token>",
    "refresh_token": "<new_refresh_token>"
  }
}
```

## 核心文件位置

| 文件 | 说明 |
|------|------|
| `apps/SM/user/models.py` | User, UserFeishu 模型定义 |
| `apps/SM/user/enums.py` | UserChoices 枚举定义 |
| `apps/SM/user/views.py` | UserViews, EnumViews 视图 |
| `apps/SM/user/signals.py` | nickname_pinyin 自动生成信号 |
| `apps/SM/auth/views.py` | LoginView, RefreshTokenView, EnumViews |
| `apps/SM/auth/enums.py` | Choices 枚举定义 |
| `apps/SM/auth/utils.py` | OAuth 处理逻辑 |
| `apps/SM/serializers.py` | LoginSerializer |
| `home/settings/base.py` | AUTH_USER_MODEL 配置 |

## API 接口清单

| 接口 | 方法 | 说明 | 模块 |
|------|------|------|------|
| `/auth/login` | POST | 飞书容器内登录（token/code） | auth |
| `/auth/refresh` | POST | JWT Token 刷新 | auth |
| `/auth/enum/` | GET | 认证枚举选项 | auth |
| `/sm/user/` | GET | 在职用户列表 | user |
| `/sm/user/enum/` | GET | 用户枚举选项 | user |

## 配置说明

### AUTH_USER_MODEL 配置

```python
# home/settings/base.py
AUTH_USER_MODEL = 'SM.User'
```

## 常见错误与解决方案

| 错误 | 解决方案 |
|------|----------|
| `AttributeError: 'User' object has no attribute 'open_id'` | `open_id` 已移至 `UserFeishu`，使用 `user.user_feishu.open_id` |
| `User.DoesNotExist: User has no open_id` | 使用 `UserFeishu.objects.get(open_id=xxx)` 查找 |
| `KeyError: 'nickname_pinyin'` | 检查信号是否正确注册，在 `apps/SM/apps.py` 中导入 `apps.SM.user.signals` |
| `'Request' object has no attribute 'custom_user'` | 直接使用 `request.user` (JWT自动认证) |

## 设计变更历史

### 变更 1：open_id 存储位置调整
- **时间**：2026-02-13
- **变更**：`open_id` 从 `User` 移至 `UserFeishu`
- **原因**：`open_id` 是飞书认证后的标识，应存储在飞书Token表中

### 变更 2：nickname_pinyin 自动生成
- **时间**：2026-02-13
- **变更**：从手动创建改为信号自动生成
- **原因**：解耦业务逻辑，确保所有创建用户场景都能自动生成拼音

### 变更 3：枚举视图独立
- **时间**：2026-02-13
- **变更**：为 user 和 auth 模块添加独立的 `EnumViews`
- **原因**：规范API设计，提供统一的枚举查询接口

### 🆕 变更 4：字段重命名（Since 2026-03-03）
- **时间**：2026-03-03
- **变更**：
  - `is_leader` → `is_executive_core`（含义从"是否为部门负责人"改为"是否为核心决策者"）
  - `in_service` → `is_in_service`（统一命名风格，is_ 前缀）
- **原因**：
  - 提高字段语义准确性
  - 统一布尔字段命名规范
- **影响范围**：
  - 数据库迁移：`apps/SM/user/migrations/0003_rename_in_service.py`
  - 所有引用该字段的代码（11个文件）

### ⚠️ 已废弃字段（Deprecated）

- `is_leader`：使用 `is_executive_core` 替代（Since 2026-03-03）
- `in_service`：使用 `is_in_service` 替代（Since 2026-03-03）
