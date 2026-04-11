---
name: utils-feishu-user_manager
description: 飞书用户管理器专家，封装飞书开放平台用户信息获取相关API调用。当用户提到"飞书用户"、"FeishuUserManager"、"get_user_info"、"batch_get_user_info"、"get_user_departments"、"open_id"、"飞书用户信息"、"批量获取用户"或相关术语时激活此技能。
---

# 飞书用户管理器 (FeishuUserManager)

## 模块定位

`FeishuUserManager` 是 PMS 系统中飞书开放平台集成的核心工具类之一，位于 `utils/openapi/feishu/user_manager.py`，负责封装所有飞书用户信息相关的 API 调用逻辑。

### 在飞书集成生态中的位置

```
飞书开放平台集成架构
├── FeishuTokenManager      # Token管理（tenant/user/app token）
├── FeishuAuthManager       # 认证管理（授权码换取token）
├── FeishuUserManager       # 用户管理（用户信息获取）← 当前模块
├── FeishuFileManager       # 文件管理
└── FeishuSheetManager      # 电子表格管理
```

---

## 模块职责边界

### 核心职责

1. **用户信息获取**：通过 access_token 获取飞书用户详细信息
2. **批量用户查询**：一次性获取多个用户的信息
3. **用户部门信息获取** 🆕：获取用户所属部门列表（Since 2026-03-07）
4. **API 错误处理**：统一处理飞书 API 的各类错误响应
5. **网络请求封装**：统一超时、重试等网络策略

### 不负责的内容

- ❌ Token 管理由 `FeishuTokenManager` 负责
- ❌ 用户认证流程由 `FeishuAuthManager` 负责
- ❌ 用户数据持久化由业务层负责
- ❌ 文件上传下载由 `FeishuFileManager` 负责

---

## 核心数据模型

### 飞书用户信息结构

```python
{
    'nickname': '张三',        # 用户昵称
    'avatar': 'https://...',   # 头像URL
    'mobile': '13800138000',   # 手机号
    'open_id': 'ou_xxx'        # 飞书用户唯一标识
}
```

### 飞书部门信息结构 🆕

```python
{
    'id': 'od_xxx',           # 飞书部门 open_department_id
    'name': '部门名称'         # 部门名称
}
```

### API 响应状态（批量查询）

```python
{
    'status': 'SUCCESS' | 'ERROR' | 'INCORRECT',
    'data': [...]  # 用户列表或错误ID列表
}
```

---

## 核心API方法

### 1. get_user_info(token: str) -> Optional[Dict]

获取单个用户信息，通过用户授权的 access_token 调用。

**调用链路**：
```
前端飞书登录 → 获取授权码
    ↓
FeishuAuthManager.exchange_code(code) → 换取 access_token
    ↓
FeishuUserManager.get_user_info(token) → 获取用户信息
    ↓
业务层处理用户数据（创建/更新 User 模型）
```

**使用示例**：
```python
from utils.openapi.feishu import FeishuUserManager

token = "Bearer xxx"
userinfo = FeishuUserManager.get_user_info(token)
if userinfo:
    print(f"用户昵称: {userinfo['nickname']}")
    print(f"Open ID: {userinfo['open_id']}")
```

### 2. batch_get_user_info(user_ids: List[str], access_token: Optional[str] = None) -> Dict

批量获取用户信息，支持通过 open_id 列表查询多个用户。

**状态说明**：
- `SUCCESS`：所有用户查询成功
- `ERROR`：API 调用失败
- `INCORRECT`：部分用户 ID 无效（data 字段包含无效 ID 列表）

**使用示例**：
```python
result = FeishuUserManager.batch_get_user_info(['ou_xxx', 'ou_yyy'])
if result['status'] == 'SUCCESS':
    for user in result['data']:
        print(f"{user['name']}: {user['open_id']}")
```

### 3. get_user_departments(open_id: str, access_token: Optional[str] = None) -> Optional[List[Dict]] 🆕

获取用户的部门信息，采用两步请求策略。

**两步请求策略**：
```
第一步：GET /contact/v3/users/{open_id}
    ↓
获取 department_ids 列表
    ↓
第二步：GET /contact/v3/departments/{department_id} (逐个请求)
    ↓
返回部门信息列表
```

**API 端点**：
- 用户信息：`https://open.feishu.cn/open-apis/contact/v3/users/{open_id}`
- 部门详情：`https://open.feishu.cn/open-apis/contact/v3/departments/{department_id}`

**使用示例**：
```python
departments = FeishuUserManager.get_user_departments('ou_xxx')
# 返回: [
#     {'id': 'od-ab811b623c0bd593bf4444c2a2542a0e', 'name': '研发部'},
#     {'id': 'od-44d1d6119b61e1ca7673a27611606b1c', 'name': '技术部'}
# ]
```

**数据映射关系**：
| 飞书 API 字段 | 返回字典字段 | 说明 |
|--------------|-------------|------|
| `open_department_id` | `id` | 飞书部门唯一标识 |
| `name` | `name` | 部门名称 |

**错误处理**：
- 用户无部门信息时返回空列表 `[]`
- 单个部门获取失败时跳过该部门，继续处理其他部门

---

## 与业务模块的集成

### 登录认证流程

```python
# apps/SM/auth/serializers.py

def _validate_feishu_request_access(self, code):
    # 1. 授权码换取 token
    token_data = FeishuAuthManager.exchange_code(code)

    # 2. 获取用户信息
    token_str = FeishuAuthManager.format_token(
        token_data['token_type'],
        token_data['access_token']
    )
    userinfo = FeishuUserManager.get_user_info(token_str)

    # 3. 业务层处理用户数据
    success, user_instance = _process_feishu_userinfo(token_data, userinfo)
    return user_instance
```

