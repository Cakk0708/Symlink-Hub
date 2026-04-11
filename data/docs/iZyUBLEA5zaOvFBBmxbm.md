# SM (System Management) 用户管理模块

## 模块定位

SM 模块是 Duolingo 后端系统的**用户管理与认证中心**，负责：
- 用户账户的注册与登录
- 多种认证方式（账号密码、手机验证码）
- JWT Token 颁发与管理
- 组织管理（需 superuser 权限）
- 系统仪表盘数据聚合

**核心职责**：作为系统的入口模块，所有外部访问请求都需要经过 SM 模块的身份验证后才能访问其他业务模块（BDM、APS、SEM）。

---

## 模块职责边界

### 核心边界
| 职责 | 负责模块 | 说明 |
|------|---------|------|
| 用户身份认证 | SM (user) | 登录、注册、Token 颁发 |
| 组织管理 | SM (organization) | 组织 CRUD（需 superuser 权限） |
| Duolingo 账号管理 | BDM | Account 模型，存储第三方账号信息 |
| 业务数据统计 | SM (dashboard) | 聚合 BDM/APS 数据展示 |
| 订单管理 | APS | Order 模型，业务订单处理 |

### 边界规则
1. **SM 不直接存储 Duolingo 账号信息**：第三方账号存储在 `BDM.Account`
2. **SM 的 User 模型**：仅存储本地系统用户信息（username、nickname）
3. **Token 双层结构**：
   - SM User 对应本地 JWT Token（系统内部认证）
   - Duolingo Account 对应第三方 Token（调用外部 API）

---

## 核心数据模型

### User 模型 (`apps/SM/user/models.py`)

```python
class User(AbstractUser):
   """用户模型"""

   nickname = models.CharField(max_length=50, verbose_name='昵称')
   organization = models.OneToOneField(
      Organization,
      null=True,
      blank=True,
      on_delete=models.SET_NULL,
      verbose_name='所属组织',
      related_name='user'
   )
   created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
   updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

   def __str__(self):
      return self.username
```

**关键特性**：
- 继承 Django `AbstractUser`，包含 `username`、`password` 等基础字段
- `password` 使用 Django 默认的 hash 加密存储
- 与 `BDM.Account` 通过 UUID 关联（非外键）
- **与 Organization 一对一关联**：每个用户只能属于一个组织（非必填）

### 序列化器 (`apps/SM/user/serializers.py`)

```python
class ParamsSerializer(serializers.Serializer):
   """列表查询参数序列化器"""

   page = serializers.IntegerField(default=1)
   username = serializers.CharField(default=None, write_only=True)

   params = serializers.SerializerMethodField()
   limit = serializers.SerializerMethodField()

   def get_params(self, obj):
      query = models.Q()
      if username := obj.get('username'):
         query &= models.Q(username__icontains=username)
      return query

   def get_limit(self, obj):
      start = (obj['page'] - 1) * 10
      return {'start': start, 'end': 10 + start}


class ListSerializer(serializers.ModelSerializer):
   """用户序列化器"""

   organizationName = serializers.CharField(
      source='organization.name',
      read_only=True,
      allow_null=True
   )
   createdAt = serializers.DateTimeField(source='created_at', read_only=True)
   updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)

   class Meta:
      model = User
      fields = [
         'id',
         'username',
         'nickname',
         'organizationName',
         'createdAt',
         'updatedAt'
      ]

   def to_representation(self, instance):
      data = super().to_representation(instance)
      data['created_at'] = common.to_local_time(str(instance.created_at))
      return data
```

### Organization 模型 (`apps/SM/organization/models.py`)

```python
class Organization(models.Model):
   """组织模型"""
   code = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name='组织编码')
   name = models.CharField(max_length=100, verbose_name='组织名称')
   remark = models.CharField(max_length=255, blank=True, default='', verbose_name='备注')
   created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
   updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
```

**关键特性**：
- 自动生成组织编码（格式：O + 日期 + 序号，如 O20260315001）
- 仅 superuser 用户可进行 CRUD 操作
- 组织名称唯一性验证

**权限控制**：
```python
class PermissionSuperUser(BasePermission):
   """仅超级用户权限"""
   def has_permission(self, request, view):
      return request.user and request.user.is_superuser
```

---

## 权限验证流程

### 认证架构
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   前端请求   │ -> │   SM 模块   │ -> │  业务模块   │
└─────────────┘    └─────────────┘    └─────────────┘
                          │
                    ┌─────┴─────┐
                    │  JWT 验证  │
                    └───────────┘
