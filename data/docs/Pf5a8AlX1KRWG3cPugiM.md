# Accounts 模块专家技能

## 模块定位

Accounts 模块是 Duolingo 后端系统的**核心账号管理模块**，负责多语种学习平台账号的完整生命周期管理。该模块位于 `apps/BDM/account/` 目录下，是业务数据管理（BDM）域的重要组成部分。

### 核心价值
- **账号资产管理**: 管理用于刷课、代练等业务的 Duolingo 账号池
- **统一认证中台**: 提供用户名密码、手机验证码、Token 三通道认证验证
- **数据同步**: 实时同步 Duolingo 官方数据（宝石、经验、打卡等）
- **业务支撑**: 为 APS 订单模块提供账号资源

---

## 模块职责边界

### 核心职责
1. **账号 CRUD 操作**: 账号的创建、查询、更新、删除
2. **认证验证**: 用户名密码验证、手机验证码登录验证、Token 验证
3. **验证码管理**: 发送验证码、验证码有效期管理
4. **数据同步**: 从 Duolingo 官方 API 同步用户数据
5. **状态管理**: 账号禁用/启用状态控制

### 边界界定
- **不属于**: 系统用户管理（见 SM 模块的 User 模型）
- **不属于**: 订单处理（见 APS 模块的 Order 模型）
- **不属于**: 客户管理（见 BDM 模块的 Customer 模型）
- **属于**: Duolingo 第三方账号的完整管理

### 依赖关系
```
account (BDM/account)
    ├─> 依赖: API.Duolingo.service (第三方API服务)
    ├─> 依赖: API.Duolingo.mapper (答题/排行榜逻辑映射器)
    ├─> 依赖: utils.code_generator (编码生成)
    ├─> 依赖: django.core.cache (缓存服务)
    ├─> 依赖: SM.Organization (组织模型)
    ├─> 被依赖: APS.Order (订单模块引用账号)
    └─> 关联: BDM.Customer (通过 customer 外键关联)
```

---

## 核心数据模型

### Account 模型 (`apps/BDM/account/models.py`)

```python
class Account(models.Model):
    # 基础身份信息
    code = models.CharField(max_length=20, unique=True, verbose_name='账户编码')  # 自增
    uuid = models.CharField(verbose_name='用户UUID', max_length=255)
    email = models.CharField(max_length=100, verbose_name='邮箱')
    username = models.CharField(max_length=50, verbose_name='用户名')
    nickname = models.CharField(max_length=50, verbose_name='昵称')
    phone = models.CharField(max_length=20, verbose_name='手机号')

    # 认证凭据
    password = models.CharField(max_length=50, verbose_name='密码')
    token = models.CharField(max_length=255, verbose_name='API Token')

    # 业务属性
    gems = models.IntegerField(default=0, verbose_name='宝石')
    exp = models.IntegerField(default=0, verbose_name='经验')

    # 时间追踪
    last_sign = models.DateTimeField(verbose_name='最后学习时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    # 状态控制
    disable_flag = models.BooleanField(default=False, verbose_name='禁用标志')

    # 客户关联
    customer = models.ForeignKey(
        'Customer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='客户',
        related_name='accounts'
    )

    # 组织关联
    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='所属组织',
        related_name='accounts'
    )
```

### 字段语义说明

| 字段 | 类型 | 业务含义 | 来源 |
|------|------|----------|------|
| `code` | CharField(20) | 账户自增编码（格式：A+日期+序号） | 自动生成 |
| `uuid` | CharField(255) | Duolingo 官方用户唯一标识 | 官方API返回 |
| `token` | CharField(255) | JWT认证令牌，用于API调用 | 登录后获取 |
| `gems` | IntegerField | 当前宝石数量 | 定期同步 |
| `exp` | IntegerField | 总经验值 | 定期同步 |
| `last_sign` | DateTimeField | 最后学习/打卡时间 | streak数据 |
| `disable_flag` | BooleanField | 禁用标志，True 表示已禁用 | 手动/自动设置 |
| `organization` | ForeignKey | 所属组织 | 当前用户组织 |

---

## 认证验证流程

### 统一认证架构

重构后的认证系统采用**统一验证接口**，支持三种验证方式：

