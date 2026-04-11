# SM 用户模块 (sm-user)

## 模块定位

SM（System Management）用户模块位于 `apps/SM/user/`，负责系统中统一用户模型的管理、飞书认证扩展、用户信号处理和异步任务。

### 在 SM 模块中的位置

```
SM 模块架构
├── user/              # 用户管理 ← 当前模块
│   ├── models.py      # User, UserFeishu 模型
│   ├── signals.py     # 用户信号处理器
│   ├── tasks.py       # 用户异步任务
│   ├── serializers.py # 用户序列化器
│   ├── views.py       # 用户视图
│   ├── urls.py        # 用户路由
│   └── utils.py       # 用户工具函数
├── role/              # 角色管理
├── code/              # 编码管理
└── approval/          # 审批流管理
```


## 模块职责边界

### 核心职责

1. **统一用户模型管理**：User 模型的 CRUD 操作
2. **飞书认证扩展**：UserFeishu 模型存储飞书 OAuth Token
3. **用户信号处理**：监听用户模型变化，触发自动化操作
4. **异步任务处理**：用户部门同步等异步操作

### 不负责的内容

- ❌ 用户认证流程由 SM/auth 模块负责
- ❌ 部门信息管理由 BDM/department 模块负责
- ❌ 飞书 API 调用由 utils/openapi/feishu 模块负责


## 核心数据模型

### 1. User 模型

统一用户模型，继承自 Django 的 AbstractUser，支持多种登录方式。

```python
class User(AbstractUser):
    # Django AbstractUser 内置字段
    username, email, password, is_staff, is_active, etc.

    # 飞书用户字段
    avatar = models.CharField(max_length=255)          # 头像URL
    nickname = models.CharField(max_length=255)        # 昵称
    mobile = models.CharField(max_length=255)          # 手机号
    nickname_pinyin = models.JSONField(default=list)  # 昵称拼音

    # 状态字段
    is_executive_core = models.BooleanField()          # 是否为核心决策者
    is_in_service = models.BooleanField()             # 是否在职
    uses = models.IntegerField()                      # 使用次数
    initial_password = models.BooleanField()          # 是否为初始密码
    disable_flag = models.BooleanField()              # 禁用标志
```

**Django AbstractUser 内置字段**：

| 字段 | 类型 | 说明 |
|-----|------|------|
| `username` | CharField | 用户名（唯一） |
| `email` | EmailField | 邮箱 |
| `password` | CharField | 密码哈希 |
| `is_staff` | BooleanField | 是否可访问 admin |
| `is_active` | BooleanField | 是否激活 |
| `is_superuser` | BooleanField | 是否超级用户 |
| `last_login` | DateTimeField | 最后登录时间 |
| `date_joined` | DateTimeField | 注册时间 |

### 2. UserFeishu 模型

飞书 OAuth Token 存储扩展模型，与 User 是 OneToOne 关系。

```python
class UserFeishu(models.Model):
    user = models.OneToOneField(User, ...)            # 关联用户
    open_id = models.CharField(max_length=255, unique=True)  # 飞书Open ID
    token_type = models.CharField(max_length=50)      # Token类型
    access_token = models.CharField(max_length=255)   # 访问令牌
    refresh_token = models.CharField(max_length=255)  # 刷新令牌
    expires_at = models.DateTimeField()               # 过期时间
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**关系说明**：

- 通过 `user.user_feishu` 可以获取用户的飞书 Token 信息
- `open_id` 是飞书用户的唯一标识，用于识别飞书用户


## 用户属性

### 1. open_id 属性

**位置**：`apps/SM/user/models.py:93`

```python
@property
def open_id(self):
    """
    返回飞书用户的open_id
    """
    return self.user_feishu.open_id if self.user_feishu else None
```

**用途**：
- 简化获取用户飞书 open_id
- 用于飞书 API 调用和权限验证

### 2. 🆕 department 属性（Since 2026-03-12）

**位置**：`apps/SM/user/models.py:100`

```python
@property
def department(self):
    """
    返回用户的部门信息列表
    从 UserDepartment 关联关系中获取部门信息
    返回格式: [{'id': 'feishu_dept_id', 'name': 'dept_name'}, ...]
    """
    try:
        from apps.BDM.department.models import UserDepartment
        depts = UserDepartment.objects.filter(user=self).select_related('department')
        return [
            {
                'id': ud.feishu_department_id,
                'name': ud.department.name
            }
            for ud in depts
        ]
    except:
        return []