```

### 登录流程

#### 1. 账号密码登录 (`views_login`)
```python
# 流程：apps/SM/user.py:85-110
POST /SM/user/login
Body: {username, password}

1. 验证参数完整性
2. 查询 User 表（本地用户）
3. 验证密码（check_password）
4. 生成 JWT Token（refresh + access）
5. 返回用户信息和 Token
```

#### 2. Duolingo 账号登录 (`views_login_add`)
```python
# 流程：apps/SM/user.py:122-154
POST /SM/user/login/add
Body: {username, password}

1. 调用 api_service.login() -> Duolingo API
2. 获取 Duolingo Token 和 UUID
3. 调用 api_service.get_user_data() -> 用户详情
4. 创建/更新 BDM.Account 记录
5. 生成本地 JWT Token
6. 返回用户数据（包含 Duolingo 信息）和本地 Token
```

#### 3. 手机验证码登录 (`views_verification`)
```python
# 流程：apps/SM/user.py:177-198
GET  /SM/user/verification/<phone_number>  -> 发送验证码
POST /SM/user/verification
Body: {phoneNumber, id, code}

1. 调用 api_service.verification_login()
2. 获取 Duolingo Token 和 UUID
3. 同步创建本地 User 和 BDM.Account
4. 生成 JWT Token
```

### Token 结构
```json
{
  "msg": "登录成功",
  "data": {
    "user": "用户信息对象",
    "token": {
      "refresh_token": "用于刷新 access_token",
      "access_token": "用于 API 请求认证"
    }
  }
}
```

---

## 认证与授权区别说明

### 认证 (Authentication)
- **目的**：确认"你是谁"
- **实现**：SM 模块通过 JWT Token 验证
- **涉及组件**：`views_login`、`views_register`、`views_verification`
- **Token 来源**：`rest_framework_simplejwt.tokens.RefreshToken`

### 授权 (Authorization)
- **目的**：确认"你能做什么"
- **实现**：Django REST Framework `permission_classes`
- **当前状态**：公开端点使用 `AllowAny`，其他端点使用默认认证

### 配置示例
```python
class views_login(views.APIView):
    permission_classes = [AllowAny]  # 允许未认证用户访问
    authentication_classes = []      # 不进行认证检查

class views_user(views.APIView):
    # 默认需要认证（通过 JWT Token）
    def get(self, request):
        # 只有认证用户才能访问
```

---

## 与其他模块关系

### 模块依赖图
```
                    ┌─────────────┐
                    │  API 模块   │
                    │ (Duolingo)  │
                    └──────┬──────┘
                           │ HTTP API
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼───────┐   ┌──────▼──────┐   ┌──────▼──────┐
│  SM 模块      │   │  BDM 模块   │   │  APS 模块   │
│ (用户认证)    │   │ (账号管理)  │   │ (订单处理)  │
└───────────────┘   └─────────────┘   └─────────────┘
        │                  │                  │
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                    ┌──────▼──────┐
                    │ Dashboard   │
                    │ (数据聚合)  │
                    └─────────────┘
```

### 数据流向
1. **登录流程**：前端 -> SM -> API (Duolingo) -> 返回数据 -> 创建 BDM.Account
2. **Dashboard**：SM 聚合 BDM.Account 和 APS.Order 数据
3. **API 调用**：BDM.Account.token -> API 模块 -> Duolingo 外部服务

---

## 常见业务场景

### 场景 0：查询用户列表
```
GET /SM/user?page=1&username=admin

响应:
{
  "msg": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "username": "admin",
        "nickname": "管理员",
        "created_at": "2025-03-08 10:00:00",
        "updated_at": "2025-03-08 10:00:00"
      }
    ],
    "pagination": {
      "total": 25,
      "start": 0,
      "end": 10
    }
  }
}
```

**实现位置**: `apps/SM/user.py:58-81`

### 场景 1：新用户注册
```
用户输入 -> POST /SM/user/register
         -> serializer_user 验证
         -> 创建 User 记录
         -> 返回用户信息
```

### 场景 2：Duolingo 账号绑定登录
```
用户输入 Duolingo 账号密码
         -> POST /SM/user/login/add
         -> api_service.login() 验证
         -> 获取 Duolingo UUID/Token
         -> api_service.get_user_data() 获取详情
         -> 创建/更新 BDM.Account
         -> 生成本地 JWT Token
         -> 返回完整用户数据
```

### 场景 3：手机验证码快捷登录
```
用户输入手机号 -> GET /SM/user/verification/<phone>
              -> 发送验证码（通过第三方接口）
用户输入验证码 -> POST /SM/user/verification
              -> api_service.verification_login()
              -> 创建本地用户和 Duolingo 账号
              -> 返回 JWT Token