### 用户部门同步流程 🆕

```python
# apps/SM/user/signals.py

@receiver(post_save, sender=UserFeishu)
def handle_user_feishu_update(sender, instance, created, **kwargs):
    """
    飞书用户登录时触发部门同步
    """
    if instance.open_id:
        from apps.SM.user.tasks import sync_user_departments
        sync_user_departments.delay(user_id=instance.user.id, open_id=instance.open_id)

# apps/SM/user/tasks.py

@shared_task
def sync_user_departments(user_id: int, open_id: str):
    """
    异步同步用户部门信息：
    1. 调用 FeishuUserManager.get_user_departments(open_id)
    2. 检查部门是否存在于 BDM.Department 表
    3. 不存在则自动创建
    4. 创建 UserDepartment 关联关系
    """
    departments = FeishuUserManager.get_user_departments(open_id)
    # ... 处理部门同步逻辑
```

### 用户数据模型映射

飞书用户信息 → PMS User 模型：

| 飞书字段 | User 模型字段 | 说明 |
|---------|--------------|------|
| `name` | `nickname` | 用户昵称 |
| `avatar_url` | `avatar` | 头像URL |
| `mobile` | `mobile` | 手机号 |
| `open_id` | `UserFeishu.open_id` | 飞书唯一标识（存到扩展表） |

飞书部门信息 → PMS BDM 模块 🆕：

| 飞书字段 | BDM 模型字段 | 说明 |
|---------|-------------|------|
| `open_department_id` | `Department.code` | 部门唯一标识 |
| `name` | `Department.name` | 部门名称 |
| `open_department_id` | `UserDepartment.feishu_department_id` | 用户部门关联表 |

---

## 错误处理机制

### HTTP 错误

```python
if response.status_code != 200:
    print(f'[FeishuUserManager] HTTP 错误: {response.status_code}')
    return None
```

### API 业务错误

```python
if response.get('code') != 0:
    print(f'[FeishuUserManager] API 错误: {response}')
    return None
```

### 网络异常

```python
except requests.RequestException as e:
    print(f'[FeishuUserManager] 网络请求错误: {e}')
    return None
```

### 错误码参考

| 错误码 | 含义 | 处理建议 |
|-------|------|---------|
| 99992351 | 部分用户 ID 无效 | 检查返回的 field_violations 列表 |
| 0 | 成功 | 正常处理 |
| 其他 | API 错误 | 记录日志，返回错误状态 |

---

## 技术实现建议

### 1. 日志输出规范 🆕

不再使用 `logger`，改用 `print` 输出，格式为 `[FeishuUserManager] ...`：

```python
print(f'[FeishuUserManager] 获取用户信息 HTTP 错误: {response.status_code}')
print(f'[FeishuUserManager] 用户 {open_id} 没有部门信息')
print(f'[FeishuUserManager] 获取部门信息网络请求错误: {e}, dept_id: {department_id}')
```

### 2. 超时设置

```python
response = requests.get(url, headers=headers, timeout=10)
```

统一设置 10 秒超时，防止长时间阻塞。

### 3. 返回值设计

- 单个用户查询失败返回 `None`
- 批量查询返回统一格式的状态字典
- 部门查询无结果时返回空列表 `[]`（非 `None`）

### 4. 部门信息容错处理 🆕

当获取单个部门信息失败时，跳过该部门继续处理：

```python
for dept_id in department_ids:
    dept_info = cls._get_department_info(dept_id, headers)
    if dept_info:  # 仅在成功时添加
        departments.append(dept_info)
```

---

## API 端点参考

| 端点常量 | URL | 用途 |
|---------|-----|------|
| `_ENDPOINT_USER_INFO` | `/open-apis/authen/v1/user_info` | 获取用户基本信息（OAuth） |
| `_ENDPOINT_BATCH_GET_USER` | `/open-apis/contact/v3/users/batch` | 批量获取用户信息 |
| `_ENDPOINT_GET_USER` | `/open-apis/contact/v3/users` | 获取用户详细信息 |
| `_ENDPOINT_GET_DEPARTMENT` 🆕 | `/open-apis/contact/v3/departments` | 获取部门详情 |

---

## 特有名词索引

当以下名词出现时，应关联到此技能：

| 名词 | 说明 |
|------|------|
| **FeishuUserManager** | 飞书用户管理器类 |
| **get_user_info** | 获取单个飞书用户信息的方法 |
| **batch_get_user_info** | 批量获取飞书用户信息的方法 |
| **get_user_departments** 🆕 | 获取用户部门信息的方法 |
| **open_id** | 飞书用户的唯一标识符 |
| **department_ids** 🆕 | 用户所属部门 ID 列表 |
| **open_department_id** 🆕 | 飞书部门的唯一标识符 |
| **nickname** | 飞书用户昵称 |
| **avatar** | 飞书用户头像URL |
| **mobile** | 飞书用户手机号 |
| **field_violations** | 批量查询时的无效字段列表 |

---

## 相关技能

- **FeishuTokenManager**：飞书 Token 管理
- **FeishuAuthManager**：飞书认证管理
- **user-token-management**：PMS 用户认证与飞书 Token 管理
- **bdm-department** 🆕：BDM 部门管理模块（UserDepartment 模型）
- **sm-user** 🆕：SM 用户模块（信号和异步任务）