```

**用途**：
- 简化用户部门信息获取
- 用于权限验证中的同部门判断
- 与旧系统 `feishu_users.department` 字段格式兼容

**返回格式**：
```python
[
    {'id': 'od_xxx', 'name': '部门名称'},
    {'id': 'od_yyy', 'name': '另一个部门名称'}
]
```


## 信号处理机制

### 1. handle_user_nickname_pinyin

监听 `User` 模型的 `pre_save` 事件，自动生成昵称拼音。

```python
# apps/SM/user/signals.py

@receiver(pre_save, sender=User)
def handle_user_nickname_pinyin(sender, instance, **kwargs):
    """
    监听 User 模型保存前事件，自动补充 nickname_pinyin 字段

    如果 nickname 存在但 nickname_pinyin 为空或默认值，则自动生成拼音
    """
    if instance.nickname:
        if (not instance.pk or
            instance.nickname_pinyin == list or
            not instance.nickname_pinyin):
            instance.nickname_pinyin = lazy_pinyin(instance.nickname)
```

**触发时机**：
- 新建用户且设置了 nickname
- 更新用户 nickname 且 nickname_pinyin 为空

### 2. handle_user_feishu_update

监听 `UserFeishu` 模型的 `post_save` 事件，触发用户部门同步。

```python
# apps/SM/user/signals.py

@receiver(post_save, sender=UserFeishu)
def handle_user_feishu_update(sender, instance, created, **kwargs):
    """
    监听 UserFeishu 模型保存后事件，触发部门同步

    当飞书用户登录时（UserFeishu 被创建或更新）：
    1. 触发异步任务获取用户的飞书部门信息
    2. 检查部门是否存在于 BDM.Department 表中
    3. 如果不存在，自动创建部门
    4. 创建 UserDepartment 关联关系
    """
    if not instance.open_id:
        return

    from apps.SM.user.tasks import sync_user_departments
    sync_user_departments.delay(user_id=instance.user.id, open_id=instance.open_id)
```

**触发时机**：
- 飞书用户首次登录（UserFeishu 创建）
- 飞书用户再次登录（UserFeishu 更新）

**触发条件**：
- `instance.open_id` 存在（有效飞书用户）


## 异步任务

### sync_user_departments

异步同步用户部门信息的 Celery 任务。

```python
# apps/SM/user/tasks.py

@shared_task(bind=True, max_retries=3)
def sync_user_departments(self, user_id: int, open_id: str):
    """
    同步用户部门信息的异步任务

    Args:
        user_id: 用户 ID
        open_id: 飞书用户的 open_id
    """
    from apps.SM.user.models import User
    from apps.BDM.department.models import Department, UserDepartment
    from utils.openapi.feishu.user_manager import FeishuUserManager

    try:
        # 1. 获取用户实例
        user = User.objects.filter(id=user_id).first()
        if not user:
            print(f'[SM] 用户 ID {user_id} 不存在，跳过部门同步')
            return

        # 2. 设置缓存防止重复执行（5分钟）
        cache_key = f'user_department_sync:{user_id}'
        if cache.get(cache_key):
            print(f'[SM] 用户 {user_id} 的部门同步任务正在执行中，跳过')
            return
        cache.set(cache_key, True, timeout=300)

        # 3. 获取用户的飞书部门信息
        departments = FeishuUserManager.get_user_departments(open_id)
        if not departments:
            print(f'[SM] 用户 {user_id} ({open_id}) 没有部门信息')
            return

        # 4. 同步部门到 BDM.Department 表并创建关联关系
        _sync_departments_and_create_relations(user, departments)

        print(f'[SM] 用户 {user_id} ({user.nickname or user.username}) 部门同步成功')

    except Exception as e:
        print(f'[SM] 同步用户 {user_id} 部门信息失败: {e}')
        raise self.retry(exc=e, countdown=60)
    finally:
        cache.delete(cache_key)