```
                  ┌─────────────────────────┐
                  │  CredentialsVerifyView   │
                  │  (POST /credentials/verify) │
                  └────────────┬──────────────┘
                               │
               ┌───────────────┼───────────────┐
               ▼               ▼               ▼
         ┌─────────┐     ┌─────────┐     ┌─────────┐
         │ username│     │  phone  │     │  token  │
         │ password│     │   code  │     │         │
         └────┬────┘     └────┬────┘     └────┬────┘
              │               │               │
              ▼               ▼               ▼
         Duolingo API    Cache 提取    Duolingo API
              │           verification_id      │
              └───────────────┴───────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Cache 储存成功数据  │
                    │  返回 cacheKey    │
                    └──────────────────┘
```

### 1. 用户名密码验证

**请求**:
```json
POST /account/credentials/verify
{
  "type": "username",
  "username": "example",
  "password": "password123"
}
```

**流程**:
```
客户端
  → [username, password]
  → CheckAccountSerializer.validate()
  → api_service().login(username, password)
  → Duolingo 官方 API
  ← {token, uuid, status: 200}
  → 储存到 Cache (3600秒过期)
  → 返回 {checkPassed: true, cacheKey: "hash"}
```

### 2. 手机验证码验证

**第一步：获取验证码**
```json
POST /account/verification-codes
{
  "target": "13800138000",
  "type": "sms",
  "scene": "login"
}
```

**返回**:
```json
{
  "msg": "success",
  "data": {
    "key": "verification_hash"
  }
}
```

**第二步：验证码登录**
```json
POST /account/credentials/verify
{
  "type": "phone",
  "verificationKey": "verification_hash",
  "code": "123456"
}
```

**流程**:
```
客户端
  → [verificationKey, code]
  → CheckAccountSerializer.validate()
  → 从 Cache 提取 [phone_number, verification_id]
  → api_service().verification_login_second(phone, verification_id, code)
  → Duolingo 官方 API
  ← {jwt_token, user_id, username}
  → 储存到 Cache (3600秒过期)
  → 返回 {checkPassed: true, cacheKey: "hash"}
```

### 3. Token 直接验证

**请求**:
```json
POST /account/credentials/verify
{
  "type": "token",
  "token": "duolingo_jwt_token"
}
```

**流程**:
```
客户端
  → [token]
  → CheckAccountSerializer.validate()
  → api_service().get_uuid(token)
  → Duolingo 官方 API
  ← {uuid: "..."}
  → 储存到 Cache (3600秒过期)
  → 返回 {checkPassed: true, cacheKey: "hash"}
```

---

## 账户创建流程

### 通过 cacheKey 创建账户

**请求**:
```json
POST /account
{
  "cacheKey": "验证成功返回的 hash",
  "customerId": 1,
  "remark": "备注（可选）"
}
```

**流程**:
```
客户端
  → [cacheKey, customerId, remark]
  → WriteSerializer.validate()
  → 从 Cache 提取账户数据 [username, password, uuid, token]
  → 验证 Customer 是否存在
  → 获取当前用户的组织 (request.user.organization)
  → Account.objects.create(..., organization=organization)
  → 生成 account code (A20250315001)
  → 清除 Cache
  → 返回 {id, username, uuid}
```

---

## 与其他模块关系

### 1. 与 SM 模块的关系
| 维度 | SM.User | SM.Organization | Account |
|------|---------|-----------------|---------|
| 用途 | 系统管理员登录 | 组织管理 | Duolingo业务账号 |
| 认证方式 | 本地密码验证 | - | 第三方API验证 |
| Token类型 | JWT (SimpleJWT) | - | Duolingo JWT |
| 使用场景 | 后台管理 | 组织隔离 | 业务操作 |

**组织自动关联**:
- 创建账户时自动关联当前用户的组织
- 支持按组织进行数据隔离和权限控制

### 2. 与 APS 模块的关系
```python
# APS.Order 模型引用 Account
class Order(models.Model):
    account = models.ForeignKey('BDM.Account', on_delete=models.CASCADE)
    # 一个账号可以有多个订单
    # 订单完成需要更新账号的 exp/gems
```

### 3. 与 API.Duolingo 模块的关系
```python
# account 模块调用第三方API服务
from apps.API.Duolingo import service as api_service

mapper = api_service()
mapper.login(username, password)  # 登录验证
mapper.get_uuid(token)  # Token验证
mapper.get_user_data(uuid, token)  # 数据同步
```

---

## API 接口清单

### 认证验证类