```

### 场景 4：组织管理
```
# 超级用户操作
GET /SM/organizations          -> 组织列表（分页）
POST /SM/organizations         -> 创建组织
GET /SM/organizations/<id>     -> 组织详情
PUT /SM/organizations/<id>     -> 更新组织
DELETE /SM/organizations/<id>  -> 删除组织
```

**实现位置**: `apps/SM/organization/`

### 场景 5：Dashboard 数据加载
```
前端请求 -> GET /SM/dashboard
         -> serializer_dashboard 聚合数据
         -> Account.objects.filter(disable_flag=False).count()  # 有效账号数
         -> Order.objects.filter(created_at__date=today)        # 今日订单
         -> 返回统计数据
```

---

## 技术实现建议（Django）

### 新增 API 端点
```python
# apps/SM/urls.py 添加路径
path('user/profile', views_profile.as_view(), name='profile'),
```

### 新增视图类
```python
# 命名规范：views_<功能>
class views_profile(views.APIView):
    def get(self, request):
        # 获取当前用户信息
        user = request.user
        serializer = serializer_user(user)
        return JsonResponse({'msg': 'success', 'data': serializer.data})
```

### 新增序列化器
```python
# 命名规范：serializer_<模型>
class serializer_profile(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'nickname', 'email')
```

---

## 演进方向 (Future Evolution)

### 短期优化
- [x] 用户列表 API 响应格式标准化（支持分页） (2025-03-08 完成)
- [ ] 增加用户角色/权限系统（Django Groups/Permissions）
- [ ] 实现 Token 刷新机制自动化
- [ ] 添加登录日志和审计功能
- [ ] 手机验证码限流（防刷）

### 中期规划
- [ ] OAuth 2.0 / OpenID Connect 集成
- [ ] 多因素认证（MFA）
- [ ] 单点登录（SSO）
- [ ] 用户画像与行为分析

### 长期愿景
- [ ] 分布式认证系统
- [ ] 区块链身份认证
- [ ] 生物识别集成
- [ ] 跨域用户同步

---

## 模块特有名词索引

| 名词 | 定位位置 | 说明 |
|------|---------|------|
| `User` | apps/SM/user/models.py:15 | 用户模型，继承 AbstractUser，含 Organization 一对一关联 |
| `ParamsSerializer` | apps/SM/user/serializers.py:18 | 列表查询参数序列化器 |
| `ListSerializer` | apps/SM/user/serializers.py:39 | 用户序列化器（列表） |
| `views_user` | apps/SM/user/views.py:22 | 用户列表视图 |
| `views_login` | apps/SM/user/views.py:87 | 账号密码登录视图 |
| `views_login_add` | apps/SM/user/views.py:110 | Duolingo 账号登录视图 |
| `views_register` | apps/SM/user/views.py:61 | 用户注册视图 |
| `views_dashboard` | apps/SM/dashboard/views.py:16 | 仪表盘数据视图 |
| `serializer_dashboard` | apps/SM/dashboard/serializers.py:12 | 仪表盘数据序列化器 |
| `Organization` | apps/SM/organization/models.py:13 | 组织模型 |
| `ListView` | apps/SM/organization/views.py:38 | 组织列表视图 |
| `DetailView` | apps/SM/organization/views.py:100 | 组织详情视图 |
| `PermissionSuperUser` | apps/SM/organization/views.py:13 | 超级用户权限类 |
| `api_service` | apps/API/Duolingo.py:39 | Duolingo API 服务类 |
| `refresh_token` | 登录响应 | 用于刷新 access_token 的长期令牌 |
| `access_token` | 登录响应 | 用于 API 请求认证的短期令牌 |

---

## 快速定位指南

### 常见文件位置
- **用户模块**: `apps/SM/user/`（多文件模块）
  - `models.py`: User 模型定义
  - `serializers.py`: 序列化器
  - `views.py`: 视图
  - `utils.py`: 工具函数
- **组织模块**: `apps/SM/organization/`
- **仪表盘**: `apps/SM/dashboard/`
- **URL路由**: `apps/SM/urls.py`

### 关键API端点
- 用户列表: `GET /SM/user`
- 用户注册: `POST /SM/user/register`
- 系统登录: `POST /SM/user/login`
- 组织列表: `GET /SM/organizations`
- 组织详情: `GET /SM/organizations/<id>`
- 创建组织: `POST /SM/organizations`
- 更新组织: `PUT /SM/organizations/<id>`
- 删除组织: `DELETE /SM/organizations/<id>`
- 仪表盘: `GET /SM/dashboard`

---

**最后更新**: 2026-03-15