```

**任务特性**：

| 特性 | 说明 |
|-----|------|
| 重试机制 | 最多重试 3 次，重试间隔 60 秒 |
| 缓存锁 | 5分钟内防止同一用户的重复同步任务 |
| 异步执行 | 通过 Celery 异步队列执行 |
| 错误处理 | 失败时记录日志并重试 |

**日志输出格式**：
```
[SM] 用户 ID {user_id} 不存在，跳过部门同步
[SM] 用户 {user_id} 的部门同步任务正在执行中，跳过
[SM] 用户 {user_id} ({open_id}) 没有部门信息
[SM] 自动创建部门: {dept_name} (ID: {dept_id})
[SM] 更新部门名称: {dept_id} -> {dept_name}
[SM] 创建用户部门关联: {username} -> {dept_name}
[SM] 用户 {user_id} ({username}) 部门同步成功
[SM] 同步用户 {user_id} 部门信息失败: {error}
```


## 用户与部门关联流程

### 完整流程图

```
飞书用户登录
    ↓
apps/API/auth/utils.py::process_feishu_userinfo()
    ├── 创建/更新 User 模型
    └── 创建/更新 UserFeishu 模型
    ↓
UserFeishu.post_save 信号触发
    ↓
apps/SM/user/signals.py::handle_user_feishu_update()
    ↓
异步任务: sync_user_departments.delay()
    ↓
apps/SM/user/tasks.py::sync_user_departments()
    ├── 缓存检查
    ├── FeishuUserManager.get_user_departments()
    └── _sync_departments_and_create_relations()
        ├── 检查/创建 Department 记录
        └── 创建 UserDepartment 关联
```

### 数据流

```
飞书 API
    ↓
FeishuUserManager.get_user_departments()
    ↓
{'id': 'od_xxx', 'name': '部门名称'}
    ↓
_sync_departments_and_create_relations()
    ├── Department.objects.get_or_create(code='od_xxx')
    └── UserDepartment.objects.create()
```


## 文件结构

```
apps/SM/user/
├── __init__.py
├── enums.py          # 枚举定义
├── models.py         # User, UserFeishu 模型
├── signals.py        # 信号处理器
├── tasks.py          # 异步任务
├── serializers.py    # 序列化器
├── urls.py           # 路由配置
├── utils.py          # 工具函数
└── views.py          # 视图
```


## 使用示例

### 获取用户的飞书 Token

```python
user = User.objects.get(id=1)
feishu_token = user.user_feishu

if feishu_token:
    print(f"Open ID: {feishu_token.open_id}")
    print(f"Access Token: {feishu_token.access_token}")
```

### 🆕 获取用户的部门信息（Since 2026-03-12）

```python
user = User.objects.get(id=1)
departments = user.department

for dept in departments:
    print(f"部门ID: {dept['id']}, 部门名称: {dept['name']}")
```

### 查询用户的所有部门

```python
user = User.objects.get(id=1)
user_depts = user.user_departments.all()

for ud in user_depts:
    print(f"部门: {ud.department.name}, 是否负责人: {ud.is_leader}")
```

### 手动触发部门同步

```python
from apps.SM.user.tasks import sync_user_departments

# 同步用户部门
sync_user_departments.delay(user_id=1, open_id='ou_xxx')
```


## 特有名词索引

当以下名词出现时，应关联到此技能：

| 名词 | 说明 |
|------|------|
| **User** | 统一用户模型 |
| **UserFeishu** | 飞书 Token 扩展模型 |
| **open_id** | 飞书用户唯一标识 |
| **access_token** | 飞书访问令牌 |
| **refresh_token** | 飞书刷新令牌 |
| **handle_user_nickname_pinyin** | 用户昵称拼音生成信号 |
| **handle_user_feishu_update** | 飞书用户更新信号（触发部门同步） |
| **sync_user_departments** | 异步同步用户部门任务 |
| **user_departments** | User 模型的部门关联字段 |
| **nickname_pinyin** | 昵称拼音字段 |
| 🆕 **User.department** | 🆕 用户模型的部门属性（Since 2026-03-12） |


## 相关技能

- **bdm-department**：BDM 部门管理模块（Department, UserDepartment 模型）
- **utils-feishu-user_manager**：飞书用户管理器（获取部门信息）
- **user-token-management**：PMS 用户认证与飞书 Token 管理
- **sm-auth**：SM 认证模块（登录流程）