| 端点 | 方法 | 说明 |
|------|------|------|
| `/account/credentials/verify` | POST | 统一账户验证（支持3种方式）|
| `/account/verification-codes` | POST | 发送验证码 |

### 账户管理类

| 端点 | 方法 | 说明 |
|------|------|------|
| `/account` | GET | 账户列表（分页、筛选，响应含 `disableFlag`）|
| `/account` | POST | 创建账户（通过 cacheKey，自动禁用同组织同 UUID 旧账户）|
| `/account/<id>` | GET | 账户详情同步（响应 `others` 含 `disableFlag`）|
| `/account/<id>` | PATCH | 更新账户信息 |
| `/account/<id>/disable` | PATCH | 禁用/启用账户（请求体 `{"disableFlag": true/false}`）|
| `/account/<id>/leaderboard` | GET | 获取排行榜数据（调用 `mapper.get_leaderboard()`）|
| `/account/simple` | GET | 账户简化列表（响应含 `disableFlag`）|
| `/account/enums` | GET | 账户枚举（下拉列表）|

### 禁用业务影响

- 禁用账户后，APS 订单模块的 `WriteSerializer` 和 `WriteV2Serializer` 会拒绝使用该账户创建订单
- 账户创建时，同组织内同 UUID 的旧账户自动设置 `disable_flag=True`

---

## 技术实现规范

### 序列化器规范

#### 命名规范
```python
# 列表序列化器
class ListSerializer(serializers.ModelSerializer):
   """账户列表序列化器"""
   # 字段使用驼峰型命名
   createdAt = serializers.SerializerMethodField()
   customerName = serializers.SerializerMethodField()

   def get_createdAt(self, obj):
      return common.to_local_time(str(obj.created_at))
```

#### 验证规范
```python
class CheckAccountSerializer(serializers.Serializer):
   """统一账户检查序列化器"""
   type = serializers.ChoiceField(choices=['username', 'phone', 'token'])

   def validate(self, data):
      # 验证逻辑
      # 验证成功后存储到 Cache
      cache.set(cache_key, account_data, timeout=3600)
      data['checkPassed'] = True
      data['cacheKey'] = hash_key
      return data
```

### 缓存使用规范

#### Cache Key 命名
```python
# 账户验证数据
'BDM:account:credentials:verify:{hash}'

# 验证码数据
'BDM:account:verification:code:{hash}'
```

#### 过期时间
- 账户验证数据：3600秒（1小时）
- 验证码数据：600秒（10分钟）

### 编码生成规范

```python
from utils.code_generator import generate_code

def save(self, *args, **kwargs):
   if not self.code:
      self.code = generate_code(Account, prefix='A')
   super().save(*args, **kwargs)
```

编码格式：`A` + `YYYYMMDD` + `序号`
示例：`A20250315001`

---

## 常见业务场景

### 场景1: 账号列表查询
**API**: `GET /account`

**查询参数**:
- `page`: 页码（默认0）
- `customer`: 客户筛选
- `phone`: 手机号筛选
- `name`: 用户名筛选
- `search`: 综合搜索

**返回格式**:
```json
{
  "msg": "success",
  "items": [...],
  "pagination": {
    "page": 0,
    "page_size": 10,
    "total": 100
  }
}
```

### 场景2: 账号数据同步
**API**: `GET /account/<id>`

**流程**:
1. 根据 id 查询本地 Account 记录
2. 调用 `mapper.get_user_data(uuid, token)` 获取最新数据
3. 更新本地字段: gems, exp, username, nickname, email, last_sign
4. 返回完整的用户数据

### 场景3: 新客户账号创建流程
```
1. POST /account/verification-codes
   → 发送验证码到手机

2. POST /account/credentials/verify (type=phone)
   → 验证手机号和验证码
   → 获得 cacheKey

3. POST /account
   → 使用 cacheKey + customerId 创建账户
   → 自动生成 account code
```

---

## 重要提醒

1. **Token 安全**: Duolingo JWT Token 有时效性，需定期刷新
2. **API限流**: 注意 Duolingo 官方 API 的调用频率限制
3. **密码加密**: 当前密码明文存储，生产环境需加密
4. **数据一致性**: gems/exp 等数据以官方 API 为准，本地数据仅作缓存
5. **缓存时效**: 验证数据和验证码都有时效性，过期需重新获取
6. **Code 唯一性**: 账户编码自动生成且唯一，不能手动修改

---

**最后更新**: 2026-04-09
**维护者**: 项目开发团队
